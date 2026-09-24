"""
ConnectorSelector Subsystem

Purpose:
    Defines the `ConnectorSelector` class responsible for selecting main battery and power distribution connectors.

Role in Architecture:
    `ConnectorSelector` selects main power connector types (XT60, XT90, AS150, QS8, Amass) based on peak total current draw.
"""

from typing import Any


class ConnectorSelector:
    """
    Selection service for main power connectors.

    Design Principles:
        - Single Responsibility Principle: Power connector current rating and anti-spark protection selection only.
    """

    def select_connectors(self, peak_current_total_a: float) -> dict[str, Any]:
        """
        Determines optimal power connector type.

        Args:
            peak_current_total_a (float): Peak total current draw in Amperes.

        Returns:
            dict[str, Any]: Selected connector specifications dictionary.
        """
        if peak_current_total_a > 180.0:
            conn_type = "QS8-S Anti-Spark"
            rated_a = 200.0
            weight_g = 35.0
        elif peak_current_total_a > 100.0:
            conn_type = "AS150 Anti-Spark 7mm"
            rated_a = 150.0
            weight_g = 24.0
        elif peak_current_total_a > 60.0:
            conn_type = "XT90-S Anti-Spark"
            rated_a = 90.0
            weight_g = 15.0
        else:
            conn_type = "XT60"
            rated_a = 60.0
            weight_g = 7.0

        return {
            "main_connector_type": conn_type,
            "rated_continuous_current_a": rated_a,
            "anti_spark_protected": "Anti-Spark" in conn_type,
            "connector_weight_g": weight_g,
        }
