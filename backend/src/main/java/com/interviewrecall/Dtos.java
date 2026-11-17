package com.interviewrecall;

import jakarta.validation.constraints.*;
import java.time.*;

class Dtos {
  record Register(
      @NotBlank @Size(max = 80) String name,
      @NotBlank @Email @Size(max = 254) String email,
      @NotBlank @Size(min = 8, max = 72) String password,
      @NotBlank String zoneId) {}

  record Login(@NotBlank @Email String email, @NotBlank @Size(max = 72) String password) {}

  record Preferences(
      @NotBlank @Size(max = 80) String name,
      @Min(1) @Max(50) int dailyGoal,
      @NotBlank String zoneId) {}

  record UserView(String name, String email, int dailyGoal, String zoneId) {
    static UserView of(Account a) {
      return new UserView(a.name, a.email, a.dailyGoal, a.zoneId);
    }
  }

  record ProblemInput(
      @NotBlank @Size(max = 180) String title,
      @NotBlank
          @Size(max = 2048)
          @Pattern(regexp = "https?://.+", message = "Use an HTTP or HTTPS problem URL")
          String url,
      @NotBlank @Size(max = 80) String platform,
      @Pattern(regexp = "Easy|Medium|Hard") @NotNull String difficulty,
      @NotBlank @Size(max = 80) String topic,
      @Size(max = 10000) String notes,
      @NotBlank @Size(max = 10000) String approach) {}

  record ProblemView(
      Long id,
      String title,
      String url,
      String platform,
      String difficulty,
      String topic,
      String notes,
      String approach,
      int confidence,
      int intervalDays,
      int repetitions,
      double ease,
      LocalDate solvedOn,
      LocalDate nextReviewOn) {
    static ProblemView of(Problem p) {
      return new ProblemView(
          p.id,
          p.title,
          p.url,
          p.platform,
          p.difficulty,
          p.topic,
          p.notes,
          p.approach,
          p.confidence,
          p.intervalDays,
          p.repetitions,
          p.ease,
          p.solvedOn,
          p.nextReviewOn);
    }
  }

  record Grade(@Min(0) @Max(3) int grade) {}

  record RevisionView(Long id, Long problemId, int grade, Instant reviewedAt, int intervalDays) {
    static RevisionView of(Revision r) {
      return new RevisionView(r.id, r.problem.id, r.grade, r.reviewedAt, r.intervalDays);
    }
  }
}
