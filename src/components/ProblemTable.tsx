import { Code2, ArrowUpRight, CheckCheck } from "lucide-react";
import type { Problem } from "../model";
export function ProblemTable({
  items,
  queue = false,
  date,
  search,
  onOpen,
}: {
  items: Problem[];
  queue?: boolean;
  date: string;
  search: string;
  onOpen: (p: Problem, revise?: boolean) => void;
}) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Problem</th>
            <th>Difficulty</th>
            <th>Topic</th>
            <th>Confidence</th>
            <th>{queue ? "Status" : "Next review"}</th>
            <th>
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {items.map((p) => (
            <tr key={p.id}>
              <td>
                <button className="problem-title" onClick={() => onOpen(p)}>
                  <span className="platform-icon">
                    <Code2 size={17} />
                  </span>
                  <span>
                    {p.title}
                    <small>{p.platform}</small>
                  </span>
                </button>
              </td>
              <td>
                <span className={"badge " + p.difficulty.toLowerCase()}>
                  {p.difficulty}
                </span>
              </td>
              <td>
                <span className="topic-tag">{p.topic}</span>
              </td>
              <td>
                <span className="confidence">
                  <i>
                    <b style={{ width: p.confidence + "%" }} />
                  </i>
                  {p.confidence}%
                </span>
              </td>
              <td>
                {p.nextReviewOn < date ? (
                  <span className="overdue">
                    <i />
                    Overdue
                  </span>
                ) : p.nextReviewOn === date ? (
                  <span className="due">
                    <i />
                    Due today
                  </span>
                ) : (
                  <span className="muted">
                    {new Date(p.nextReviewOn + "T12:00:00").toLocaleDateString(
                      "en",
                      {
                        month: "short",
                        day: "numeric",
                      },
                    )}
                  </span>
                )}
              </td>
              <td>
                <button
                  className="row-action"
                  aria-label={"Revise " + p.title}
                  onClick={() => onOpen(p, true)}
                >
                  <ArrowUpRight size={17} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!items.length && (
        <div className="empty">
          <CheckCheck size={32} />
          <h3>{search ? "No matching problems" : "You’re all caught up"}</h3>
          <p>
            {search
              ? "Try another title or topic."
              : "Add a problem or return when your next revision is due."}
          </p>
        </div>
      )}
    </div>
  );
}
