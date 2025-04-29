## **Project Overview**

- **Topic:** Tradeoffs in Fidelity and Entanglement Generation Rate in Small Quantum Networks
- This project investigates how different entanglement distribution strategies-such as purification, filtering, and single-click schemes-perform in small quantum networks.
- We explore tradeoffs between fidelity and entanglement generation rate under realistic constraints including memory decoherence.
- The simulation is developed in Python with custom-built modules and tested across varying topologies and noise regimes.

---

## **Network Architecture and Strategies**

- We focus on second-generation quantum repeater networks because they support entanglement purification and memory-aware coordination without the complexity of full quantum error correction.
- Three network topologies are analyzed: 
  - A linear chain (e.g., A-B-C-D)
  - A triangular ring (A-B-C-A)
  - A star configuration
- Strategies include heralded single-click entanglement generation, fidelity-based filtering, and purification using protocols like DEJMPS or BBPSSW.
- Both purify-then-swap and swap-then-purify orders are implemented and compared.

---

## **Model and Simulation Assumptions**

- Entanglement generation over each link is modeled as a Bernoulli process with success probability dependent on the distance (Link Length).
- Classical communication is assumed free and instantaneous, enabling full synchronization across nodes.
- Quantum gates and measurements are treated as ideal, where each node has a dedicated communication qubit per link interface for parallel link generation.
- Memory decoherence is modeled with exponential decay:  
  \( F(t) = F_0 e^{-t/T_{\text{coh}}} \),  
  where \( T_{\text{coh}} \) is the coherence time.

---

## **Implementation Approach**

- We will be using Python and libraries like SimPy, NumPy, NetSquid, etc., for the simulation.
- Core components will include:  
  `Node`, `Link`, `MemoryRegister`, `EntanglementSwapper`, and `PurificationModule`, designed for modular testing and reuse.
- Logging will be performed in CSV or JSON format, and all experiments are reproducible via analysis notebooks.

---

## **Evaluation Metrics and Experiments**

- Metrics include:
  - Final entanglement fidelity
  - Generation rate (pairs per unit time)
  - Latency (time to usable end-to-end pair)
  - Resource cost (raw pairs consumed)
- We vary initial link success probabilities, memory coherence times, purification rounds, and network topology.
- Plots include fidelity vs. rate curves, topology comparisons, and heatmaps of performance across parameter regimes.
- We expect purify-then-swap to outperform swap-then-purify in low-fidelity or high-loss regimes, and we aim to quantify when filtering becomes efficient.

---

## **Goals and Insights**

- Our goal is to understand which strategies optimize fidelity or rate under various noise models, memory limits, and topologies.
- Insights will include when fidelity improvements justify the cost of purification and how memory coherence constraints alter protocol performance.

---

## **Risks and Mitigation Strategies**

- Increasing the network complexity may slow debugging; we mitigate this by limiting topologies to five nodes and testing modules incrementally.
- The memory models may oversimplify physical processes, so exponential decay is used as a baseline, with sensitivity analysis planned.
- Visualization complexity is reduced by using standardized templates and automatic plotting scripts.
