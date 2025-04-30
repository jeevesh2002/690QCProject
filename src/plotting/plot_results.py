import json
import glob
import matplotlib.pyplot as plt

files = glob.glob('results/result_*.json')
if not files:
    raise SystemExit('Run some experiments first.')
latencies = []
fidelities = []
for f in files:
    with open(f) as fh:
        data = json.load(fh)
        latencies.append(data['aggregates']['mean_latency_s'])
        fidelities.append(data['aggregates']['mean_fidelity'])

plt.scatter([1/x for x in latencies], fidelities)
plt.xlabel('Generation Rate (Hz)')
plt.ylabel('Average Fidelity')
plt.title('Rate–Fidelity Trade‑off')
plt.grid()
plt.savefig('results/rate_fidelity_rate.png')
# plt.show()
