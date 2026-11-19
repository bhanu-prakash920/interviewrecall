import { chromium } from "@playwright/test";
import assert from "node:assert/strict";
const origin = "http://127.0.0.1:5173";
const browser = await chromium.launch({ channel: "chrome", headless: true });
let temporaryId;
let page;
async function mutate(path, method, data) {
  const tokenResponse = await page.request.get(origin + "/api/auth/csrf");
  assert.equal(tokenResponse.status(), 200);
  const { token } = await tokenResponse.json();
  return page.request.fetch(origin + "/api" + path, {
    method,
    headers: { "X-CSRF-TOKEN": token },
    ...(data ? { data } : {}),
  });
}
try {
  page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(origin);
  await page.getByRole("button", { name: "Connect your account" }).click();
  await page.getByLabel("Email address").fill("demo@interviewrecall.test");
  await page.getByLabel("Password", { exact: true }).fill("Recall@123456");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await page
    .locator(".profile")
    .filter({ hasText: "Bhanu Prakash Kusha" })
    .waitFor();
  assert.equal(await page.locator(".demo-label").count(), 0);
  const me = await (await page.request.get(origin + "/api/auth/me")).json();
  assert.equal(me.email, "demo@interviewrecall.test");
  const beforeProblems = await (
    await page.request.get(origin + "/api/problems")
  ).json();
  const beforeHistory = await (
    await page.request.get(origin + "/api/revisions")
  ).json();
  assert.equal(beforeProblems.length, 12);
  assert.equal(beforeHistory.length, 41);
  await page.screenshot({
    path: ".local/presentation-account.png",
    fullPage: true,
  });

  // Real MySQL regression: two large explanations must not exceed an inline VARCHAR row limit.
  const added = await mutate("/problems", "POST", {
    title: "Presentation verification (temporary)",
    url: "https://leetcode.com/problems/two-sum/",
    platform: "LeetCode",
    difficulty: "Easy",
    topic: "Arrays",
    approach: "A".repeat(9500),
    notes: "B".repeat(9500),
  });
  assert.equal(added.status(), 201, await added.text());
  const problem = await added.json();
  temporaryId = problem.id;
  assert.equal(problem.approach.length, 9500);
  assert.equal(problem.notes.length, 9500);
  const reviewed = await mutate(`/problems/${temporaryId}/reviews`, "POST", {
    grade: 3,
  });
  assert.equal(reviewed.status(), 200);
  assert.equal((await reviewed.json()).intervalDays, 4);
  const afterHistory = await (
    await page.request.get(origin + "/api/revisions")
  ).json();
  assert.equal(afterHistory.length, beforeHistory.length + 1);
  assert.equal(
    (await mutate(`/problems/${temporaryId}`, "DELETE")).status(),
    204,
  );
  temporaryId = undefined;
  assert.equal(
    (await (await page.request.get(origin + "/api/revisions")).json()).length,
    41,
  );

  await page.reload();
  await page
    .locator(".profile")
    .filter({ hasText: "Bhanu Prakash Kusha" })
    .waitFor();
  const restored = await (
    await page.request.get(origin + "/api/problems")
  ).json();
  assert.equal(restored.length, 12);
  await page
    .getByRole("button", { name: "Revision queue", exact: false })
    .click();
  await page.locator(".row-action").first().click();
  await page.getByRole("button", { name: "Reveal my approach" }).click();
  await page.getByRole("button", { name: "Close dialog" }).click();
  assert.equal((await mutate("/auth/logout", "POST")).status(), 204);
  assert.equal((await page.request.get(origin + "/api/auth/me")).status(), 401);
  assert.deepEqual(errors, []);
  console.log(
    "PASS: real browser login, seeded MySQL records, large TEXT fields, review/history transaction, reload persistence, recall UI, cleanup, and logout. Demo remains at 12 problems and 41 sample revisions.",
  );
} finally {
  if (temporaryId)
    await mutate(`/problems/${temporaryId}`, "DELETE").catch(() => {});
  await browser.close();
}
