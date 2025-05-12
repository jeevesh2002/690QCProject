
#!/usr/bin/env python3
"""sweep.py – parameter sweep and data collection for the quantum‑network simulator.
Example
    python srcipts/sweep.py --runs 150 --outfile results/sweep_150.csv --plots
"""

from __future__ import annotations
import argparse, csv, itertools, sys, math
from pathlib import Path
from datetime import datetime

# Local import – works when you run from the project root
try:
    from simulation import runner
except ImportError:
    sys.stderr.write(
        "[sweep] ERROR: cannot import 'simulation.runner'. "
        "Launch this script from the project root (where simulation/ lives).\n"
    )
    sys.exit(1)

# --------------------------------------------------------------------------- #
# Parameter grid defintion                                                    #
# --------------------------------------------------------------------------- #
TOPOLOGIES        = ["chain", "ring", "star"]
STRATEGIES        = ["purify_then_swap", "swap_then_purify"]
LINK_LENGTHS_KM   = [10, 20, 30, 50]        # km per hop
ROUNDS            = [1, 2, 3]               # purification rounds

# Strategy‑specific, empirically safe filter thresholds
STRAT_FILTERS = {
    "purify_then_swap" : [0.80, 0.90],
    "swap_then_purify" : [0.60, 0.70],
}

# Default physical / protocol constants – tweak if desired
BASE_CFG = dict(
    nodes          = 4,
    protocol       = "dejmps",
    coherence_time = 1.0,     # seconds
    att_len        = 22.0,    # km attenuation length
    seed           = 42,
)

# --------------------------------------------------------------------------- #
def _run_once(cfg: dict, runs: int):
    """Call simulation.runner.run; return dict with 'status'."""
    try:
        summary = runner.run({**cfg, "runs": runs}, collect=True)
        summary["status"] = "ok"
    except RuntimeError as exc:
        summary = {"status": "error", "error": str(exc)}
    return summary


def _adaptive_run(cfg_base: dict, runs: int, thr_init: float) -> tuple[dict, float]:
    """Run with *thr_init*; on 'Exceeded max trials' lower threshold.

    Returns (summary, actual_threshold_used).
    """
    thr = thr_init
    while thr >= 0.50:
        cfg = {**cfg_base, "filter_threshold": thr}
        summary = _run_once(cfg, runs)
        if summary["status"] == "ok":
            return summary, thr
        # If the error is anything other than max‑trials, give up
        if "Exceeded max trials" not in summary.get("error", ""):
            return summary, thr
        thr = round(thr - 0.2, 2)    # relax by 0.05 and retry
    return summary, thr_init   # return last error if all relaxed attempts failed


def _write_csv(rows: list[dict], outfile: Path):
    fieldnames = sorted({k for row in rows for k in row})
    with outfile.open("w", newline="") as fh:
        csv.DictWriter(fh, fieldnames=fieldnames).writeheader()
        for row in rows:
            csv.DictWriter(fh, fieldnames=fieldnames).writerow(row)


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--runs", type=int, default=100,
                    help="Monte‑Carlo repetitions per grid point")
    ap.add_argument("--outfile", type=Path, default=Path("results/sweep.csv"),
                    help="CSV destination")
    ap.add_argument("--plots", action="store_true",
                    help="Generate quick‑look PDF plots via matplotlib/pandas")
    args = ap.parse_args()
    args.outfile.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    total = (len(TOPOLOGIES) * len(STRATEGIES)
             * len(LINK_LENGTHS_KM) * len(ROUNDS))
    counter = 0

    for topo, strat, L, R in itertools.product(
            TOPOLOGIES, STRATEGIES, LINK_LENGTHS_KM, ROUNDS):
        for thr0 in STRAT_FILTERS[strat]:
            counter += 1
            base_cfg = {
                **BASE_CFG,
                "topology": topo,
                "strategy": strat,
                "link_length": float(L),
                "rounds": R,
            }
            summary, thr_used = _adaptive_run(base_cfg, args.runs, thr0)
            summary.update(
                topology        = topo,
                strategy        = strat,
                link_length_km  = L,
                rounds          = R,
                filter_threshold_requested = thr0,
                filter_threshold_used      = thr_used,
            )
            rows.append(summary)

            print(f"[{counter:3d}/{total*len(STRAT_FILTERS[strat]):3d}] "
                  f"{topo:5s} {strat:18s} L={L:2d}km R={R} "
                  f"thr→{thr_used:.2f}  →  {summary['status']}",
                  file=sys.stderr)

    _write_csv(rows, args.outfile)
    print(f"[sweep] Wrote {len(rows)} rows to {args.outfile}", file=sys.stderr)

    if args.plots:
        _make_plots(args.outfile)


# --------------------------------------------------------------------------- #
# --- Optional plotting helper (only when --plots given) -------------------- #
def _make_plots(csv_path: Path):
    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_csv(csv_path)
    ok = df[df.status == "ok"]
    if ok.empty:
        print("[sweep] No successful rows – nothing to plot", file=sys.stderr)
        return

    for topo in ok.topology.unique():
        subt = ok[ok.topology == topo]

        # Fidelity vs rate
        plt.figure()
        for strat, grp in subt.groupby("strategy"):
            plt.scatter(grp.rate_pair_mean, grp.fidelity_mean, label=strat.replace('_',' '))
        plt.xlabel("Delivered pairs per second (rate_pair_mean)")
        plt.ylabel("End‑to‑end fidelity (fidelity_mean)")
        plt.title(f"Fidelity vs Rate – {topo}")
        plt.legend()
        plt.tight_layout()
        pdf1 = csv_path.with_name(f"fidelity_vs_rate_{topo}.pdf")
        plt.savefig(pdf1)
        plt.close()
        print(f"[sweep] saved {pdf1}")

        # Rate CDF
        plt.figure()
        for strat, grp in subt.groupby("strategy"):
            x = grp.rate_pair_mean.sort_values()
            y = (x.rank(method='max') - 1) / (len(x) - 1)
            plt.step(x, y, where='post', label=strat.replace('_',' '))
        plt.xlabel("Delivered pairs per second")
        plt.ylabel("CDF")
        plt.title(f"Rate CDF – {topo}")
        plt.legend()
        plt.tight_layout()
        pdf2 = csv_path.with_name(f"rate_cdf_{topo}.pdf")
        plt.savefig(pdf2)
        plt.close()
        print(f"[sweep] saved {pdf2}")


if __name__ == "__main__":     # pragma: no cover
    main()
