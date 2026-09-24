class MountingSelector:
    """
    Selects structural mount configurations based on component type and vibration sensitivity.
    """
    @staticmethod
    def get_mount_for_component(name: str) -> str:
        """
        Maps components to their recommended mechanical mount interface.
        """
        if name == "FlightController":
            return "Damped Dampener Mount (Anti-Vibration Gel Pads)"
        elif name == "GPSReceiver":
            return "Carbon Fiber Mast Standoff (150mm High Tube)"
        elif name == "BatteryPack":
            return "Battery Plate Tray with Quick-Release Hook-and-Loop Velcro Straps"
        elif name == "PayloadBay":
            return "Bottom Rail Gimbal Mount (Dual Carbon Rod suspension)"
        elif name == "PowerDistributionBoard":
            return "Rigid PCB Standoffs (Nylon spacers on center plate)"
        else:
            return "Rigid Hook-and-Loop Velcro tape"
