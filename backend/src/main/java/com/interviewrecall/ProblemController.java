package com.interviewrecall;

import jakarta.validation.Valid;
import java.security.Principal;
import java.util.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
class ProblemController {
  private final ProblemService service;

  ProblemController(ProblemService s) {
    service = s;
  }

  @GetMapping("/problems")
  List<Dtos.ProblemView> list(Principal p) {
    return service.list(p.getName());
  }

  @PostMapping("/problems")
  @ResponseStatus(org.springframework.http.HttpStatus.CREATED)
  Dtos.ProblemView add(Principal p, @Valid @RequestBody Dtos.ProblemInput d) {
    return service.save(p.getName(), null, d);
  }

  @PutMapping("/problems/{id}")
  Dtos.ProblemView update(
      Principal p, @PathVariable Long id, @Valid @RequestBody Dtos.ProblemInput d) {
    return service.save(p.getName(), id, d);
  }

  @DeleteMapping("/problems/{id}")
  @ResponseStatus(org.springframework.http.HttpStatus.NO_CONTENT)
  void delete(Principal p, @PathVariable Long id) {
    service.delete(p.getName(), id);
  }

  @PostMapping("/problems/{id}/reviews")
  Dtos.ProblemView review(Principal p, @PathVariable Long id, @Valid @RequestBody Dtos.Grade d) {
    return service.review(p.getName(), id, d.grade());
  }

  @GetMapping("/revisions")
  List<Dtos.RevisionView> history(Principal p) {
    return service.history(p.getName());
  }
}
