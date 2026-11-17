import { schedule, plusDays, dayOf } from "./model.ts";
import { test } from "node:test";
import assert from "node:assert/strict";
test("forgotten recall resets the progression and floors ease", () => {
  assert.deepEqual(
    schedule({ ease: 1.3, intervalDays: 90, repetitions: 5 }, 0),
    { ease: 1.3, intervalDays: 1, repetitions: 0 },
  );
});
test("good recall advances through the learning steps", () => {
  let p = { ease: 2.5, intervalDays: 1, repetitions: 0 };
  p = schedule(p, 2);
  assert.equal(p.intervalDays, 1);
  p = schedule(p, 2);
  assert.equal(p.intervalDays, 6);
  p = schedule(p, 2);
  assert.equal(p.intervalDays, 15);
});
test("hard recall preserves repetitions and easy recall caps the interval", () => {
  assert.equal(
    schedule({ ease: 2.5, intervalDays: 6, repetitions: 2 }, 1).repetitions,
    2,
  );
  assert.equal(
    schedule({ ease: 3, intervalDays: 200, repetitions: 5 }, 3).intervalDays,
    365,
  );
});
test("date arithmetic crosses calendar boundaries without DST drift", () => {
  assert.equal(plusDays("2026-12-31", 1), "2027-01-01");
  assert.equal(plusDays("2026-03-08", 1), "2026-03-09");
  assert.equal(dayOf("2026-12-31T23:30:00Z", "Asia/Kolkata"), "2027-01-01");
});
