# -*- coding: utf-8 -*-
import random
from functools import partial

import BattleReplay
import BigWorld
import Keys
import SoundGroups
from Avatar import PlayerAvatar as PlayerAvatar
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.app_loader import g_appLoader
from gui.battle_control.battle_constants import DEVICE_STATE_AS_DAMAGE, DEVICE_STATE_DESTROYED, VEHICLE_DEVICE_IN_COMPLEX_ITEM, VEHICLE_VIEW_STATE
from gui.mods.mod_mods_gui import g_gui, inject
from gui.shared.gui_items import Vehicle
from gui import InputHandler


class Config(object):
    def __init__(self):
        self.ids = 'repair_extended'
        self.version = '3.00 (27.04.2017)'
        self.author = 'by spoter'
        self.version_id = 300
        self.buttons = {
            'buttonChassis': [[Keys.KEY_LALT, Keys.KEY_RALT]]
        }
        self.data = {
            'version'       : self.version_id,
            'enabled'       : True,
            'buttonChassis' : self.buttons['buttonChassis'],
            'removeStun'    : True,
            'useGoldKits'   : True,
            'timerMin'      : 0.3,
            'timerMax'      : 0.8,
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
                    'repairkit': ['engine', 'ammoBay', 'gun', 'turretRotator', 'chassis', 'surveyingDevice', 'radio', 'fuelTank']
                }
            }
        }
        self.i18n = {
            'version'                        : self.version_id,
            'UI_repair_name'                 : 'Repair extended Cheat edition',
            'UI_repair_buttonChassis_text'   : 'Button: Restore Chassis',
            'UI_repair_buttonChassis_tooltip': '',
            'UI_repair_removeStun_text'      : 'Remove stun',
            'UI_repair_removeStun_tooltip'   : '',
            'UI_repair_useGoldKits_text'     : 'Use Gold Kits',
            'UI_repair_useGoldKits_tooltip'  : '',
            'UI_repair_timerMin_text'        : 'Min delay auto usage',
            'UI_repair_timerMin_format'      : ' sec.',
            'UI_repair_timerMax_text'        : 'Max delay auto usage',
            'UI_repair_timerMax_format'      : ' sec.',

        }
        print '[LOAD_MOD]:  [%s v%s, %s]' % (self.ids, self.version, self.author)
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n)
        g_gui.register(self.ids, self.template, self.data, self.apply)

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
                'type'        : 'Slider',
                'text'        : self.i18n['UI_repair_timerMin_text'],
                'minimum'     : 0.1,
                'maximum'     : 0.5,
                'snapInterval': 0.1,
                'value'       : self.data['timerMin'],
                'format'      : '{{value}}%s' % self.i18n['UI_repair_timerMin_format'],
                'varName'     : 'timerMin'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_repair_timerMax_text'],
                'minimum'     : 0.6,
                'maximum'     : 3.0,
                'snapInterval': 0.1,
                'value'       : self.data['timerMax'],
                'format'      : '{{value}}%s' % self.i18n['UI_repair_timerMax_format'],
                'varName'     : 'timerMax'
            }],
            'column2'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_removeStun_text'],
                'value'  : self.data['removeStun'],
                'tooltip': self.i18n['UI_repair_removeStun_tooltip'],
                'varName': 'removeStun'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_useGoldKits_text'],
                'value'  : self.data['useGoldKits'],
                'tooltip': self.i18n['UI_repair_useGoldKits_tooltip'],
                'varName': 'useGoldKits'
            }]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings)
        g_gui.update(self.ids, self.template)


class Repair(object):
    def __init__(self):
        self.ctrl = None
        self.consumablesPanel = None
        self.items = {
            'extinguisher': [251, 251],
            'medkit'      : [763, 1019],
            'repairkit'   : [1275, 1531]
        }

    def startBattle(self):
        self.ctrl = BigWorld.player().guiSessionProvider.shared
        InputHandler.g_instance.onKeyDown += self.injectButton
        InputHandler.g_instance.onKeyUp += self.injectButton
        if self.ctrl.vehicleState is not None:
            self.ctrl.vehicleState.onVehicleStateUpdated += self.autoUse

    def stopBattle(self):
        InputHandler.g_instance.onKeyDown -= self.injectButton
        InputHandler.g_instance.onKeyUp -= self.injectButton
        if self.ctrl.vehicleState is not None:
            self.ctrl.vehicleState.onVehicleStateUpdated -= self.autoUse

    def useItem(self, equipmentTag, item=None):
        if not config.data['enabled']: return
        if BattleReplay.g_replayCtrl.isPlaying: return
        if self.ctrl is None:
            return

        sound = False
        equipment = self.ctrl.equipments.getEquipment(self.items[equipmentTag][0])
        if equipment is not None and equipment.isReady and equipment.isAvailableToUse:
            # noinspection PyProtectedMember
            self.consumablesPanel._ConsumablesPanel__handleEquipmentPressed(self.items[equipmentTag][0], item)
            sound = True
        else:
            if config.data['useGoldKits']:
                equipment = self.ctrl.equipments.getEquipment(self.items[equipmentTag][1])
                if equipment is not None and equipment.isReady and equipment.isAvailableToUse:
                    # noinspection PyProtectedMember
                    self.consumablesPanel._ConsumablesPanel__handleEquipmentPressed(self.items[equipmentTag][1])
                    sound = True
        if sound:
            sound = SoundGroups.g_instance.getSound2D('vo_flt_repair')
            BigWorld.callback(1.0, sound.play)

    def repair(self):
        if self.ctrl is None:
            return
        if self.ctrl.vehicleState.getStateValue(VEHICLE_VIEW_STATE.FIRE):
            self.useItem('extinguisher')

        if config.data['removeStun'] and self.ctrl.vehicleState.getStateValue(VEHICLE_VIEW_STATE.STUN):
            self.useItem('medkit')

        for equipmentTag in ('medkit', 'repairkit'):
            for intCD, equipment in self.ctrl.equipments.iterEquipmentsByTag(equipmentTag):
                if equipment.isReady and equipment.isAvailableToUse:
                    devices = list(set([name if name not in VEHICLE_DEVICE_IN_COMPLEX_ITEM else VEHICLE_DEVICE_IN_COMPLEX_ITEM[name] for name, state in equipment.getEntitiesIterator() if state in DEVICE_STATE_AS_DAMAGE]))
                    specific = config.data['repairPriority'][Vehicle.getVehicleClassTag(BigWorld.player().vehicleTypeDescriptor.type.tags)][equipmentTag]
                    for item in specific:
                        if item in devices:
                            self.useItem(equipmentTag, item)
                            break

    def repairChassis(self):
        if self.ctrl is None:
            return
        equipmentTag = 'repairkit'
        for intCD, equipment in self.ctrl.equipments.iterEquipmentsByTag(equipmentTag):
            if equipment.isReady and equipment.isAvailableToUse:
                devices = [name for name, state in equipment.getEntitiesIterator() if state in DEVICE_STATE_DESTROYED]
                for name in devices:
                    if name in ['chassis', 'leftTrack', 'rightTrack']:
                        self.useItem(equipmentTag, name)
                        return

    @inject.log
    def injectButton(self, event):
        if g_appLoader.getDefBattleApp():
            if g_gui.get_key(config.data['buttonChassis']) and event.isKeyDown():
                self.repairChassis()

    @inject.log
    def autoUse(self, state, value):
        if self.ctrl is None:
            return
        # status = '%s' % [key for key, ids in VEHICLE_VIEW_STATE.__dict__.iteritems() if ids == state][0]
        if state == VEHICLE_VIEW_STATE.FIRE:
            time = random.uniform(config.data['timerMin'], config.data['timerMax'])
            BigWorld.callback(time, partial(self.useItem, 'extinguisher'))

        if config.data['removeStun'] and state == VEHICLE_VIEW_STATE.STUN:
            time = random.uniform(config.data['timerMin'], config.data['timerMax'])
            BigWorld.callback(time, partial(self.useItem, 'medkit'))

        if state == VEHICLE_VIEW_STATE.DEVICES:
            deviceName, deviceState, actualState = value
            if deviceState in DEVICE_STATE_AS_DAMAGE:
                if deviceName in VEHICLE_DEVICE_IN_COMPLEX_ITEM:
                    itemName = VEHICLE_DEVICE_IN_COMPLEX_ITEM[deviceName]
                else:
                    itemName = deviceName
                equipmentTag = 'medkit' if itemName in TANKMEN_ROLES_ORDER_DICT['enum'] else 'repairkit'
                specific = config.data['repairPriority'][Vehicle.getVehicleClassTag(BigWorld.player().vehicleTypeDescriptor.type.tags)][equipmentTag]
                if itemName in specific:
                    time = random.uniform(config.data['timerMin'], config.data['timerMax'])
                    BigWorld.callback(time, partial(self.useItem, equipmentTag, itemName))


config = Config()
repair = Repair()


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    repair.startBattle()


@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
@inject.log
def hookDestroyGUI(func, *args):
    func(*args)
    repair.stopBattle()


@inject.hook(ConsumablesPanel, '_ConsumablesPanel__onEquipmentAdded')
@inject.log
def onEquipmentAdded(func, *args):
    func(*args)
    repair.consumablesPanel = args[0]
