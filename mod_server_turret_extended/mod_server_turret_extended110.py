# -*- coding: utf-8 -*-
import datetime
import re
import random
import string
import os
import json
import codecs
import urllib2
import urllib
import threading

import BigWorld
import CommandMapping
import VehicleGunRotator
from gui.app_loader import g_appLoader
from gun_rotation_shared import decodeGunAngles
from constants import AUTH_REALM, SERVER_TICK_LENGTH
from gui.Scaleform import Minimap
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from Avatar import PlayerAvatar


class Config(object):
    def __init__(self):
        self.enable = True
        self.debug = False
        self.ru = True if 'RU' in AUTH_REALM else False
        self.version = 'v1.10(18.11.2015)'
        self.author = 'by spoter, reven86'
        self.description = 'Mod: "Muzzle chaos"'
        self.description_ru = 'Мод: "Стволик Хаоса"'
        self.author_ru = 'авторы: spoter, reven86'
        self.name = 'server_turret_extended'
        self.description_analytics = 'Mod: "Muzzle chaos"'
        self.tid = 'UA-57975916-13'
        self.sys_mes = {}
        self.setup = {'MODIFIER': {'MODIFIER_NONE': 0, 'MODIFIER_SHIFT': 1, 'MODIFIER_CTRL': 2, 'MODIFIER_ALT': 4}}
        self._thread_analytics = None
        self.analytics_started = False
        self.language = None
        self.xvm_installed = False
        self.xvm_check()
        self.res_mods = self.res_mods_init()
        self.data = {}
        self.default_config()

        new_config = self.load_json(self.name, self.data)
        self.data = new_config
        if 'Русский' in self.data['config'].get('language'): self.ru = True
        if self.ru:
            self.description = self.description_ru
            self.author = self.author_ru

    @staticmethod
    def res_mods_init():
        wd = os.path.dirname(os.path.realpath(__file__))
        wd = wd[0:wd.rfind('\\')]
        wd = wd[0:wd.rfind('\\')]
        wd = wd[0:wd.rfind('\\')]
        return wd

    def xvm_check(self):
        try:
            import xvm_main
            self.xvm_installed = True
        except StandardError:
            pass

    def default_config(self):
        self.data = {
            'config': {
                'enable': True, 'debug': False, 'activate_message': True, 'fix_gun_for_serverCross': True, 'fix_turret_for_serverCross': True, 'fix_accuracy_in_move': True, 'language': 'Русский'
            }, 'language': {
                'Русский': {
                    'activate_message': '"Стволик Хаоса": Активирован'
                }, 'English': {
                    'activate_message': '"Muzzle chaos": Activated'

                }, 'Deutsch': {
                    'activate_message': '"Muzzle chaos": Aktiviert'
                }
            }
        }

    def do_config(self):
        self.enable = self.data['config'].get('enable', False)
        self.debug = self.data['config'].get('debug', False)
        if self.data['config'].get('language') in self.data['language']:
            self.language = self.data['language'].get(self.data['config'].get('language'))
        else:
            self.data['config']['language'] = 'English'
            self.language = self.data['language'].get('English')

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

    def load_json(self, name, config_old, save=False):
        config_new = config_old
        path = './res_mods/configs/spoter_mods/%s/' % self.name
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
                    self.sys_mess()
                    print '%s%s' % (self.sys_mes['ERROR'], e)

            else:
                self.sys_mess()
                print '%s[%s, %s %s]' % (self.sys_mes['ERROR'], self.code_pa(self.description), self.version, self.sys_mes['MSG_RECREATE_CONFIG'])
                with codecs.open(new_path, 'w', encoding='utf-8-sig') as json_file:
                    data = json.dumps(config_old, sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig', separators=(',', ': '))
                    json_file.write('%s' % self.byte_ify(data))
                    json_file.close()
                    config_new = config_old
                print '%s[%s, %s %s]' % (self.sys_mes['INFO'], self.code_pa(self.description), self.version, self.sys_mes['MSG_RECREATE_CONFIG_DONE'])
        return config_new

    @staticmethod
    def code_pa(text):
        try:
            return text.encode('windows-1251')
        except StandardError:
            return text

    def debugs(self, text):
        if self.debug:
            try:
                text = text.encode('windows-1251')
            except StandardError:
                pass
            print '%s%s [%s]: %s' % (datetime.datetime.now(), self.sys_mes['DEBUG'], self.code_pa(self.description), text)

    def analytics_do(self):
        if not self.analytics_started:
            player = BigWorld.player()
            param = urllib.urlencode({
                'v': 1, # Version.
                'tid': '%s' % self.tid, # Tracking ID / Property ID.
                'cid': player.databaseID, # Anonymous Client ID.
                't': 'screenview', # Screenview hit type.
                'an': '%s' % self.description_analytics, # App name.
                'av': '%s %s' % (self.description_analytics, self.version), # App version.
                'cd': 'start [%s]' % AUTH_REALM                            # Screen name / content description.
            })
            self.debugs('http://www.google-analytics.com/collect?%s' % param)
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=param).read()
            self.analytics_started = True

    def analytics(self):
        self._thread_analytics = threading.Thread(target=self.analytics_do, name='Thread')
        self._thread_analytics.start()

    def sys_mess(self):
        self.sys_mes = {
            'DEBUG': '[DEBUG]', 'LOAD_MOD': self.code_pa('[ЗАГРУЗКА]:  ') if self.ru else '[LOAD_MOD]:  ', 'INFO': self.code_pa('[ИНФО]:      ') if self.ru else '[INFO]:      ',
            'ERROR': self.code_pa('[ОШИБКА]:    ') if self.ru else '[ERROR]:     ',
            'MSG_RECREATE_CONFIG': self.code_pa('конфиг не найден, создаем заново') if self.ru else 'Config not found, recreating',
            'MSG_RECREATE_CONFIG_DONE': self.code_pa('конфиг создан УСПЕШНО') if self.ru else 'Config recreating DONE',
            'MSG_INIT': self.code_pa('применение настроек...') if self.ru else 'initialized ...', 'MSG_LANGUAGE_SET': self.code_pa('Выбран язык:') if self.ru else 'Language set to:',
            'MSG_DISABLED': self.code_pa('отключен ...') if self.ru else 'disabled ...'
        }

    def load_mod(self):
        self.do_config()
        self.sys_mess()
        print ''
        print '%s[%s, %s]' % (self.sys_mes['LOAD_MOD'], self.code_pa(self.description), self.code_pa(self.author))
        if self.enable:
            self.debugs('Debug Activated ...')
            print '%s[%s %s %s...]' % (self.sys_mes['INFO'], self.code_pa(self.description), self.sys_mes['MSG_LANGUAGE_SET'], self.code_pa(self.data['config'].get('language')))
            print '%s[%s, %s %s]' % (self.sys_mes['INFO'], self.code_pa(self.description), self.version, self.sys_mes['MSG_INIT'])
        else:
            print '%s[%s, %s %s]' % (self.sys_mes['INFO'], self.code_pa(self.description), self.version, self.sys_mes['MSG_DISABLED'])
        print ''


class MovementControl(object):
    @staticmethod
    def move_pressed(avatar, is_down, key):
        if CommandMapping.g_instance.isFiredList(
                (CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD, CommandMapping.CMD_ROTATE_LEFT, CommandMapping.CMD_ROTATE_RIGHT), key):
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
        gun_rotator._VehicleGunRotator__dispersionAngle = dispersion_angle
        if shot_point is None:
            marker_pos, marker_direction, marker_size, coll_data = gun_rotator._VehicleGunRotator__getGunMarkerPosition(shot_pos, shot_vector, dispersion_angle)
            gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker2(marker_pos, marker_direction, marker_size, SERVER_TICK_LENGTH, coll_data)
            gun_rotator._VehicleGunRotator__lastShotPoint = marker_pos
            gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker(marker_pos, marker_direction, marker_size, SERVER_TICK_LENGTH, coll_data)
            gun_rotator._VehicleGunRotator__markerInfo = (marker_pos, marker_direction, marker_size)
            self.coll_data = coll_data
        else:
            gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker2(shot_point, gun_rotator._VehicleGunRotator__markerInfo[1], gun_rotator._VehicleGunRotator__markerInfo[2],
                SERVER_TICK_LENGTH, self.coll_data)
            gun_rotator._VehicleGunRotator__lastShotPoint = shot_point
            gun_rotator._VehicleGunRotator__avatar.inputHandler.updateGunMarker(shot_point, gun_rotator._VehicleGunRotator__markerInfo[1], gun_rotator._VehicleGunRotator__markerInfo[2],
                SERVER_TICK_LENGTH, self.coll_data)
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
    def message(status=None):
        app = g_appLoader.getDefBattleApp()
        if status: app.call('battle.PlayerMessagesPanel.ShowMessage',
            [config.language[status] + random.choice(string.ascii_letters), config.language[status].decode('utf-8-sig'), 'gold'])
        else: app.call('battle.PlayerMessagesPanel.ShowMessage',
            [config.language['activate_message'] + random.choice(string.ascii_letters), config.language['activate_message'].decode('utf-8-sig'), 'gold'])

    def start_battle(self):
        if not config.enable: return
        if config.data['config'].get('activate_message'):
            BigWorld.callback(5.0, self.message)


# deformed functions:
def hook_update_all(self):
    hooked_update_all(self)
    config.analytics()


def hook_handle_key(self, is_down, key, mods):
    if config.enable and config.data['config'].get('fix_accuracy_in_move'):
        movement_control.move_pressed(self, is_down, key)
    return hooked_handleKey(self, is_down, key, mods)


def hook_set_shot_position(self, shot_pos, shot_vector, dispersion_angle):
    if config.enable and 'strategic' not in BigWorld.player().inputHandler.aim.mode:
        self._VehicleGunRotator__dispersionAngle = dispersion_angle
        gunRotatorMod.blockGunRotator = self._VehicleGunRotator__clientMode and self._VehicleGunRotator__showServerMarker
        if gunRotatorMod.blockGunRotator:
            return gunRotatorMod.on_set_shot_position(self, shot_pos, shot_vector, dispersion_angle)
    return hooked_setShotPosition(self, shot_pos, shot_vector, dispersion_angle)


def hook_minimap_start(self):
    hooked_Minimap_start(self)
    support.start_battle()


#start mod
gunRotatorMod = GunRotatorMod()
movement_control = MovementControl()
support = Support()
config = Config()
config.load_mod()

#hooked
# noinspection PyProtectedMember
hooked_update_all = Hangar._Hangar__updateAll
hooked_handleKey = PlayerAvatar.handleKey
hooked_setShotPosition = VehicleGunRotator.VehicleGunRotator.setShotPosition
hooked_Minimap_start = Minimap.Minimap.start

#hook
# noinspection PyProtectedMember
Hangar._Hangar__updateAll = hook_update_all
PlayerAvatar.handleKey = hook_handle_key
VehicleGunRotator.VehicleGunRotator.setShotPosition = hook_set_shot_position
Minimap.Minimap.start = hook_minimap_start
