# Embedded file name: AutoEquip.py
"""AutoEquip by Skino88"""
import BigWorld
import ResMgr
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
from gui.shared import g_itemsCache, REQ_CRITERIA
from adisp import process
from gui.shared.utils.requesters.deprecated import Requester

description = 'AutoEquip'
author = 'by Skino88, spoter'
version = 'v1.03(10.02.2014)'


class AutoEquip(object):
    def __init__(self):
        self.g_xmlSetting = ResMgr.openSection('../res_mods/configs/spoter_mods/repair_extended/repair_extended_AutoEquip.xml', True)
        if not self.g_xmlSetting:
            self.g_xmlSetting.save()
        self.g_prevVehicle = None

    def saveDeviceOnVehicle(self, vehicle, deviceId, slotId, isRemove):
        self.g_xmlSetting.write(vehicle.name, '')
        if isRemove:
            self.g_xmlSetting[vehicle.name].writeInt('slot' + str(slotId + 1), 0)
        else:
            self.g_xmlSetting[vehicle.name].writeInt('slot' + str(slotId + 1), int(deviceId))
        self.g_xmlSetting.save()

    def vehicleCheckCallback(self):
        if g_currentVehicle.isInHangar:
            curVehicle = g_currentVehicle.item
            if self.g_prevVehicle is not curVehicle:
                if self.g_prevVehicle and curVehicle:
                    if self.g_prevVehicle.name is not curVehicle.name:
                        self.onCurrentVehicleChanged(curVehicle)
                self.g_prevVehicle = curVehicle
        BigWorld.callback(0.1, self.vehicleCheckCallback)

    def onCurrentVehicleChanged(self, curVehicle):
        self.removeAllRemovableDevicesFromAllVehicle(curVehicle)
        self.equipAllRemovableDevicesOnVehicle(curVehicle)

    @staticmethod
    def callback(resultID):
        _ = resultID

    @process
    def removeAllRemovableDevicesFromAllVehicle(self, curVehicle):
        deviceAllInventory = yield Requester('optionalDevice').getFromInventory()
        alreadyRemoved = []
        vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        for vehicle in vehicles:
            if curVehicle is not vehicle:
                if not vehicle.isInBattle:
                    for slotIdx in range(0, 3):
                        device = vehicle.descriptor.optionalDevices[slotIdx]
                        if device and device.removable:
                            devCount = self.getDeviceInventoryCounts(deviceAllInventory, device)
                            if devCount is 0 and device.compactDescr not in alreadyRemoved:
                                BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, 0, slotIdx, False, self.callback)
                                alreadyRemoved.append(device.compactDescr)

    def equipAllRemovableDevicesOnVehicle(self, vehicle):
        if self.g_xmlSetting[vehicle.name]:
            for slotIdx in range(0, 3):
                device = vehicle.descriptor.optionalDevices[slotIdx]
                if not device:
                    deviceCompactDescr = self.g_xmlSetting[vehicle.name].readInt('slot' + str(slotIdx + 1), 0)
                    if deviceCompactDescr is not 0:
                        BigWorld.player().inventory.equipOptionalDevice(vehicle.invID, deviceCompactDescr, slotIdx, False, self.callback)

    @staticmethod
    def getDeviceInventoryCounts(inventoryDevices, device):
        invCount = 0
        try:
            invCount = inventoryDevices[inventoryDevices.index(device)].count
        except StandardError:
            pass
        return invCount


auto_equip = AutoEquip()
auto_equip.vehicleCheckCallback()


def hook_setVehicleModule(self, newId, slotIdx, oldId, isRemove):
    hooked_setVehicleModule(self, newId, slotIdx, oldId, isRemove)
    auto_equip.saveDeviceOnVehicle(g_currentVehicle.item, newId, slotIdx, isRemove)


hooked_setVehicleModule = AmmunitionPanel.setVehicleModule
AmmunitionPanel.setVehicleModule = hook_setVehicleModule

print ''
print '[LOAD_MOD]:  [' + str(description) + ' ' + str(author) + ']'
print '[INFO]:      [' + str(description) + ' ' + str(version) + ' initialized ...]'
print ''
