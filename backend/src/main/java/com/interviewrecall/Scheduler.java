package com.interviewrecall;

import java.time.*;

public final class Scheduler {
  public record Result(int intervalDays, int repetitions, double ease, LocalDate nextReviewOn) {}

  public static Result next(
      int previous, int repetitions, double ease, int grade, LocalDate today) {
    if (grade < 0 || grade > 3)
      throw new IllegalArgumentException("Recall grade must be between 0 and 3");
    int days;
    if (grade == 0) {
      days = 1;
      repetitions = 0;
      ease = Math.max(1.3, ease - .2);
    } else if (grade == 1) {
      days = Math.max(1, (int) Math.round(previous * 1.2));
      ease = Math.max(1.3, ease - .15);
    } else if (grade == 2) {
      days = repetitions == 0 ? 1 : repetitions == 1 ? 6 : (int) Math.round(previous * ease);
      repetitions++;
    } else {
      days =
          repetitions == 0 ? 4 : Math.max(previous + 1, (int) Math.round(previous * (ease + .3)));
      ease = Math.min(3, ease + .15);
      repetitions++;
    }
    days = Math.min(365, Math.max(1, days));
    return new Result(days, repetitions, ease, today.plusDays(days));
  }
}
