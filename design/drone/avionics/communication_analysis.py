"""
CommunicationAnalysis Subsystem

Purpose:
    Defines the `CommunicationAnalysis` class and `CommunicationAnalysisResult` dataclass for RF link range and bandwidth calculations.

Role in Architecture:
    `CommunicationAnalysis` estimates RC link line-of-sight range in km, telemetry radio link range in km,
    telemetry data link bandwidth in kbps, and link fade margin in dB.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CommunicationAnalysisResult:
    """
    Multirotor RF communication link analysis output model.

    Attributes:
        rc_link_range_km (float): Maximum Line-of-Sight (LOS) RC control link range in km.
        telemetry_link_range_km (float): Maximum telemetry data link range in km.
        telemetry_bandwidth_kbps (float): Telemetry data throughput in kbps.
        link_margin_db (float): RF link budget margin in dB (>= 10 dB recommended).
        metadata (dict[str, Any]): Additional diagnostic metadata.
    """

    rc_link_range_km: float
    telemetry_link_range_km: float
    telemetry_bandwidth_kbps: float
    link_margin_db: float
    metadata: dict[str, Any] = field(default_factory=dict)


class CommunicationAnalysis:
    """
    Analysis service for RF communication link budget and bandwidth.

    Design Principles:
        - Single Responsibility Principle: RF range, telemetry bandwidth, and link margin calculations only.
    """

    def analyze_communication(
        self,
        rc_protocol: str = "ExpressLRS 900MHz",
        telemetry_power_mw: float = 500.0,
        target_range_km: float = 10.0
    ) -> CommunicationAnalysisResult:
        """
        Calculates communication range and link margin.

        Args:
            rc_protocol (str): RC receiver protocol string.
            telemetry_power_mw (float): Telemetry transmitter RF power in mW.
            target_range_km (float): Mission target operational range in km.

        Returns:
            CommunicationAnalysisResult: Computed communication analysis output.
        """
        if "900MHz" in rc_protocol or "Crossfire" in rc_protocol or "ExpressLRS 900" in rc_protocol:
            rc_range = 25.0
        else:
            rc_range = 10.0

        if telemetry_power_mw >= 1000.0:
            telem_range = 30.0
            bandwidth = 115.2
        elif telemetry_power_mw >= 500.0:
            telem_range = 15.0
            bandwidth = 57.6
        else:
            telem_range = 5.0
            bandwidth = 57.6

        # Friis path loss link margin estimate
        link_margin = round(18.0 - (target_range_km * 0.5), 1)

        return CommunicationAnalysisResult(
            rc_link_range_km=rc_range,
            telemetry_link_range_km=telem_range,
            telemetry_bandwidth_kbps=bandwidth,
            link_margin_db=max(5.0, link_margin)
        )
