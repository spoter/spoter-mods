# -*- coding: utf-8 -*-

import math

import BigWorld
import CommandMapping
import Keys
import VehicleGunRotator
import gun_rotation_shared
from Avatar import PlayerAvatar, _MOVEMENT_FLAGS as MOVEMENT_FLAGS
from constants import VEHICLE_MISC_STATUS, VEHICLE_SETTING, VEHICLE_SIEGE_STATE
from gui import InputHandler
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject


class _Config(object):
    def __init__(self):
        self.ids = 'serverTurretExtended'
        self.version = 'v3.01 (2020-06-01)'
        self.version_id = 301
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
            'autoActivateWheelMode': False,
            'buttonAutoMode'       : self.buttons['buttonAutoMode'],

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
            'UI_setting_autoActivateWheelMode_text'   : 'Activate\\deactivate Max Wheel mode',
            'UI_setting_autoActivateWheelMode_tooltip': '{HEADER}Info:{/HEADER}{BODY}Try automate Max wheel mode{/BODY}',
            'UI_setting_buttonAutoMode_text'          : 'Button: Max Wheel mode',
            'UI_setting_buttonAutoMode_tooltip'       : '{HEADER}Info:{/HEADER}{BODY}Button: Max Wheel mode enable or disable{/BODY}',
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

    @staticmethod
    def move_pressed(avatar, is_down, key):
        if CommandMapping.g_instance.isFiredList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD, CommandMapping.CMD_ROTATE_LEFT, CommandMapping.CMD_ROTATE_RIGHT), key):
            avatar.moveVehicle(0, is_down)

    def startBattle(self):
        InputHandler.g_instance.onKeyDown += self.keyPressed
        InputHandler.g_instance.onKeyUp += self.keyPressed
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
        if _config.data['enabled']:
            self.changeMovement()
        self.callback = BigWorld.callback(0.1, self.onCallback)

    @staticmethod
    def keyPressed(event):
        if not _config.data['enabled']: return
        if g_gui.get_key(_config.data['buttonAutoMode']) and event.isKeyDown():
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle and vehicle.isAlive() and vehicle.isWheeledTech and vehicle.typeDescriptor.hasSiegeMode:
                _config.data['autoActivateWheelMode'] = not _config.data['autoActivateWheelMode']
                message = 'Wheel Max Mode: %s' % ('ON' if _config.data['autoActivateWheelMode'] else 'OFF')
                inject.message(message, '#8378FC')

    def changeMovement(self):
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        if vehicle and vehicle.isAlive() and vehicle.isWheeledTech and vehicle.typeDescriptor.hasSiegeMode:
            flags = player.makeVehicleMovementCommandByKeys()
            if vehicle.siegeState == VEHICLE_SIEGE_STATE.DISABLED:
                if player._PlayerAvatar__cruiseControlMode:
                    return self.changeSiege(True)
                if flags & MOVEMENT_FLAGS.ROTATE_RIGHT or flags & MOVEMENT_FLAGS.ROTATE_LEFT or flags & MOVEMENT_FLAGS.BLOCK_TRACKS:
                    return
                if flags & MOVEMENT_FLAGS.FORWARD:
                    return self.changeSiege(True)
                if flags & MOVEMENT_FLAGS.BACKWARD:
                    return self.changeSiege(True)
            if vehicle.siegeState == VEHICLE_SIEGE_STATE.ENABLED:
                if not player._PlayerAvatar__cruiseControlMode:
                    realSpeed = int(vehicle.speedInfo.value[0] * 3.6)
                    checkSpeedLimits = self.checkSpeedLimits(vehicle, realSpeed)
                    if flags & MOVEMENT_FLAGS.ROTATE_RIGHT and checkSpeedLimits:
                        return self.changeSiege(False)
                    if flags & MOVEMENT_FLAGS.ROTATE_LEFT and checkSpeedLimits:
                        return self.changeSiege(False)
                    if flags & MOVEMENT_FLAGS.BLOCK_TRACKS:
                        return self.changeSiege(False)
                    if 20 > realSpeed > -20:
                        if not CommandMapping.g_instance.isActiveList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD)):
                            return self.changeSiege(False)
                        if realSpeed < 0 and flags & MOVEMENT_FLAGS.FORWARD:
                            return self.changeSiege(False)
                        if realSpeed > 0 and flags & MOVEMENT_FLAGS.BACKWARD:
                            return self.changeSiege(False)

    def changeSiege(self, status):
        BigWorld.player().base.vehicle_changeSetting(VEHICLE_SETTING.SIEGE_MODE_ENABLED, status)
        self.timer = BigWorld.time()

    @staticmethod
    def checkSpeedLimits(vehicle, speed):
        if not _config.data['autoActivateWheelMode']:
            return True
        speedLimits = vehicle.typeDescriptor.defaultVehicleDescr.physics['speedLimits']
        return  int(speedLimits[0] * 3.6) > speed > -int(speedLimits[1] * 3.6)

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


def decodeRestrictedValueFromUint(code, bits, minBound, maxBound):
    code -= 0.5
    t = float(code) / ((1 << bits) - 1)
    return minBound + t * (maxBound - minBound)


def decodeAngleFromUint(code, bits):
    code -= 0.5
    return math.pi * 2.0 * code / (1 << bits) - math.pi


gun_rotation_shared.decodeRestrictedValueFromUint = decodeRestrictedValueFromUint
gun_rotation_shared.decodeAngleFromUint = decodeAngleFromUint
