# Quantum Final Project  
**Avni Gunjikar and Jeevesh Krishna Arigala**

---

## Project Overview  
**Topic:** Trade‑offs in Fidelity and Entanglement Generation Rate in Small Quantum Networks  
This project investigates how different entanglement‑distribution strategies—such as purification, filtering, and single‑click schemes—perform in small quantum repeater networks. We quantify the trade‑off between end‑to‑end fidelity and entanglement generation rate under realistic constraints, including memory decoherence.  

The simulation is written in Python with custom‑built modules and tested across multiple topologies and noise regimes.

---

## Network Architecture & Strategies  
We focus on **first‑generation quantum repeaters**, which support two‑way purification and heralded entanglement without the overhead of full error correction.  

**Topologies analyzed:**  
- **Linear chain** (A–B–C–D)  
- **Triangular ring** (A–B–C–A)  
- **Star** (hub B with leaves A, C, D)  

**Entanglement strategies:**  
- **Heralded single‑click generation**  
- **Fidelity‑based filtering**  
- **Purification (DEJMPS only)**  
- Two protocol orders: **purify‑then‑swap** and **swap‑then‑purify**

---

## Model & Simulation Assumptions  

1. **Entanglement generation**  
   - Modeled as independent Bernoulli trials:  
     \[
       p_{\rm succ}(L)
       = \eta_{\rm det}\, e^{-L/L_{\rm att}},
     \]  
     with \(\eta_{\rm det}\) the detector efficiency and  
     \(L_{\rm att}=1/\alpha\) the fibre‑attenuation length.  
   - **No multi‑photon or dark‑count errors** are modeled.

2. **Initial raw states**  
   - Werner states  
     \[
       \rho_{\rm raw} 
       = F_0\,|\Phi^+\rangle\langle\Phi^+|
       + (1-F_0)\,\frac{I - |\Phi^+\rangle\langle\Phi^+|}{3}.
     \]

3. **Memory decoherence**  
   - Each qubit stamps its write time \(t_{\rm write}\).  
   - At current time \(t\), fidelity decays as  
     \[
       F(t) = F_0 \exp\!\bigl[-(t - t_{\rm write})/T_{\rm coh}\bigr],
     \]  
     where \(T_{\rm coh}\) is the coherence time parameter.  

4. **Local operations & classical communication**  
   - **All quantum gates, measurements, and Pauli corrections are ideal and instantaneous.**  
   - **Classical messaging is error‑free and instantaneous.**  
   - **Node clock synchronization** is perfect; there is no timing jitter.

5. **Resource constraints**  
   - Each node has one **communication qubit per link** and two **memory registers** (where applicable).  
   - **No limit** on classical bandwidth or memory‑buffer size beyond those registers.

6. **Protocol‑specific**  
   - **Only the DEJMPS purification protocol** is implemented.  
   - **Filtering** applies a fixed cutoff \(F_{\rm th}\) on incoming link fidelity—and discards any pair below that threshold.

7. **State abstraction**  
   - We track only the **scalar fidelity** and **write‑time stamp** for each qubit pair—no full density‑matrix propagation.

---

## Implementation Approach  
- **Language & frameworks:** Python, SimPy, NumPy (and optionally NetSquid for advanced QC primitives).  
- **Core modules:**  
  - `Node`, `Link`, `MemoryRegister`  
  - `EntanglementSwapper`, `PurificationModule`  
- **Reproducibility:**  
  - Configurable via JSON/CSV logs  
  - Analysis notebooks for post‑processing and plotting  

---

## Evaluation Metrics & Experiments  

- **Metrics:**  
  - **End‑to‑end fidelity** \(F_{\rm end}\)  
  - **Generation rate** \(R_{\rm pair} = 1/T\) (pairs per unit time)  
  - **Latency** \(T\) (time until first usable pair)  
  - **Resource cost** (raw pairs consumed \(N_{\rm raw}\))  

- **Experimental variables:**  
  - Link length \(L\)  
  - Coherence time \(T_{\rm coh}\)  
  - Purification rounds \(R\)  
  - Network topology  
  - Protocol order (PTS vs STP)  

- **Visualization:**  
  - Fidelity vs. rate scatterplots  
  - Topology‑comparison curves  
  - Heatmaps over \((L,R)\) parameter space  

---

## Goals & Insights  
- **Primary Goal:** Systematically explore the **trade‑off** between end‑to‑end fidelity and entanglement generation rate by sweeping key parameters—link length \(L\), memory coherence time \(T_{\rm coh}\), purification rounds \(R\), topology, and protocol order (PTS vs STP).  

- **Insights to Uncover:**  
  1. **Pareto Frontiers:** Chart fidelity vs. rate curves for each protocol and topology, and identify the regions where one strategy strictly dominates another.  
  2. **Regime Mapping:** Determine which strategies (purification depth, filtering threshold, or single‑click) are optimal in different parameter regimes (e.g., low‑\(T_{\rm coh}\)/long \(L\) vs. high‑\(T_{\rm coh}\)/short \(L\)).  
  3. **Diminishing Returns:** Pinpoint thresholds in purification rounds \(R\) and coherence time \(T_{\rm coh}\) beyond which additional effort yields minimal fidelity gain.  
  4. **Topology Comparison:** Reveal how network layout (chain, ring, star) shifts the trade‑off landscape and under what conditions each topology is preferable.  
  5. **Protocol Ordering:** Quantify when purify‑then‑swap outperforms swap‑then‑purify (and vice versa), across the full sweep of parameters.  
---

## Risks & Mitigation  
- **Complexity blow‑up**  
  - _Risk:_ Large topologies make debugging hard.  
  - _Mitigation:_ Limit to ≤ 5 nodes, test modules incrementally.  

- **Over‑simplified memory model**  
  - _Risk:_ Exponential decay may miss physics.  
  - _Mitigation:_ Conduct sensitivity analysis on \(T_{\rm coh}\).  

- **Visualization overload**  
  - _Risk:_ Too many plots impede clarity.  
  - _Mitigation:_ Use standard templates & automated plotting scripts.



## Reproducing the Code & Figures

Follow these four steps to rebuild every experiment and plot that appears in the paper.

---

### 1. Set-up (Python ≥ 3.10)

```bash
# Clone or unzip the project, then from the project root:
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:$(pwd)/src   # lets Python find `simulation/`
````

---

### 2. Command-Line Interface

`src/qnet_cli.py` is the main entry-point.  It accepts the flags below.

| Short | Long option          | Type / unit |       Default      | Description                                   |
| :---: | -------------------- | ----------- | :----------------: | --------------------------------------------- |
|  `-t` | `--topology`         | str         |         — ‡        | Network shape: `chain`, `ring`, `star`.       |
|  `-n` | `--nodes`            | int         |        **4**       | Total nodes in the graph.                     |
|  `-L` | `--link-length`      | float (km)  |       **25**       | Fibre length per hop.                         |
|  `-s` | `--strategy`         | str         | `purify_then_swap` | `purify_then_swap` or `swap_then_purify`.     |
|  `-p` | `--protocol`         | str         |      `dejmps`      | Purification protocol (`dejmps`, `bbpssw`).   |
|  `-r` | `--rounds`           | int         |        **2**       | DEJMPS/BBPSSW purification rounds.            |
|  `-f` | `--filter-threshold` | float       |       **0.9**      | Post-selection cut-off; use `0.0` to disable. |
|  `-c` | `--coherence-time`   | float (s)   |       **1.0**      | Memory coherence time $T_{\text{coh}}$.       |
|  `-a` | `--att-len`          | float (km)  |       **22**       | Fibre attenuation length $L_{\text{att}}$.    |
|   —   | `--runs`             | int         |       **100**      | Monte-Carlo repetitions.                      |
|   —   | `--seed`             | int/None    |       `None`       | PRNG seed (deterministic if set).             |
|  `-o` | `--output`           | path        |          —         | Save run summary as JSON (stdout if omitted). |

‡ *Required flag*

> **Note** Initial raw-pair fidelity $F_0$ is **not** CLI-configurable; edit
> `configs/physics.py::PhysicsConfig.F0_LINK` if you need a different baseline.

#### Example

```bash
# single 4-node chain, 25 km hops, 2 purification rounds
python src/qnet_cli.py \
    --topology chain \
    --link-length 25 \
    --strategy purify_then_swap \
    --rounds 2 \
    --runs 10 \
    -o results/quick_chain.json

cat results/quick_chain.json   # shows latency, fidelity, rates, etc.
```

---

### 3. Parameter Sweeps

The paper’s data is harvested via two drivers:

| Script                | What it does                                                                                                                                  | Typical invocation                                          |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **`src/sweep.py`**    | Scans link-length × rounds × topology × strategy, adapting the filter threshold to the highest viable value for each setting; writes one CSV. | `python src/sweep.py --runs 50 --outfile results/sweep.csv` |
| **`src/qnet_cli.py`** | Used inside shell loops when you want every trial’s raw JSON.                                                                                 | see example above   |

Both expect to run from the **project root**, so `simulation/…` is on `PYTHONPATH`.

---

### 4. Plotting

A notebook and a one-liner script reproduce all figures:

```bash
python plot_tradeoffs.py \
       --csv results/sweep.csv \
       --outdir figs/
```

The PDFs/PNGs will appear in `figs/`.

---

With **install → one-shot run → sweep → plot** complete, you should obtain identical latency, fidelity and rate numbers (and plots) to those in the report.