# -*- coding: utf-8 -*-
import threading
import urllib
import urllib2

import BigWorld

import CommandMapping
import VehicleGunRotator
from Avatar import PlayerAvatar
from constants import AUTH_REALM
from constants import SERVER_TICK_LENGTH
from gui.Scaleform import Minimap
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.mods.mod_mods_gui import g_gui, inject
from gun_rotation_shared import decodeGunAngles
from helpers import getLanguageCode

class _Config(object):
    def __init__(self):
        self.ids = 'server_turret_extended'
        self.version = '1.14 (02.08.2016)'
        self.version_id = 113
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
        self.data = g_gui.update_data(self.ids, settings)
        g_gui.update(self.ids, self.template)

    def load(self):
        self.do_config()
        print '[LOAD_MOD]:  [%s v%s, %s]' % (self.ids, self.version, self.author)

    @inject.log
    def do_config(self):
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n)
        g_gui.register(self.ids, self.template, self.data, self.apply)

class Statistics(object):
    def __init__(self):
        self.analytics_started = False
        self.thread_analytics = None
        self.user = None
        self.old_user = None

    @inject.log
    def analytics_start(self):
        if not self.analytics_started:
            lang = str(getLanguageCode()).upper()
            param = urllib.urlencode({
                'v'  : 1, # Version.
                'tid': 'UA-57975916-13',
                'cid': self.user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Стволик Хаоса"', # App name.
                'av' : 'Мод: "Стволик Хаоса" %s' % _config.version,
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, lang), # Screen name / content description.
                'ul' : '%s' % lang,
                'sc' : 'start'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=param).read()
            self.analytics_started = True
            self.old_user = BigWorld.player().databaseID

    def start(self):
        player = BigWorld.player()
        if self.user and self.user != player.databaseID:
            self.old_user = player.databaseID
            self.thread_analytics = threading.Thread(target=self.end, name='Thread')
            self.thread_analytics.start()
        self.user = player.databaseID
        self.thread_analytics = threading.Thread(target=self.analytics_start, name='Thread')
        self.thread_analytics.start()

    @inject.log
    def end(self):
        if self.analytics_started:
            lang = str(getLanguageCode()).upper()
            param = urllib.urlencode({
                'v'  : 1, # Version.
                'tid': 'UA-57975916-13',
                'cid': self.old_user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Стволик Хаоса"', # App name.
                'av' : 'Мод: "Стволик Хаоса" %s' % _config.version,
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, lang), # Screen name / content description.
                'ul' : '%s' % lang,
                'sc' : 'end'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=param).read()
            self.analytics_started = False

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
        marker_pos, marker_direction, marker_size, ideal_marker_size, coll_data = gun_rotator._VehicleGunRotator__getGunMarkerPosition(shot_pos, shot_vector, gun_rotator._VehicleGunRotator__dispersionAngles)
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
    @inject.log
    def message():
        inject.message(_config.i18n['UI_battle_activate_message'])

    def start_battle(self):
        if _config.data['enabled'] and _config.data['activate_message']:
            BigWorld.callback(5.0, self.message)

#start mod

_config = _Config()
stat = Statistics()
gunRotatorMod = GunRotatorMod()
movement_control = MovementControl()
support = Support()

@inject.log
def init():
    _config.load()

@inject.log
def fini():
    stat.end()

@inject.hook(LobbyView, '_populate')
@inject.log
def hookLobbyViewPopulate(func, *args):
    func(*args)
    stat.start()

@inject.hook(PlayerAvatar, 'handleKey')
@inject.log
def hookPlayerAvatarHandleKey(func, *args):
    if _config.data['enabled'] and _config.data['fix_accuracy_in_move']:
        self, is_down, key, mods = args
        movement_control.move_pressed(self, is_down, key)
    return func(*args)

@inject.hook(VehicleGunRotator.VehicleGunRotator, 'setShotPosition')
@inject.log
def hookVehicleGunRotatorSetShotPosition(func, *args):
    if _config.data['enabled'] and _config.data['server_turret'] and not BigWorld.player().inputHandler.isSPG:
        try:
            self, shot_pos, shot_vector, dispersion_angle = args
            self._VehicleGunRotator__dispersionAngles[0] = dispersion_angle
            gunRotatorMod.blockGunRotator = self._VehicleGunRotator__clientMode and self._VehicleGunRotator__showServerMarker
            if gunRotatorMod.blockGunRotator:
                return gunRotatorMod.calc_marker_pos(self, shot_pos, shot_vector)
        except StandardError:
            pass
    return func(*args)

@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    support.start_battle()
