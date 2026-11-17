package com.interviewrecall;

import java.util.List;
import org.springframework.context.annotation.*;
import org.springframework.security.authentication.*;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.*;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.session.*;
import org.springframework.security.web.context.*;
import org.springframework.security.web.csrf.*;

@Configuration
class SecurityConfig {
  @Bean
  PasswordEncoder encoder() {
    return new BCryptPasswordEncoder();
  }

  @Bean
  UserDetailsService users(AccountRepository accounts) {
    return email ->
        accounts
            .findByEmail(email.toLowerCase(java.util.Locale.ROOT).trim())
            .map(a -> User.withUsername(a.email).password(a.passwordHash).roles("USER").build())
            .orElseThrow(() -> new UsernameNotFoundException("Invalid email or password"));
  }

  @Bean
  AuthenticationManager authenticationManager(UserDetailsService users, PasswordEncoder encoder) {
    var provider = new DaoAuthenticationProvider();
    provider.setUserDetailsService(users);
    provider.setPasswordEncoder(encoder);
    return new ProviderManager(provider);
  }

  @Bean
  SecurityContextRepository contextRepository() {
    return new HttpSessionSecurityContextRepository();
  }

  @Bean
  CsrfTokenRepository csrfRepository() {
    return new HttpSessionCsrfTokenRepository();
  }

  @Bean
  SessionAuthenticationStrategy sessionStrategy(CsrfTokenRepository csrf) {
    return new CompositeSessionAuthenticationStrategy(
        List.of(new ChangeSessionIdAuthenticationStrategy(), new CsrfAuthenticationStrategy(csrf)));
  }

  @Bean
  SecurityFilterChain security(
      HttpSecurity http, SecurityContextRepository contexts, CsrfTokenRepository csrf)
      throws Exception {
    var handler = new CsrfTokenRequestAttributeHandler();
    handler.setCsrfRequestAttributeName("_csrf");
    return http.csrf(c -> c.csrfTokenRepository(csrf).csrfTokenRequestHandler(handler))
        .securityContext(c -> c.securityContextRepository(contexts))
        .authorizeHttpRequests(
            a ->
                a.requestMatchers(
                        "/api/auth/csrf", "/api/auth/register", "/api/auth/login", "/error")
                    .permitAll()
                    .anyRequest()
                    .authenticated())
        .exceptionHandling(
            e ->
                e.authenticationEntryPoint(
                        (req, res, ex) -> {
                          res.setStatus(401);
                          res.setContentType("application/json");
                          res.getWriter().write("{\"message\":\"Please sign in to continue\"}");
                        })
                    .accessDeniedHandler(
                        (req, res, ex) -> {
                          res.setStatus(403);
                          res.setContentType("application/json");
                          res.getWriter()
                              .write(
                                  "{\"message\":\"Session security check failed. Refresh and try again.\"}");
                        }))
        .logout(
            l ->
                l.logoutUrl("/api/auth/logout")
                    .logoutSuccessHandler((req, res, auth) -> res.setStatus(204))
                    .invalidateHttpSession(true)
                    .deleteCookies("JSESSIONID"))
        .build();
  }
}
