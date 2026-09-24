import math
from typing import Dict, Any

class InertiaCalculator:
    """
    Calculates aircraft moments of inertia (Ixx, Iyy, Izz) using the Parallel Axis Theorem.
    Diagonalizes the inertia tensor to compute principal moments and principal axes.
    """
    @staticmethod
    def _compute_inertia_tensor(
        coords: Dict[str, tuple[float, float, float]],
        m_payload: float,
        m_battery: float,
        m_frame: float,
        m_motor: float,
        m_prop: float,
        m_esc: float,
        m_wire: float,
        m_pdb: float,
        arm_count: int,
        wheelbase_m: float,
        cg: tuple[float, float, float],
        motor_coords: list[tuple[float, float, float]] = None
    ) -> tuple[list[float], list[list[float]]]:
        """
        Assembles the full 3D inertia tensor and solves for eigenvalues and eigenvectors.
        Returns (eigenvalues, eigenvectors).
        """
        cg_x, cg_y, cg_z = cg
        
        # 1. Compile point-like components and shapes with self-inertia
        # Each item is (mass, x, y, z, self_ixx, self_iyy, self_izz)
        components = []
        
        # FC
        if "FlightController" in coords:
            x, y, z = coords["FlightController"]
            components.append((0.015, x, y, z, 0.0, 0.0, 0.0))
        # GPS
        if "GPSReceiver" in coords:
            x, y, z = coords["GPSReceiver"]
            components.append((0.010, x, y, z, 0.0, 0.0, 0.0))
        # PDB + Wire
        if "PowerDistributionBoard" in coords:
            x, y, z = coords["PowerDistributionBoard"]
            components.append((m_pdb + m_wire, x, y, z, 0.0, 0.0, 0.0))
        # Telemetry
        if "TelemetryModem" in coords:
            x, y, z = coords["TelemetryModem"]
            components.append((0.008, x, y, z, 0.0, 0.0, 0.0))
        # Receiver
        if "RcReceiver" in coords:
            x, y, z = coords["RcReceiver"]
            components.append((0.004, x, y, z, 0.0, 0.0, 0.0))
            
        # Battery (modeled as solid brick 120mm x 60mm x 50mm)
        if "BatteryPack" in coords:
            x, y, z = coords["BatteryPack"]
            self_ixx = (1.0 / 12.0) * m_battery * (0.06**2 + 0.05**2)
            self_iyy = (1.0 / 12.0) * m_battery * (0.12**2 + 0.05**2)
            self_izz = (1.0 / 12.0) * m_battery * (0.12**2 + 0.06**2)
            components.append((m_battery, x, y, z, self_ixx, self_iyy, self_izz))
            
        # Payload (modeled as solid box 150mm x 100mm x 80mm)
        if "PayloadBay" in coords:
            x, y, z = coords["PayloadBay"]
            self_ixx = (1.0 / 12.0) * m_payload * (0.10**2 + 0.08**2)
            self_iyy = (1.0 / 12.0) * m_payload * (0.15**2 + 0.08**2)
            self_izz = (1.0 / 12.0) * m_payload * (0.15**2 + 0.10**2)
            components.append((m_payload, x, y, z, self_ixx, self_iyy, self_izz))

        # 2. Add frame center core (cylinder of radius R = 0.08m)
        m_core = m_frame * 0.40
        self_ixx = 0.25 * m_core * (0.08**2)
        self_iyy = 0.25 * m_core * (0.08**2)
        self_izz = 0.50 * m_core * (0.08**2)
        components.append((m_core, 0.0, 0.0, 0.0, self_ixx, self_iyy, self_izz))

        # 3. Sum point-like and shaped components using Parallel Axis Theorem
        ixx = 0.0
        iyy = 0.0
        izz = 0.0
        ixy = 0.0
        ixz = 0.0
        iyz = 0.0
        
        for m, x, y, z, s_ixx, s_iyy, s_izz in components:
            dx = x - cg_x
            dy = y - cg_y
            dz = z - cg_z
            
            ixx += s_ixx + m * (dy**2 + dz**2)
            iyy += s_iyy + m * (dx**2 + dz**2)
            izz += s_izz + m * (dx**2 + dy**2)
            ixy += m * dx * dy
            ixz += m * dx * dz
            iyz += m * dy * dz

        # 4. Add Radially Symmetric Slender Arm Rods and Tip Propulsion Components
        m_single_arm = (m_frame * 0.60) / arm_count
        
        # Populate motor_coords if not provided
        if not motor_coords or len(motor_coords) == 0:
            motor_coords = []
            for k in range(arm_count):
                angle = (2.0 * math.pi * k) / arm_count
                mx = 0.5 * wheelbase_m * math.cos(angle)
                my = 0.5 * wheelbase_m * math.sin(angle)
                mz = 0.0
                motor_coords.append((mx, my, mz))
                
        for mx, my, mz in motor_coords:
            l_arm = math.sqrt(mx**2 + my**2 + mz**2)
            if l_arm > 1e-4:
                ux = mx / l_arm
                uy = my / l_arm
                uz = mz / l_arm
                
                # Self-inertia of the arm rod about its center of gravity
                i_self = (1.0 / 12.0) * m_single_arm * (l_arm**2)
                self_ixx = i_self * (1.0 - ux**2)
                self_iyy = i_self * (1.0 - uy**2)
                self_izz = i_self * (1.0 - uz**2)
                self_ixy = -i_self * ux * uy
                self_ixz = -i_self * ux * uz
                self_iyz = -i_self * uy * uz
            else:
                self_ixx = self_iyy = self_izz = self_ixy = self_ixz = self_iyz = 0.0
                
            ax, ay, az = 0.5 * mx, 0.5 * my, 0.5 * mz
            dx = ax - cg_x
            dy = ay - cg_y
            dz = az - cg_z
            
            ixx += self_ixx + m_single_arm * (dy**2 + dz**2)
            iyy += self_iyy + m_single_arm * (dx**2 + dz**2)
            izz += self_izz + m_single_arm * (dx**2 + dy**2)
            ixy += self_ixy + m_single_arm * dx * dy
            ixz += self_ixz + m_single_arm * dx * dz
            iyz += self_iyz + m_single_arm * dy * dz
            
            # Tip propulsion components
            # Motor
            m_m, x_m, y_m, z_m = m_motor, mx, my, mz + 0.02
            dx_m, dy_m, dz_m = x_m - cg_x, y_m - cg_y, z_m - cg_z
            ixx += m_m * (dy_m**2 + dz_m**2)
            iyy += m_m * (dx_m**2 + dz_m**2)
            izz += m_m * (dx_m**2 + dy_m**2)
            ixy += m_m * dx_m * dy_m
            ixz += m_m * dx_m * dz_m
            iyz += m_m * dy_m * dz_m
            
            # Propeller
            m_p, x_p, y_p, z_p = m_prop, mx, my, mz + 0.025
            dx_p, dy_p, dz_p = x_p - cg_x, y_p - cg_y, z_p - cg_z
            ixx += m_p * (dy_p**2 + dz_p**2)
            iyy += m_p * (dx_p**2 + dz_p**2)
            izz += m_p * (dx_p**2 + dy_p**2)
            ixy += m_p * dx_p * dy_p
            ixz += m_p * dx_p * dz_p
            iyz += m_p * dy_p * dz_p
            
            # ESC
            m_e, x_e, y_e, z_e = m_esc, 0.5 * mx, 0.5 * my, mz - 0.01
            dx_e, dy_e, dz_e = x_e - cg_x, y_e - cg_y, z_e - cg_z
            ixx += m_e * (dy_e**2 + dz_e**2)
            iyy += m_e * (dx_e**2 + dz_e**2)
            izz += m_e * (dx_e**2 + dy_e**2)
            ixy += m_e * dx_e * dy_e
            ixz += m_e * dx_e * dz_e
            iyz += m_e * dy_e * dz_e

        # 5. Diagonalize 3x3 symmetric matrix A
        A = [
            [ixx, -ixy, -ixz],
            [-ixy, iyy, -iyz],
            [-ixz, -iyz, izz]
        ]
        
        eigenvalues, eigenvectors = InertiaCalculator._jacobi_diagonalize(A)
        
        # 6. Map eigenvalues/eigenvectors to closest geometric axes
        used_cols = set()
        mapping = {}
        for axis in range(3):
            best_col = -1
            best_val = -1.0
            for col in range(3):
                if col in used_cols:
                    continue
                val = abs(eigenvectors[col][axis])
                if val > best_val:
                    best_val = val
                    best_col = col
            mapping[axis] = best_col
            used_cols.add(best_col)
            
        mapped_eigenvalues = [eigenvalues[mapping[0]], eigenvalues[mapping[1]], eigenvalues[mapping[2]]]
        mapped_eigenvectors = [eigenvectors[mapping[0]], eigenvectors[mapping[1]], eigenvectors[mapping[2]]]
        
        # Ensure eigenvectors are aligned with positive directions of coordinate axes
        for axis in range(3):
            vec = list(mapped_eigenvectors[axis])
            if vec[axis] < 0:
                vec = [-x for x in vec]
            
            # Normalize
            norm = math.sqrt(sum(x**2 for x in vec))
            if norm > 1e-9:
                vec = [x / norm for x in vec]
            mapped_eigenvectors[axis] = tuple(vec)
            
        return mapped_eigenvalues, mapped_eigenvectors

    @staticmethod
    def _jacobi_diagonalize(A_in: list[list[float]], tolerance: float = 1e-9, max_sweeps: int = 50) -> tuple[list[float], list[tuple[float, float, float]]]:
        n = 3
        A = [[A_in[i][j] for j in range(n)] for i in range(n)]
        V = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        
        for sweep in range(max_sweeps):
            max_val = 0.0
            p, q = -1, -1
            for i in range(n):
                for j in range(i + 1, n):
                    val = abs(A[i][j])
                    if val > max_val:
                        max_val = val
                        p, q = i, j
                        
            if max_val < tolerance:
                break
                
            diff = A[q][q] - A[p][p]
            if abs(A[p][q]) < tolerance * 1e-4:
                c = 1.0
                s = 0.0
            else:
                phi = 0.5 * diff / A[p][q]
                t = 1.0 / (abs(phi) + math.sqrt(phi**2 + 1.0))
                if phi < 0:
                    t = -t
                c = 1.0 / math.sqrt(t**2 + 1.0)
                s = t * c
                
            tau = s / (1.0 + c)
            apq = A[p][q]
            A[p][q] = 0.0
            A[p][p] -= t * apq
            A[q][q] += t * apq
            
            for r in range(n):
                if r != p and r != q:
                    arp = A[r][p]
                    arq = A[r][q]
                    A[r][p] = arp - s * (arq + arp * tau)
                    A[p][r] = A[r][p]
                    A[r][q] = arq + s * (arp - arq * tau)
                    A[q][r] = A[r][q]
                    
            for r in range(n):
                vrp = V[r][p]
                vrq = V[r][q]
                V[r][p] = vrp - s * (vrq + vrp * tau)
                V[r][q] = vrq + s * (vrp - vrq * tau)
                
        eigenvalues = [A[i][i] for i in range(n)]
        eigenvectors = []
        for j in range(n):
            eigenvectors.append((V[0][j], V[1][j], V[2][j]))
        return eigenvalues, eigenvectors

    @staticmethod
    def calculate_inertia(
        coords: Dict[str, tuple[float, float, float]],
        m_payload: float,
        m_battery: float,
        m_frame: float,
        m_motor: float,
        m_prop: float,
        m_esc: float,
        m_wire: float,
        m_pdb: float,
        arm_count: int,
        wheelbase_m: float,
        cg: tuple[float, float, float],
        motor_coords: list[tuple[float, float, float]] = None
    ) -> tuple[float, float, float]:
        """
        Computes principal moments of inertia about the Center of Gravity.
        """
        eigenvalues, _ = InertiaCalculator._compute_inertia_tensor(
            coords=coords,
            m_payload=m_payload,
            m_battery=m_battery,
            m_frame=m_frame,
            m_motor=m_motor,
            m_prop=m_prop,
            m_esc=m_esc,
            m_wire=m_wire,
            m_pdb=m_pdb,
            arm_count=arm_count,
            wheelbase_m=wheelbase_m,
            cg=cg,
            motor_coords=motor_coords
        )
        return max(0.0001, eigenvalues[0]), max(0.0001, eigenvalues[1]), max(0.0001, eigenvalues[2])

    @staticmethod
    def calculate_principal_axes(
        coords: Dict[str, tuple[float, float, float]],
        m_payload: float,
        m_battery: float,
        m_frame: float,
        m_motor: float,
        m_prop: float,
        m_esc: float,
        m_wire: float,
        m_pdb: float,
        arm_count: int,
        wheelbase_m: float,
        cg: tuple[float, float, float],
        motor_coords: list[tuple[float, float, float]] = None
    ) -> Dict[str, tuple[float, float, float]]:
        """
        Computes unit vector directions of principal axes of inertia.
        """
        _, eigenvectors = InertiaCalculator._compute_inertia_tensor(
            coords=coords,
            m_payload=m_payload,
            m_battery=m_battery,
            m_frame=m_frame,
            m_motor=m_motor,
            m_prop=m_prop,
            m_esc=m_esc,
            m_wire=m_wire,
            m_pdb=m_pdb,
            arm_count=arm_count,
            wheelbase_m=wheelbase_m,
            cg=cg,
            motor_coords=motor_coords
        )
        return {
            "roll_axis": eigenvectors[0],
            "pitch_axis": eigenvectors[1],
            "yaw_axis": eigenvectors[2]
        }
