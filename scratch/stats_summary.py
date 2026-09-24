import json

d = json.load(open('artifacts/phase5_validation_campaign_results.json', encoding='utf-8'))

print("=== STATS SUMMARY ===")
total_cases = 0
total_success = 0
total_rejected = 0

for cat, cases in d.items():
    if isinstance(cases, dict):
        cat_cases = 0
        cat_succ = 0
        if cat == 'mission_payload_matrix':
            for m, p_dict in cases.items():
                for p, res in p_dict.items():
                    cat_cases += 1
                    if res.get('success'): cat_succ += 1
        else:
            for k, res in cases.items():
                cat_cases += 1
                if res.get('success'): cat_succ += 1
        total_cases += cat_cases
        total_success += cat_succ
        print(f"{cat:<30}: {cat_cases:>3} cases | {cat_succ:>3} passed | {cat_cases - cat_succ:>3} rejected/failed")

print(f"\nTotal runs: {total_cases} | Total passed: {total_success} | Total rejected/failed: {total_cases - total_success}")

# Check Mass Conservation across all successful runs
max_mass_err = 0.0
for cat, cases in d.items():
    if cat == 'mission_payload_matrix':
        for m, p_dict in cases.items():
            for p, res in p_dict.items():
                if res.get('success'):
                    err = abs(res.get('mass_error_pct', 0.0))
                    if err > max_mass_err: max_mass_err = err
    else:
        for k, res in cases.items():
            if res.get('success'):
                err = abs(res.get('mass_error_pct', 0.0))
                if err > max_mass_err: max_mass_err = err

print(f"Max component mass conservation error across all successful runs: {max_mass_err:.6f}%")
