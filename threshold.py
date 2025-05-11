#!/usr/bin/env python3

from __future__ import annotations
import argparse, subprocess, sys, re
from pathlib import Path

CLI = Path(__file__).with_name("qnet_cli.py")
ERR = re.compile(r"exceeded | Exceeded", re.I)

def parse_args() -> tuple[argparse.Namespace, list[str]]:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--start", type=float, default=0.5)
    p.add_argument("--max", type=float, default=1.0)
    p.add_argument("--step", type=float, default=0.02)
    p.add_argument("--runs", type=int, default=400)

    known, rest = p.parse_known_args()
    return known, rest

def run_once(thresh: float, extra_args: list[str], runs: int) -> bool:
    cmd = [sys.executable, str(CLI),
           "--strategy", "swap_then_purify",
           "--filter-threshold", f"{thresh:.4f}",
           "--runs", str(runs),
           *extra_args]

    result = subprocess.run(cmd, capture_output=True, text=True)
    combined_out = (result.stdout or "") + (result.stderr or "")
    failed = (
        result.returncode != 0 or
        ERR.search(combined_out) is not None
    )
    print(f"  {'FAIL' if failed else 'OK'}: {thresh:.4f} ({result.returncode})")

    return not failed

def main() -> None:
    wrap, forwarded = parse_args()
    current = wrap.start
    step = wrap.step
    upper = wrap.max
    runs = wrap.runs

    last_ok = None
    while current <= upper + 1e-9:
        ok = run_once(current, forwarded, runs)
        if not ok:
            break
        last_ok = current
        current = round(current + step, 4)
    if last_ok is None:
        print("No valid threshold found")
    else:
        print(f"Last valid threshold: {last_ok:.4f}")
        print(f"Next threshold: {round(last_ok + step, 4):.4f}")

if __name__ == "__main__":
    main()