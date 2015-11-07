from gui.shared.tooltips.vehicle import VehicleParamsField

old_getValue = VehicleParamsField._getValue

def new_getValue(self):
    vehicle = self._tooltip.item
    if vehicle.hasTurrets:
        VehicleParamsField.PARAMS = {'lightTank': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor', 'turretArmor'),
         'mediumTank': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor', 'turretArmor'),
         'heavyTank': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor', 'turretArmor'),
         'SPG': ('circularVisionRadius', 'piercingPower', 'explosionRadius', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor', 'turretArmor'),
         'AT-SPG': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor', 'turretArmor'),
         'default': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor', 'turretArmor')}
    else:
        VehicleParamsField.PARAMS = {'lightTank': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor'),
         'mediumTank': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor'),
         'heavyTank': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor'),
         'SPG': ('circularVisionRadius', 'piercingPower', 'explosionRadius', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor'),
         'AT-SPG': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor'),
         'default': ('circularVisionRadius', 'piercingPower', 'damageAvg', 'damageAvgPerMinute', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'hullArmor')}
    return old_getValue(self)
    
VehicleParamsField._getValue = new_getValue