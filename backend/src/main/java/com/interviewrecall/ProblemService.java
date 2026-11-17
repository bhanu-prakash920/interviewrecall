package com.interviewrecall;

import static org.springframework.http.HttpStatus.*;

import java.time.*;
import java.util.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional
class ProblemService {
  private final AccountRepository accounts;
  private final ProblemRepository problems;
  private final RevisionRepository revisions;

  ProblemService(AccountRepository a, ProblemRepository p, RevisionRepository r) {
    accounts = a;
    problems = p;
    revisions = r;
  }

  Account account(String email) {
    return accounts
        .findByEmail(email)
        .orElseThrow(() -> new ResponseStatusException(UNAUTHORIZED, "Please sign in"));
  }

  Problem owned(Long id, Account a) {
    return problems
        .findByIdAndOwnerId(id, a.id)
        .orElseThrow(() -> new ResponseStatusException(NOT_FOUND, "Problem not found"));
  }

  @Transactional(readOnly = true)
  List<Dtos.ProblemView> list(String email) {
    return problems.findAllByOwnerIdOrderByNextReviewOnAsc(account(email).id).stream()
        .map(Dtos.ProblemView::of)
        .toList();
  }

  Dtos.ProblemView save(String email, Long id, Dtos.ProblemInput d) {
    Account a = account(email);
    Problem p = id == null ? new Problem() : owned(id, a);
    if (id == null) {
      p.owner = a;
      p.solvedOn = LocalDate.now(ZoneId.of(a.zoneId));
      p.nextReviewOn = p.solvedOn.plusDays(1);
    }
    p.title = d.title().trim();
    p.url = d.url();
    p.platform = d.platform();
    p.difficulty = d.difficulty();
    p.topic = d.topic();
    p.notes = d.notes();
    p.approach = d.approach();
    return Dtos.ProblemView.of(problems.save(p));
  }

  void delete(String email, Long id) {
    Problem p = owned(id, account(email));
    revisions.deleteAllByProblemId(id);
    revisions.flush();
    problems.delete(p);
  }

  Dtos.ProblemView review(String email, Long id, int grade) {
    Account a = account(email);
    Problem p =
        problems
            .lockOwned(id, a.id)
            .orElseThrow(() -> new ResponseStatusException(NOT_FOUND, "Problem not found"));
    LocalDate today = LocalDate.now(ZoneId.of(a.zoneId));
    var result = Scheduler.next(p.intervalDays, p.repetitions, p.ease, grade, today);
    Revision r = new Revision();
    r.owner = a;
    r.problem = p;
    r.grade = grade;
    r.reviewedAt = Instant.now();
    r.scheduledOn = p.nextReviewOn;
    r.intervalDays = result.intervalDays();
    revisions.save(r);
    p.intervalDays = result.intervalDays();
    p.repetitions = result.repetitions();
    p.ease = result.ease();
    p.nextReviewOn = result.nextReviewOn();
    p.confidence = new int[] {20, 45, 75, 95}[grade];
    return Dtos.ProblemView.of(p);
  }

  @Transactional(readOnly = true)
  List<Dtos.RevisionView> history(String email) {
    return revisions.findAllByOwnerIdOrderByReviewedAtDesc(account(email).id).stream()
        .map(Dtos.RevisionView::of)
        .toList();
  }
}
