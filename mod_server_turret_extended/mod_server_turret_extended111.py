# -*- coding: utf-8 -*-
import codecs
import json
import os
import random
import re
import string
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
from gui.app_loader import g_appLoader
from gun_rotation_shared import decodeGunAngles
from helpers import getLanguageCode


class _GUIConfig(object):
    def __init__(self):
        self.gui = {}

    def register(self, name, template_func, settings_dict, apply_func):
        if hasattr(BigWorld, 'mods_gui'):
            # noinspection PyProtectedMember
            self.gui[name] = BigWorld.mods_gui(name, template_func(), settings_dict, apply_func)
            apply_func(self.gui[name].actual_settings)

    def update(self, name, template_func):
        self.gui[name].update_template(template_func())


class _Config(object):
    def __init__(self):
        self.ids = 'server_turret_extended'
        self.version = '1.11 (11.03.2016)'
        self.author = 'by spoter, reven86'
        self.path_config = './res_mods/configs/spoter_mods/%s/' % self.ids
        self.path_lang = '%si18n/' % self.path_config
        self.data = {
            'enabled'             : True,
            'activate_message'    : True,
            'fix_accuracy_in_move': True,
            'server_turret'       : True
        }

        self.i18n = {
            'UI_description'                         : 'Server Turret and Fix Accuracy',
            'UI_setting_activate_message_text'       : 'Show Activation Message',
            'UI_setting_activate_message_tooltip'    : '{HEADER}Info:{/HEADER}{BODY}Show Activation Message in battle{/BODY}',
            'UI_setting_fix_accuracy_in_move_text'   : 'Fix Accuracy',
            'UI_setting_fix_accuracy_in_move_tooltip': '{HEADER}Info:{/HEADER}{BODY}When you tank move and then stop, used fix accuracy to not lost aiming{/BODY}',
            'UI_setting_server_turret_text'          : 'Server Turret',
            'UI_setting_server_turret_tooltip'       : '{HEADER}Info:{/HEADER}{BODY}Move Turret to Server Aim coordinates (need enabled Server Sight in game settings){/BODY}',
            'UI_battle_activate_message'             : '"Muzzle chaos": Activated'
        }

        self.load_lang()
        self.no_gui = False

    def load_lang(self):
        lang = str(getLanguageCode()).lower()
        new_config = self.load_json(lang, self.i18n, self.path_lang)
        for setting in new_config:
            if setting in self.i18n:
                self.i18n[setting] = new_config[setting]

    def template_settings(self):
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

    def apply_settings(self, settings):
        for setting in settings:
            if setting in self.data:
                self.data[setting] = settings[setting]
        _gui_config.update('%s' % self.ids, self.template_settings)

    @staticmethod
    def json_comments(text):
        regex = r'\s*(#|\/{2}).*$'
        regex_inline = r'(:?(?:\s)*([A-Za-z\d\.{}]*)|((?<=\").*\"),?)(?:\s)*(((#|(\/{2})).*)|)$'
        lines = text.split('\n')
        excluded = []
        for index, line in enumerate(lines):
            if re.search(regex, line):
                if re.search(r'^' + regex, line, re.IGNORECASE):
                    excluded.append(lines[index])
                elif re.search(regex_inline, line):
                    lines[index] = re.sub(regex_inline, r'\1', line)
        for line in excluded:
            lines.remove(line)
        return '\n'.join(lines)

    def byte_ify(self, inputs):
        if inputs:
            if isinstance(inputs, dict):
                return {self.byte_ify(key): self.byte_ify(value) for key, value in inputs.iteritems()}
            elif isinstance(inputs, list):
                return [self.byte_ify(element) for element in inputs]
            elif isinstance(inputs, unicode):
                return inputs.encode('utf-8')
            else:
                return inputs
        return inputs

    def load_json(self, name, config_old, path, save=False):
        config_new = config_old
        if not os.path.exists(path):
            os.makedirs(path)
        new_path = '%s%s.json' % (path, name)
        if save:
            with codecs.open(new_path, 'w', encoding='utf-8-sig') as json_file:
                data = json.dumps(config_old, sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig', separators=(',', ': '))
                json_file.write('%s' % self.byte_ify(data))
                json_file.close()
                config_new = config_old
        else:
            if os.path.isfile(new_path):
                try:
                    with codecs.open(new_path, 'r', encoding='utf-8-sig') as json_file:
                        data = self.json_comments(json_file.read().decode('utf-8-sig'))
                        config_new = self.byte_ify(json.loads(data))
                        json_file.close()
                except Exception as e:
                    print '[ERROR]:     %s' % e
            else:
                with codecs.open(new_path, 'w', encoding='utf-8-sig') as json_file:
                    data = json.dumps(config_old, sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig', separators=(',', ': '))
                    json_file.write('%s' % self.byte_ify(data))
                    json_file.close()
                    config_new = config_old
                    print '[ERROR]:     [Not found config, create default: %s' % new_path
        return config_new

    def load(self):
        self.do_config()
        print '[LOAD_MOD]:  [%s v%s, %s]' % (self.ids, self.version, self.author)

    def do_config(self):
        if hasattr(BigWorld, 'mods_gui'):
            _gui_config.register(name='%s' % self.ids, template_func=self.template_settings, settings_dict=self.data, apply_func=self.apply_settings)
        else:
            if not self.no_gui:
                BigWorld.callback(1.0, self.do_config)


class Statistics(object):
    def __init__(self):
        self.analytics_started = False
        self._thread_analytics = None
        self.tid = 'UA-57975916-13'
        self.description_analytics = 'Мод: "Стволик Хаоса"'

    def analytics_do(self):
        if not self.analytics_started:
            player = BigWorld.player()
            param = urllib.urlencode({
                'v'  : 1, # Version.
                'tid': '%s' % self.tid, # Tracking ID / Property ID.
                'cid': player.databaseID, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : '%s' % self.description_analytics, # App name.
                'av' : '%s %s' % (self.description_analytics, _config.version), # App version.
                'cd' : 'start [%s]' % AUTH_REALM                            # Screen name / content description.
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=param).read()
            self.analytics_started = True

    def start(self):
        self._thread_analytics = threading.Thread(target=self.analytics_do, name='Thread')
        self._thread_analytics.start()


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
        self.coll_data = None
        self.lastTime = 0.0
        return

    # noinspection PyProtectedMember
    def calc_marker_pos(self, gun_rotator, shot_pos, shot_vector, dispersion_angle, shot_point):
        if shot_point is None:
            marker_pos, marker_direction, marker_size, ideal_marker_size, coll_data = gun_rotator._VehicleGunRotator__getGunMarkerPosition(shot_pos, shot_vector, gun_rotator._VehicleGunRotator__dispersionAngle)
            gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker2(marker_pos, marker_direction, (marker_size, ideal_marker_size), SERVER_TICK_LENGTH, coll_data)
            gun_rotator._VehicleGunRotator__lastShotPoint = marker_pos
            gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker(marker_pos, marker_direction, (marker_size, ideal_marker_size), SERVER_TICK_LENGTH, coll_data)
            gun_rotator._VehicleGunRotator__markerInfo = (marker_pos, marker_direction, marker_size)
            self.coll_data = coll_data
        else:
            gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker2(shot_point, gun_rotator._VehicleGunRotator__markerInfo[1], gun_rotator._VehicleGunRotator__markerInfo[2], SERVER_TICK_LENGTH, self.coll_data)
            gun_rotator._VehicleGunRotator__lastShotPoint = shot_point
            gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker(shot_point, gun_rotator._VehicleGunRotator__markerInfo[1], gun_rotator._VehicleGunRotator__markerInfo[2], SERVER_TICK_LENGTH, self.coll_data)
            gun_rotator._VehicleGunRotator__markerInfo = (shot_point, gun_rotator._VehicleGunRotator__markerInfo[1], gun_rotator._VehicleGunRotator__markerInfo[2])

        vehicle = BigWorld.entity(gun_rotator._VehicleGunRotator__avatar.playerVehicleID)
        vehicle_descr = vehicle.typeDescriptor

        gun_rotator._VehicleGunRotator__turretYaw, gun_rotator._VehicleGunRotator__gunPitch = decodeGunAngles(vehicle.gunAnglesPacked, vehicle_descr.gun['pitchLimits']['absolute'])
        gun_rotator._VehicleGunRotator__updateTurretMatrix(gun_rotator._VehicleGunRotator__turretYaw, SERVER_TICK_LENGTH)
        gun_rotator._VehicleGunRotator__updateGunMatrix(gun_rotator._VehicleGunRotator__gunPitch, SERVER_TICK_LENGTH)
        self.serverTurretYaw = gun_rotator._VehicleGunRotator__turretYaw
        self.serverGunPitch = gun_rotator._VehicleGunRotator__gunPitch
        self.serverReceiveTime = BigWorld.time()
        return

    def on_set_shot_position(self, gun_rotator, shot_pos, shot_vector, dispersion_angle):
        self.calc_marker_pos(gun_rotator, shot_pos, shot_vector, dispersion_angle, None)
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
def hook_update_all(self):
    hooked_update_all(self)
    try:
        stat.start()
    except Exception as e:
        print('hook_update_all get stat', e)


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
                return gunRotatorMod.on_set_shot_position(self, shot_pos, shot_vector, dispersion_angle)
        except StandardError:
            return hooked_setShotPosition(self, shot_pos, shot_vector, dispersion_angle)
    return hooked_setShotPosition(self, shot_pos, shot_vector, dispersion_angle)


def hook_minimap_start(self):
    hooked_Minimap_start(self)
    support.start_battle()


#start mod
gunRotatorMod = GunRotatorMod()
movement_control = MovementControl()
support = Support()
stat = Statistics()
_gui_config = _GUIConfig()
_config = _Config()
_config.load()

#hooked
# noinspection PyProtectedMember
hooked_update_all = LobbyView._populate
hooked_handleKey = PlayerAvatar.handleKey
hooked_setShotPosition = VehicleGunRotator.VehicleGunRotator.setShotPosition
hooked_Minimap_start = Minimap.Minimap.start

#hook
LobbyView._populate = hook_update_all
PlayerAvatar.handleKey = hook_handle_key
VehicleGunRotator.VehicleGunRotator.setShotPosition = hook_set_shot_position
Minimap.Minimap.start = hook_minimap_start
