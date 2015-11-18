# -*- coding: utf-8 -*-
import datetime
import re
import os
import json
import codecs
import urllib2
import urllib
import threading

from tutorial.control.battle.functional import IDirectionIndicator
from Avatar import PlayerAvatar
from constants import AUTH_REALM
import BigWorld
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.battle_control import g_sessionProvider
from gui import DEPTH_OF_Aim
from gui.Scaleform.Flash import Flash
from gui.Scaleform.Battle import Battle
# noinspection PyUnresolvedReferences
from Math import Vector3, Matrix


class Config(object):
    def __init__(self):
        self.enable = True
        self.debug = False
        self.ru = True if 'RU' in AUTH_REALM else False
        self.version = 'v1.15(18.11.2015)'
        self.author = 'by spoter, Thx to Lp()rtii'
        self.description = 'dir_indicator_extended'
        self.description_ru = 'Мод: "Тылы"'
        self.author_ru = 'автор: spoter, спасибо! Lp()rtii'
        self.name = 'dir_indicator_extended'
        self.description_analytics = 'Мод: "Тылы"'
        self.tid = 'UA-57975916-14'
        self.setup = {'MODIFIER': {'MODIFIER_NONE': 0, 'MODIFIER_SHIFT': 1, 'MODIFIER_CTRL': 2, 'MODIFIER_ALT': 4}}
        self.sys_mes = {}
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
            # 
            import xvm_main
            self.xvm_installed = True
        except StandardError:
            pass

    def default_config(self):
        self.data = {
            'config': {
                'enable': True, 'debug': False, 'primary_indication': True, 'secondary_indication': True, 'max_distance_primary_indication': 150, 'max_distance_secondary_indication': 707,
                'strategic_fear_mode': False, 'red_to_purple_indication': True, 'distance_indicator': True, 'tank_name_indicator': True, 'language': 'Русский'
            }, 'language': {'Русский': {}, 'English': {}}
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


class CustomFlash(Flash, IDirectionIndicator):
    __SWF_FILE_NAME = 'dir_indicator_extended.swf'
    __FLASH_CLASS = 'WGDirectionIndicatorFlash'
    __FLASH_MC_NAME = 'directionalIndicatorMc'
    __FLASH_SIZE = (680, 680)

    def __init__(self):
        Flash.__init__(self, self.__SWF_FILE_NAME, self.__FLASH_CLASS, [self.__FLASH_MC_NAME]) #, self.__FLASH_PATH)
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.movie.scaleMode = 'NoScale'
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.flashSize = self.__FLASH_SIZE
        self.component.relativeRadius = 0.5
        self.__dObject = getattr(self.movie, self.__FLASH_MC_NAME, None)
        return

    def set_shape(self, shape):
        if self.__dObject:
            self.__dObject.setShape(shape)

    def set_distance(self, distance):
        if self.__dObject:
            self.__dObject.setDistance(distance)

    def set_vehicle_name(self, vehicle_name):
        if self.__dObject:
            self.__dObject.setVName(vehicle_name)

    def track(self, position):
        if not self.component.visible:
            self.active(True)
            self.component.visible = True
        self.component.position3D = position

    def stop(self):
        if self.component.visible:
            self.active(False)
            self.component.visible = False


class DirIndication(object):
    def __init__(self):
        self.primary_indication = config.data['config'].get('primary_indication')
        self.secondary_indication = config.data['config'].get('secondary_indication')
        self.max_distance_primary_indication = config.data['config'].get('max_distance_primary_indication', 0)
        self.max_distance_secondary_indication = config.data['config'].get('max_distance_secondary_indication', 0)
        self.strategic_fear_mode = config.data['config'].get('strategic_fear_mode')
        self.red_to_purple_indication = config.data['config'].get('red_to_purple_indication')
        self.distance_indicator = config.data['config'].get('distance_indicator')
        self.tank_name_indicator = config.data['config'].get('tank_name_indicator')
        self.enemies_list = {}
        self.callback = None

    def clear_vars(self):
        for i in self.enemies_list.keys():
            self.del_indicator(i)
        self.enemies_list.clear()
        self.callback = None

    def start_battle(self):
        if config.enable:
            BigWorld.player().arena.onVehicleKilled += self.on_vehicle_killed
            self.clear_vars()
            self.callback = BigWorld.callback(0.5, self.refresh_indicator)

    def stop_battle(self):
        if config.enable:
            BigWorld.player().arena.onVehicleKilled -= self.on_vehicle_killed
            if self.callback:
                BigWorld.cancelCallback(self.callback)
                self.callback = None

            self.clear_vars()

    def init_vehicle(self, vehicle_id):
        if self.get_is_live(vehicle_id):
            self.check_visible(vehicle_id)
            if not self.get_is_friendly(vehicle_id) and vehicle_id not in self.enemies_list:
                self.enemies_list[vehicle_id] = {}
                self.enemies_list[vehicle_id]['dir_indicator'] = CustomFlash()
                self.enemies_list[vehicle_id]['distance'] = 10000

    def fin_vehicle(self, vehicle_id):
        if vehicle_id in self.enemies_list:
            self.disable_indicator(vehicle_id)

    @staticmethod
    def add_observed_point(vehicle_id):
        vehicle = BigWorld.player().arena.vehicles[vehicle_id]
        try:
            if 'vehicleType' in vehicle:
                vehicle_type = vehicle['vehicleType']
                if not hasattr(vehicle_type, 'observer_pos_on_chassis'):
                    hull_pos = vehicle_type.chassis['hullPosition']
                    hull_bbox_min, hull_bbox_max, _ = vehicle_type.hull['hitTester'].bbox
                    turret_pos_on_hull = vehicle_type.hull['turretPositions'][0]
                    turret_local_top_y = max(hull_bbox_max.y, turret_pos_on_hull.y + vehicle_type.turret['hitTester'].bbox[1].y)
                    vehicle_type.observer_pos_on_chassis = Vector3(0, hull_pos.y + turret_local_top_y, 0)
                return True
            return False
        except StandardError:
            return False

    def enable_indicator(self, vehicle_id, checkpoint):
        if vehicle_id in self.enemies_list:
            if 'dir_indicator' in self.enemies_list[vehicle_id]:
                self.enemies_list[vehicle_id]['dir_indicator'].track(checkpoint)
                if self.distance_indicator:
                    self.enemies_list[vehicle_id]['dir_indicator'].set_distance(self.enemies_list[vehicle_id]['distance'])
                if self.tank_name_indicator:
                    target_info = g_sessionProvider.getCtx().getFullPlayerNameWithParts(vehicle_id)
                    if target_info and target_info[4]:
                        self.enemies_list[vehicle_id]['dir_indicator'].set_vehicle_name(target_info[4])

    def on_vehicle_killed(self, target_id, attacker_id, equipment_id, reason):
        _, _, _ = attacker_id, reason, equipment_id
        if target_id in self.enemies_list:
            self.disable_indicator(target_id)
        if target_id == BigWorld.player().playerVehicleID:
            self.clear_vars()

    def disable_indicator(self, vehicle_id):
        if vehicle_id in self.enemies_list:
            if 'dir_indicator' in self.enemies_list[vehicle_id]: self.enemies_list[vehicle_id]['dir_indicator'].stop()
            if 'distance' in self.enemies_list[vehicle_id] and self.enemies_list[vehicle_id]['distance'] < 10000: self.enemies_list[vehicle_id]['distance'] = 10000

    def del_indicator(self, vehicle_id):
        if vehicle_id in self.enemies_list:
            if 'dir_indicator' in self.enemies_list[vehicle_id]:
                self.enemies_list[vehicle_id]['dir_indicator'].close()
                del self.enemies_list[vehicle_id]

    def check_visible(self, slave):
        player = BigWorld.player()
        master = player.playerVehicleID
        if self.add_observed_point(master) and self.add_observed_point(slave):
            master_vehicle = player.arena.vehicles[master]['vehicleType']
            slave_vehicle = player.arena.vehicles[slave]['vehicleType']
            current_checkpoint = self.translation_points(slave, slave_vehicle.observer_pos_on_chassis)
            if current_checkpoint:
                current_observe = self.translation_points(master, master_vehicle.observer_pos_on_chassis)
                if current_observe and BigWorld.wg_collideSegment(player.spaceID, current_observe, current_checkpoint, False) is None:
                    return True, current_observe, current_checkpoint
                return False, current_observe, current_checkpoint
        return False, None, None

    def refresh_indicator(self):
        aim_mode = BigWorld.player().inputHandler.aim.mode
        for vehicle_id in self.enemies_list:
            if self.get_is_on_arena(vehicle_id) and self.get_is_live(vehicle_id):
                visible, observe, checkpoint = self.check_visible(vehicle_id)
                if observe and checkpoint:
                    position = observe
                    if self.strategic_fear_mode and 'strategic' in aim_mode:
                        position = BigWorld.camera().position
                    self.enemies_list[vehicle_id]['distance'] = (position - checkpoint).length
                    if visible:
                        if self.secondary_indication:
                            if self.enemies_list[vehicle_id]['distance'] < self.max_distance_secondary_indication:
                                self.enemies_list[vehicle_id]['dir_indicator'].set_shape('purple' if self.red_to_purple_indication else 'red')
                                self.enable_indicator(vehicle_id, checkpoint)
                    elif self.primary_indication:
                        if self.enemies_list[vehicle_id]['distance'] < self.max_distance_primary_indication and vehicle_id in self.check_nearest_target():
                            self.enemies_list[vehicle_id]['dir_indicator'].set_shape('green')
                            self.enable_indicator(vehicle_id, checkpoint)
                        else: self.disable_indicator(vehicle_id)
                    else: self.disable_indicator(vehicle_id)
                else: self.disable_indicator(vehicle_id)
            else: self.disable_indicator(vehicle_id)
        self.callback = BigWorld.callback(0.5, self.refresh_indicator)

    def check_nearest_target(self):
        return min(self.enemies_list.iterkeys(), key=(lambda key: self.enemies_list[key]['distance'])),

    @staticmethod
    def translation_points(vehicle_id, point):
        try: return Matrix(BigWorld.entity(vehicle_id).model.matrix).applyPoint(point)
        except StandardError: return

    @staticmethod
    def get_battle_on():
        try:
            if BigWorld.player().arena: return True
        except StandardError: return False
        return hasattr(BigWorld.player(), 'arena')

    def get_is_on_arena(self, vehicle_id):
        return self.get_battle_on() and vehicle_id in self.enemies_list

    @staticmethod
    def get_is_live(vehicle_id):
        try: return BigWorld.player().arena.vehicles[vehicle_id]['isAlive']
        except StandardError: return False

    def get_is_friendly(self, vehicle_id):
        player = BigWorld.player()
        return self.get_battle_on() and player.arena.vehicles[player.playerVehicleID]['team'] == player.arena.vehicles[vehicle_id]['team']


# deformed functions:
def hook_update_all(self):
    hooked_update_all(self)
    config.analytics()


def hook_vehicle_on_enter_world(self, vehicle):
    hooked_vehicle_on_enter_world(self, vehicle)
    if config.enable: dir_ind.init_vehicle(vehicle.id)


def hook_vehicle_on_leave_world(self, vehicle):
    hooked_vehicle_on_leave_world(self, vehicle)
    if config.enable: dir_ind.fin_vehicle(vehicle.id)


def hook_start_battle(self):
    hooked_start_battle(self)
    dir_ind.start_battle()


def hook_stop_battle(self):
    hooked_stop_battle(self)
    dir_ind.stop_battle()


#start mod
config = Config()
config.load_mod()
dir_ind = DirIndication()

#hooked
# noinspection PyProtectedMember
hooked_update_all = Hangar._Hangar__updateAll
hooked_vehicle_on_enter_world = PlayerAvatar.vehicle_onEnterWorld
hooked_vehicle_on_leave_world = PlayerAvatar.vehicle_onLeaveWorld
hooked_start_battle = Battle.afterCreate
hooked_stop_battle = Battle.beforeDelete

#hook
# noinspection PyProtectedMember
Hangar._Hangar__updateAll = hook_update_all
PlayerAvatar.vehicle_onEnterWorld = hook_vehicle_on_enter_world
PlayerAvatar.vehicle_onLeaveWorld = hook_vehicle_on_leave_world
Battle.afterCreate = hook_start_battle
Battle.beforeDelete = hook_stop_battle
