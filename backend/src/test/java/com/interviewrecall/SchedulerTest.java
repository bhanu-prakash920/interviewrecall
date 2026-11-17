package com.interviewrecall;

import static org.junit.jupiter.api.Assertions.*;

import java.time.*;
import org.junit.jupiter.api.Test;

class SchedulerTest {
  final LocalDate date = LocalDate.of(2026, 12, 31);

  @Test
  void forgottenResetsAndCrossesYearBoundary() {
    var r = Scheduler.next(30, 5, 1.3, 0, date);
    assertEquals(1, r.intervalDays());
    assertEquals(0, r.repetitions());
    assertEquals(1.3, r.ease());
    assertEquals(LocalDate.of(2027, 1, 1), r.nextReviewOn());
  }

  @Test
  void goodUsesLearningSteps() {
    assertEquals(1, Scheduler.next(1, 0, 2.5, 2, date).intervalDays());
    assertEquals(6, Scheduler.next(1, 1, 2.5, 2, date).intervalDays());
    assertEquals(15, Scheduler.next(6, 2, 2.5, 2, date).intervalDays());
  }

  @Test
  void hardPreservesRepetitionsAndEaseFloor() {
    var r = Scheduler.next(6, 2, 1.3, 1, date);
    assertEquals(7, r.intervalDays());
    assertEquals(2, r.repetitions());
    assertEquals(1.3, r.ease());
  }

  @Test
  void easyAcceleratesAndCaps() {
    assertEquals(4, Scheduler.next(1, 0, 2.5, 3, date).intervalDays());
    var r = Scheduler.next(200, 5, 3, 3, date);
    assertEquals(365, r.intervalDays());
    assertEquals(3, r.ease());
  }

  @Test
  void lateReviewsStartFromCurrentDate() {
    assertEquals(date.plusDays(15), Scheduler.next(6, 2, 2.5, 2, date).nextReviewOn());
  }

  @Test
  void invalidGradeRejected() {
    assertThrows(IllegalArgumentException.class, () -> Scheduler.next(1, 0, 2.5, 4, date));
  }

  @Test
  void localDateCanDifferFromUtc() {
    Instant instant = Instant.parse("2026-12-31T23:30:00Z");
    LocalDate india = instant.atZone(ZoneId.of("Asia/Kolkata")).toLocalDate();
    assertEquals(LocalDate.of(2027, 1, 2), Scheduler.next(1, 0, 2.5, 0, india).nextReviewOn());
  }
}
