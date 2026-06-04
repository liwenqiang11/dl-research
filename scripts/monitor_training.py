#!/usr/bin/env python3
"""Persistent Active Monitoring runner for long DL training jobs.

The runner performs deterministic checks on logs, metric CSV files,
checkpoints, and an optional process id/query. It records each observation as
JSONL so an agent can resume diagnosis without relying on chat memory.

Examples:
    python monitor_training.py --run-dir ./log/exp_001 --primary-metric val_loss --once
    setsid -f python monitor_training.py --run-dir ./log/exp_001 --pid 1234 \
        --primary-metric val_dose_mae > ./log/exp_001/monitor.out 2>&1 < /dev/null
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CRASH_PATTERNS = (
    "traceback",
    "runtimeerror",
    "cuda out of memory",
    "outofmemory",
    "segmentation fault",
    "killed",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def path_mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None


def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"missing_counts": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"missing_counts": {}}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n")


def process_alive_by_pid(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def process_alive_by_query(query: str) -> bool:
    try:
        output = subprocess.check_output(
            ["ps", "-eo", "pid=,cmd="],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        return False

    current_pid = os.getpid()
    parent_pid = os.getppid()
    for line in output.splitlines():
        line = line.strip()
        if not line or query not in line:
            continue
        parts = line.split(None, 1)
        try:
            pid = int(parts[0])
        except (IndexError, ValueError):
            continue
        if pid not in {current_pid, parent_pid}:
            return True
    return False


def tail_text(path: Path, max_bytes: int) -> str:
    try:
        size = path.stat().st_size
        with path.open("rb") as fh:
            fh.seek(max(0, size - max_bytes))
            return fh.read().decode("utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def has_nan_or_inf_text(text: str) -> bool:
    return bool(re.search(r"(^|[^a-zA-Z])(nan|inf|infinity)([^a-zA-Z]|$)", text, re.IGNORECASE))


def has_crash_text(text: str) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in CRASH_PATTERNS)


def read_metrics_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
    except (OSError, csv.Error, UnicodeDecodeError):
        return []

    parsed: list[dict[str, Any]] = []
    for row in rows:
        item: dict[str, Any] = {}
        for key, value in row.items():
            if key is None:
                continue
            value = "" if value is None else value.strip()
            if value == "":
                item[key] = value
                continue
            try:
                number = float(value)
            except ValueError:
                item[key] = value
            else:
                item[key] = number
        parsed.append(item)
    return parsed


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def infer_metric_mode(metric: str) -> str:
    name = metric.lower()
    maximize_tokens = ("acc", "auc", "dice", "iou", "ssim", "psnr", "f1", "precision", "recall")
    minimize_tokens = ("loss", "mae", "mse", "rmse", "error", "err", "wer", "cer")
    if any(token in name for token in maximize_tokens):
        return "max"
    if any(token in name for token in minimize_tokens):
        return "min"
    return "min"


def is_better(value: float, best: float, mode: str, min_delta: float) -> bool:
    if mode == "max":
        return value > best + min_delta
    return value < best - min_delta


def no_improvement_count(rows: list[dict[str, Any]], metric: str, mode: str, min_delta: float) -> int:
    values = [float(row[metric]) for row in rows if finite_number(row.get(metric))]
    if not values:
        return 0
    best = values[0]
    best_index = 0
    for index, value in enumerate(values[1:], start=1):
        if is_better(value, best, mode, min_delta):
            best = value
            best_index = index
    return len(values) - 1 - best_index


def consecutive_worse_count(values: list[float], mode: str, min_delta: float) -> int:
    count = 0
    for prev, cur in zip(reversed(values[:-1]), reversed(values[1:])):
        worse = cur < prev - min_delta if mode == "max" else cur > prev + min_delta
        if not worse:
            break
        count += 1
    return count


def find_first_existing_column(rows: list[dict[str, Any]], names: tuple[str, ...]) -> str | None:
    if not rows:
        return None
    columns = set(rows[-1].keys())
    for name in names:
        if name in columns:
            return name
    return None


def latest_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    row = rows[-1]
    wanted: dict[str, Any] = {}
    for key, value in row.items():
        lower = key.lower()
        if key == "epoch" or any(token in lower for token in ("loss", "metric", "mae", "psnr", "ssim", "acc", "dice", "lr")):
            wanted[key] = value
    return wanted


def classify(args: argparse.Namespace, state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    now = time.time()
    status = "normal"
    triggers: list[dict[str, Any]] = []
    diagnosis: list[str] = []

    train_log = Path(args.train_log) if args.train_log else None
    metrics_file = Path(args.metrics_file) if args.metrics_file else None
    heartbeat = Path(args.heartbeat) if args.heartbeat else None
    checkpoints = [Path(item) for item in args.checkpoint]

    monitored_paths: list[tuple[str, Path]] = []
    if train_log:
        monitored_paths.append(("train_log", train_log))
    if metrics_file:
        monitored_paths.append(("metrics_file", metrics_file))
    if heartbeat:
        monitored_paths.append(("heartbeat", heartbeat))
    monitored_paths.extend((f"checkpoint:{path.name}", path) for path in checkpoints)

    missing_counts = dict(state.get("missing_counts", {}))
    mtimes: dict[str, float] = {}
    missing: list[str] = []
    for label, path in monitored_paths:
        mtime = path_mtime(path)
        if mtime is None:
            missing.append(str(path))
            missing_counts[str(path)] = missing_counts.get(str(path), 0) + 1
            count = missing_counts[str(path)]
            if count >= 2:
                triggers.append({"status": "critical", "type": "missing_artifact", "path": str(path), "count": count})
            else:
                triggers.append({"status": "warning", "type": "missing_artifact", "path": str(path), "count": count})
        else:
            missing_counts[str(path)] = 0
            mtimes[label] = mtime

    fresh_mtimes = list(mtimes.values())
    if fresh_mtimes:
        age_minutes = (now - max(fresh_mtimes)) / 60.0
        if age_minutes >= args.heartbeat_critical_minutes:
            triggers.append({"status": "critical", "type": "stale_heartbeat", "age_minutes": round(age_minutes, 2)})
        elif age_minutes >= args.heartbeat_warning_minutes:
            triggers.append({"status": "warning", "type": "stale_heartbeat", "age_minutes": round(age_minutes, 2)})

    process_checked = bool(args.pid or args.process_query)
    process_alive = None
    if args.pid:
        process_alive = process_alive_by_pid(args.pid)
    elif args.process_query:
        process_alive = process_alive_by_query(args.process_query)
    if process_checked and not process_alive:
        triggers.append({"status": "critical", "type": "process_exit", "pid": args.pid, "query": args.process_query})

    log_tail = tail_text(train_log, args.log_tail_bytes) if train_log else ""
    if log_tail:
        if has_nan_or_inf_text(log_tail):
            triggers.append({"status": "critical", "type": "nan_or_inf_in_log"})
        if has_crash_text(log_tail):
            triggers.append({"status": "critical", "type": "crash_text_in_log"})

    rows = read_metrics_csv(metrics_file) if metrics_file else []
    nan_metrics: list[str] = []
    for row in rows[-args.trend_window :]:
        for key, value in row.items():
            if isinstance(value, float) and not math.isfinite(value):
                nan_metrics.append(key)
    if nan_metrics:
        triggers.append({"status": "critical", "type": "nan_or_inf_in_metrics", "columns": sorted(set(nan_metrics))})

    primary_mode = args.primary_mode
    if primary_mode == "auto":
        primary_mode = infer_metric_mode(args.primary_metric) if args.primary_metric else "min"

    primary_values: list[float] = []
    if args.primary_metric and rows and args.primary_metric in rows[-1]:
        primary_values = [float(row[args.primary_metric]) for row in rows if finite_number(row.get(args.primary_metric))]
        stale_count = no_improvement_count(rows, args.primary_metric, primary_mode, args.min_delta)
        if stale_count >= args.no_improve_fail_epochs:
            triggers.append({"status": "failed", "type": "no_primary_improvement", "epochs": stale_count})
        elif stale_count >= args.no_improve_warning_epochs:
            triggers.append({"status": "warning", "type": "no_primary_improvement", "epochs": stale_count})
        worse_count = consecutive_worse_count(primary_values, primary_mode, args.min_delta)
        if worse_count >= args.primary_worsen_critical_epochs:
            triggers.append({"status": "critical", "type": "primary_metric_worsening", "epochs": worse_count})
        elif worse_count >= args.primary_worsen_warning_epochs:
            triggers.append({"status": "warning", "type": "primary_metric_worsening", "epochs": worse_count})

    train_loss_col = find_first_existing_column(rows, ("train_loss", "loss_train", "training_loss"))
    val_loss_col = find_first_existing_column(rows, ("val_loss", "valid_loss", "validation_loss"))
    if rows and train_loss_col and val_loss_col:
        train_values = [float(row[train_loss_col]) for row in rows if finite_number(row.get(train_loss_col))]
        val_values = [float(row[val_loss_col]) for row in rows if finite_number(row.get(val_loss_col))]
        loss_stale = no_improvement_count(rows, train_loss_col, "min", args.min_delta)
        if loss_stale >= args.loss_no_decrease_fail_epochs:
            triggers.append({"status": "failed", "type": "loss_no_meaningful_decrease", "epochs": loss_stale})
        elif loss_stale >= args.loss_no_decrease_warning_epochs:
            triggers.append({"status": "warning", "type": "loss_no_meaningful_decrease", "epochs": loss_stale})

        paired = min(len(train_values), len(val_values))
        if paired >= 2:
            overfit_count = 0
            for idx in range(paired - 1, 0, -1):
                train_improves = train_values[idx] < train_values[idx - 1] - args.min_delta
                val_degrades = val_values[idx] > val_values[idx - 1] + args.min_delta
                if not (train_improves and val_degrades):
                    break
                overfit_count += 1
            if overfit_count >= args.overfit_critical_epochs:
                triggers.append({"status": "critical", "type": "train_improves_val_degrades", "epochs": overfit_count})
            elif overfit_count >= args.overfit_warning_epochs:
                triggers.append({"status": "warning", "type": "train_improves_val_degrades", "epochs": overfit_count})

    severity_order = {"normal": 0, "warning": 1, "critical": 2, "failed": 3}
    for trigger in triggers:
        if severity_order[trigger["status"]] > severity_order[status]:
            status = trigger["status"]

    if status == "normal":
        diagnosis.append("No default trigger fired.")
    else:
        trigger_types = ", ".join(sorted({item["type"] for item in triggers}))
        diagnosis.append(f"Triggered checks: {trigger_types}.")
    if process_checked:
        diagnosis.append("Process is alive." if process_alive else "Process is not alive.")
    if rows:
        diagnosis.append(f"Metrics rows parsed: {len(rows)}.")
    elif metrics_file:
        diagnosis.append("No metric rows parsed yet.")

    record = {
        "time": utc_now(),
        "run_dir": str(args.run_dir) if args.run_dir else None,
        "status": status,
        "triggers": triggers,
        "latest_metrics": latest_metrics(rows),
        "primary_metric": args.primary_metric,
        "primary_mode": primary_mode,
        "process": {"checked": process_checked, "alive": process_alive, "pid": args.pid, "query": args.process_query},
        "files": {"mtimes": mtimes, "missing": missing},
        "diagnosis": diagnosis,
        "next_check_seconds": args.interval_seconds if not args.once else None,
    }

    next_state = dict(state)
    next_state["missing_counts"] = missing_counts
    next_state["last_record"] = record
    return record, next_state


def default_paths(run_dir: Path | None, args: argparse.Namespace) -> None:
    if run_dir is None:
        return
    if args.train_log is None:
        candidate = run_dir / "train.log"
        if candidate.exists():
            args.train_log = str(candidate)
    if args.metrics_file is None:
        candidate = run_dir / "history.csv"
        if candidate.exists():
            args.metrics_file = str(candidate)
    if not args.checkpoint:
        checkpoint_candidates = (
            run_dir / "latest.pt",
            run_dir / "best.pt",
            run_dir / "checkpoints" / "latest.pt",
            run_dir / "checkpoints" / "best.pt",
        )
        args.checkpoint = [str(path) for path in checkpoint_candidates if path.exists()]
    if args.output_jsonl is None:
        args.output_jsonl = str(run_dir / "monitoring_events.jsonl")
    if args.state_file is None:
        args.state_file = str(run_dir / "monitoring_state.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Active Monitoring runner for DL training jobs")
    parser.add_argument("--run-dir", type=Path, help="Experiment output directory")
    parser.add_argument("--train-log", help="Training log file")
    parser.add_argument("--metrics-file", help="CSV metrics file, such as history.csv")
    parser.add_argument("--heartbeat", help="Optional heartbeat/status file")
    parser.add_argument("--checkpoint", action="append", default=[], help="Checkpoint artifact to monitor; repeatable")
    parser.add_argument("--pid", type=int, help="Training process id")
    parser.add_argument("--process-query", help="Substring to find in `ps -eo pid,cmd`")
    parser.add_argument("--primary-metric", help="Primary validation metric column in the CSV")
    parser.add_argument("--primary-mode", choices=("auto", "min", "max"), default="auto")
    parser.add_argument("--interval-seconds", type=int, default=300, help="Check interval; default 5 minutes")
    parser.add_argument("--once", action="store_true", help="Run one check and exit")
    parser.add_argument("--output-jsonl", help="Monitoring event log path")
    parser.add_argument("--state-file", help="Persistent state path")
    parser.add_argument("--trend-window", type=int, default=10)
    parser.add_argument("--heartbeat-warning-minutes", type=float, default=10.0)
    parser.add_argument("--heartbeat-critical-minutes", type=float, default=20.0)
    parser.add_argument("--no-improve-warning-epochs", type=int, default=10)
    parser.add_argument("--no-improve-fail-epochs", type=int, default=20)
    parser.add_argument("--overfit-warning-epochs", type=int, default=5)
    parser.add_argument("--overfit-critical-epochs", type=int, default=10)
    parser.add_argument("--primary-worsen-warning-epochs", type=int, default=5)
    parser.add_argument("--primary-worsen-critical-epochs", type=int, default=10)
    parser.add_argument("--loss-no-decrease-warning-epochs", type=int, default=10)
    parser.add_argument("--loss-no-decrease-fail-epochs", type=int, default=20)
    parser.add_argument("--min-delta", type=float, default=1e-8)
    parser.add_argument("--log-tail-bytes", type=int, default=65536)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    default_paths(args.run_dir, args)

    if not args.output_jsonl:
        args.output_jsonl = "monitoring_events.jsonl"
    if not args.state_file:
        args.state_file = "monitoring_state.json"

    output_jsonl = Path(args.output_jsonl)
    state_file = Path(args.state_file)

    stop_requested = False

    def request_stop(signum: int, _frame: Any) -> None:
        nonlocal stop_requested
        stop_requested = True
        append_jsonl(output_jsonl, {"time": utc_now(), "status": "stopped", "signal": signum})

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    while True:
        state = read_state(state_file)
        record, next_state = classify(args, state)
        append_jsonl(output_jsonl, record)
        write_json(state_file, next_state)
        print(json.dumps(record, ensure_ascii=False), flush=True)

        if args.once or stop_requested:
            break
        time.sleep(max(1, args.interval_seconds))

    return 0


if __name__ == "__main__":
    sys.exit(main())
