import json

d = json.load(open('artifacts/phase5_validation_campaign_results.json', encoding='utf-8'))

print('=== ENVIRONMENT MATRIX ===')
for k, v in d['environment_matrix'].items():
    print(f"{k:<12} | Succ: {v['success']} | Status: {v['status']:<15} | MTOW: {v.get('mtow_kg')} kg | Iter: {v.get('iterations')} | Span: {v.get('span_m')}m | L/D: {v.get('lift_to_drag')}")

print('\n=== MTOW BOUNDARY MATRIX ===')
for k, v in d['mtow_boundary_matrix'].items():
    print(f"{k:<30} | Succ: {v['success']} | Status: {v['status']:<25} | MTOW: {v.get('mtow_kg')} kg | Iter: {v.get('iterations')}")

print('\n=== PAYLOAD BOUNDARY MATRIX (DELIVERY) ===')
for k, v in d['payload_boundary_matrix'].items():
    print(f"{k:>5} kg | Succ: {v['success']} | Status: {v['status']:<22} | MTOW: {v.get('mtow_kg')} kg | Iter: {v.get('iterations')} | Runtime: {v.get('runtime_s')}s")

print('\n=== CONVERGENCE STRESS ===')
for k, v in d['convergence_stress'].items():
    print(f"{k:<30} | Succ: {v['success']} | Status: {v['status']:<28} | MTOW: {v.get('mtow_kg')} kg | Iter: {v.get('iterations')}")

print('\n=== FAILURE MODES ===')
for k, v in d['failure_modes'].items():
    print(f"{k:<30} | Succ: {v['success']} | Status: {v['status']:<25} | Errors: {v.get('errors')}")
