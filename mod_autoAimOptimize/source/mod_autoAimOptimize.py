# -*- coding: utf-8 -*-
import math

import Math

import BigWorld
import CommandMapping
from Avatar import PlayerAvatar
from AvatarInputHandler import cameras, control_modes
from gui.app_loader import g_appLoader
from gui.mods.mod_mods_gui import g_gui, inject


class Config(object):
    def __init__(self):
        self.ids = 'autoAimOptimize'
        self.version = 'v1.05 (2018-11-28)'
        self.version_id = 105
        self.author = 'by spoter'
        self.data = {
            'version'          : self.version_id,
            'enabled'          : True,
            'angle'            : 1.3,
            'catchHiddenTarget': True,
            'disableArtyMode'  : True
        }
        self.i18n = {
            'version'                             : self.version_id,
            'UI_description'                      : 'AutoAim Optimize',
            'UI_setting_angle_text'               : 'Set angle to catch target',
            'UI_setting_angle_value'              : '%s' % unichr(176),
            'UI_setting_catchHiddenTarget_text'   : 'Catch target hidden behind an obstacle',
            'UI_setting_catchHiddenTarget_tooltip': '',
            'UI_setting_disableArtyMode_text'     : 'Disable in Arty mode',
            'UI_setting_disableArtyMode_tooltip'  : ''
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
                'type'        : 'Slider',
                'text'        : self.i18n['UI_setting_angle_text'],
                'minimum'     : 0,
                'maximum'     : 90,
                'snapInterval': 0.1,
                'value'       : self.data['angle'],
                'format'      : '{{value}}%s [1.3%s]' % (self.i18n['UI_setting_angle_value'], self.i18n['UI_setting_angle_value']),
                'varName'     : 'angle'
            }],
            'column2'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_catchHiddenTarget_text'],
                'value'  : self.data['catchHiddenTarget'],
                'tooltip': self.i18n['UI_setting_catchHiddenTarget_tooltip'],
                'varName': 'catchHiddenTarget'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_disableArtyMode_text'],
                'value'  : self.data['disableArtyMode'],
                'tooltip': self.i18n['UI_setting_disableArtyMode_tooltip'],
                'varName': 'disableArtyMode'
            }]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class Worked(object):
    def __init__(self):
        self.player = None
        self.angle = math.radians(config.data['angle'])

    def startBattle(self):
        self.player = BigWorld.player()
        self.angle = math.radians(config.data['angle'])

    def catch(self):
        # noinspection PyProtectedMember
        if self.player._PlayerAvatar__autoAimVehID: return
        if BigWorld.target() is not None: return
        if self.player.isObserver(): return
        playerPosition = self.player.getOwnVehiclePosition()
        minRadian = 100000.0
        result = None
        result_len = None
        for vId, vData in self.player.arena.vehicles.iteritems():
            if vData['team'] != self.player.team and vData['isAlive']:
                vehicle = BigWorld.entity(vId)
                if vehicle is not None and vehicle.isStarted and vehicle.isAlive():
                    radian = self.calc_radian(vehicle.position, self.angle)  # 1.289 градуса в радианах
                    if radian:
                        length = Math.Vector3(vehicle.position - playerPosition).length
                        if result_len is None:
                            result_len = length
                            result = vehicle
                        if radian < minRadian and result_len >= length:
                            minRadian = radian
                            result = vehicle
        if config.data['catchHiddenTarget']:
            self.player.autoAim(result)
            return result if result is not None else None
        if result is not None and BigWorld.wg_collideSegment(self.player.spaceID, result.position, cameras.getWorldRayAndPoint(0, 0)[1], 128) is None:
            self.player.autoAim(result)
            return result if result is not None else None
        return

    # рассчёт угла видимости от камеры до противника
    @staticmethod
    def calc_radian(target_position, angle):
        cameraDir, cameraPos = cameras.getWorldRayAndPoint(0, 0)
        cameraDir.normalise()
        cameraToTarget = target_position - cameraPos
        dot = cameraToTarget.dot(cameraDir)
        if dot < 0: return
        targetRadian = cameraToTarget.lengthSquared
        radian = 1.0 - dot * dot / targetRadian
        if radian > angle: return
        return radian

    @inject.log
    def injectButton(self, isDown, key):
        if config.data['enabled'] and self.player is not None:
            if g_appLoader.getDefBattleApp():
                if CommandMapping.g_instance.isFired(CommandMapping.CMD_CM_LOCK_TARGET, key) and isDown:
                    return self.catch()
        return


config = Config()
mod = Worked()


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    mod.startBattle()


@inject.hook(control_modes.SniperControlMode, 'handleKeyEvent')
@inject.log
def hookKeyEventSniper(func, *args):
    if mod.injectButton(args[1], args[2]):
        return True
    func(*args)


@inject.hook(control_modes.StrategicControlMode, 'handleKeyEvent')
@inject.log
def hookKeyEventStrategic(func, *args):
    if not config.data['disableArtyMode'] and mod.injectButton(args[1], args[2]):
        return True
    func(*args)


@inject.hook(control_modes.ArtyControlMode, 'handleKeyEvent')
@inject.log
def hookKeyEventArty(func, *args):
    if not config.data['disableArtyMode'] and mod.injectButton(args[1], args[2]):
        return True
    func(*args)


@inject.hook(control_modes.ArcadeControlMode, 'handleKeyEvent')
@inject.log
def hookKeyEventArcade(func, *args):
    if mod.injectButton(args[1], args[2]):
        return True
    func(*args)
