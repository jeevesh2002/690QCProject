
#!/usr/bin/env python3
"""plot_tradeoffs.py – analysis & visuals for threshold_scan.csv

The script expects the CSV produced by adaptive_threshold.py
and generates three sets of publication‑ready PDF figures:

1. Threshold frontier:
     thr_max vs rounds  (one figure per topology × strategy;
     curves coloured by link length)

2. Performance lines:
     • fidelity_mean vs rounds
     • rate_pair_mean vs rounds
   (again per topology × strategy, coloured by link length)

3. Pareto scatter:
     fidelity_mean vs rate_pair_mean, markers encode rounds, colour strategy.

Usage
-----
    python scripts/plot_tradeoffs.py results/threshold_scan.csv
"""

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Consistent style
plt.rcParams.update({
    "figure.dpi": 150,
    "font.size": 9,
})

def save(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    print("[plot]", path)

def plot_thr_frontier(df: pd.DataFrame, outdir: Path):
    for topo in df.topology.unique():
        for strat in df.strategy.unique():
            sub = df[(df.topology == topo) & (df.strategy == strat)]
            if sub.empty:
                continue
            fig, ax = plt.subplots()
            for L, grp in sub.groupby("link_length_km"):
                grp_sorted = grp.sort_values("rounds")
                ax.plot(grp_sorted["rounds"], grp_sorted["thr_max"],
                        marker="o", label=f"{L} km")
            ax.set_xlabel("Purification rounds R")
            ax.set_ylabel("Max working threshold")
            ax.set_title(f"{topo} – {strat.replace('_', ' ')}")
            ax.legend(title="Link length")
            save(fig, outdir / f"{topo}_{strat}_thr_front.pdf")
            plt.close(fig)

def plot_metric_vs_rounds(df: pd.DataFrame, metric: str, ylabel: str, outdir: Path):
    for topo in df.topology.unique():
        for strat in df.strategy.unique():
            sub = df[(df.topology == topo) & (df.strategy == strat)]
            if sub.empty:
                continue
            fig, ax = plt.subplots()
            for L, grp in sub.groupby("link_length_km"):
                grp_sorted = grp.sort_values("rounds")
                ax.plot(grp_sorted["rounds"], grp_sorted[metric],
                        marker="o", label=f"{L} km")
            ax.set_xlabel("Purification rounds R")
            ax.set_ylabel(ylabel)
            ax.set_title(f"{topo} – {strat.replace('_', ' ')}")
            ax.legend(title="Link length")
            save(fig, outdir / f"{topo}_{strat}_{metric}.pdf")
            plt.close(fig)

def plot_pareto(df: pd.DataFrame, outdir: Path):
    import matplotlib.cm as cm
    strategies = df.strategy.unique()
    colors = cm.get_cmap("tab10", len(strategies))
    fig, ax = plt.subplots()
    for idx, strat in enumerate(strategies):
        sub = df[df.strategy == strat]
        sc = ax.scatter(sub["rate_pair_mean"], sub["fidelity_mean"],
                        c=[colors(idx)]*len(sub),
                        label=strat.replace('_', ' '),
                        alpha=0.6, edgecolor="k", s=30)
    ax.set_xlabel("Delivered pairs per second")
    ax.set_ylabel("Fidelity")
    ax.set_title("Fidelity vs Rate – Pareto space")
    ax.legend()
    save(fig, outdir / "pareto_fid_vs_rate.pdf")
    plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path, help="threshold_scan.csv")
    ap.add_argument("-o", "--outdir", type=Path, default=None,
                    help="directory for PDFs (default: alongside CSV)")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    df = df[df.status == "ok"].copy()
    if df.empty:
        print("No successful rows; nothing to plot"); return

    outdir = args.outdir or args.csv.parent
    outdir.mkdir(parents=True, exist_ok=True)

    plot_thr_frontier(df, outdir)
    plot_metric_vs_rounds(df, metric="fidelity_mean", ylabel="Fidelity", outdir=outdir)
    plot_metric_vs_rounds(df, metric="rate_pair_mean", ylabel="Pairs / second", outdir=outdir)
    plot_pareto(df, outdir)

if __name__ == "__main__":
    main()
