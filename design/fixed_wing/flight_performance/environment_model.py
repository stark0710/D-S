"""
Fixed-Wing Flight Performance Environment Model Subsystem

Purpose:
    Defines the `EnvironmentModel` class representing standard atmosphere calculations.

Role in Architecture:
    `EnvironmentModel` provides density, pressure, and temperature variations with altitude.
"""

from typing import Tuple


class EnvironmentModel:
    """
    Standard International Standard Atmosphere (ISA) model solver.
    """

    def get_atmospheric_properties(self, altitude_m: float) -> Tuple[float, float, float]:
        """
        Computes standard atmosphere properties for the given altitude.

        Args:
            altitude_m (float): Flight altitude in meters.

        Returns:
            Tuple[float, float, float]: (air_density_kg_m3, pressure_pa, temperature_k)
        """
        t0 = 288.15      # sea level temp in K
        p0 = 101325.0    # sea level pressure in Pa
        rho0 = 1.225     # sea level density in kg/m^3
        g = 9.80665
        r = 287.05
        lapse_rate = -0.0065  # K/m

        if altitude_m <= 11000.0:
            temperature = t0 + lapse_rate * altitude_m
            pressure = p0 * (temperature / t0) ** (-g / (lapse_rate * r))
            density = pressure / (r * temperature)
        else:
            # Stratosphere base
            t_strat = t0 + lapse_rate * 11000.0
            p_strat = p0 * (t_strat / t0) ** (-g / (lapse_rate * r))
            dh = altitude_m - 11000.0
            temperature = t_strat
            pressure = p_strat * math.exp(-g * dh / (r * t_strat))
            density = pressure / (r * temperature)

        return density, pressure, temperature
