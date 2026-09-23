import json

d = json.load(open('artifacts/phase5_validation_campaign_results.json', encoding='utf-8'))

print("=== STEP 9 DATA: SURVEY PAYLOAD SWEEP (0.2 - 2.0 kg) ===")
survey_payloads = d['mission_payload_matrix']['SURVEY']
for p, res in survey_payloads.items():
    print(f"Payload: {p:>4} kg | MTOW: {res['mtow_kg']:>6.3f} kg | Span: {res['span_m']:>5.3f}m | Area: {res['area_m2']:>5.3f}m2 | L/D: {res['lift_to_drag']:>4.1f} | Pwr: {res['cruise_power_w']:>5.1f}W | T/W: {res['tw_ratio']:>4.2f} | SM: {res['static_margin_pct']:>4.1f}%")

print("\n=== STEP 15 DATA: BASELINE QUALITY METRICS (7 CANONICAL CASES) ===")
reg = d['regression_baseline']
for cid, res in reg.items():
    mtow = res['mtow_kg']
    # If payload is in name
    p_wt = 0.5
    if "1.0kg" in cid: p_wt = 1.0
    elif "2.0kg" in cid: p_wt = 2.0
    elif "1.5kg" in cid: p_wt = 1.5
    
    pay_frac = p_wt / mtow if mtow > 0 else 0
    print(f"{cid:<20} | MTOW: {mtow:>6.3f} kg | PayFrac: {pay_frac*100:>4.1f}% | Span: {res['span_m']:>5.3f}m | AR: {res['aspect_ratio']:>4.1f} | L/D: {res['lift_to_drag']:>4.1f} | Pwr: {res['cruise_power_w']:>5.1f}W | Endur: {res['endurance_min']:>5.1f}m | SM: {res['static_margin_pct']:>4.1f}%")
