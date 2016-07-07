# -*- coding: utf-8 -*-
import random
import string
import threading
import traceback
import urllib
import urllib2

import BigWorld

import CommandMapping
import VehicleGunRotator
import game
from Avatar import PlayerAvatar
from constants import AUTH_REALM
from constants import SERVER_TICK_LENGTH
from gui.Scaleform import Minimap
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.app_loader import g_appLoader
from gun_rotation_shared import decodeGunAngles
from helpers import getLanguageCode

SHOW_DEBUG = False
mod_mods_gui = None
try:
    from gui.mods import mod_mods_gui
except StandardError:
    traceback.print_exc()


def log(*args):
    if SHOW_DEBUG:
        msg = 'DEBUG[%s]: ' % _config.ids
        length = len(args)
        for text in args:
            length -= 1
            if length:
                msg += '%s, ' % text
            else:
                msg += '%s' % text
        print msg


class _Config(object):
    def __init__(self):
        self.ids = 'server_turret_extended'
        self.version = '1.12 (01.07.2016)'
        self.version_id = 112
        self.author = 'by spoter, reven86'
        self.data = {
            'version'             : self.version_id,
            'enabled'             : True,
            'activate_message'    : False,
            'fix_accuracy_in_move': True,
            'server_turret'       : True
        }
        self.i18n = {
            'version'                                : self.version_id,
            'UI_description'                         : 'Server Turret and Fix Accuracy',
            'UI_setting_activate_message_text'       : 'Show Activation Message',
            'UI_setting_activate_message_tooltip'    : '{HEADER}Info:{/HEADER}{BODY}Show Activation Message in battle{/BODY}',
            'UI_setting_fix_accuracy_in_move_text'   : 'Fix Accuracy',
            'UI_setting_fix_accuracy_in_move_tooltip': '{HEADER}Info:{/HEADER}{BODY}When you tank move and then stop, used fix accuracy to not lost aiming{/BODY}',
            'UI_setting_server_turret_text'          : 'Server Turret',
            'UI_setting_server_turret_tooltip'       : '{HEADER}Info:{/HEADER}{BODY}Move Turret to Server Aim coordinates (need enabled Server Sight in game settings){/BODY}',
            'UI_battle_activate_message'             : '"Muzzle chaos": Activated'
        }

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': 200,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_server_turret_text'],
                'value'  : self.data['server_turret'],
                'tooltip': self.i18n['UI_setting_server_turret_tooltip'],
                'varName': 'server_turret'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_fix_accuracy_in_move_text'],
                'value'  : self.data['fix_accuracy_in_move'],
                'tooltip': self.i18n['UI_setting_fix_accuracy_in_move_tooltip'],
                'varName': 'fix_accuracy_in_move'
            }],
            'column2'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_activate_message_text'],
                'value'  : self.data['activate_message'],
                'tooltip': self.i18n['UI_setting_activate_message_tooltip'],
                'varName': 'activate_message'
            }]
        }

    def apply(self, settings):
        self.data = mod_mods_gui.g_gui.update_data(self.ids, settings)
        mod_mods_gui.g_gui.update(self.ids, self.template)

    def load(self):
        self.do_config()
        print '[LOAD_MOD]:  [%s v%s, %s]' % (self.ids, self.version, self.author)

    def do_config(self):
        if mod_mods_gui:
            self.data, self.i18n = mod_mods_gui.g_gui.register_data(self.ids, self.data, self.i18n)
            mod_mods_gui.g_gui.register(self.ids, self.template, self.data, self.apply)
            return
        BigWorld.callback(1.0, self.do_config)


class Statistics(object):
    def __init__(self):
        self.p__analytics_started = False
        self.p__thread_analytics = None
        self.p__user = None
        self.p__old_user = None

    def p__analytics_start(self):
        if not self.p__analytics_started:
            p__lang = str(getLanguageCode()).upper()
            p__param = urllib.urlencode({
                'v'  : 1, # Version.
                'tid': 'UA-57975916-13',
                'cid': self.p__user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Стволик Хаоса"', # App name.
                'av' : 'Мод: "Стволик Хаоса" %s' % _config.version,
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, p__lang), # Screen name / content description.
                'ul' : '%s' % p__lang,
                'sc' : 'start'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=p__param).read()
            self.p__analytics_started = True
            self.p__old_user = BigWorld.player().databaseID

    def p__start(self):
        p__player = BigWorld.player()
        if self.p__user and self.p__user != p__player.databaseID:
            self.p__old_user = p__player.databaseID
            self.p__thread_analytics = threading.Thread(target=self.p__end, name='Thread')
            self.p__thread_analytics.start()
        self.p__user = p__player.databaseID
        self.p__thread_analytics = threading.Thread(target=self.p__analytics_start, name='Thread')
        self.p__thread_analytics.start()

    def p__end(self):
        if self.p__analytics_started:
            p__lang = str(getLanguageCode()).upper()
            p__param = urllib.urlencode({
                'v'  : 1, # Version.
                'tid': 'UA-57975916-13',
                'cid': self.p__old_user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Стволик Хаоса"', # App name.
                'av' : 'Мод: "Стволик Хаоса" %s' % _config.version,
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, p__lang), # Screen name / content description.
                'ul' : '%s' % p__lang,
                'sc' : 'end'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=p__param).read()
            self.p__analytics_started = False


class MovementControl(object):
    @staticmethod
    def move_pressed(avatar, is_down, key):
        if CommandMapping.g_instance.isFiredList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD, CommandMapping.CMD_ROTATE_LEFT, CommandMapping.CMD_ROTATE_RIGHT), key):
            avatar.moveVehicle(0, is_down)


class GunRotatorMod:
    def __init__(self):
        self.blockGunRotator = False
        self.serverTurretYaw = 0.0
        self.serverGunPitch = 0.0
        self.serverReceiveTime = 0.0
        self.lastTime = 0.0
        return

    # noinspection PyProtectedMember
    def calc_marker_pos(self, gun_rotator, shot_pos, shot_vector):
        marker_pos, marker_direction, marker_size, ideal_marker_size, coll_data = gun_rotator._VehicleGunRotator__getGunMarkerPosition(shot_pos, shot_vector, gun_rotator._VehicleGunRotator__dispersionAngle)
        gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker2(marker_pos, marker_direction, (marker_size, ideal_marker_size), SERVER_TICK_LENGTH, coll_data)
        gun_rotator._VehicleGunRotator__lastShotPoint = marker_pos
        gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker(marker_pos, marker_direction, (marker_size, ideal_marker_size), SERVER_TICK_LENGTH, coll_data)
        gun_rotator._VehicleGunRotator__markerInfo = (marker_pos, marker_direction, marker_size)

        vehicle = BigWorld.entity(gun_rotator._VehicleGunRotator__avatar.playerVehicleID)
        vehicle_descr = vehicle.typeDescriptor

        gun_rotator._VehicleGunRotator__turretYaw, gun_rotator._VehicleGunRotator__gunPitch = decodeGunAngles(vehicle.gunAnglesPacked, vehicle_descr.gun['pitchLimits']['absolute'])
        gun_rotator._VehicleGunRotator__updateTurretMatrix(gun_rotator._VehicleGunRotator__turretYaw, SERVER_TICK_LENGTH)
        gun_rotator._VehicleGunRotator__updateGunMatrix(gun_rotator._VehicleGunRotator__gunPitch, SERVER_TICK_LENGTH)
        self.serverTurretYaw = gun_rotator._VehicleGunRotator__turretYaw
        self.serverGunPitch = gun_rotator._VehicleGunRotator__gunPitch
        self.serverReceiveTime = BigWorld.time()
        return

class Support(object):
    @staticmethod
    def message():
        app = g_appLoader.getDefBattleApp()
        if app is not None:
            app.call('battle.PlayerMessagesPanel.ShowMessage', [_config.i18n['UI_battle_activate_message'] + random.choice(string.ascii_letters), _config.i18n['UI_battle_activate_message'].decode('utf-8-sig'), 'gold'])

    def start_battle(self):
        if not _config.data['enabled']: return
        if _config.data['activate_message']:
            BigWorld.callback(5.0, self.message)


# deformed functions:
def hook_update_all(*args):
    hooked_update_all(*args)
    try:
        p__stat.p__start()
    except Exception as e:
        if SHOW_DEBUG:
            log('hook_update_all', e)
            traceback.print_exc()


def hook_fini():
    try:
        p__stat.p__end()
    except Exception as e:
        if SHOW_DEBUG:
            log('hook_fini', e)
            traceback.print_exc()
    hooked_fini()


def hook_handle_key(self, is_down, key, mods):
    if _config.data['enabled'] and _config.data['fix_accuracy_in_move']:
        movement_control.move_pressed(self, is_down, key)
    return hooked_handleKey(self, is_down, key, mods)


def hook_set_shot_position(self, shot_pos, shot_vector, dispersion_angle):
    if _config.data['enabled'] and _config.data['server_turret'] and 'strategic' not in BigWorld.player().inputHandler.aim.mode:
        try:
            self._VehicleGunRotator__dispersionAngle[0] = dispersion_angle
            gunRotatorMod.blockGunRotator = self._VehicleGunRotator__clientMode and self._VehicleGunRotator__showServerMarker
            if gunRotatorMod.blockGunRotator:
                return gunRotatorMod.calc_marker_pos(self, shot_pos, shot_vector)
        except StandardError:
            return hooked_setShotPosition(self, shot_pos, shot_vector, dispersion_angle)
    return hooked_setShotPosition(self, shot_pos, shot_vector, dispersion_angle)


def hook_minimap_start(self):
    hooked_Minimap_start(self)
    support.start_battle()


#start mod
_config = _Config()
_config.load()
p__stat = Statistics()
gunRotatorMod = GunRotatorMod()
movement_control = MovementControl()
support = Support()

#hooked
# noinspection PyProtectedMember
hooked_update_all = LobbyView._populate
hooked_fini = game.fini
hooked_handleKey = PlayerAvatar.handleKey
hooked_setShotPosition = VehicleGunRotator.VehicleGunRotator.setShotPosition
hooked_Minimap_start = Minimap.Minimap.start

#hook
LobbyView._populate = hook_update_all
game.fini = hook_fini
PlayerAvatar.handleKey = hook_handle_key
VehicleGunRotator.VehicleGunRotator.setShotPosition = hook_set_shot_position
Minimap.Minimap.start = hook_minimap_start
