package com.interviewrecall;

import java.time.*;
import java.util.List;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/** Explicit local presentation fixture. Ordinary application startup does not create this account. */
@Component
@Profile("presentation")
class PresentationData implements ApplicationRunner {
  static final String EMAIL = "demo@interviewrecall.test";
  static final String PASSWORD = "Recall@123456";
  private final AccountRepository accounts;
  private final ProblemRepository problems;
  private final RevisionRepository revisions;
  private final PasswordEncoder encoder;

  PresentationData(AccountRepository accounts, ProblemRepository problems,
      RevisionRepository revisions, PasswordEncoder encoder) {
    this.accounts = accounts;
    this.problems = problems;
    this.revisions = revisions;
    this.encoder = encoder;
  }

  @Override
  @Transactional
  public void run(ApplicationArguments arguments) {
    // Do not overwrite an existing account, reset its password, or duplicate its fixtures.
    if (accounts.findByEmail(EMAIL).isPresent()) return;
    Account account = new Account();
    account.email = EMAIL;
    account.name = "Bhanu Prakash Kusha";
    account.passwordHash = encoder.encode(PASSWORD);
    account.zoneId = "Asia/Kolkata";
    account.dailyGoal = 5;
    accounts.save(account);
    LocalDate today = LocalDate.now(ZoneId.of(account.zoneId));
    List<Sample> samples = List.of(
        new Sample("Two Sum", "two-sum", "Easy", "Arrays",
            "Store previously visited values and their indices in a hash map. For each value, check target minus value before inserting. Time O(n), space O(n).",
            "Check the complement before inserting so the same element is not used twice.", -1, 75),
        new Sample("Longest Substring Without Repeating Characters", "longest-substring-without-repeating-characters", "Medium", "Sliding Window",
            "Maintain a sliding window with a map of last-seen indices. Move the left boundary past a duplicate without moving it backwards. Time O(n).",
            "The left pointer must be max(left, lastSeen + 1).", 0, 45),
        new Sample("Merge Intervals", "merge-intervals", "Medium", "Arrays",
            "Sort intervals by start. Merge with the last result whenever the next start is at most its end. Time O(n log n).",
            "Intervals that meet at an endpoint overlap.", 0, 75),
        new Sample("Binary Tree Level Order Traversal", "binary-tree-level-order-traversal", "Medium", "Trees",
            "Use breadth-first search. Save the queue size at each level, then process exactly that many nodes before starting the next level. Time O(n).",
            "Capture the current queue length before adding the next level's children.", 0, 75),
        new Sample("LRU Cache", "lru-cache", "Hard", "Linked Lists",
            "Combine a hash map and doubly linked list. Move accessed nodes to the front and evict from the back. Each operation is O(1).",
            "On removal, update both neighboring pointers and remove evicted keys from the map.", -2, 20),
        new Sample("Climbing Stairs", "climbing-stairs", "Easy", "Dynamic Programming",
            "Ways(n) equals ways(n-1) plus ways(n-2). Keep only the previous two totals. Time O(n), space O(1).",
            "Initialize the first two states carefully; one empty sequence solves zero steps.", 1, 95),
        new Sample("Valid Parentheses", "valid-parentheses", "Easy", "Stacks",
            "Push opening brackets. For each closer, require a matching top element. Accept only if the stack is empty at the end. Time O(n).",
            "An empty stack cannot match a closing bracket.", 2, 95),
        new Sample("Search in Rotated Sorted Array", "search-in-rotated-sorted-array", "Medium", "Binary Search",
            "At each binary-search step identify the sorted half, then keep it only if it contains the target. Time O(log n).",
            "Use inclusive endpoint tests consistently and exclude the middle after checking it.", 3, 45),
        new Sample("Number of Islands", "number-of-islands", "Medium", "Graphs",
            "Start DFS or BFS at each unvisited land cell and mark its connected component. Count the number of starts. Time O(rows * columns).",
            "Mark a cell as visited before exploring neighbors to prevent repeated work.", 1, 75),
        new Sample("Best Time to Buy and Sell Stock", "best-time-to-buy-and-sell-stock", "Easy", "Arrays",
            "Track the minimum price seen so far and the largest current price minus that minimum. Time O(n), space O(1).",
            "Buy before selling; never use a later minimum to compute an earlier sale.", 4, 95),
        new Sample("Coin Change", "coin-change", "Medium", "Dynamic Programming",
            "Let dp[a] be the minimum number of coins needed for amount a. Relax each valid previous amount and use an unreachable sentinel. Time O(amount * coins).",
            "Do not turn an unreachable previous amount into a valid solution by adding one.", 0, 45),
        new Sample("Top K Frequent Elements", "top-k-frequent-elements", "Medium", "Heaps",
            "Count values with a hash map and maintain a size-k min heap, or use frequency buckets. Heap time O(n log k).",
            "The heap must order by frequency, not by the numeric value of the element.", 5, 75));
    for (int i = 0; i < samples.size(); i++) {
      Sample sample = samples.get(i);
      Problem problem = new Problem();
      problem.owner = account;
      problem.title = sample.title();
      problem.url = "https://leetcode.com/problems/" + sample.slug() + "/";
      problem.platform = "LeetCode";
      problem.difficulty = sample.difficulty();
      problem.topic = sample.topic();
      problem.approach = sample.approach();
      problem.notes = sample.notes();
      problem.confidence = sample.confidence();
      problem.intervalDays = sample.confidence() >= 75 ? 6 : 1;
      problem.repetitions = sample.confidence() >= 75 ? 2 : 0;
      problem.ease = sample.confidence() < 50 ? 2.15 : 2.5;
      problem.solvedOn = today.minusDays(30 - i);
      problem.nextReviewOn = today.plusDays(sample.dueOffset());
      problems.save(problem);
    }
    List<Problem> library = problems.findAllByOwnerIdOrderByNextReviewOnAsc(account.id);
    // Illustrative presentation history, not a claim about the student's real study activity.
    for (int daysAgo = 13; daysAgo >= 0; daysAgo--) {
      int count = daysAgo == 0 ? 2 : 3;
      for (int j = 0; j < count; j++) {
        Problem problem = library.get((daysAgo * 3 + j) % library.size());
        Revision revision = new Revision();
        revision.owner = account;
        revision.problem = problem;
        revision.grade = (daysAgo + j) % 7 == 0 ? 0 : (daysAgo + j) % 4 == 0 ? 1 : 2;
        revision.reviewedAt = today.minusDays(daysAgo).atTime(10, j * 10)
            .atZone(ZoneId.of(account.zoneId)).toInstant();
        revision.scheduledOn = today.minusDays(daysAgo);
        revision.intervalDays = revision.grade < 2 ? 1 : 6;
        revisions.save(revision);
      }
    }
  }

  private record Sample(String title, String slug, String difficulty, String topic,
      String approach, String notes, int dueOffset, int confidence) {}
}
