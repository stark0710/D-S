import csv
import os

def generate_before_after():
    before_file = "reports/fixed_wing_phase5_before_outputs.csv"
    after_file = "reports/fixed_wing_phase5b_after_outputs.csv"
    comparison_file = "reports/fixed_wing_phase5b_before_after.csv"

    if not os.path.exists(before_file):
        print(f"Error: {before_file} not found.")
        return
    if not os.path.exists(after_file):
        print(f"Error: {after_file} not found.")
        return

    # Read before outputs
    before_data = {}
    with open(before_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            before_data[row["case_id"]] = row

    # Read after outputs
    after_data = {}
    with open(after_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            after_data[row["case_id"]] = row

    headers = [
        "case_id",
        "before_status",
        "after_status",
        "before_mtow_kg",
        "after_mtow_kg",
        "before_wingspan_m",
        "after_wingspan_m",
        "before_ar",
        "after_ar",
        "before_airfoil",
        "after_airfoil",
        "before_telemetry",
        "after_telemetry",
        "before_static_margin_percent",
        "after_static_margin_percent",
        "before_review_priority",
        "after_review_priority",
        "change_reason"
    ]

    rows = []
    for case_id in sorted(before_data.keys()):
        b = before_data[case_id]
        a = after_data.get(case_id, {})

        if not a:
            continue

        reasons = []

        # Compare status
        b_status = b.get("pipeline_status", "UNKNOWN")
        a_status = a.get("pipeline_status", "UNKNOWN")

        b_verif = b.get("verification_status", "UNKNOWN")
        a_verif = a.get("verification_status", "UNKNOWN")

        # Status text mapping differences
        if b_status != a_status:
            if b_status == "INTERNAL_EXCEPTION" and a_status != "INTERNAL_EXCEPTION":
                reasons.append(f"Internal crash resolved: mapped to sizing failure category '{a_status}'")
            elif b_status == "NON_CONVERGED" and a_status == "CONVERGENCE_FAILURE":
                reasons.append("Convergence failure status text standardized")
            elif a_status == "COMPONENT_DATABASE_LIMITATION":
                reasons.append("Telemetry/payload database limitation error handled cleanly")
            elif a_status == "COMMUNICATION_INFEASIBLE":
                reasons.append("Telemetry link infeasibility caught cleanly")
            else:
                reasons.append(f"Status changed from {b_status} to {a_status}")

        if b_verif != a_verif:
            reasons.append(f"Verification status changed from {b_verif} to {a_verif} due to strict aggregate rule checks")

        # Aspect ratio / Airfoil
        b_ar = b.get("aspect_ratio", "")
        a_ar = a.get("aspect_ratio", "")
        b_airfoil = b.get("selected_airfoil", "")
        a_airfoil = a.get("selected_airfoil", "")

        if b_ar != a_ar or b_airfoil != a_airfoil:
            if a_ar and b_ar and float(a_ar) != float(b_ar):
                reasons.append(f"AR adjusted from {b_ar} to {a_ar} due to structural thickness limits")
            if a_airfoil != b_airfoil:
                reasons.append(f"Airfoil fallback applied: '{b_airfoil}' -> '{a_airfoil}'")

        # Telemetry
        b_tel = b.get("telemetry", "")
        a_tel = a.get("telemetry", "")
        if b_tel != a_tel:
            reasons.append(f"Telemetry reselected from '{b_tel}' to '{a_tel}' due to link checks")

        # MTOW / Margins / Priorities
        b_mtow = b.get("final_mtow_kg", "")
        a_mtow = a.get("final_mtow_kg", "")
        if b_mtow != a_mtow:
            try:
                diff = float(a_mtow) - float(b_mtow)
                if abs(diff) > 0.05:
                    reasons.append(f"MTOW changed by {diff:+.3f} kg due to corrected battery continuous sizing or payload propagation")
            except ValueError:
                pass

        b_priority = b.get("manual_review_priority", "")
        a_priority = a.get("manual_review_priority", "")
        if b_priority != a_priority:
            reasons.append(f"Review priority changed: {b_priority} -> {a_priority} (hardened classification)")

        if not reasons:
            reasons.append("No changes. Sizing results identical.")

        rows.append([
            case_id,
            b_status,
            a_status,
            b_mtow,
            a_mtow,
            b.get("wingspan_m", ""),
            a.get("wingspan_m", ""),
            b_ar,
            a_ar,
            b_airfoil,
            a_airfoil,
            b_tel,
            a_tel,
            b.get("static_margin_percent", ""),
            a.get("static_margin_percent", ""),
            b_priority,
            a_priority,
            "; ".join(reasons)
        ])

    with open(comparison_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Before/after comparison CSV successfully written to {comparison_file}")

if __name__ == "__main__":
    generate_before_after()
