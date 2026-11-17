export type Grade = 0 | 1 | 2 | 3;
export type Problem = {
  id: number;
  title: string;
  url: string;
  platform: string;
  difficulty: string;
  topic: string;
  notes: string;
  approach: string;
  confidence: number;
  intervalDays: number;
  repetitions: number;
  ease: number;
  solvedOn: string;
  nextReviewOn: string;
};
export type Review = {
  id: number;
  problemId: number;
  grade: Grade;
  reviewedAt: string;
  intervalDays: number;
};
export type User = {
  name: string;
  email: string;
  dailyGoal: number;
  zoneId: string;
};
export function dayOf(value: string | Date, zone?: string) {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: zone || Intl.DateTimeFormat().resolvedOptions().timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(value));
}
export function today(zone?: string) {
  return dayOf(new Date(), zone);
}
export function plusDays(date: string, days: number) {
  const d = new Date(date + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}
export function schedule(
  p: Pick<Problem, "ease" | "intervalDays" | "repetitions">,
  grade: Grade,
) {
  let { ease, intervalDays, repetitions } = p;
  if (grade === 0) {
    intervalDays = 1;
    repetitions = 0;
    ease = Math.max(1.3, ease - 0.2);
  } else if (grade === 1) {
    intervalDays = Math.max(1, Math.round(intervalDays * 1.2));
    ease = Math.max(1.3, ease - 0.15);
  } else if (grade === 2) {
    intervalDays =
      repetitions === 0
        ? 1
        : repetitions === 1
          ? 6
          : Math.round(intervalDays * ease);
    repetitions++;
  } else {
    intervalDays =
      repetitions === 0
        ? 4
        : Math.max(intervalDays + 1, Math.round(intervalDays * (ease + 0.3)));
    ease = Math.min(3, ease + 0.15);
    repetitions++;
  }
  return {
    ease,
    intervalDays: Math.min(365, Math.max(1, intervalDays)),
    repetitions,
  };
}
const samples = [
  [
    "Two Sum",
    "Easy",
    "Arrays",
    "Hash map",
    "Store each number’s index in a hash map. Check whether target − current exists before inserting.",
    "Check before inserting to avoid using the same element twice.",
  ],
  [
    "Longest Substring Without Repeating Characters",
    "Medium",
    "Sliding Window",
    "Sliding window",
    "Move the left pointer past the last occurrence of a repeated character. Track the maximum window size.",
    "The left pointer must never move backwards.",
  ],
  [
    "Merge Intervals",
    "Medium",
    "Arrays",
    "Sorting",
    "Sort by start time. Merge into the previous interval if the current start is at most the previous end.",
    "Overlapping endpoints count as an overlap.",
  ],
  [
    "Binary Tree Level Order Traversal",
    "Medium",
    "Trees",
    "BFS",
    "Use a queue. Process the current queue size as one level before adding the next level.",
    "Capture queue length before the inner loop.",
  ],
  [
    "LRU Cache",
    "Hard",
    "Linked Lists",
    "Design",
    "Combine a hash map with a doubly linked list. Move accessed nodes to the front; evict from the back.",
    "Update both neighboring pointers when removing a node.",
  ],
  [
    "Climbing Stairs",
    "Easy",
    "Dynamic Programming",
    "DP",
    "Ways(n) = ways(n−1) + ways(n−2). Keep only the previous two values.",
    "Use 1 as the base case for zero steps.",
  ],
  [
    "Valid Parentheses",
    "Easy",
    "Stacks",
    "Stack",
    "Push opening brackets. Match every closing bracket with the top, and ensure the stack is empty at the end.",
    "An empty stack cannot match a closing bracket.",
  ],
  [
    "Search in Rotated Sorted Array",
    "Medium",
    "Binary Search",
    "Binary search",
    "Identify the sorted half and decide whether the target lies inside it. Discard the other half.",
    "Use inclusive bounds carefully at the middle element.",
  ],
];
export function seedProblems(): Problem[] {
  return samples.map((s, i) => ({
    id: i + 1,
    title: s[0],
    difficulty: s[1],
    topic: s[2],
    platform: "LeetCode",
    url:
      "https://leetcode.com/problems/" +
      s[0].toLowerCase().replaceAll(" ", "-") +
      "/",
    approach: s[4],
    notes: s[5],
    confidence: [82, 48, 65, 72, 35, 90, 95, 57][i],
    intervalDays: [6, 3, 6, 4, 1, 12, 21, 3][i],
    repetitions: 2,
    ease: 2.5,
    solvedOn: plusDays(today(), -20 + i),
    nextReviewOn: plusDays(today(), i < 5 ? (i === 1 ? -1 : 0) : i - 4),
  }));
}
export function seedReviews(): Review[] {
  return Array.from({ length: 43 }, (_, i) => ({
    id: i + 1,
    problemId: (i % 8) + 1,
    grade: (i % 7 === 0 ? 0 : i % 4 === 0 ? 1 : i % 3 === 0 ? 3 : 2) as Grade,
    reviewedAt: plusDays(today(), -Math.floor(i / 3)) + "T09:00:00Z",
    intervalDays: 6,
  }));
}
