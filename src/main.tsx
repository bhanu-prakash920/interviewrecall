import React, { useState, useEffect, useMemo, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  LayoutDashboard,
  Library,
  RotateCcw,
  ChartNoAxesCombined,
  NotebookPen,
  Settings,
  ArrowUpRight,
  ArrowRight,
  Plus,
  Search,
  ChevronDown,
  ChevronRight,
  Flame,
  Clock,
  Check,
  CheckCheck,
  X,
  Target,
  Code2,
  MoreHorizontal,
  Lightbulb,
  Bell,
  Menu,
  LogOut,
  ExternalLink,
  Eye,
  Leaf,
  CalendarDays,
  Download,
  Trash2,
  Brain,
  CircleHelp,
} from "lucide-react";
import {
  type Problem,
  type Review,
  type User,
  type Grade,
  today,
  dayOf,
  plusDays,
  schedule,
  seedProblems,
  seedReviews,
} from "./model";
import { api } from "./api";
import "./styles.css";
import { Metric } from "./components/Metric";
import { Activity } from "./components/Activity";
import { ProblemTable } from "./components/ProblemTable";
const navigation = [
  { name: "Overview", icon: LayoutDashboard },
  { name: "My problems", icon: Library },
  { name: "Revision queue", icon: RotateCcw },
  { name: "Analytics", icon: ChartNoAxesCombined },
  { name: "Mistake notebook", icon: NotebookPen },
];
function routeName() {
  try {
    const name = decodeURIComponent(location.hash.slice(1));
    return [...navigation.map((n) => n.name), "Settings"].includes(name)
      ? name
      : "Overview";
  } catch {
    return "Overview";
  }
}
function read<T>(key: string, fallback: T): T {
  try {
    return JSON.parse(localStorage.getItem(key) || "null") ?? fallback;
  } catch {
    return fallback;
  }
}
function App() {
  const [page, setPage] = useState(() => routeName()),
    [problems, setProblems] = useState<Problem[]>(() =>
      read("ir-problems", seedProblems()),
    ),
    [reviews, setReviews] = useState<Review[]>(() =>
      read("ir-reviews", seedReviews()),
    ),
    [user, setUser] = useState<User>(() =>
      read("ir-user", {
        name: "Alex Morgan",
        email: "alex@example.com",
        dailyGoal: 5,
        zoneId: Intl.DateTimeFormat().resolvedOptions().timeZone,
      }),
    );
  const [account, setAccount] = useState(false),
    [search, setSearch] = useState(""),
    [topic, setTopic] = useState("All topics"),
    [modal, setModal] = useState<"add" | "auth" | "help" | null>(null),
    [selected, setSelected] = useState<Problem | null>(null),
    [editing, setEditing] = useState<Problem | null>(null),
    [focus, setFocus] = useState(false),
    [revealed, setRevealed] = useState(false),
    [toast, setToast] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [sidebar, setSidebar] = useState(false),
    [notifications, setNotifications] = useState(false),
    [range, setRange] = useState(7),
    [authRegister, setAuthRegister] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null),
    dialogRef = useRef<HTMLDivElement>(null);
  const date = today(user.zoneId),
    due = problems
      .filter((p) => p.nextReviewOn <= date)
      .sort(
        (a, b) =>
          a.nextReviewOn.localeCompare(b.nextReviewOn) ||
          a.confidence - b.confidence,
      ),
    completed = reviews.filter(
      (r) => dayOf(r.reviewedAt, user.zoneId) === date,
    ).length,
    topics = [...new Set(problems.map((p) => p.topic))];
  const filtered = problems.filter(
    (p) =>
      (topic === "All topics" || p.topic === topic) &&
      (p.title + " " + p.topic + " " + p.notes)
        .toLowerCase()
        .includes(search.toLowerCase()),
  );
  const recall = reviews.length
    ? Math.round(
        (100 * reviews.filter((r) => r.grade >= 2).length) / reviews.length,
      )
    : 0;
  const recent = reviews.filter(
    (r) => dayOf(r.reviewedAt, user.zoneId) >= plusDays(date, -range + 1),
  );
  useEffect(() => {
    api<User>("/auth/me")
      .then(async (u) => {
        const [p, r] = await Promise.all([
          api<Problem[]>("/problems"),
          api<Review[]>("/revisions"),
        ]);
        setUser(u);
        setProblems(p);
        setReviews(r);
        setAccount(true);
      })
      .catch(() => {});
  }, []);
  useEffect(() => {
    if (!account) {
      localStorage.setItem("ir-problems", JSON.stringify(problems));
      localStorage.setItem("ir-reviews", JSON.stringify(reviews));
      localStorage.setItem("ir-user", JSON.stringify(user));
    }
  }, [problems, reviews, user, account]);
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(""), 4500);
    return () => clearTimeout(t);
  }, [toast]);
  useEffect(() => {
    const handler = () => setPage(routeName());
    window.addEventListener("hashchange", handler);
    return () => window.removeEventListener("hashchange", handler);
  }, []);
  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        searchRef.current?.focus();
      }
      if (e.key === "Escape") {
        setModal(null);
        setSelected(null);
        setNotifications(false);
      }
    };
    window.addEventListener("keydown", handle);
    return () => window.removeEventListener("keydown", handle);
  }, []);
  useEffect(() => {
    if (!modal && !selected) return;
    const previous = document.activeElement as HTMLElement;
    const el = dialogRef.current;
    el?.querySelector<HTMLElement>("button,input")?.focus();
    const trap = (e: KeyboardEvent) => {
      if (e.key !== "Tab" || !el) return;
      const nodes = Array.from(
        el.querySelectorAll<HTMLElement>(
          "button,input,select,textarea,a[href]",
        ),
      ).filter((n) => !n.hasAttribute("disabled"));
      const first = nodes[0],
        last = nodes[nodes.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last?.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first?.focus();
      }
    };
    document.addEventListener("keydown", trap);
    return () => {
      document.removeEventListener("keydown", trap);
      previous?.focus();
    };
  }, [modal, selected?.id]);
  function go(name: string) {
    location.hash = encodeURIComponent(name);
    setPage(name);
    setSearch("");
    setTopic("All topics");
    setSidebar(false);
  }
  function openProblem(p: Problem, revise = false) {
    setSelected(p);
    setFocus(revise);
    setRevealed(false);
    setError("");
  }
  async function review(grade: Grade) {
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      const next = schedule(selected, grade);
      const updated = account
        ? await api<Problem>(`/problems/${selected.id}/reviews`, "POST", {
            grade,
          })
        : {
            ...selected,
            ...next,
            confidence: [20, 45, 75, 95][grade],
            nextReviewOn: plusDays(date, next.intervalDays),
          };
      setProblems((ps) => ps.map((p) => (p.id === updated.id ? updated : p)));
      if (account) setReviews(await api<Review[]>("/revisions"));
      else
        setReviews((rs) => [
          {
            id: Date.now(),
            problemId: updated.id,
            grade,
            reviewedAt: new Date().toISOString(),
            intervalDays: updated.intervalDays,
          },
          ...rs,
        ]);
      setSelected(null);
      setToast(
        `Revision saved. Next review in ${updated.intervalDays} day${updated.intervalDays === 1 ? "" : "s"}.`,
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function addProblem(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setBusy(true);
    setError("");
    try {
      const p = {
        title: String(f.get("title")).trim(),
        url: String(f.get("url")),
        platform: String(f.get("platform")),
        difficulty: String(f.get("difficulty")),
        topic: String(f.get("topic")),
        approach: String(f.get("approach")),
        notes: String(f.get("notes")),
        confidence: 50,
        intervalDays: 1,
        repetitions: 0,
        ease: 2.5,
        solvedOn: date,
        nextReviewOn: plusDays(date, 1),
      };
      const saved = account
        ? await api<Problem>(
            editing ? `/problems/${editing.id}` : "/problems",
            editing ? "PUT" : "POST",
            p,
          )
        : editing
          ? {
              ...editing,
              ...p,
              intervalDays: editing.intervalDays,
              repetitions: editing.repetitions,
              ease: editing.ease,
              confidence: editing.confidence,
              solvedOn: editing.solvedOn,
              nextReviewOn: editing.nextReviewOn,
            }
          : { ...p, id: Date.now() };
      setProblems((ps) =>
        editing
          ? ps.map((item) => (item.id === editing.id ? saved : item))
          : [saved, ...ps],
      );
      setModal(null);
      setEditing(null);
      setToast(
        editing
          ? "Problem updated. Your revision schedule is preserved."
          : "Problem added. Your first revision is tomorrow.",
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function authenticate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const f = new FormData(e.currentTarget);
    try {
      if (authRegister)
        await api("/auth/register", "POST", {
          name: f.get("name"),
          email: f.get("email"),
          password: f.get("password"),
          zoneId: user.zoneId,
        });
      await api("/auth/login", "POST", {
        email: f.get("email"),
        password: f.get("password"),
      });
      const u = await api<User>("/auth/me");
      const [p, r] = await Promise.all([
        api<Problem[]>("/problems"),
        api<Review[]>("/revisions"),
      ]);
      setUser(u);
      setProblems(p);
      setReviews(r);
      setAccount(true);
      setModal(null);
      setToast("Your account is ready.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function removeProblem(p: Problem) {
    setBusy(true);
    try {
      if (account) await api(`/problems/${p.id}`, "DELETE");
      setProblems((ps) => ps.filter((x) => x.id !== p.id));
      setReviews((rs) => rs.filter((r) => r.problemId !== p.id));
      setSelected(null);
      setToast("Problem removed.");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const activity = useMemo(
    () =>
      Array.from({ length: 84 }, (_, i) => {
        const d = plusDays(
          date,
          -77 - ((new Date(date + "T12:00:00Z").getUTCDay() + 6) % 7) + i,
        );
        return {
          date: d,
          count: reviews.filter((r) => dayOf(r.reviewedAt, user.zoneId) === d)
            .length,
        };
      }),
    [reviews, date, user.zoneId],
  );
  let streak = 0;
  for (
    let i = reviews.some((r) => dayOf(r.reviewedAt, user.zoneId) === date)
      ? 0
      : 1;
    i < 365;
    i++
  ) {
    if (
      reviews.some(
        (r) => dayOf(r.reviewedAt, user.zoneId) === plusDays(date, -i),
      )
    )
      streak++;
    else break;
  }
  function exportData() {
    const blob = new Blob([JSON.stringify({ problems, reviews }, null, 2)], {
      type: "application/json",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "interviewrecall-export.json";
    a.click();
    URL.revokeObjectURL(a.href);
    setToast("Your preparation data was exported.");
  }

  return (
    <div className="app-shell">
      <div className="ambient one" />
      <div className="ambient two" />
      {sidebar && (
        <div className="sidebar-scrim" onClick={() => setSidebar(false)} />
      )}
      <aside className={"sidebar " + (sidebar ? "is-open" : "")}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            go("Overview");
          }}
        >
          <span className="brand-mark">
            <span />
            <span />
          </span>
          <span>
            interview<span className="brand-bold">recall</span>
            <b>MAKE IT STICK.</b>
          </span>
        </a>
        <div className="workspace">
          <span className="workspace-avatar">
            A<span />
          </span>
          <div>
            My workspace<small>Personal workspace</small>
          </div>
          <ChevronDown size={15} />
        </div>
        <span className="nav-label">WORKSPACE</span>
        <nav>
          {navigation.map((n) => (
            <button
              key={n.name}
              className={page === n.name ? "active" : ""}
              aria-current={page === n.name ? "page" : undefined}
              onClick={() => go(n.name)}
            >
              <n.icon size={19} />
              <span>{n.name}</span>
              {n.name === "Revision queue" && <b>{due.length}</b>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="tip-card">
            <div className="tip-icon">
              <Leaf size={20} />
              <span>A LITTLE EVERY DAY</span>
            </div>
            <h3>
              Small steps.
              <br />
              Stronger recall.
            </h3>
            <p>Your next interview starts with today’s revision.</p>
            <button
              onClick={() =>
                due[0] ? openProblem(due[0], true) : go("My problems")
              }
            >
              Build your momentum <ArrowUpRight size={16} />
            </button>
          </div>
          <button
            className={"settings-nav " + (page === "Settings" ? "active" : "")}
            onClick={() => go("Settings")}
          >
            <Settings size={19} />
            Settings
          </button>
          <button
            className="profile"
            onClick={() => {
              setError("");
              setModal("auth");
            }}
          >
            <span className="avatar">
              {user.name
                .split(" ")
                .map((s) => s[0])
                .slice(0, 2)
                .join("")}
            </span>
            <span>
              {user.name}
              <small>
                {account ? "Personal account" : "Local demo workspace"}
              </small>
            </span>
            <MoreHorizontal size={18} />
          </button>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-menu"
              aria-label="Open navigation"
              aria-expanded={sidebar}
              onClick={() => setSidebar(true)}
            >
              <Menu size={20} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={13} />
            <strong>{page}</strong>
          </div>
          <div className="topbar-actions">
            <div className="global-search">
              <Search size={16} />
              <input
                ref={searchRef}
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  if (page !== "My problems" && page !== "Revision queue")
                    setPage("My problems");
                }}
                placeholder="Search anything..."
                aria-label="Search problems"
              />
              <kbd>⌘ K</kbd>
            </div>
            <span className="top-divider" />
            <button
              className="icon-button notification-button"
              aria-label="Revision notifications"
              aria-expanded={notifications}
              onClick={() => setNotifications(!notifications)}
            >
              <Bell size={19} />
              {due.length > 0 && <i />}
            </button>
            <button
              className="avatar small"
              aria-label="Account"
              onClick={() => {
                setError("");
                setModal("auth");
              }}
            >
              {user.name[0]}
            </button>
          </div>
          {notifications && (
            <div className="notifications glass">
              <h3>Your revision reminders</h3>
              <p>{due.length} problems are ready for another look.</p>
              <button
                className="text-button"
                onClick={() => {
                  go("Revision queue");
                  setNotifications(false);
                }}
              >
                Open your queue <ArrowRight size={16} />
              </button>
            </div>
          )}
        </header>
        <main>
          <div className="page-heading">
            <div>
              <div className="eyebrow">
                <span /> YOUR PREPARATION, IN PERSPECTIVE
              </div>
              <h1>
                {page === "Overview" ? (
                  <>
                    A little better, every day
                    <span className="lime-dot">.</span>
                  </>
                ) : (
                  page
                )}
              </h1>
              <p>
                {page === "Overview"
                  ? `Welcome back, ${user.name.split(" ")[0]}. Let’s turn what you’ve learned into what you remember.`
                  : page === "My problems"
                    ? "Your personal collection of patterns, approaches, and hard-earned lessons."
                    : page === "Revision queue"
                      ? "A little active recall today. A stronger memory tomorrow."
                      : page === "Analytics"
                        ? "See what’s sticking — and where a little attention will go a long way."
                        : page === "Mistake notebook"
                          ? "Every mistake is a shortcut to a better solution next time."
                          : "Make this workspace feel like yours."}
              </p>
            </div>
            <div className="heading-actions">
              <span className="date-label">
                <CalendarDays size={15} />
                {new Date().toLocaleDateString("en", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                  timeZone: user.zoneId,
                })}
              </span>
              <button
                className="button primary"
                onClick={() => {
                  setError("");
                  setEditing(null);
                  setModal("add");
                }}
              >
                <Plus size={17} />
                Add problem
              </button>
            </div>
          </div>
          {!account && (
            <div className="demo-label">
              <span className="live-dot" />
              Demo workspace <span>·</span> Sample history, saved on this
              browser.
              <button
                onClick={() => {
                  setError("");
                  setModal("auth");
                }}
              >
                Connect your account <ArrowUpRight size={12} />
              </button>
            </div>
          )}
          {page === "Overview" && (
            <>
              <section className="hero-row">
                <div className="revision-hero">
                  <div className="hero-copy">
                    <span className="hero-label">
                      <span /> YOUR DAILY RESET
                    </span>
                    <h2>
                      Solved it once.
                      <br />
                      <span>Remember it for good.</span>
                    </h2>
                    <p>
                      Your future self will thank you.
                      <br />
                      {due.length} problems are ready for a fresh look today.
                    </p>
                    <div className="hero-bottom">
                      <button
                        className="button lime"
                        disabled={!due.length}
                        onClick={() => due[0] && openProblem(due[0], true)}
                      >
                        Start today’s revision <ArrowUpRight size={18} />
                      </button>
                      <span>
                        <Clock size={14} />~{due.length * 5} min
                      </span>
                    </div>
                  </div>
                  <div className="orbit-art" aria-hidden="true">
                    <div className="orbit orbit-a" />
                    <div className="orbit orbit-b" />
                    <div className="orbit orbit-c" />
                    <div className="orbit-center">
                      <Brain size={44} strokeWidth={1.25} />
                    </div>
                    <span className="orbit-node node-code">
                      <Code2 size={23} />
                    </span>
                    <span className="orbit-node node-check">
                      <Check size={19} />
                    </span>
                    <span className="node-dot dot-a" />
                    <span className="node-dot dot-b" />
                    <span className="orbit-caption">
                      LEARN. RECALL. REPEAT.
                    </span>
                  </div>
                </div>
                <div className="daily-goal glass">
                  <div className="card-label">
                    <span>Today’s goal</span>
                    <Target size={18} />
                  </div>
                  <div className="goal-content">
                    <div
                      className="progress-ring"
                      style={
                        {
                          "--progress":
                            Math.min(100, (completed / user.dailyGoal) * 100) +
                            "%",
                        } as React.CSSProperties
                      }
                    >
                      <div>
                        <strong>
                          {completed}
                          <small>/{user.dailyGoal}</small>
                        </strong>
                        <span>revisions</span>
                      </div>
                    </div>
                    <h3>
                      {completed >= user.dailyGoal
                        ? "Goal complete. Well done!"
                        : "Your next small win awaits."}
                    </h3>
                    <p>
                      {completed >= user.dailyGoal
                        ? "Every recall makes a difference."
                        : `${Math.max(0, user.dailyGoal - completed)} more to reach your daily goal.`}
                    </p>
                  </div>
                  <div className="goal-footer">
                    <Flame size={16} />
                    <strong>{streak}-day streak</strong>
                    <span>Keep the spark alive</span>
                  </div>
                </div>
              </section>
              <section className="stats-grid">
                <Metric
                  icon={Code2}
                  label="Problems in your library"
                  value={problems.length}
                  detail="A growing toolkit of approaches"
                />
                <Metric
                  icon={RotateCcw}
                  label="Ready for revision"
                  value={due.length}
                  detail={`${due.filter((p) => p.nextReviewOn < date).length} overdue · Let’s bring them back`}
                />
                <Metric
                  icon={Brain}
                  label="Successful recall"
                  value={recall + "%"}
                  detail="Good or easy across your history"
                />
                <Metric
                  icon={CheckCheck}
                  label="Revisions this week"
                  value={
                    reviews.filter(
                      (r) =>
                        dayOf(r.reviewedAt, user.zoneId) >= plusDays(date, -6),
                    ).length
                  }
                  detail="Every revisit makes it stick"
                />
              </section>
              <section className="dashboard-lower">
                <div className="queue-card glass">
                  <div className="section-header">
                    <div>
                      <h2>
                        Up for a recall{" "}
                        <span className="count-badge">{due.length}</span>
                      </h2>
                      <p>A few familiar problems. A stronger connection.</p>
                    </div>
                    <button
                      className="text-button"
                      onClick={() => go("Revision queue")}
                    >
                      View queue <ArrowUpRight size={15} />
                    </button>
                  </div>
                  <div className="table-toolbar">
                    <div className="tabs">
                      <button
                        className="selected"
                        onClick={() => setTopic("All topics")}
                      >
                        Today’s queue <span>{due.length}</span>
                      </button>
                      <button onClick={() => go("My problems")}>
                        All problems
                      </button>
                    </div>
                    <button
                      className="icon-button"
                      aria-label="Queue help"
                      onClick={() => setModal("help")}
                    >
                      <CircleHelp size={16} />
                    </button>
                  </div>
                  <ProblemTable
                    date={date}
                    search={search}
                    onOpen={openProblem}
                    items={due.slice(0, 4)}
                    queue
                  />
                  <div className="table-footer">
                    <span>
                      <span className="live-dot" />
                      Prioritized for your memory, not just your calendar
                    </span>
                    <button
                      className="text-button"
                      onClick={() => go("Revision queue")}
                    >
                      See all {due.length} <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
                <div className="focus-card glass">
                  <div className="section-header">
                    <h2>Your next focus</h2>
                    <Lightbulb size={18} />
                  </div>
                  <span className="eyebrow">
                    A LITTLE ATTENTION GOES A LONG WAY
                  </span>
                  <h3>
                    {[...problems].sort(
                      (a, b) => a.confidence - b.confidence,
                    )[0]?.topic || "Start your collection"}
                  </h3>
                  <p>
                    {problems.length
                      ? "Your lowest-confidence topic could use a refresh. Revisit the approach before you move on."
                      : "Add your first problem to see a personalized focus here."}
                  </p>
                  <div className="focus-topic">
                    <span>
                      <i />
                      Recall confidence
                    </span>
                    <strong>
                      {Math.min(...problems.map((p) => p.confidence), 100)}%
                    </strong>
                  </div>
                  <div className="focus-track">
                    <span
                      style={{
                        width:
                          Math.min(...problems.map((p) => p.confidence), 100) +
                          "%",
                      }}
                    />
                  </div>
                  <button
                    className="button outline"
                    onClick={() => {
                      const p = [...problems].sort(
                        (a, b) => a.confidence - b.confidence,
                      )[0];
                      if (p) openProblem(p, true);
                      else {
                        setEditing(null);
                        setModal("add");
                      }
                    }}
                  >
                    Give it a fresh look <ArrowUpRight size={16} />
                  </button>
                </div>
              </section>
              <section className="bottom-grid">
                <Activity activity={activity} />
                <div className="note-strip glass">
                  <img src="/assets/growth.svg" alt="" />
                  <div>
                    <span className="eyebrow">THE RECALL MINDSET</span>
                    <h3>
                      Understanding is the start.
                      <br />
                      Remembering is the advantage.
                    </h3>
                    <button
                      className="text-button"
                      onClick={() => setModal("help")}
                    >
                      How spaced repetition works <ArrowUpRight size={14} />
                    </button>
                  </div>
                </div>
              </section>
            </>
          )}
          {(page === "My problems" || page === "Revision queue") && (
            <section className="glass library-panel">
              <div className="section-header">
                <div>
                  <h2>
                    {page === "My problems"
                      ? "Your problem library"
                      : "Ready when you are"}{" "}
                    <span className="count-badge">
                      {page === "My problems" ? problems.length : due.length}
                    </span>
                  </h2>
                  <p>
                    {page === "My problems"
                      ? "Capture the thinking behind every solution."
                      : "Overdue problems come first. Recall the approach before revealing your notes."}
                  </p>
                </div>
                {page === "Revision queue" && (
                  <button
                    className="button primary"
                    disabled={!due.length}
                    onClick={() => due[0] && openProblem(due[0], true)}
                  >
                    Start session <ArrowRight size={17} />
                  </button>
                )}
              </div>
              <div className="library-tools">
                <div className="input-search">
                  <Search size={16} />
                  <input
                    placeholder="Find a problem..."
                    aria-label="Find a problem"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
                <select
                  aria-label="Filter by topic"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                >
                  <option>All topics</option>
                  {topics.map((t) => (
                    <option key={t}>{t}</option>
                  ))}
                </select>
                <button className="button outline" onClick={exportData}>
                  <Download size={15} />
                  Export
                </button>
              </div>
              <ProblemTable
                date={date}
                search={search}
                onOpen={openProblem}
                items={filtered
                  .filter(
                    (p) => page === "My problems" || p.nextReviewOn <= date,
                  )
                  .sort((a, b) => a.nextReviewOn.localeCompare(b.nextReviewOn))}
                queue={page === "Revision queue"}
              />
            </section>
          )}
          {page === "Analytics" && (
            <>
              <div className="section-header analytics-heading">
                <h2>Your preparation at a glance</h2>
                <select
                  aria-label="Analytics time range"
                  value={range}
                  onChange={(e) => setRange(Number(e.target.value))}
                >
                  <option value={7}>Last 7 days</option>
                  <option value={30}>Last 30 days</option>
                </select>
              </div>
              <section className="stats-grid">
                <Metric
                  icon={CheckCheck}
                  label="Revisions in period"
                  value={recent.length}
                  detail={`Over the last ${range} days`}
                />
                <Metric
                  icon={Brain}
                  label="Period recall rate"
                  value={
                    (recent.length
                      ? Math.round(
                          (recent.filter((r) => r.grade >= 2).length /
                            recent.length) *
                            100,
                        )
                      : 0) + "%"
                  }
                  detail="Graded good or easy"
                />
                <Metric
                  icon={Flame}
                  label="Current streak"
                  value={streak + " days"}
                  detail="Consecutive active days"
                />
                <Metric
                  icon={Target}
                  label="Topics practiced"
                  value={topics.length}
                  detail="In your problem library"
                />
              </section>
              <div className="analytics-grid">
                <section className="glass topic-analysis">
                  <div className="section-header">
                    <h2>Where your confidence stands</h2>
                    <Brain size={20} />
                  </div>
                  {topics.map((t) => {
                    const ps = problems.filter((p) => p.topic === t),
                      avg = Math.round(
                        ps.reduce((s, p) => s + p.confidence, 0) / ps.length,
                      );
                    return (
                      <button
                        key={t}
                        className="topic-analysis-row"
                        onClick={() => {
                          go("My problems");
                          setTopic(t);
                        }}
                      >
                        <div>
                          <strong>{t}</strong>
                          <span>
                            {ps.length} problem{ps.length !== 1 ? "s" : ""}
                          </span>
                        </div>
                        <div className="topic-bar">
                          <i style={{ width: avg + "%" }} />
                        </div>
                        <b>{avg}%</b>
                        <ArrowUpRight size={16} />
                      </button>
                    );
                  })}
                </section>
                <section className="glass history">
                  <div className="section-header">
                    <h2>Recent recall sessions</h2>
                    <Clock size={18} />
                  </div>
                  {recent.slice(0, 7).map((r) => (
                    <div className="history-row" key={r.id}>
                      <span
                        className={
                          "history-icon " + (r.grade >= 2 ? "good" : "")
                        }
                      >
                        <RotateCcw size={16} />
                      </span>
                      <div>
                        <strong>
                          {problems.find((p) => p.id === r.problemId)?.title ||
                            "Removed problem"}
                        </strong>
                        <small>
                          {new Date(r.reviewedAt).toLocaleDateString("en", {
                            month: "short",
                            day: "numeric",
                            timeZone: user.zoneId,
                          })}{" "}
                          · Next interval: {r.intervalDays} days
                        </small>
                      </div>
                      <span className="badge easy">
                        {["Again", "Hard", "Good", "Easy"][r.grade]}
                      </span>
                    </div>
                  ))}
                  {!recent.length && (
                    <div className="empty">
                      Complete a revision to see your history.
                    </div>
                  )}
                </section>
              </div>
              <Activity activity={activity} />
            </>
          )}
          {page === "Mistake notebook" && (
            <section className="notebook-grid">
              {filtered
                .filter((p) => p.notes)
                .map((p, i) => (
                  <button
                    className="notebook-card glass"
                    key={p.id}
                    onClick={() => openProblem(p)}
                  >
                    <div>
                      <span className="notebook-index">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                      <span className="topic-tag">{p.topic}</span>
                      <ArrowUpRight size={18} />
                    </div>
                    <h2>{p.title}</h2>
                    <span className="eyebrow">THE LESSON</span>
                    <p>{p.notes}</p>
                    <span className="notebook-footer">
                      <NotebookPen size={14} />A mistake remembered is a mistake
                      avoided.
                    </span>
                  </button>
                ))}
              {!filtered.some((p) => p.notes) && (
                <div className="empty glass">
                  <NotebookPen size={30} />
                  <h3>Your lessons start here</h3>
                  <p>Add mistake notes when you save a problem.</p>
                  <button
                    className="button primary"
                    onClick={() => {
                      setEditing(null);
                      setModal("add");
                    }}
                  >
                    Add problem
                  </button>
                </div>
              )}
            </section>
          )}
          {page === "Settings" && (
            <div className="settings-grid">
              <form
                className="glass settings-card"
                onSubmit={async (e) => {
                  e.preventDefault();
                  setError("");
                  const f = new FormData(e.currentTarget);
                  const next = {
                    ...user,
                    name: String(f.get("name")).trim(),
                    dailyGoal: Number(f.get("goal")),
                    zoneId: String(f.get("zone")),
                  };
                  try {
                    Intl.DateTimeFormat("en", { timeZone: next.zoneId });
                    const saved = account
                      ? await api<User>("/auth/preferences", "PUT", next)
                      : next;
                    setUser(saved);
                    setToast("Preferences saved.");
                  } catch (e) {
                    setError((e as Error).message);
                  }
                }}
              >
                <h2>Your workspace, your pace</h2>
                <p>Choose a sustainable daily goal.</p>
                <label>
                  Your name
                  <input
                    name="name"
                    defaultValue={user.name}
                    required
                    maxLength={80}
                  />
                </label>
                <label>
                  Daily revision goal
                  <input
                    name="goal"
                    type="number"
                    min="1"
                    max="50"
                    defaultValue={user.dailyGoal}
                    required
                  />
                </label>
                <label>
                  Timezone
                  <select name="zone" defaultValue={user.zoneId}>
                    {[
                      ...new Set([
                        user.zoneId,
                        "Asia/Kolkata",
                        "UTC",
                        "America/New_York",
                        "America/Los_Angeles",
                        "Europe/London",
                      ]),
                    ].map((z) => (
                      <option key={z}>{z}</option>
                    ))}
                  </select>
                </label>
                {error && (
                  <p className="error" role="alert">
                    {error}
                  </p>
                )}
                <button className="button primary" type="submit">
                  Save preferences <Check size={16} />
                </button>
              </form>
              <section className="glass settings-card">
                <h2>Your data belongs to you</h2>
                <p>
                  {account
                    ? "Your collection is stored in your account database."
                    : "You’re exploring sample data in local demo mode. Changes stay in this browser."}
                </p>
                <button className="button outline" onClick={exportData}>
                  <Download size={16} />
                  Export preparation data
                </button>
                <hr />
                {account ? (
                  <button
                    className="button outline"
                    onClick={async () => {
                      try {
                        await api("/auth/logout", "POST");
                        setAccount(false);
                        setProblems(read("ir-problems", seedProblems()));
                        setReviews(read("ir-reviews", seedReviews()));
                        setUser(
                          read("ir-user", {
                            name: "Alex Morgan",
                            email: "alex@example.com",
                            dailyGoal: 5,
                            zoneId:
                              Intl.DateTimeFormat().resolvedOptions().timeZone,
                          }),
                        );
                        setToast("Signed out. Local demo restored.");
                      } catch (e) {
                        setToast((e as Error).message);
                      }
                    }}
                  >
                    <LogOut size={16} />
                    Sign out
                  </button>
                ) : (
                  <button
                    className="button primary"
                    onClick={() => {
                      setError("");
                      setModal("auth");
                    }}
                  >
                    Sign in to your account <ArrowUpRight size={16} />
                  </button>
                )}
              </section>
            </div>
          )}
          <footer className="page-footer">
            <span>
              <span className="mini-brand" /> Built for the long game.
            </span>
            <button onClick={() => setModal("help")}>
              A little about recall <ArrowUpRight size={13} />
            </button>
          </footer>
        </main>
      </div>
      {toast && (
        <div className="toast" role="status">
          <span>
            <Check size={16} />
          </span>
          {toast}
          <button
            aria-label="Dismiss notification"
            onClick={() => setToast("")}
          >
            <X size={15} />
          </button>
        </div>
      )}
      {(modal || selected) && (
        <div
          className="modal-backdrop"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) {
              setModal(null);
              setSelected(null);
            }
          }}
        >
          <div
            className={"modal glass " + (selected ? "problem-modal" : "")}
            role="dialog"
            aria-modal="true"
            aria-labelledby="dialog-title"
            ref={dialogRef}
          >
            <button
              className="modal-close icon-button"
              aria-label="Close dialog"
              onClick={() => {
                setModal(null);
                setSelected(null);
              }}
            >
              <X size={20} />
            </button>
            {modal === "add" && (
              <>
                <span className="modal-symbol">
                  <Plus size={24} />
                </span>
                <h2 id="dialog-title">
                  {editing
                    ? "Refine your thinking."
                    : "One more in your toolkit."}
                </h2>
                <p>Save the problem. Keep the thinking.</p>
                <form onSubmit={addProblem}>
                  <label>
                    Problem title
                    <input
                      name="title"
                      defaultValue={editing?.title}
                      autoFocus
                      required
                      maxLength={180}
                      placeholder="e.g. Two Sum"
                    />
                  </label>
                  <label>
                    Problem URL
                    <input
                      name="url"
                      defaultValue={editing?.url}
                      type="url"
                      required
                      placeholder="https://leetcode.com/problems/..."
                    />
                  </label>
                  <div className="form-row">
                    <label>
                      Platform
                      <select name="platform" defaultValue={editing?.platform}>
                        <option>LeetCode</option>
                        <option>GeeksforGeeks</option>
                        <option>Codeforces</option>
                        <option>Other</option>
                      </select>
                    </label>
                    <label>
                      Difficulty
                      <select
                        name="difficulty"
                        defaultValue={editing?.difficulty}
                      >
                        <option>Easy</option>
                        <option>Medium</option>
                        <option>Hard</option>
                      </select>
                    </label>
                  </div>
                  <label>
                    Topic
                    <select name="topic" defaultValue={editing?.topic}>
                      {[
                        "Arrays",
                        "Sliding Window",
                        "Trees",
                        "Linked Lists",
                        "Dynamic Programming",
                        "Stacks",
                        "Binary Search",
                        "Graphs",
                        "Backtracking",
                        "Heaps",
                      ].map((t) => (
                        <option key={t}>{t}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Your approach
                    <textarea
                      name="approach"
                      defaultValue={editing?.approach}
                      rows={3}
                      maxLength={10000}
                      required
                      placeholder="What’s the key idea? Capture it in your own words."
                    />
                  </label>
                  <label>
                    Mistake or lesson <span className="muted">(optional)</span>
                    <textarea
                      name="notes"
                      defaultValue={editing?.notes}
                      rows={2}
                      maxLength={10000}
                      placeholder="What would you tell your future self?"
                    />
                  </label>
                  <div className="info-note">
                    <CalendarDays size={16} />
                    {editing
                      ? "Your current revision schedule will be preserved."
                      : "Your first revision will be scheduled for tomorrow."}
                  </div>
                  {error && (
                    <p className="error" role="alert">
                      {error}
                    </p>
                  )}
                  <button className="button primary full" disabled={busy}>
                    {busy
                      ? "Saving…"
                      : editing
                        ? "Save changes"
                        : "Add to my library"}
                    <ArrowRight size={17} />
                  </button>
                </form>
              </>
            )}
            {modal === "auth" && (
              <>
                <span className="modal-symbol">
                  <Leaf size={25} />
                </span>
                <h2 id="dialog-title">
                  {authRegister
                    ? "Start building your recall."
                    : "Welcome back."}
                </h2>
                <p>Connect to the Java backend to save your own collection.</p>
                <div className="info-note">
                  The hosted preview uses local demo data. Accounts require the
                  local Spring Boot server.
                </div>
                <form onSubmit={authenticate}>
                  {authRegister && (
                    <label>
                      Your name
                      <input
                        name="name"
                        required
                        maxLength={80}
                        placeholder="Alex Morgan"
                      />
                    </label>
                  )}
                  <label>
                    Email address
                    <input
                      name="email"
                      type="email"
                      required
                      placeholder="you@example.com"
                    />
                  </label>
                  <label>
                    Password
                    <input
                      name="password"
                      type="password"
                      required
                      minLength={8}
                      maxLength={72}
                      autoComplete={
                        authRegister ? "new-password" : "current-password"
                      }
                      placeholder="At least 8 characters"
                    />
                  </label>
                  {error && (
                    <p className="error" role="alert">
                      {error}
                    </p>
                  )}
                  <button className="button primary full" disabled={busy}>
                    {busy
                      ? "Connecting…"
                      : authRegister
                        ? "Create account"
                        : "Sign in"}
                    <ArrowRight size={17} />
                  </button>
                </form>
                <button
                  className="auth-toggle"
                  onClick={() => {
                    setAuthRegister(!authRegister);
                    setError("");
                  }}
                >
                  {authRegister
                    ? "Already have an account? Sign in"
                    : "New here? Create an account"}
                </button>
              </>
            )}
            {modal === "help" && (
              <>
                <span className="modal-symbol">
                  <Brain size={25} />
                </span>
                <h2 id="dialog-title">Give your memory a second chance.</h2>
                <p>
                  Spaced repetition brings back a problem just as its approach
                  starts to fade.
                </p>
                <div className="help-steps">
                  <div>
                    <b>01</b>
                    <span>
                      <strong>Save what you learned</strong>
                      <p>
                        Add the approach and the trap you want to avoid. First
                        revision: tomorrow.
                      </p>
                    </span>
                  </div>
                  <div>
                    <b>02</b>
                    <span>
                      <strong>Recall before you reveal</strong>
                      <p>
                        Explain the algorithm and complexity to yourself, then
                        compare your notes.
                      </p>
                    </span>
                  </div>
                  <div>
                    <b>03</b>
                    <span>
                      <strong>Be honest about recall</strong>
                      <p>
                        Again returns tomorrow. Good and Easy grow the interval.
                        Hard keeps it close.
                      </p>
                    </span>
                  </div>
                </div>
                <div className="info-note">
                  Intervals adapt to your previous attempts. Overdue problems
                  reschedule from today in your timezone.
                </div>
                <button
                  className="button primary full"
                  onClick={() => {
                    setModal(null);
                    go("Revision queue");
                  }}
                >
                  Find my next revision <ArrowRight size={17} />
                </button>
              </>
            )}
            {selected && (
              <>
                <div className="problem-modal-header">
                  <span className="eyebrow">
                    {focus
                      ? "FOCUS MODE · ONE PROBLEM AT A TIME"
                      : "FROM YOUR PROBLEM LIBRARY"}
                  </span>
                  <h2 id="dialog-title">{selected.title}</h2>
                  <div className="detail-tags">
                    <span
                      className={"badge " + selected.difficulty.toLowerCase()}
                    >
                      {selected.difficulty}
                    </span>
                    <span className="topic-tag">{selected.topic}</span>
                    <a href={selected.url} target="_blank" rel="noreferrer">
                      Open on {selected.platform} <ExternalLink size={13} />
                    </a>
                  </div>
                </div>
                {focus && (
                  <div className="recall-prompt">
                    <Brain size={28} />
                    <h3>Pause. Can you find the approach?</h3>
                    <p>
                      Think through the algorithm, its time complexity, and the
                      tricky edge cases. No peeking just yet.
                    </p>
                  </div>
                )}
                {!focus || revealed ? (
                  <div className="approach-notes">
                    <span className="eyebrow">YOUR SAVED APPROACH</span>
                    <p>{selected.approach}</p>
                    {selected.notes && (
                      <>
                        <span className="eyebrow">THE LESSON TO REMEMBER</span>
                        <p className="lesson">
                          <Lightbulb size={18} />
                          {selected.notes}
                        </p>
                      </>
                    )}
                  </div>
                ) : (
                  <button
                    className="reveal-button"
                    onClick={() => setRevealed(true)}
                  >
                    <Eye size={19} />
                    Reveal my approach <ChevronDown size={16} />
                  </button>
                )}
                {focus ? (
                  <>
                    <h3 className="grade-title">How well did you recall it?</h3>
                    <div className="grade-grid">
                      {(["Again", "Hard", "Good", "Easy"] as const).map(
                        (g, i) => (
                          <button
                            disabled={busy}
                            key={g}
                            className={"grade grade-" + i}
                            onClick={() => review(i as Grade)}
                          >
                            <strong>{g}</strong>
                            <span>
                              {schedule(selected, i as Grade).intervalDays}d
                            </span>
                          </button>
                        ),
                      )}
                    </div>
                    <p className="grade-help">
                      {selected.nextReviewOn < date
                        ? "Overdue: we’ll schedule your next review from today."
                        : `Scheduled after a ${selected.intervalDays}-day interval. Your grade sets the next one.`}
                    </p>
                  </>
                ) : (
                  <div className="detail-actions">
                    <button
                      className="button outline"
                      onClick={() => {
                        setEditing(selected);
                        setSelected(null);
                        setModal("add");
                      }}
                    >
                      <NotebookPen size={16} />
                      Edit
                    </button>
                    <button
                      className="button danger"
                      disabled={busy}
                      onClick={() => removeProblem(selected)}
                    >
                      <Trash2 size={16} />
                      Remove
                    </button>
                    <button
                      className="button primary"
                      onClick={() => {
                        setFocus(true);
                        setRevealed(false);
                      }}
                    >
                      Revise this problem <RotateCcw size={16} />
                    </button>
                  </div>
                )}
                {error && (
                  <p className="error" role="alert">
                    {error}
                  </p>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
