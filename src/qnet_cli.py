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
import argparse, json, random
from pathlib import Path
from typing import Any, Dict

from simulation.runner import run


# helpers
def build_parser() -> argparse.ArgumentParser:
    """Builds and returns the argument parser for the qnet_cli command-line interface.

    This function defines all command-line arguments for configuring the quantum network Monte-Carlo simulation.

    Returns:
        An argparse.ArgumentParser instance configured with all CLI options.
    """
    p = argparse.ArgumentParser(
        prog="qnet_cli.py",
        description="Run a quantum‑network Monte‑Carlo simulation."
    )

    # topology
    p.add_argument("-t", "--topology", required=True,
                   choices=["chain", "ring", "star"],
                   help="Network topology")
    p.add_argument("-n", "--nodes", type=int, default=4,
                   help="Number of nodes")
    p.add_argument("-L", "--link-length", type=float, default=25, metavar="KM",
                   help="Link length per hop (km)")

    # strategy / protocol
    p.add_argument("-s", "--strategy",
                   choices=["purify_then_swap", "swap_then_purify"],
                   default="purify_then_swap")
    p.add_argument("-p", "--protocol",
                   choices=["dejmps", "bbpssw"], default="dejmps")
    p.add_argument("-r", "--rounds", type=int, default=2,
                   help="Purification rounds")
    p.add_argument("-f", "--filter-threshold", type=float, default=0.9,
                   help="Fidelity acceptance threshold")

    # physical parameters
    p.add_argument("-c", "--coherence-time", type=float, default=1.0, metavar="S",
                   help="Memory coherence time (s)")
    p.add_argument("-a", "--att-len", type=float, default=22, metavar="KM",
                   help="Attenuation length L_att (km)")

    # Monte‑Carlo
    p.add_argument("--runs", type=int, default=100,
                   help="Number of repetitions")
    p.add_argument("--seed", type=int, default=None,
                   help="PRNG seed")

    # output
    p.add_argument("-o", "--output", type=Path,
                   help="Write JSON summary to this file (stdout if omitted)")
    return p


# main
def main(argv: list[str] | None = None) -> None:
    """Main entry point for the qnet_cli command-line interface.

    This function parses command-line arguments, runs the simulation, and outputs the results to a file or stdout.
    """
    args = build_parser().parse_args(argv)
    cfg: Dict[str, Any] = vars(args).copy()

    out_path: Path | None = cfg.pop("output", None)

    if cfg.get("seed") is not None:
        import numpy as np
        np.random.seed(cfg["seed"])
        random.seed(cfg["seed"])

    summary = run(cfg, collect=True)
    summary_json = json.dumps(summary, indent=2)

    if out_path:
        out_path.write_text(summary_json)
        print(f"[qnet‑cli] results saved to {out_path}")
    else:
        print(summary_json)


if __name__ == "__main__":
    main()
