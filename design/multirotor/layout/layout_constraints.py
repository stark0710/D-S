import math
from backend.design.multirotor.layout.layout_models import LayoutCandidate, LayoutContext

class LayoutConstraintsEvaluator:
    """
    Enforces spatial collision-free, clearance, magnetic isolation, and GPS sky visibility constraint rules.
    """
    @staticmethod
    def evaluate_constraints(candidate: LayoutCandidate, context: LayoutContext) -> bool:
        """
        Runs safety checks. Updates constraint results.
        """
        candidate.constraint_results = {}
        
        # 1. 3D Spatial Collision overlap check
        collision_detected = False
        colliding_pair = ""
        keys = list(candidate.boxes.keys())
        
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                k1, k2 = keys[i], keys[j]
                box1 = candidate.boxes[k1]
                box2 = candidate.boxes[k2]
                if box1.intersects(box2):
                    collision_detected = True
                    colliding_pair = f"{k1} and {k2}"
                    break
            if collision_detected:
                break
                
        collision_passed = not collision_detected
        candidate.constraint_results["CollisionFree"] = {
            "status": "PASS" if collision_passed else "FAIL",
            "reason": "Collision free" if collision_passed else f"Collision between: {colliding_pair}"
        }

        # 2. GPS sky shadowing check (GPS must be highest component z_c)
        gps_box = candidate.boxes.get("GPSReceiver")
        gps_passed = True
        if gps_box:
            for name, box in candidate.boxes.items():
                if name != "GPSReceiver" and box.z_c >= gps_box.z_c:
                    gps_passed = False
                    break
        candidate.constraint_results["GpsVisibility"] = {
            "status": "PASS" if gps_passed else "FAIL",
            "reason": "GPS is top-most element" if gps_passed else "GPS is shadowed by other components"
        }

        # 3. Compass magnetic isolation check (GPS/Compass >= 10cm away from high-current PDB)
        pdb_box = candidate.boxes.get("PowerDistributionBoard")
        compass_passed = True
        if gps_box and pdb_box:
            dx = gps_box.x_c - pdb_box.x_c
            dy = gps_box.y_c - pdb_box.y_c
            dz = gps_box.z_c - pdb_box.z_c
            dist = math.sqrt(dx**2 + dy**2 + dz**2)
            compass_passed = dist >= 0.10  # 10 cm isolation
        candidate.constraint_results["CompassMagneticIsolation"] = {
            "status": "PASS" if compass_passed else "FAIL",
            "reason": f"GPS-PDB separation: {dist*100:.1f} cm (Limit: >= 10.0 cm)" if (gps_box and pdb_box) else "N/A"
        }

        # 4. Battery access check (Battery should not sit on the exact same vertical slot/plate as FC)
        batt_box = candidate.boxes.get("BatteryPack")
        fc_box = candidate.boxes.get("FlightController")
        battery_access_passed = True
        if batt_box and fc_box:
            # If battery and FC are on the exact same plate center, replacement is blocked
            battery_access_passed = abs(batt_box.z_c - fc_box.z_c) >= 0.02
        candidate.constraint_results["BatteryAccessibility"] = {
            "status": "PASS" if battery_access_passed else "FAIL",
            "reason": "Battery tray is accessible on separate deck" if battery_access_passed else "Battery overlaps FC deck"
        }

        all_passed = collision_passed and gps_passed and compass_passed and battery_access_passed
        candidate.constraints_passed = all_passed
        return all_passed
