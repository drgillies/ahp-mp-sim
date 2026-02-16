from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _fmt_float(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):,.{digits}f}"


def _find_latest_run_file(root: Path) -> Path:
    data_dir = root / "data"
    run_files = list(data_dir.glob("work_order_sim_*.csv"))
    if not run_files:
        run_files = list(root.glob("work_order_sim_*.csv"))
    if not run_files:
        raise FileNotFoundError("No run files found matching work_order_sim_*.csv")
    return max(run_files, key=lambda p: p.stat().st_mtime)


def _build_stats(df: pd.DataFrame) -> dict[str, float | int | None]:
    total_rows = len(df)
    called = int(df["called"].sum()) if "called" in df else 0
    completed = int(df["completion"].sum()) if "completion" in df else 0
    completion_rate = (completed / total_rows * 100) if total_rows else 0

    first_call_day = df["call_day"].dropna().min() if "call_day" in df else None
    last_call_day = df["call_day"].dropna().max() if "call_day" in df else None
    first_completion_day = (
        df["completion_day"].dropna().min() if "completion_day" in df else None
    )
    last_completion_day = (
        df["completion_day"].dropna().max() if "completion_day" in df else None
    )

    completed_df = df[df["completion"] == True].copy()
    if not completed_df.empty:
        completed_df["lead_days"] = completed_df["completion_day"] - completed_df["call_day"]
        avg_lead_days = completed_df["lead_days"].mean()
        avg_completion_counter = completed_df["completion_counter"].mean()
        avg_planned_counter = completed_df["next_planned_counter"].mean()
        avg_counter_variance = (
            completed_df["completion_counter"] - completed_df["next_planned_counter"]
        ).mean()
    else:
        avg_lead_days = None
        avg_completion_counter = None
        avg_planned_counter = None
        avg_counter_variance = None

    return {
        "total_rows": total_rows,
        "called": called,
        "completed": completed,
        "completion_rate": completion_rate,
        "first_call_day": first_call_day,
        "last_call_day": last_call_day,
        "first_completion_day": first_completion_day,
        "last_completion_day": last_completion_day,
        "avg_lead_days": avg_lead_days,
        "avg_completion_counter": avg_completion_counter,
        "avg_planned_counter": avg_planned_counter,
        "avg_counter_variance": avg_counter_variance,
    }


def _save_visuals(df: pd.DataFrame, assets_dir: Path) -> dict[str, str]:
    assets_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}

    # 1) Planned vs actual counter progression
    completed_df = df[df["completion"] == True].sort_values("call_number")
    plt.figure(figsize=(9, 4))
    if not completed_df.empty:
        plt.plot(
            completed_df["call_number"],
            completed_df["next_planned_counter"],
            marker="o",
            linewidth=1.8,
            color="#4a5568",
            label="Planned Counter",
        )
        plt.plot(
            completed_df["call_number"],
            completed_df["completion_counter"],
            marker="o",
            linewidth=1.8,
            color="#2b6cb0",
            label="Actual Completion Counter",
        )
    plt.title("Planned vs Actual Counter by Call Number")
    plt.xlabel("Call Number")
    plt.ylabel("Counter")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    counter_file = assets_dir / "completion_counter_trend.png"
    plt.savefig(counter_file, dpi=140)
    plt.close()
    paths["completion_counter"] = counter_file.name

    # 2) Counter variance by call (actual - planned)
    plt.figure(figsize=(9, 4))
    if not completed_df.empty:
        counter_variance = (
            completed_df["completion_counter"] - completed_df["next_planned_counter"]
        )
        colors = ["#38a169" if v <= 0 else "#dd6b20" for v in counter_variance]
        bars = plt.bar(completed_df["call_number"], counter_variance, color=colors)
        plt.axhline(0, color="#4a5568", linewidth=1)
        for bar, val in zip(bars, counter_variance):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:.1f}",
                ha="center",
                va="bottom" if val >= 0 else "top",
            )
    plt.title("Counter Variance by Call")
    plt.xlabel("Call Number")
    plt.ylabel("Counter (Actual - Planned)")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    counter_var_file = assets_dir / "counter_variance.png"
    plt.savefig(counter_var_file, dpi=140)
    plt.close()
    paths["counter_variance"] = counter_var_file.name

    return paths


def build_markdown_report(
    df: pd.DataFrame, run_file: Path, stats: dict[str, float | int | None]
) -> str:
    per_item = []
    if "item" in df.columns:
        grouped = df.groupby("item", dropna=False)
        for item, item_df in grouped:
            item_completed = item_df[item_df["completion"] == True]
            item_completion_rate = (
                (len(item_completed) / len(item_df) * 100) if len(item_df) else 0
            )
            per_item.append(
                (
                    str(item),
                    len(item_df),
                    int(item_df["called"].sum()),
                    int(item_df["completion"].sum()),
                    item_completion_rate,
                    item_completed["completion_counter"].mean()
                    if not item_completed.empty
                    else None,
                )
            )

    timeline = df.sort_values(
        by=["call_day", "completion_day", "call_number"], na_position="last"
    ).head(12)

    lines: list[str] = []
    lines.append("# Last Run Report")
    lines.append("")
    lines.append(f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"- Source file: `{run_file.name}`")
    lines.append("")
    lines.append("## Run Summary")
    lines.append("")
    lines.append(f"- Total planned work orders: **{stats['total_rows']}**")
    lines.append(f"- Called work orders: **{stats['called']}**")
    lines.append(f"- Completed work orders: **{stats['completed']}**")
    lines.append(f"- Completion rate: **{stats['completion_rate']:.1f}%**")
    lines.append(f"- First call day: **{_fmt_float(stats['first_call_day'], 0)}**")
    lines.append(f"- Last call day: **{_fmt_float(stats['last_call_day'], 0)}**")
    lines.append(
        f"- First completion day: **{_fmt_float(stats['first_completion_day'], 0)}**"
    )
    lines.append(
        f"- Last completion day: **{_fmt_float(stats['last_completion_day'], 0)}**"
    )
    lines.append(f"- Average lead time (days): **{_fmt_float(stats['avg_lead_days'])}**")
    lines.append(
        f"- Average planned counter: **{_fmt_float(stats['avg_planned_counter'])}**"
    )
    lines.append(
        f"- Average completion counter: **{_fmt_float(stats['avg_completion_counter'])}**"
    )
    lines.append(
        f"- Average counter variance (actual - planned): **{_fmt_float(stats['avg_counter_variance'])}**"
    )
    lines.append("")
    lines.append("## Per Item Breakdown")
    lines.append("")
    lines.append(
        "| Item | Planned | Called | Completed | Completion Rate | Avg Completion Counter |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|")
    for item, planned, item_called, item_completed, item_rate, item_counter in per_item:
        lines.append(
            f"| {item} | {planned} | {item_called} | {item_completed} | {item_rate:.1f}% | {_fmt_float(item_counter)} |"
        )
    lines.append("")
    lines.append("## First 12 Timeline Rows")
    lines.append("")
    lines.append(
        "| Call # | Item | Call Day | Planned Day | Completion Day | Completion Counter |"
    )
    lines.append("|---:|---|---:|---:|---:|---:|")
    for row in timeline.itertuples():
        lines.append(
            f"| {int(row.call_number)} | {row.item} | {_fmt_float(row.call_day, 0)} | "
            f"{_fmt_float(row.planned_day, 0)} | {_fmt_float(row.completion_day, 0)} | "
            f"{_fmt_float(row.completion_counter)} |"
        )
    return "\n".join(lines) + "\n"


def build_html_dashboard(
    run_file: Path, stats: dict[str, float | int | None], image_paths: dict[str, str]
) -> str:
    generated_at = datetime.now().isoformat(timespec="seconds")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Last Run Dashboard</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --accent: #2563eb;
      --border: #e5e7eb;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      color: var(--text);
      background: linear-gradient(180deg, #f9fbff 0%, #eef3fb 100%);
    }}
    .wrap {{
      max-width: 1100px;
      margin: 28px auto;
      padding: 0 16px 24px;
    }}
    .header {{
      margin-bottom: 16px;
    }}
    .header h1 {{
      margin: 0 0 8px;
      font-size: 1.9rem;
    }}
    .meta {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 16px 0 20px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }}
    .label {{
      color: var(--muted);
      font-size: 0.88rem;
    }}
    .value {{
      margin-top: 6px;
      font-size: 1.3rem;
      font-weight: 700;
    }}
    .section {{
      margin-top: 20px;
    }}
    .section h2 {{
      margin: 0 0 10px;
      font-size: 1.2rem;
    }}
    .charts {{
      display: grid;
      gap: 14px;
      grid-template-columns: 1fr;
    }}
    .charts img {{
      width: 100%;
      height: auto;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: #fff;
      display: block;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <h1>Last Run Dashboard</h1>
      <div class="meta">Source: {run_file.name} | Generated: {generated_at}</div>
    </div>

    <div class="grid">
      <div class="card"><div class="label">Planned Work Orders</div><div class="value">{int(stats["total_rows"] or 0)}</div></div>
      <div class="card"><div class="label">Called Work Orders</div><div class="value">{int(stats["called"] or 0)}</div></div>
      <div class="card"><div class="label">Completed Work Orders</div><div class="value">{int(stats["completed"] or 0)}</div></div>
      <div class="card"><div class="label">Completion Rate</div><div class="value">{(stats["completion_rate"] or 0):.1f}%</div></div>
      <div class="card"><div class="label">Avg Planned Counter</div><div class="value">{_fmt_float(stats["avg_planned_counter"])}</div></div>
      <div class="card"><div class="label">Avg Actual Counter</div><div class="value">{_fmt_float(stats["avg_completion_counter"])}</div></div>
      <div class="card"><div class="label">Counter Variance (A-P)</div><div class="value">{_fmt_float(stats["avg_counter_variance"])}</div></div>
    </div>

    <div class="section">
      <h2>Run Visuals</h2>
      <div class="charts">
        <img src="last_run_assets/{image_paths['completion_counter']}" alt="Planned vs actual counter trend">
        <img src="last_run_assets/{image_paths['counter_variance']}" alt="Counter variance by call">
      </div>
    </div>
  </div>
</body>
</html>
"""


def main() -> None:
    root = Path(".")
    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    latest_run = _find_latest_run_file(root)
    df = pd.read_csv(latest_run)
    stats = _build_stats(df)

    assets_dir = reports_dir / "last_run_assets"
    image_paths = _save_visuals(df, assets_dir)

    markdown_report = build_markdown_report(df, latest_run, stats)
    (reports_dir / "last_run_report.md").write_text(markdown_report, encoding="utf-8")

    html_report = build_html_dashboard(latest_run, stats, image_paths)
    (reports_dir / "last_run_report.html").write_text(html_report, encoding="utf-8")

    print(f"Wrote reports/last_run_report.md from {latest_run.name}")
    print(f"Wrote reports/last_run_report.html with visuals from {latest_run.name}")


if __name__ == "__main__":
    main()
