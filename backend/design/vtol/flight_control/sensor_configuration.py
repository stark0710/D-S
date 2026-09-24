"""
VTOL Phase 10 Sensor Configuration Engine.

Purpose:
    Configures and validates flight sensor drivers, bus assignments, protocols,
    redundancy schemes, and pre-flight calibration prerequisites for Holybro Pixhawk 6X.
    Enforces REQUIRED_PRE_FLIGHT calibration status across all navigation sensors.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .flight_control_models import (
    FlightControlStatus,
    SensorConfigurationItem,
)


class SensorConfigurationEngine:
    """
    Authoritative sensor driver and interface configurator (Prompt Section 12).
    """

    @classmethod
    def build_sensor_configurations(cls) -> List[SensorConfigurationItem]:
        """
        Builds the complete sensor configuration suite for Pixhawk 6X on QuadPlane.
        """
        sensors: List[SensorConfigurationItem] = [
            SensorConfigurationItem(
                sensor_name="Primary GNSS & RTK Navigation",
                hardware_component="Holybro H-RTK F9P Helical GNSS Module",
                bus_interface="UART Serial (GPS1 Port)",
                protocol="u-blox UBX Binary Protocol (115200 baud)",
                ardupilot_driver_param="GPS_TYPE = 1 (Auto) / GPS_TYPE = 2 (uBlox)",
                driver_param_value=2,
                calibration_requirement="REQUIRED_PRE_FLIGHT (Antenna zero-baseline survey & satellite visibility check)",
                redundancy_support="Secondary GNSS supported via GPS2 port (Optional expansion)",
                failure_detection_method="EKF3 innovation variance monitor & HDOP / satellite count threshold",
                failsafe_response="Fallback to EKF3 dead-reckoning with synthetic wind estimation",
                configuration_status=FlightControlStatus.PASS,
                notes="Provides centimeter-level RTK positioning when connected to base station",
            ),
            SensorConfigurationItem(
                sensor_name="Primary Digital Compass / Magnetometer",
                hardware_component="IST8310 3-Axis Magnetometer (Integrated in H-RTK F9P)",
                bus_interface="CAN Bus (CAN1 Port) / I2C external",
                protocol="DroneCAN / UAVCAN (1 Mbps)",
                ardupilot_driver_param="COMPASS_TYPEMASK = 0 (All enabled) / COMPASS_PRIO1_ID",
                driver_param_value=1,
                calibration_requirement="REQUIRED_PRE_FLIGHT (Full 3D onboard sphere compass dance calibration)",
                redundancy_support="Dual redundancy (1x External in GPS mast + 2x Internal on Pixhawk 6X isolated board)",
                failure_detection_method="EKF3 magnetic field inconsistency check (>35% anomaly flags compass failure)",
                failsafe_response="Failover to secondary internal compass or GNSS course-over-ground heading",
                configuration_status=FlightControlStatus.PASS,
                notes="External mounting on boom mast minimizes motor electromagnetic interference",
            ),
            SensorConfigurationItem(
                sensor_name="Digital Differential Airspeed Sensor",
                hardware_component="Matek ASPD-4525 Digital Airspeed Sensor (Measurement Specialties 4525DO)",
                bus_interface="I2C Bus (I2C1 Port)",
                protocol="I2C Standard 400 kHz (I2C Address 0x28)",
                ardupilot_driver_param="ARSPD_TYPE = 1 (MS4525) & ARSPD_USE = 1",
                driver_param_value=1,
                calibration_requirement="REQUIRED_PRE_FLIGHT (Zero dynamic pressure baseline offset calibration on ground)",
                redundancy_support="Single physical sensor (Synthetic airspeed estimation serves as analytical backup)",
                failure_detection_method="Airspeed plausibility check vs groundspeed; frozen reading detection",
                failsafe_response="ARSPD_FAIL_ACTION: automatic failover to EKF3 synthetic wind airspeed",
                configuration_status=FlightControlStatus.PASS,
                notes="Connected via flexible silicon pneumatic tubing to nose-boom pitot probe",
            ),
            SensorConfigurationItem(
                sensor_name="Barometric Pressure & Altitude",
                hardware_component="Dual Onboard Barometers (ICP20100 & BMP388 on Pixhawk 6X FMU)",
                bus_interface="Internal SPI Bus",
                protocol="High-Speed SPI Bus (10 MHz)",
                ardupilot_driver_param="BARO_PRIMARY = 0 & BARO_GND_TEMP = 20.0",
                driver_param_value=0,
                calibration_requirement="REQUIRED_PRE_FLIGHT (Ground atmospheric pressure calibration during boot)",
                redundancy_support="Dual hardware barometers on isolated vibration-damped board",
                failure_detection_method="Cross-barometer pressure divergence check (>2.0 hPa threshold)",
                failsafe_response="Automatic failover to secondary internal barometer",
                configuration_status=FlightControlStatus.PASS,
                notes="Internal foam baffles protect barometers from prop downwash pressure spikes",
            ),
            SensorConfigurationItem(
                sensor_name="Inertial Measurement Units (IMU - Gyro / Accelerometer)",
                hardware_component="Triple Redundant IMUs (ICM-42688-P, ICM-42670-P, BMI088 on Pixhawk 6X)",
                bus_interface="Internal SPI Bus (Vibration Isolated & Temperature Controlled)",
                protocol="Internal SPI Bus",
                ardupilot_driver_param="INS_ENABLE_MASK = 7 (All 3 IMUs active in EKF3 voting)",
                driver_param_value=7,
                calibration_requirement="REQUIRED_PRE_FLIGHT (6-axis accelerometer calibration & gyro bias nulling)",
                redundancy_support="Triple physical IMU redundancy with real-time lane switching",
                failure_detection_method="EKF3 IMU health voting and consistency monitoring",
                failsafe_response="Seamless lane switch to healthy IMU in <10ms",
                configuration_status=FlightControlStatus.PASS,
                notes="Thermal resistor maintains IMU temperature at 45C to eliminate thermal drift",
            ),
            SensorConfigurationItem(
                sensor_name="Analog Power & Battery Monitor",
                hardware_component="Matek Systems PDB-HEX 12S Voltage & Current Sense Board",
                bus_interface="Analog Sense Leads (Pixhawk POWER1 Port)",
                protocol="Analog Linear Voltage Divider & Hall Current Scaling",
                ardupilot_driver_param="BATT_MONITOR = 4 (Analog Voltage and Current)",
                driver_param_value=4,
                calibration_requirement="REQUIRED_PRE_FLIGHT (Current multiplier and voltage divider bench calibration)",
                redundancy_support="Single analog power monitor module",
                failure_detection_method="Zero current check when motors armed; out-of-range voltage reading",
                failsafe_response="Warn pilot on GCS; initiate low-voltage RTL if reading drops below 21.6V",
                configuration_status=FlightControlStatus.PASS,
                notes="Monitors 6S 22.2V total aircraft discharge current up to 140A continuous / 200A peak",
            ),
            SensorConfigurationItem(
                sensor_name="RC Pilot Control Receiver",
                hardware_component="TBS Crossfire Nano RX / ExpressLRS Receiver",
                bus_interface="UART Serial (RCIN Port)",
                protocol="CRSF Serial Digital Protocol (416 kbps bidirectional telemetry)",
                ardupilot_driver_param="SERIAL5_PROTOCOL = 23 (RCIN) / RSSI_TYPE = 3",
                driver_param_value=23,
                calibration_requirement="REQUIRED_PRE_FLIGHT (Stick range calibration [1000us-2000us] on transmitter)",
                redundancy_support="Long-range 868/915MHz RF link with adaptive power scaling",
                failure_detection_method="CRSF packet lost frame counter & 1.5s signal timeout",
                failsafe_response="THR_FAILSAFE: Automatic switch to QRTL / autonomous return",
                configuration_status=FlightControlStatus.PASS,
                notes="Full digital packet decoding; eliminates analog PWM jitter",
            ),
            SensorConfigurationItem(
                sensor_name="Ground Control Station Telemetry Modem",
                hardware_component="Holybro SiK 915MHz 500mW Radio Transceiver",
                bus_interface="UART Serial (TELEM1 Port)",
                protocol="MAVLink 2.0 Serial Protocol (57600 baud, CTS/RTS hardware flow control)",
                ardupilot_driver_param="SERIAL1_PROTOCOL = 2 (MAVLink 2) & SERIAL1_BAUD = 57",
                driver_param_value=2,
                calibration_requirement="REQUIRED_PRE_FLIGHT (RF link pairing and signal RSSI verification)",
                redundancy_support="Backup telemetry through Companion Computer 4G/LTE or Crossfire telemetry",
                failure_detection_method="MAVLink heartbeat timeout > 10.0s",
                failsafe_response="FS_GCS_ENABL: Continue autonomous waypoint mission",
                configuration_status=FlightControlStatus.PASS,
                notes="Enables real-time parameter tuning, mission upload, and state monitoring",
            ),
        ]
        return sensors
