import json
import statistics

d = json.load(open('artifacts/phase5_validation_campaign_results.json', encoding='utf-8'))

runtimes_all = []
runtimes_succ = []
runtimes_fail = []

def collect(res):
    t = res.get('runtime_s', 0.0)
    runtimes_all.append(t)
    if res.get('success'):
        runtimes_succ.append(t)
    else:
        runtimes_fail.append(t)

for cat, cases in d.items():
    if cat == 'mission_payload_matrix':
        for m, p_dict in cases.items():
            for p, res in p_dict.items():
                collect(res)
    else:
        for k, res in cases.items():
            collect(res)

print("=== RUNTIME PERFORMANCE BENCHMARKS (111 RUNS) ===")
print(f"All runs (111): Mean={statistics.mean(runtimes_all):.2f}s, Median={statistics.median(runtimes_all):.2f}s, Min={min(runtimes_all):.2f}s, Max={max(runtimes_all):.2f}s")
print(f"Successful runs (90): Mean={statistics.mean(runtimes_succ):.2f}s, Median={statistics.median(runtimes_succ):.2f}s, Min={min(runtimes_succ):.2f}s, Max={max(runtimes_succ):.2f}s")
print(f"Failed/Rejected runs (21): Mean={statistics.mean(runtimes_fail):.2f}s, Median={statistics.median(runtimes_fail):.2f}s, Min={min(runtimes_fail):.2f}s, Max={max(runtimes_fail):.2f}s")

sorted_succ = sorted(runtimes_succ)
p90 = sorted_succ[int(len(sorted_succ)*0.90)]
p95 = sorted_succ[int(len(sorted_succ)*0.95)]
print(f"Successful P90: {p90:.2f}s, P95: {p95:.2f}s")
