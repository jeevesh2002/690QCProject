
#!/usr/bin/env python3
"""adaptive_threshold.py – determine maximal viable filter threshold.

Steps:
  • Start at 0.70, add 0.05 until the run trips 'Exceeded max trials'.
  • Step back, then lower in 0.002 decrements until run succeeds again.
  • Save that threshold and performance metrics.

Writes CSV rows for each (topology, strategy, link length, rounds).
"""

import argparse, csv, itertools, sys
from pathlib import Path

try:
    from simulation import runner
except ImportError:
    sys.stderr.write("Run from project root so 'simulation' is importable\n")
    sys.exit(1)

BASE = dict(nodes=4, protocol="dejmps", coherence_time=1.0, att_len=22.0, seed=42)
TOPO = ["chain", "ring", "star"]
STRAT = ["purify_then_swap", "swap_then_purify"]
LKM = [10, 20, 30, 50]
ROUNDS = range(3, 15, 3)

def sim(cfg, runs):
    try:
        s = runner.run({**cfg, "runs": runs}, collect=True)
        s["status"] = "ok"
    except RuntimeError as e:
        s = {"status": "error", "error": str(e)}
    return s

def find_threshold(base_cfg, runs):
    thr = 0.70
    step = 0.0002
    # upward sweep
    while True:
        result = sim({**base_cfg, "filter_threshold": thr}, runs)
        if result["status"] != "ok":
            thr = round(thr - step, 5)   # last working
            break
        thr += step
        thr = round(thr, 5)
    # fine‑grained descent
    thr_fine = thr
    while True:
        test = sim({**base_cfg, "filter_threshold": thr_fine + 0.0002}, runs)
        if test["status"] == "ok":
            thr_fine += 0.00001
            thr_fine = round(thr_fine, 5)
        else:
            break
    final = sim({**base_cfg, "filter_threshold": thr_fine}, runs)
    return thr_fine, final

def write_csv(rows, out):
    if not rows: return
    keys = sorted({k for r in rows for k in r})
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def main():
    pa = argparse.ArgumentParser()
    pa.add_argument("--runs", type=int, default=50)
    pa.add_argument("--outfile", type=Path, default=Path("results/threshold_scan.csv"))
    args = pa.parse_args()
    args.outfile.parent.mkdir(exist_ok=True, parents=True)
    rows = []
    total = len(TOPO)*len(STRAT)*len(LKM)*len(ROUNDS)
    i = 0
    for t, s, L, R in itertools.product(TOPO, STRAT, LKM, ROUNDS):
        i += 1
        base = {**BASE, "topology": t, "strategy": s, "link_length": float(L), "rounds": R}
        thr_max, res = find_threshold(base, args.runs)
        res.update(topology=t, strategy=s, link_length_km=L, rounds=R, thr_max=thr_max)
        rows.append(res)
        print(f"[{i}/{total}] {t:5s} {s:18s} L={L} R={R} thr_max={thr_max:.3f} status={res['status']}", file=sys.stderr)
    write_csv(rows, args.outfile)
    print("Saved", args.outfile)

if __name__ == "__main__":
    main()