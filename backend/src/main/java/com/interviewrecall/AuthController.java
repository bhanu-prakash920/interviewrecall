package com.interviewrecall;

import static org.springframework.http.HttpStatus.*;

import jakarta.servlet.http.*;
import jakarta.validation.Valid;
import java.security.Principal;
import java.time.ZoneId;
import java.util.*;
import org.springframework.security.authentication.*;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.authentication.session.SessionAuthenticationStrategy;
import org.springframework.security.web.context.SecurityContextRepository;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/auth")
class AuthController {
  private final AccountRepository accounts;
  private final PasswordEncoder encoder;
  private final AuthenticationManager manager;
  private final SecurityContextRepository contexts;
  private final SessionAuthenticationStrategy sessions;

  AuthController(
      AccountRepository a,
      PasswordEncoder e,
      AuthenticationManager m,
      SecurityContextRepository c,
      SessionAuthenticationStrategy s) {
    accounts = a;
    encoder = e;
    manager = m;
    contexts = c;
    sessions = s;
  }

  @GetMapping("/csrf")
  Map<String, String> csrf(CsrfToken token) {
    return Map.of("token", token.getToken());
  }

  @PostMapping("/register")
  @ResponseStatus(CREATED)
  @Transactional
  Dtos.UserView register(@Valid @RequestBody Dtos.Register d) {
    String email = d.email().trim().toLowerCase(Locale.ROOT);
    if (accounts.findByEmail(email).isPresent())
      throw new ResponseStatusException(CONFLICT, "An account with this email already exists");
    ZoneId.of(d.zoneId());
    Account a = new Account();
    a.email = email;
    a.name = d.name().trim();
    a.zoneId = d.zoneId();
    a.passwordHash = encoder.encode(d.password());
    return Dtos.UserView.of(accounts.saveAndFlush(a));
  }

  @PostMapping("/login")
  Map<String, String> login(
      @Valid @RequestBody Dtos.Login d, HttpServletRequest request, HttpServletResponse response) {
    var auth =
        manager.authenticate(
            UsernamePasswordAuthenticationToken.unauthenticated(
                d.email().trim().toLowerCase(Locale.ROOT), d.password()));
    sessions.onAuthentication(auth, request, response);
    var context = SecurityContextHolder.createEmptyContext();
    context.setAuthentication(auth);
    SecurityContextHolder.setContext(context);
    contexts.saveContext(context, request, response);
    return Map.of("message", "Signed in");
  }

  @GetMapping("/me")
  Dtos.UserView me(Principal p) {
    return Dtos.UserView.of(account(p));
  }

  @PutMapping("/preferences")
  @Transactional
  Dtos.UserView preferences(Principal p, @Valid @RequestBody Dtos.Preferences d) {
    ZoneId.of(d.zoneId());
    Account a = account(p);
    a.name = d.name().trim();
    a.dailyGoal = d.dailyGoal();
    a.zoneId = d.zoneId();
    return Dtos.UserView.of(accounts.save(a));
  }

  private Account account(Principal p) {
    if (p == null) throw new ResponseStatusException(UNAUTHORIZED, "Please sign in");
    return accounts
        .findByEmail(p.getName())
        .orElseThrow(() -> new ResponseStatusException(UNAUTHORIZED, "Please sign in"));
  }
}
