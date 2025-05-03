#!/usr/bin/env python3
"""
qnet_cli.py – lightweight CLI wrapper around simulation.runner.run

Example
-------
Run a 4‑node chain, 50 km per hop, DEJMPS purification (2 rounds):

    python qnet_cli.py \
        --topology chain \
        --nodes 4 \
        --link-length 50 \
        --strategy purify_then_swap \
        --protocol dejmps \
        --rounds 2 \
        --coherence-time 1.0 \
        --att-len 20000 \
        --runs 500 \
        --seed 42 \
        --output chain_run.json
"""
import argparse
import json
from pathlib import Path
from typing import Any, Dict

from simulation.runner import run


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="qnet_cli.py",
        description="Run a quantum‑network Monte‑Carlo simulation."
    )

    # --- topology & layout --------------------------------------------------
    p.add_argument("-t", "--topology",
                   required=True,
                   choices=["chain", "ring", "star"],
                   help="Network topology")
    p.add_argument("-n", "--nodes",
                   type=int,
                   default=4,
                   help="Number of nodes (≥3, ≥4 for chain)")
    p.add_argument("-L", "--link-length",
                   type=float,
                   default=25,
                   metavar="KM",
                   help="Link length PER HOP in kilometres (default 25 km)")

    # --- strategy & protocol ------------------------------------------------
    p.add_argument("-s", "--strategy",
                   choices=["purify_then_swap", "swap_then_purify"],
                   default="purify_then_swap",
                   help="High‑level entanglement‑distribution strategy")
    p.add_argument("-p", "--protocol",
                   choices=["dejmps", "bbpssw"],
                   default="dejmps",
                   help="Purification protocol")
    p.add_argument("-r", "--rounds",
                   type=int,
                   default=2,
                   help="Number of purification rounds")
    p.add_argument("-f", "--filter-threshold",
                   type=float,
                   default=0.9,
                   help="Fidelity threshold for optional local filtering")

    # --- noise / channel ----------------------------------------------------
    p.add_argument("-c", "--coherence-time",
                   type=float,
                   default=1.0,
                   metavar="SEC",
                   help="Memory coherence time T_coh (seconds)")
    p.add_argument("-a", "--att-len",
                   type=float,
                   default=20_000,
                   metavar="M",
                   help="Attenuation length L_att (metres)")

    # --- Monte‑Carlo settings ----------------------------------------------
    p.add_argument("--runs",
                   type=int,
                   default=100,
                   help="Number of independent repetitions")
    p.add_argument("--seed",
                   type=int,
                   default=0,
                   help="PRNG seed")

    # --- output -------------------------------------------------------------
    p.add_argument("-o", "--output",
                   type=Path,
                   help="Write JSON summary to this file (stdout if omitted)")

    return p


# main entry‑point
def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Convert argparse Namespace to plain dict
    cfg: Dict[str, Any] = vars(args).copy()

    # 1. Path objects are NOT JSON‑serialisable -> convert to str / drop
    # 2. simulation.runner.run should NOT see a Path ->convert to str
    out_path: Path | None = cfg.pop("output", None)
    if out_path is not None:
        cfg["output"] = str(out_path)
    # Seed NumPy
    if cfg.get("seed") is not None:
        import numpy as np
        np.random.seed(cfg["seed"])

    summary = run(cfg, collect=True)

    summary_json = json.dumps(summary, indent=2)

    if out_path:
        out_path.write_text(summary_json)
        print(f"[qnet‑cli] results at {out_path}")
    else:
        print(summary_json)


if __name__ == "__main__":
    main()
