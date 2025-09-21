﻿# -*- coding: utf-8 -*-

import BattleReplay
import BigWorld
import Keys
import SoundGroups
from gui import InputHandler
from gui.battle_control.battle_constants import DEVICE_STATE_DESTROYED, VEHICLE_VIEW_STATE, DEVICE_STATE_NORMAL
# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject
from gui.shared.gui_items import Vehicle

from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE

COMPLEX_ITEM = {
    'leftTrack0' : 'chassis',
    'rightTrack0': 'chassis',
    'leftTrack1' : 'chassis',
    'rightTrack1': 'chassis',
    'gunner1'   : 'gunner',
    'gunner2'   : 'gunner',
    'radioman1' : 'radioman',
    'radioman2' : 'radioman',
    'loader1'   : 'loader',
    'loader2'   : 'loader',
    'wheel0'    : 'wheel',
    'wheel1'    : 'wheel',
    'wheel2'    : 'wheel',
    'wheel3'    : 'wheel',
    'wheel4'    : 'wheel',
    'wheel5'    : 'wheel',
    'wheel6'    : 'wheel',
    'wheel7'    : 'wheel'
}

CHASSIS = ['chassis', 'leftTrack', 'rightTrack', 'leftTrack0', 'rightTrack0', 'leftTrack1', 'rightTrack1', 'wheel', 'wheel0', 'wheel1', 'wheel2', 'wheel3', 'wheel4', 'wheel5', 'wheel6', 'wheel7']


class Config(object):
    def __init__(self):
        self.ids = 'repair_extended'
        self.version = 'v3.14 (2025-09-21)'
        self.author = 'by spoter'
        self.version_id = 314
        self.buttons = {
            'buttonRepair' : [Keys.KEY_SPACE],
            'buttonChassis': [[Keys.KEY_LALT, Keys.KEY_RALT]]
        }
        self.data = {
            'version'       : self.version_id,
            'enabled'       : True,
            'buttonChassis' : self.buttons['buttonChassis'],
            'buttonRepair'  : self.buttons['buttonRepair'],
            'removeStun'    : True,
            'extinguishFire': True,
            'healCrew'      : True,
            'repairDevices' : True,
            'restoreChassis': False,
            'useGoldKits'   : True,
            'repairPriority': {
                'lightTank'            : {
                    'medkit'   : ['driver', 'commander', 'gunner', 'loader'],
                    'repairkit': ['engine', 'ammoBay', 'gun', 'turretRotator', 'fuelTank']
                },
                'mediumTank'           : {
                    'medkit'   : ['loader', 'driver', 'commander', 'gunner'],
                    'repairkit': ['turretRotator', 'engine', 'ammoBay', 'gun', 'fuelTank']
                },
                'heavyTank'            : {
                    'medkit'   : ['commander', 'loader', 'gunner', 'driver'],
                    'repairkit': ['turretRotator', 'ammoBay', 'engine', 'gun', 'fuelTank']
                },
                'SPG'                  : {
                    'medkit'   : ['commander', 'loader', 'gunner', 'driver'],
                    'repairkit': ['ammoBay', 'engine', 'gun', 'turretRotator', 'fuelTank']
                },
                'AT-SPG'               : {
                    'medkit'   : ['loader', 'gunner', 'commander', 'driver'],
                    'repairkit': ['ammoBay', 'gun', 'engine', 'turretRotator', 'fuelTank']
                },
                'AllAvailableVariables': {
                    'medkit'   : ['commander', 'gunner', 'driver', 'radioman', 'loader'],
                    'repairkit': ['engine', 'ammoBay', 'gun', 'turretRotator', 'chassis', 'surveyingDevice', 'radio', 'fuelTank', 'wheel']
                }
            }
        }
        self.i18n = {
            'version'                         : self.version_id,
            'UI_repair_name'                  : 'Repair extended',
            'UI_repair_buttonChassis_text'    : 'Button: Restore Chassis',
            'UI_repair_buttonChassis_tooltip' : '',
            'UI_repair_buttonRepair_text'     : 'Button: Smart Repair',
            'UI_repair_buttonRepair_tooltip'  : '',
            'UI_repair_removeStun_text'       : 'Remove stun',
            'UI_repair_removeStun_tooltip'    : '',
            'UI_repair_useGoldKits_text'      : 'Use Gold Kits',
            'UI_repair_useGoldKits_tooltip'   : '',
            'UI_repair_extinguishFire_text'   : 'Extinguish fire',
            'UI_repair_extinguishFire_tooltip': '',
            'UI_repair_healCrew_text'         : 'Heal crew',
            'UI_repair_healCrew_tooltip'      : '',
            'UI_repair_restoreChassis_text'   : 'Restore chassis',
            'UI_repair_restoreChassis_tooltip': '',
            'UI_repair_repairDevices_text'    : 'Repair devices',
            'UI_repair_repairDevices_tooltip' : ''
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_repair_name'],
            'settingsVersion': self.version,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_repair_buttonChassis_text'],
                'tooltip'     : self.i18n['UI_repair_buttonChassis_tooltip'],
                'value'       : self.data['buttonChassis'],
                'defaultValue': self.buttons['buttonChassis'],
                'varName'     : 'buttonChassis'
            }, {
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_repair_buttonRepair_text'],
                'tooltip'     : self.i18n['UI_repair_buttonRepair_tooltip'],
                'value'       : self.data['buttonRepair'],
                'defaultValue': self.buttons['buttonRepair'],
                'varName'     : 'buttonRepair'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_useGoldKits_text'],
                'value'  : self.data['useGoldKits'],
                'tooltip': self.i18n['UI_repair_useGoldKits_tooltip'],
                'varName': 'useGoldKits'
            }],
            'column2'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_restoreChassis_text'],
                'value'  : self.data['restoreChassis'],
                'tooltip': self.i18n['UI_repair_restoreChassis_tooltip'],
                'varName': 'restoreChassis'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_removeStun_text'],
                'value'  : self.data['removeStun'],
                'tooltip': self.i18n['UI_repair_removeStun_tooltip'],
                'varName': 'removeStun'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_extinguishFire_text'],
                'value'  : self.data['extinguishFire'],
                'tooltip': self.i18n['UI_repair_extinguishFire_tooltip'],
                'varName': 'extinguishFire'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_healCrew_text'],
                'value'  : self.data['healCrew'],
                'tooltip': self.i18n['UI_repair_healCrew_tooltip'],
                'varName': 'healCrew'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_repairDevices_text'],
                'value'  : self.data['repairDevices'],
                'tooltip': self.i18n['UI_repair_repairDevices_tooltip'],
                'varName': 'repairDevices'
            }]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class Repair(object):
    def __init__(self):
        self.player = None
        self.ctrl = None
        self.consumablesPanel = None
        self.items = {
            'extinguisher': [251, 251, None, None],
            'medkit'      : [763, 1019, None, None],
            'repairkit'   : [1275, 1531, None, None]
        }
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__onComponentRegistered, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_UNREGISTERED, self.__onComponentUnregistered, EVENT_BUS_SCOPE.GLOBAL)

    def startBattle(self):
        self.player = BigWorld.player()
        self.ctrl = self.player.guiSessionProvider.shared
        InputHandler.g_instance.onKeyDown += self.injectButton
        InputHandler.g_instance.onKeyUp += self.injectButton
        self.checkBattleStarted()

    def stopBattle(self):
        InputHandler.g_instance.onKeyDown -= self.injectButton
        InputHandler.g_instance.onKeyUp -= self.injectButton
        for equipmentTag in self.items:
            self.items[equipmentTag][2] = None
            self.items[equipmentTag][3] = None
        self.items['repairkit'][1] = 1531

    def checkBattleStarted(self):
        if hasattr(BigWorld.player(), 'arena') and BigWorld.player().arena.period is 3:
            for equipmentTag in self.items:
                self.items[equipmentTag][2] = self.ctrl.equipments.getEquipment(self.items[equipmentTag][0]) if self.ctrl.equipments.hasEquipment(self.items[equipmentTag][0]) else None
                self.items[equipmentTag][3] = self.ctrl.equipments.getEquipment(self.items[equipmentTag][1]) if self.ctrl.equipments.hasEquipment(self.items[equipmentTag][1]) else None
            equipmentTag = 'repairkit'
            if self.ctrl.equipments.hasEquipment(46331):
                self.items[equipmentTag][1] = 46331
                self.items[equipmentTag][3] = self.ctrl.equipments.getEquipment(self.items[equipmentTag][1]) if self.ctrl.equipments.hasEquipment(self.items[equipmentTag][1]) else None
        else:
            BigWorld.callback(0.1, self.checkBattleStarted)

    def useItem(self, equipmentTag, item=None):
        if not config.data['enabled']: return
        if BattleReplay.g_replayCtrl.isPlaying: return
        if self.ctrl is None:
            return
        selfVehicle = self.player.getVehicleAttached()
        if selfVehicle is None:
            return
        if self.ctrl.vehicleState.getControllingVehicleID() != selfVehicle.id:
            return
        equipment = self.ctrl.equipments.getEquipment(self.items[equipmentTag][0]) if self.ctrl.equipments.hasEquipment(self.items[equipmentTag][0]) else None
        if equipment is not None and equipment.isReady and equipment.isAvailableToUse:
            self.consumablesPanel._handleEquipmentPressed(self.items[equipmentTag][0], item)
            sound = SoundGroups.g_instance.getSound2D('vo_flt_repair')
            BigWorld.callback(1.0, sound.play)

    def useItemGold(self, equipmentTag):
        if not config.data['enabled']: return
        if BattleReplay.g_replayCtrl.isPlaying: return
        if self.ctrl is None:
            return
        selfVehicle = self.player.getVehicleAttached()
        if selfVehicle is None:
            return
        if self.ctrl.vehicleState.getControllingVehicleID() != selfVehicle.id:
            return
        equipment = self.ctrl.equipments.getEquipment(self.items[equipmentTag][1]) if self.ctrl.equipments.hasEquipment(self.items[equipmentTag][1]) else None
        if equipment is not None and equipment.isReady and equipment.isAvailableToUse:
            self.consumablesPanel._handleEquipmentPressed(self.items[equipmentTag][1])
            sound = SoundGroups.g_instance.getSound2D('vo_flt_repair')
            BigWorld.callback(1.0, sound.play)

    def extinguishFire(self):
        if self.ctrl.vehicleState.getStateValue(VEHICLE_VIEW_STATE.FIRE):
            equipmentTag = 'extinguisher'
            if self.items[equipmentTag][2]:
                self.useItem(equipmentTag)

    def removeStun(self):
        if self.ctrl.vehicleState.getStateValue(VEHICLE_VIEW_STATE.STUN):
            equipmentTag = 'medkit'
            if self.items[equipmentTag][2]:
                self.useItem(equipmentTag)
            elif config.data['useGoldKits'] and self.items[equipmentTag][3]:
                self.useItemGold(equipmentTag)

    def repair(self, equipmentTag):
        specific = config.data['repairPriority'][Vehicle.getVehicleClassTag(BigWorld.player().vehicleTypeDescriptor.type.tags)][equipmentTag]
        if config.data['useGoldKits'] and self.items[equipmentTag][3]:
            equipment = self.items[equipmentTag][3]
            if equipment is not None:
                # noinspection PyUnresolvedReferences
                devices = [name for name, state in equipment.getEntitiesIterator() if state and state != DEVICE_STATE_NORMAL]
                result = []
                for device in devices:
                    if device in COMPLEX_ITEM:
                        itemName = COMPLEX_ITEM[device]
                    else:
                        itemName = device
                    if itemName in specific:
                        result.append(device)
                if len(result) > 1:
                    self.useItemGold(equipmentTag)
                elif result:
                    self.useItem(equipmentTag, result[0])
        elif self.items[equipmentTag][2]:
            equipment = self.items[equipmentTag][2]
            if equipment is not None:
                # noinspection PyUnresolvedReferences
                devices = [name for name, state in equipment.getEntitiesIterator() if state and state != DEVICE_STATE_NORMAL]
                result = []
                for device in devices:
                    if device in COMPLEX_ITEM:
                        itemName = COMPLEX_ITEM[device]
                    else:
                        itemName = device
                    if itemName in specific:
                        result.append(device)
                if len(result) > 1:
                    self.useItemGold(equipmentTag)
                elif result:
                    self.useItem(equipmentTag, result[0])

    def repairAll(self):
        if self.ctrl is None:
            return
        selfVehicle = self.player.getVehicleAttached()
        if selfVehicle is None:
            return
        if self.ctrl.vehicleState.getControllingVehicleID() != selfVehicle.id:
            return
        if config.data['extinguishFire']:
            self.extinguishFire()
        if config.data['repairDevices']:
            self.repair('repairkit')
        if config.data['healCrew']:
            self.repair('medkit')
        if config.data['removeStun']:
            self.removeStun()
        if config.data['restoreChassis']:
            self.repairChassis()

    def repairChassis(self):
        if self.ctrl is None:
            return
        selfVehicle = self.player.getVehicleAttached()
        if selfVehicle is None:
            return
        if self.ctrl.vehicleState.getControllingVehicleID() != selfVehicle.id:
            return
        equipmentTag = 'repairkit'
        for intCD, equipment in self.ctrl.equipments.iterEquipmentsByTag(equipmentTag):
            if equipment.isReady and equipment.isAvailableToUse:
                devices = [name for name, state in equipment.getEntitiesIterator() if state and state in DEVICE_STATE_DESTROYED]
                for name in devices:
                    if name in CHASSIS:
                        self.useItem(equipmentTag, name)
                        return

    @inject.log
    def injectButton(self, event):
        if inject.g_appLoader().getDefBattleApp():
            if g_gui.get_key(config.data['buttonChassis']) and event.isKeyDown():
                self.repairChassis()
            if g_gui.get_key(config.data['buttonRepair']) and event.isKeyDown():
                self.repairAll()

    def __onComponentRegistered(self, event):
        if event.alias == BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL:
            self.consumablesPanel = event.componentPy
            self.startBattle()

    def __onComponentUnregistered(self, event):
        if event.alias == BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL:
            self.stopBattle()


config = Config()
repair = Repair()
