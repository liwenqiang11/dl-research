#!/usr/bin/env python3
"""Run an Evidence-phase sanity check command.

Usage:
    python sanity_check.py --train-script train.py [--num-steps 50] [--target-loss 0.01]
    python sanity_check.py --command "python train.py --fast-dev-run"

The train-script mode assumes the target script supports:
    --sanity-check --num-steps <N> --target-loss <X>
"""

import argparse
import os
import shlex
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Sanity check for DL training")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--train-script", help="Path to a training script with --sanity-check support")
    mode.add_argument("--command", help="Full sanity command to run, quoted as one string")
    parser.add_argument("--num-steps", type=int, default=50, help="Number of overfit steps")
    parser.add_argument("--target-loss", type=float, default=0.01, help="Target loss threshold")
    parser.add_argument(
        "--extra-args",
        nargs=argparse.REMAINDER,
        default=[],
        help="Extra args passed through to the train script",
    )
    parser.add_argument("--cwd", default=os.getcwd(), help="Working directory for the command")
    parser.add_argument("--dry-run", action="store_true", help="Print the command without running it")
    args = parser.parse_args()

    extra_args = args.extra_args
    if extra_args and extra_args[0] == "--":
        extra_args = extra_args[1:]

    if args.command:
        cmd = shlex.split(args.command)
    else:
        cmd = [
            sys.executable,
            args.train_script,
            "--sanity-check",
            "--num-steps",
            str(args.num_steps),
            "--target-loss",
            str(args.target_loss),
            *extra_args,
        ]

    print("[sanity_check] Evidence sanity check")
    print(f"[sanity_check] cwd: {args.cwd}")
    print(f"[sanity_check] command: {shlex.join(cmd)}")
    if not args.command:
        print(f"[sanity_check] expected behavior: tiny-batch overfit for {args.num_steps} steps")
        print(f"[sanity_check] target loss: {args.target_loss}")

    if args.dry_run:
        print("[sanity_check] dry run complete")
        return

    result = subprocess.run(cmd, cwd=args.cwd)

    if result.returncode != 0:
        print(f"[sanity_check] FAILED: command exited with code {result.returncode}")
        sys.exit(1)

    print("[sanity_check] Complete. Record loss convergence, shape/gradient checks, and any limitations.")


if __name__ == "__main__":
    main()
