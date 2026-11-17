package com.interviewrecall;

import jakarta.persistence.*;
import java.time.*;

@Entity
@Table(name = "users")
class Account {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  Long id;

  @Column(nullable = false, unique = true, length = 254)
  String email;

  @Column(nullable = false)
  String passwordHash;

  @Column(nullable = false, length = 80)
  String name;

  int dailyGoal = 5;
  String zoneId = "UTC";
}

@Entity
@Table(name = "problems", indexes = @Index(columnList = "owner_id,nextReviewOn"))
class Problem {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  Long id;

  @ManyToOne(optional = false, fetch = FetchType.LAZY)
  Account owner;

  @Column(nullable = false, length = 180)
  String title;

  @Column(length = 2048)
  String url;

  String platform, difficulty, topic;

  @Column(length = 10000)
  String notes;

  @Column(length = 10000)
  String approach;

  int confidence = 50, intervalDays = 1, repetitions = 0;
  double ease = 2.5;
  LocalDate solvedOn, nextReviewOn;
}

@Entity
@Table(name = "revisions", indexes = @Index(columnList = "owner_id,reviewedAt"))
class Revision {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  Long id;

  @ManyToOne(optional = false, fetch = FetchType.LAZY)
  Account owner;

  @ManyToOne(optional = false, fetch = FetchType.LAZY)
  Problem problem;

  int grade, intervalDays;
  Instant reviewedAt;
  LocalDate scheduledOn;
}
