import BigWorld
from VehicleAppearance import VehicleAppearance
import items.vehicles

def new_getCamouflageParams(self, vehicle):
    camos = items.vehicles.g_cache.customization(vehicle.typeDescriptor.type.customizationNationID)['camouflages']
    for ids in camos:
        if vehicle.typeDescriptor.type.compactDescr in camos[ids]['tiling'] and 'Cracked_ice' in camos[ids]['name']:
            return (ids, 999999999, 0)
    return old_getCamouflageParams(self, vehicle)

old_getCamouflageParams = VehicleAppearance._VehicleAppearance__getCamouflageParams      
VehicleAppearance._VehicleAppearance__getCamouflageParams = new_getCamouflageParams