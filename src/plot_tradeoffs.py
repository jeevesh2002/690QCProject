
#!/usr/bin/env python3
"""plot_tradeoffs.py – analysis & visuals for threshold_scan.csv

The script expects the CSV produced by adaptive_threshold.py
and generates three sets of publication‑ready PDF figures:

1. Threshold frontier:
     thr_max vs rounds  (one figure per topology × strategy;
     curves coloured by link length)

2. Performance lines:
      fidelity_mean vs rounds
      rate_pair_mean vs rounds
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
    """Saves a matplotlib figure to the specified path with tight layout and prints a confirmation.

    This function applies a tight layout to the figure, saves it as a PDF with bounding box, and prints the output path.

    Args:
        fig: The matplotlib figure to save.
        path: The file path where the figure will be saved.
    """
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    print("[plot]", path)

def plot_thr_frontier(df: pd.DataFrame, outdir: Path):
    """Plots the threshold frontier for each topology and strategy and saves the figures.

    This function generates and saves figures showing the maximum working threshold versus purification rounds for each combination of topology and strategy.

    Args:
        df: The pandas DataFrame containing the results data.
        outdir: The directory where the PDF figures will be saved.
    """
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
    """Plots a specified metric versus purification rounds for each topology and strategy and saves the figures.

    This function generates and saves figures showing the given metric as a function of purification rounds for each combination of topology and strategy.

    Args:
        df: The pandas DataFrame containing the results data.
        metric: The column name of the metric to plot.
        ylabel: The label for the y-axis.
        outdir: The directory where the PDF figures will be saved.
    """
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
    """Plots a Pareto scatter of fidelity versus rate for each strategy and saves the figure.

    This function generates and saves a scatter plot showing the trade-off between delivered pairs per second and fidelity, with markers and colors encoding strategy and rounds.

    Args:
        df: The pandas DataFrame containing the results data.
        outdir: The directory where the PDF figure will be saved.
    """
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
    """Main entry point for the tradeoff plotting script.

    This function parses command-line arguments, loads the results CSV, and generates all relevant plots in the specified output directory.
    """
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
