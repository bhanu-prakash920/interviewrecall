package com.interviewrecall;

import java.time.DateTimeException;
import java.util.Map;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.*;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestControllerAdvice
class ApiErrors {
  @ExceptionHandler(ResponseStatusException.class)
  ResponseEntity<?> status(ResponseStatusException e) {
    return ResponseEntity.status(e.getStatusCode())
        .body(Map.of("message", e.getReason() == null ? "Request failed" : e.getReason()));
  }

  @ExceptionHandler(MethodArgumentNotValidException.class)
  ResponseEntity<?> validation(MethodArgumentNotValidException e) {
    return ResponseEntity.badRequest()
        .body(
            Map.of(
                "message",
                e.getBindingResult().getFieldErrors().stream()
                    .map(f -> f.getField() + ": " + f.getDefaultMessage())
                    .findFirst()
                    .orElse("Check your input")));
  }

  @ExceptionHandler(AuthenticationException.class)
  ResponseEntity<?> auth() {
    return ResponseEntity.status(401).body(Map.of("message", "Invalid email or password"));
  }

  @ExceptionHandler({
    DateTimeException.class,
    IllegalArgumentException.class,
    HttpMessageNotReadableException.class
  })
  ResponseEntity<?> input() {
    return ResponseEntity.badRequest()
        .body(Map.of("message", "Invalid input. Check your fields and timezone."));
  }

  @ExceptionHandler(DataIntegrityViolationException.class)
  ResponseEntity<?> conflict() {
    return ResponseEntity.status(409)
        .body(
            Map.of("message", "This record already exists or was changed. Refresh and try again."));
  }
}
