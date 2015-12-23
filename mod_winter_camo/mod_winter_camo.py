import BigWorld
from VehicleAppearance import VehicleAppearance
import items.vehicles
import random

def new_getCamouflageParams(self, vehicle):
    if vehicle.typeDescriptor.camouflages[0][0] is not None:
        return vehicle.typeDescriptor.camouflages[0]
    camos = items.vehicles.g_cache.customization(vehicle.typeDescriptor.type.customizationNationID)['camouflages']
    camo_list = []
    names = ['Winter', 'White_Spots', 'IGR_Winter', 'IGR_Ch_Winter', 'IGR_K_Winter', 'Cracked_ice', 'WhiteDiagonal', 'SnowOnSpots', 'SnowOnBands', 'WhiteScar', 'china_historical_winter', 'china_historical_winter_2', 'winter', 'winter_white', 'winter_spots', 'Cz_winter01', 'Cz_winter']
    for ids in camos:
        if vehicle.typeDescriptor.type.compactDescr in camos[ids]['tiling'] and camos[ids]['name'] in names:
            if ids not in camo_list:
                camo_list.append(ids)
    camo_id = random.choice(camo_list)
    return (camo_id, 999999999, 0)

VehicleAppearance._VehicleAppearance__getCamouflageParams = new_getCamouflageParams