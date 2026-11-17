import { Flame } from "lucide-react";
export function Activity({
  activity,
}: {
  activity: { date: string; count: number }[];
}) {
  return (
    <div className="activity-card glass">
      <div className="activity-heading">
        <h2>
          Consistency compounds<span>Every square is a step forward.</span>
        </h2>
        <span className="activity-total">
          <Flame size={15} />
          {activity.filter((d) => d.count > 0).length} active days
        </span>
      </div>
      <div className="activity-chart">
        <div className="day-labels">
          <span>Mon</span>
          <span />
          <span>Wed</span>
          <span />
          <span>Fri</span>
          <span />
          <span />
        </div>
        <div className="heatmap">
          {activity.map((d) => (
            <div
              key={d.date}
              className={"heat-cell level-" + Math.min(d.count, 4)}
              title={`${d.date}: ${d.count} revision${d.count !== 1 ? "s" : ""}`}
              aria-label={`${d.date}: ${d.count} revisions`}
            />
          ))}
        </div>
      </div>
      <div className="activity-footer">
        <span>Last 12 weeks</span>
        <div>
          Less{" "}
          {[0, 1, 2, 3, 4].map((i) => (
            <i key={i} className={"level-" + i} />
          ))}{" "}
          More
        </div>
      </div>
    </div>
  );
}
