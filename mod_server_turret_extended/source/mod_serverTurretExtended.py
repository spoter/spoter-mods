# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

import Keys
import BigWorld
import CommandMapping
import VehicleGunRotator

from Avatar import PlayerAvatar
from constants import VEHICLE_SIEGE_STATE, VEHICLE_SETTING, VEHICLE_MISC_STATUS
from gui import InputHandler
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE


class _Config(object):
    def __init__(self):
        self.ids = 'serverTurretExtended'
        self.version = 'v2.03 (2019-04-25)'
        self.version_id = 203
        self.author = 'by spoter, reven86'
        self.buttons = {
            'buttonAutoMode': [Keys.KEY_R, [Keys.KEY_LALT, Keys.KEY_RALT]]
        }
        self.data = {
            'version'              : self.version_id,
            'enabled'              : True,
            'activateMessage'      : False,
            'fixAccuracyInMove'    : True,
            'serverTurret'         : True,
            'fixWheelCruiseControl': True,
            'autoActivateWheelMode': True,
            'buttonAutoMode': self.buttons['buttonAutoMode'],

        }
        self.i18n = {
            'version'                                 : self.version_id,
            'UI_description'                          : 'Server Turret and Fix Accuracy',
            'UI_setting_activateMessage_text'         : 'Show Activation Message',
            'UI_setting_activateMessage_tooltip'      : '{HEADER}Info:{/HEADER}{BODY}Show Activation Message in battle{/BODY}',
            'UI_setting_fixAccuracyInMove_text'       : 'Fix Accuracy',
            'UI_setting_fixAccuracyInMove_tooltip'    : '{HEADER}Info:{/HEADER}{BODY}When you tank move and then stop, used fix accuracy to not lost aiming{/BODY}',
            'UI_setting_serverTurret_text'            : 'Server Turret',
            'UI_setting_serverTurret_tooltip'         : '{HEADER}Info:{/HEADER}{BODY}Move Turret to Server Aim coordinates (need enabled Server Sight in game settings){/BODY}',
            'UI_battle_activateMessage'               : '"Muzzle chaos": Activated',
            'UI_setting_fixWheelCruiseControl_text'   : 'Fix Cruise Control on Wheels',
            'UI_setting_fixWheelCruiseControl_tooltip': '{HEADER}Info:{/HEADER}{BODY}When you activate Wheel mode with Cruise Control, vehicle stopped, this setting disable that{/BODY}',
            'UI_setting_autoActivateWheelMode_text'   : 'Auto activate\deactivate Wheel mode',
            'UI_setting_autoActivateWheelMode_tooltip': '{HEADER}Info:{/HEADER}{BODY}Try automate wheel mode{/BODY}',
            'UI_setting_buttonAutoMode_text'   : 'Button: Auto mode',
            'UI_setting_buttonAutoMode_tooltip': '{HEADER}Info:{/HEADER}{BODY}Button: Auto mode enable or disable{/BODY}',
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_serverTurret_text'],
                'value'  : self.data['serverTurret'],
                'tooltip': self.i18n['UI_setting_serverTurret_tooltip'],
                'varName': 'serverTurret'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_fixAccuracyInMove_text'],
                'value'  : self.data['fixAccuracyInMove'],
                'tooltip': self.i18n['UI_setting_fixAccuracyInMove_tooltip'],
                'varName': 'fixAccuracyInMove'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_activateMessage_text'],
                'value'  : self.data['activateMessage'],
                'tooltip': self.i18n['UI_setting_activateMessage_tooltip'],
                'varName': 'activateMessage'
            }],
            'column2'        : [{
                    'type'        : 'HotKey',
                    'text'        : self.i18n['UI_setting_buttonAutoMode_text'],
                    'tooltip'     : self.i18n['UI_setting_buttonAutoMode_tooltip'],
                    'value'       : self.data['buttonAutoMode'],
                    'defaultValue': self.buttons['buttonAutoMode'],
                    'varName'     : 'buttonAutoMode'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_fixWheelCruiseControl_text'],
                'value'  : self.data['fixWheelCruiseControl'],
                'tooltip': self.i18n['UI_setting_fixWheelCruiseControl_tooltip'],
                'varName': 'fixWheelCruiseControl'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_autoActivateWheelMode_text'],
                'value'  : self.data['autoActivateWheelMode'],
                'tooltip': self.i18n['UI_setting_autoActivateWheelMode_tooltip'],
                'varName': 'autoActivateWheelMode'
            }]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class MovementControl(object):
    timer = None
    callback = None
    limits = (0, 0)

    @staticmethod
    def move_pressed(avatar, is_down, key):
        if CommandMapping.g_instance.isFiredList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD, CommandMapping.CMD_ROTATE_LEFT, CommandMapping.CMD_ROTATE_RIGHT), key):
            avatar.moveVehicle(0, is_down)

    def startBattle(self):
        InputHandler.g_instance.onKeyDown += self.keyPressed
        InputHandler.g_instance.onKeyUp += self.keyPressed
        self.limits = (0, 0)
        self.timer = BigWorld.time()
        if self.callback is None:
            self.callback = BigWorld.callback(0.1, self.onCallback)

    def endBattle(self):
        if self.callback is not None:
            BigWorld.cancelCallback(self.callback)
            self.callback = None
        InputHandler.g_instance.onKeyDown -= self.keyPressed
        InputHandler.g_instance.onKeyUp -= self.keyPressed

    def onCallback(self):
        if _config.data['enabled'] and _config.data['autoActivateWheelMode']:
            self.changeMovement()
        self.callback = BigWorld.callback(0.1, self.onCallback)

    @staticmethod
    def keyPressed(event):
        if not _config.data['enabled']: return
        if g_gui.get_key(_config.data['buttonAutoMode']) and event.isKeyDown():
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle and vehicle.isAlive() and vehicle.isWheeledTech and vehicle.typeDescriptor.hasSiegeMode:
                _config.data['autoActivateWheelMode'] = not _config.data['autoActivateWheelMode']
                message = 'Wheel auto boost: %s' % ('ON' if _config.data['autoActivateWheelMode'] else 'OFF')
                inject.message(message, '#8378FC')

    def changeMovement(self):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle and vehicle.isAlive() and vehicle.isWheeledTech and vehicle.typeDescriptor.hasSiegeMode:
            fSpeedLimit, bSpeedLimit = vehicle.typeDescriptor.physics['speedLimits']
            forward, backward, speed = self.getSpeed(fSpeedLimit, bSpeedLimit, vehicle.speedInfo.value[0])
            timer = BigWorld.time()
            if self.timer + 2.0 < timer and vehicle.siegeState == VEHICLE_SIEGE_STATE.ENABLED:
                if -10 <= speed < 0:
                    return self.changeSiege(False)
                if forward - 25 >= speed >= 0:
                    return self.changeSiege(False)

            if self.timer + 2.0 < timer and vehicle.siegeState == VEHICLE_SIEGE_STATE.DISABLED:
                if backward + 10 >= speed:
                    return self.changeSiege(True)
                if forward - 20 <= speed:
                    return self.changeSiege(True)

    def changeSiege(self, status):
        BigWorld.player().base.vehicle_changeSetting(VEHICLE_SETTING.SIEGE_MODE_ENABLED, status)
        self.timer = BigWorld.time()

    def getSpeed(self,fSpeedLimit, bSpeedLimit, speed):
        if not self.limits[0]:
            self.limits = (int(max(min(fSpeedLimit, fSpeedLimit), -bSpeedLimit) * 3.6), -int(max(min(bSpeedLimit, fSpeedLimit), -bSpeedLimit) * 3.6))
        return self.limits[0], self.limits[1], int(max(min(speed, fSpeedLimit), -bSpeedLimit) * 3.6)


    @staticmethod
    def fixSiegeModeCruiseControl():
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        return vehicle and vehicle.isAlive() and vehicle.isWheeledTech and vehicle.typeDescriptor.hasSiegeMode


class Support(object):
    @staticmethod
    @inject.log
    def message():
        inject.message(_config.i18n['UI_battle_activateMessage'])

    def start_battle(self):
        if _config.data['enabled'] and _config.data['activateMessage']:
            BigWorld.callback(5.0, self.message)


# start mod

_config = _Config()
movement_control = MovementControl()
support = Support()


@inject.hook(PlayerAvatar, 'handleKey')
@inject.log
def hookPlayerAvatarHandleKey(func, *args):
    if _config.data['enabled']:
        self, is_down, key, mods = args
        if _config.data['fixAccuracyInMove']:
            movement_control.move_pressed(self, is_down, key)
    return func(*args)


@inject.hook(VehicleGunRotator.VehicleGunRotator, 'setShotPosition')
@inject.log
def hookVehicleGunRotatorSetShotPosition(func, self, vehicleID, shotPos, shotVec, dispersionAngle, forceValueRefresh=False):
    if _config.data['enabled']:
        if _config.data['serverTurret'] and not BigWorld.player().inputHandler.isSPG:
            if self._VehicleGunRotator__clientMode and self._VehicleGunRotator__showServerMarker and not forceValueRefresh:
                forceValueRefresh = True
    return func(self, vehicleID, shotPos, shotVec, dispersionAngle, forceValueRefresh)


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    support.start_battle()
    movement_control.startBattle()

@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
@inject.log
def hookDestroyGUI(func, *args):
    movement_control.endBattle()
    func(*args)


@inject.hook(PlayerAvatar, 'updateVehicleMiscStatus')
@inject.log
def updateVehicleMiscStatus(func, *args):
    if _config.data['enabled']:
        if _config.data['fixWheelCruiseControl']:
            self, vehicleID, code, intArg, floatArgs = args
            if vehicleID != self.playerVehicleID and vehicleID != self.observedVehicleID and vehicleID != self.inputHandler.ctrl.curVehicleID:
                return
            if code == VEHICLE_MISC_STATUS.SIEGE_MODE_STATE_CHANGED and movement_control.fixSiegeModeCruiseControl():
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.SIEGE_MODE, (intArg, floatArgs[0]))
                self._PlayerAvatar__onSiegeStateUpdated(vehicleID, intArg, floatArgs[0])
                return
    return func(*args)
