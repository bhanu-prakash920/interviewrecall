import { chromium } from "@playwright/test";
import assert from "node:assert/strict";
import { tmpdir } from "node:os";
import { join } from "node:path";
const browser = await chromium.launch({ channel: "chrome", headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
try {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("http://127.0.0.1:5173/");
  await page
    .getByRole("heading", { name: "A little better, every day." })
    .waitFor();
  await page.screenshot({
    path: join(tmpdir(), "interviewrecall-desktop.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "Add problem", exact: true }).click();
  await page.getByLabel("Problem title").fill("Browser test problem");
  await page
    .getByLabel("Problem URL")
    .fill("https://leetcode.com/problems/two-sum/");
  await page
    .getByLabel("Your approach")
    .fill("Store complements in a hash map.");
  await page
    .getByRole("textbox", { name: "Mistake or lesson" })
    .fill("Check for the complement before inserting.");
  await page.getByRole("button", { name: "Add to my library" }).click();
  await page.getByRole("button", { name: "My problems", exact: true }).click();
  await page
    .getByRole("button", { name: "Browser test problem LeetCode" })
    .click();
  await page.getByRole("button", { name: "Revise this problem" }).click();
  assert.equal(
    await page.getByText("Store complements in a hash map.").count(),
    0,
  );
  await page.getByRole("button", { name: "Reveal my approach" }).click();
  await page.getByText("Store complements in a hash map.").waitFor();
  await page.getByRole("button", { name: "Easy 4d", exact: true }).click();
  await page
    .getByRole("status")
    .filter({ hasText: "Next review in 4 days" })
    .waitFor();
  await page.reload();
  await page.getByRole("button", { name: "My problems", exact: true }).click();
  await page
    .getByRole("textbox", { name: "Find a problem", exact: true })
    .fill("Browser test");
  assert.equal(await page.locator("tbody tr").count(), 1);
  await page
    .getByRole("button", { name: "Browser test problem LeetCode" })
    .click();
  await page.getByRole("button", { name: "Edit", exact: true }).click();
  await page
    .getByLabel("Your approach")
    .fill("Updated approach: use a complement map.");
  await page.getByRole("button", { name: "Save changes", exact: true }).click();
  assert.equal(
    await page.evaluate(
      () =>
        JSON.parse(localStorage.getItem("ir-problems")).find(
          (p) => p.title === "Browser test problem",
        ).intervalDays,
    ),
    4,
  );
  await page
    .getByRole("button", { name: "Browser test problem LeetCode" })
    .click();
  await page.getByText("Updated approach: use a complement map.").waitFor();
  await page.getByRole("button", { name: "Remove", exact: true }).click();
  await page.getByRole("heading", { name: "No matching problems" }).waitFor();
  for (const nav of ["Analytics", "Mistake notebook", "Settings", "Overview"])
    await page.getByRole("button", { name: nav, exact: true }).click();
  for (const width of [375, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.waitForTimeout(150);
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
      `Overflow at ${width}`,
    );
    if (width === 375) {
      await page.screenshot({
        path: join(tmpdir(), "interviewrecall-mobile.png"),
        fullPage: true,
      });
      await page.getByRole("button", { name: "Open navigation" }).click();
      await page
        .getByRole("button", { name: "Revision queue", exact: false })
        .click();
      await page
        .getByRole("heading", { name: "Revision queue", exact: true })
        .waitFor();
    }
  }
  assert.deepEqual(errors, []);
  console.log(
    "Passed: add, reveal, grade, persistence, search, edit, delete, all navigation, mobile drawer and overflow checks at 375/768/1024/1440px.",
  );
} finally {
  await browser.close();
}
