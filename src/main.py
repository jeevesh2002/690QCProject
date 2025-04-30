"""CLI wrapper around the Monte‑Carlo runner."""
import argparse, time
from simulation.runner import run

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--topology', choices=['linear','ring','star'], default='linear')
    ap.add_argument('--nodes', type=int, default=4)
    ap.add_argument('--link-length', type=float, default=10, help='km')
    ap.add_argument('--strategy', choices=['purify_then_swap','swap_then_purify'], default='purify_then_swap')
    ap.add_argument('--protocol', choices=['dejmps','bbpssw'], default='dejmps')
    ap.add_argument('--rounds', type=int, default=2)
    ap.add_argument('--filter-threshold', type=float, default=0.9)
    ap.add_argument('--runs', type=int, default=100)
    ap.add_argument('--seed', type=int, default=int(time.time()))
    args = ap.parse_args()
    run(vars(args))
