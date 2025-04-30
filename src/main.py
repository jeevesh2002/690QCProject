"""CLI entry‑point."""
import argparse, json
from simulation.runner import run

ap = argparse.ArgumentParser()
ap.add_argument('--topology', required=True, choices=['chain', 'ring', 'star'])
ap.add_argument('--nodes', type=int, default=4)
ap.add_argument('--link-length', type=float, default=25)
ap.add_argument('--strategy', choices=['purify_then_swap', 'swap_then_purify'], default='purify_then_swap')
ap.add_argument('--protocol', choices=['dejmps', 'bbpssw'], default='dejmps')
ap.add_argument('--rounds', type=int, default=2)
ap.add_argument('--filter-threshold', type=float, default=0.9)
ap.add_argument('--coherence-time', type=float)
ap.add_argument('--att-len', type=float)
ap.add_argument('--runs', type=int, default=100)
ap.add_argument('--seed', type=int, default=0)

if __name__ == '__main__':
    run(vars(ap.parse_args()))
