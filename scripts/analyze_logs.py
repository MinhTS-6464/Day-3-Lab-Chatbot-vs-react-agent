"""Parse logs/*.log and print metrics summary for reports."""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"


def analyze(path: Path) -> dict:
    metrics = []
    events = defaultdict(int)
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        ev = row.get("event", "")
        events[ev] += 1
        if ev == "LLM_METRIC":
            metrics.append(row.get("data", {}))

    latencies = [m.get("latency_ms", 0) for m in metrics]
    tokens = [m.get("total_tokens", 0) for m in metrics]
    costs = [m.get("cost_estimate", 0) for m in metrics]

    def p50(vals):
        if not vals:
            return 0
        s = sorted(vals)
        return s[len(s) // 2]

    return {
        "file": path.name,
        "event_counts": dict(events),
        "llm_calls": len(metrics),
        "latency_p50_ms": p50(latencies),
        "latency_max_ms": max(latencies) if latencies else 0,
        "avg_tokens": round(sum(tokens) / len(tokens), 1) if tokens else 0,
        "total_cost_estimate_usd": round(sum(costs), 4),
    }


def main():
    files = sorted(LOG_DIR.glob("*.log"))
    if not files:
        print("No log files in logs/")
        sys.exit(1)
    for f in files:
        s = analyze(f)
        print(json.dumps(s, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
