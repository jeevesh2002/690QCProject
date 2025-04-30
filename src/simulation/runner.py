"""Orchestrates multiple Monte‑Carlo runs and logs output."""
import json, time, statistics, random
from pathlib import Path
import simpy
from simulation.topology import build
from simulation.repeater_chain import generate_end_to_end

def run(params: dict) -> None:
    """Run many independent repetitions and write a JSON result file."""
    random.seed(params["seed"])
    aggregates, per_run = [], []

    for _ in range(params["runs"]):
        env = simpy.Environment()

        # Build topology and decide the path you care about
        nodes, links = build(env,
                             params["topology"],
                             params["nodes"],
                             params["link_length"])
        if params["topology"] == "star":
            # end-to-end path = leaf-0 → hub → leaf-1
            hub = nodes[0]
            leaf0, leaf1 = nodes[1], nodes[-1]
            path_links = [l for l in links if {l.a, l.b} in [{hub, leaf0}, {hub, leaf1}]]
        else:                       # linear or ring: source = A, sink = last node
            path_links = links

        # --- Launch the repeater-chain coroutine --------------------------
        proc = env.process(
            generate_end_to_end(env,
                                path_links,
                                params["strategy"],
                                params["protocol"],
                                params["rounds"],
                                params["filter_threshold"])
        )

        # Run the simulation *until* that process finishes
        env.run(until=proc)                 # public API – stops when `proc` done
        end_time, F_final, raw_pairs = proc.value   # retrieve return tuple

        per_run.append(
            {"latency_s": end_time,
             "fidelity": F_final,
             "raw_pairs": raw_pairs}
        )

    # ------------- Aggregate statistics -----------------
    latency_mean = statistics.mean(r["latency_s"] for r in per_run)
    fidelity_mean = statistics.mean(r["fidelity"] for r in per_run)
    rate_hz = 1.0 / latency_mean

    summary = {
        "mean_latency_s": latency_mean,
        "mean_fidelity": fidelity_mean,
        "generation_rate_hz": rate_hz,
        "mean_raw_pairs": statistics.mean(r["raw_pairs"] for r in per_run)
    }
    aggregates.append(summary)

    out = {"params": params, "aggregates": summary, "per_run": per_run}
    Path("results").mkdir(exist_ok=True, parents=True)
    with open(Path("results") / f"result_{int(time.time())}.json", "w") as f:
        json.dump(out, f, indent=2)

    print(json.dumps(summary, indent=2))