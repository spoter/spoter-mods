# -*- coding: utf-8 -*-
import codecs
import json
import os
import re
import threading
import urllib
import urllib2

import BigWorld
import Math

from Avatar import PlayerAvatar
from constants import AUTH_REALM
from gui.Scaleform.Battle import Battle
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.battle_control import g_sessionProvider
from gui.scaleform.daapi.view.battle.indicators import _DirectionIndicatorMessage
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
        self.ids = 'dir_indicator_extended'
        self.version = '2.02 (23.06.2016)'
        self.author = 'by spoter, Thx to Lp()rtii'
        self.path_config = './res_mods/configs/spoter_mods/%s/' % self.ids
        self.path_lang = '%si18n/' % self.path_config
        self.data = {
            'enabled'                          : True,
            'primary_indication'               : True,
            'secondary_indication'             : False,
            'tertiary_indication'              : True,
            'distance_indicator'               : True,
            'tank_name_indicator'              : True,
            'max_distance_primary_indication'  : 150,
            'max_distance_secondary_indication': 300,
            'max_distance_tertiary_indication' : 565,
            'primary_indication_color'         : 2,
            'secondary_indication_color'       : 1,
            'tertiary_indication_color'        : 0,
            'color_list'                       : ['purple', 'red', 'green']
        }

        self.i18n = {
            'UI_description'                                    : 'Direction Indicator Extended',
            'UI_setting_distance_indicator_text'                : 'Show distance',
            'UI_setting_distance_indicator_tooltip'             : '{HEADER}Info:{/HEADER}{BODY}Show text in Enemy Indicator: Distance{/BODY}',
            'UI_setting_tank_name_indicator_text'               : 'Show Tank name',
            'UI_setting_tank_name_indicator_tooltip'            : '{HEADER}Info:{/HEADER}{BODY}Show text in Enemy Indicator: Tank name{/BODY}',
            'UI_setting_primary_indication_text'                : 'Primary Indication (nearest)',
            'UI_setting_primary_indication_tooltip'             : '{HEADER}Info:{/HEADER}{BODY}Show nearest enemy with a special indicator{/BODY}',
            'UI_setting_secondary_indication_text'              : 'Secondary Indication (not visible)',
            'UI_setting_secondary_indication_tooltip'           : '{HEADER}Info:{/HEADER}{BODY}Show nearest enemies with a special indicator, when not visible to you tank{/BODY}',
            'UI_setting_tertiary_indication_text'               : 'Tertiary Indication (visible)',
            'UI_setting_tertiary_indication_tooltip'            : '{HEADER}Info:{/HEADER}{BODY}Show nearest enemies with a special indicator, when enemy visible to you tank{/BODY}',
            'UI_setting_primary_indication_color_text'          : 'Color Primary (nearest)',
            'UI_setting_primary_indication_color_tooltip'       : '{HEADER}Info:{/HEADER}{BODY}Select color to Primary Indication{/BODY}',
            'UI_setting_secondary_indication_color_text'        : 'Color Secondary (not visible)',
            'UI_setting_secondary_indication_color_tooltip'     : '{HEADER}Info:{/HEADER}{BODY}Select color to Secondary Indication{/BODY}',
            'UI_setting_tertiary_indication_color_text'         : 'Color Tertiary (visible)',
            'UI_setting_tertiary_indication_color_tooltip'      : '{HEADER}Info:{/HEADER}{BODY}Select color to Tertiary Indication{/BODY}',
            'UI_setting_color_purple'                           : '<font color="#800080">Purple</font>',
            'UI_setting_color_red'                              : '<font color="#FF0000">Red</font>',
            'UI_setting_color_green'                            : '<font color="#80D639">Green</font>',
            'UI_setting_max_distance_primary_indication_text'   : 'Max distance: Primary (nearest)',
            'UI_setting_max_distance_primary_indication_value'  : 'm.',
            'UI_setting_max_distance_secondary_indication_text' : 'Max distance: Secondary (not visible)',
            'UI_setting_max_distance_secondary_indication_value': 'm.',
            'UI_setting_max_distance_tertiary_indication_text'  : 'Max distance: Tertiary (visible)',
            'UI_setting_max_distance_tertiary_indication_value' : 'm.',
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
                'text'   : self.i18n['UI_setting_primary_indication_text'],
                'value'  : self.data['primary_indication'],
                'tooltip': self.i18n['UI_setting_primary_indication_tooltip'],
                'varName': 'primary_indication'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_secondary_indication_text'],
                'value'  : self.data['secondary_indication'],
                'tooltip': self.i18n['UI_setting_secondary_indication_tooltip'],
                'varName': 'secondary_indication'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_tertiary_indication_text'],
                'value'  : self.data['tertiary_indication'],
                'tooltip': self.i18n['UI_setting_tertiary_indication_tooltip'],
                'varName': 'tertiary_indication'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_distance_indicator_text'],
                'value'  : self.data['distance_indicator'],
                'tooltip': self.i18n['UI_setting_distance_indicator_tooltip'],
                'varName': 'distance_indicator'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_tank_name_indicator_text'],
                'value'  : self.data['tank_name_indicator'],
                'tooltip': self.i18n['UI_setting_tank_name_indicator_tooltip'],
                'varName': 'tank_name_indicator'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_setting_max_distance_primary_indication_text'],
                'minimum'     : 50,
                'maximum'     : 565,
                'snapInterval': 5,
                'value'       : self.data['max_distance_primary_indication'],
                'format'      : '{{value}}%s' % self.i18n['UI_setting_max_distance_primary_indication_value'],
                'varName'     : 'max_distance_primary_indication'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_setting_max_distance_secondary_indication_text'],
                'minimum'     : 50,
                'maximum'     : 565,
                'snapInterval': 5,
                'value'       : self.data['max_distance_secondary_indication'],
                'format'      : '{{value}}%s' % self.i18n['UI_setting_max_distance_secondary_indication_value'],
                'varName'     : 'max_distance_secondary_indication'
            }],
            'column2'        : [{
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_primary_indication_color_text'],
                'tooltip'     : self.i18n['UI_setting_primary_indication_color_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : [{
                    'label': self.i18n['UI_setting_color_purple']
                }, {
                    'label': self.i18n['UI_setting_color_red']
                }, {
                    'label': self.i18n['UI_setting_color_green']
                }],
                'width'       : 200,
                'value'       : self.data['primary_indication_color'],
                'varName'     : 'primary_indication_color'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_secondary_indication_color_text'],
                'tooltip'     : self.i18n['UI_setting_secondary_indication_color_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : [{
                    'label': self.i18n['UI_setting_color_purple']
                }, {
                    'label': self.i18n['UI_setting_color_red']
                }, {
                    'label': self.i18n['UI_setting_color_green']
                }],
                'width'       : 200,
                'value'       : self.data['secondary_indication_color'],
                'varName'     : 'secondary_indication_color'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_tertiary_indication_color_text'],
                'tooltip'     : self.i18n['UI_setting_tertiary_indication_color_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : [{
                    'label': self.i18n['UI_setting_color_purple']
                }, {
                    'label': self.i18n['UI_setting_color_red']
                }, {
                    'label': self.i18n['UI_setting_color_green']
                }],
                'width'       : 200,
                'value'       : self.data['tertiary_indication_color'],
                'varName'     : 'tertiary_indication_color'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_setting_max_distance_tertiary_indication_text'],
                'minimum'     : 50,
                'maximum'     : 565,
                'snapInterval': 5,
                'value'       : self.data['max_distance_tertiary_indication'],
                'format'      : '{{value}}%s' % self.i18n['UI_setting_max_distance_tertiary_indication_value'],
                'varName'     : 'max_distance_tertiary_indication'
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
        self.tid = 'UA-57975916-14'
        self.description_analytics = 'Мод: "Тылы"'

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


class DirIndication(object):
    def __init__(self):
        self.enemies_list = {}
        self.callback = None

    def clear_vars(self):
        for i in self.enemies_list.keys():
            self.del_indicator(i)
        self.enemies_list.clear()
        self.callback = None

    def start_battle(self):
        if _config.data['enabled']:
            BigWorld.player().arena.onVehicleKilled += self.on_vehicle_killed
            self.clear_vars()
            self.callback = BigWorld.callback(0.5, self.refresh_indicator)

    def stop_battle(self):
        if _config.data['enabled']:
            BigWorld.player().arena.onVehicleKilled -= self.on_vehicle_killed
            if self.callback:
                BigWorld.cancelCallback(self.callback)
                self.callback = None

            self.clear_vars()

    def init_vehicle(self, vehicle_id):
        if self.get_is_live(vehicle_id):
            self.check_visible(vehicle_id)
            if not self.get_is_friendly(vehicle_id) and vehicle_id not in self.enemies_list:
                self.enemies_list[vehicle_id] = {
                    'dir_indicator': _DirectionIndicatorMessage('dir_indicator_extended.swf'),
                    'distance'     : 10000
                }

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
                    vehicle_type.observer_pos_on_chassis = Math.Vector3(0, hull_pos.y + turret_local_top_y, 0)
                return True
            return False
        except StandardError:
            return False

    def enable_indicator(self, vehicle_id, checkpoint):
        if vehicle_id in self.enemies_list:
            if 'dir_indicator' in self.enemies_list[vehicle_id]:
                self.enemies_list[vehicle_id]['dir_indicator'].track(checkpoint)
                if _config.data['distance_indicator']:
                    self.enemies_list[vehicle_id]['dir_indicator'].setDistance(self.enemies_list[vehicle_id]['distance'])
                if _config.data['tank_name_indicator']:
                    target_info = g_sessionProvider.getCtx().getPlayerFullNameParts(vehicle_id)
                    if self.enemies_list[vehicle_id]['dir_indicator']._dObject and target_info and target_info[4]:
                        self.enemies_list[vehicle_id]['dir_indicator']._dObject.setVName(target_info[4])

    def on_vehicle_killed(self, target_id, attacker_id, equipment_id, reason):
        _, _, _ = attacker_id, reason, equipment_id
        if target_id in self.enemies_list:
            self.disable_indicator(target_id)
        if target_id == BigWorld.player().playerVehicleID:
            self.clear_vars()

    def disable_indicator(self, vehicle_id):
        if vehicle_id in self.enemies_list:
            if 'dir_indicator' in self.enemies_list[vehicle_id]:
                self.enemies_list[vehicle_id]['dir_indicator'].setVisibility(False)
                if self.enemies_list[vehicle_id]['dir_indicator'].component.visible:
                    self.enemies_list[vehicle_id]['dir_indicator'].active(False)
                    self.enemies_list[vehicle_id]['dir_indicator'].component.visible = False
            if 'distance' in self.enemies_list[vehicle_id] and self.enemies_list[vehicle_id]['distance'] < 10000: self.enemies_list[vehicle_id]['distance'] = 10000

    def del_indicator(self, vehicle_id):
        if vehicle_id in self.enemies_list:
            if 'dir_indicator' in self.enemies_list[vehicle_id]:
                self.enemies_list[vehicle_id]['dir_indicator'].remove()
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
        for vehicle_id in self.enemies_list:
            if self.get_is_on_arena(vehicle_id) and self.get_is_live(vehicle_id):
                visible, observe, checkpoint = self.check_visible(vehicle_id)
                if observe and checkpoint:
                    self.enemies_list[vehicle_id]['distance'] = (observe - checkpoint).length
                    if visible:
                        if _config.data['tertiary_indication']:
                            if self.enemies_list[vehicle_id]['distance'] < _config.data['max_distance_tertiary_indication']:
                                self.enemies_list[vehicle_id]['dir_indicator'].setShape(_config.data['color_list'][_config.data['tertiary_indication_color']])
                                self.enable_indicator(vehicle_id, checkpoint)
                                continue
                    else:
                        if _config.data['primary_indication'] and self.enemies_list[vehicle_id]['distance'] < _config.data['max_distance_primary_indication'] and vehicle_id in self.check_nearest_target():
                            self.enemies_list[vehicle_id]['dir_indicator'].setShape(_config.data['color_list'][_config.data['primary_indication_color']])
                            self.enable_indicator(vehicle_id, checkpoint)
                            continue
                        elif _config.data['secondary_indication'] and self.enemies_list[vehicle_id]['distance'] < _config.data['max_distance_secondary_indication']:
                            self.enemies_list[vehicle_id]['dir_indicator'].setShape(_config.data['color_list'][_config.data['secondary_indication_color']])
                            self.enable_indicator(vehicle_id, checkpoint)
                            continue
                        else: self.disable_indicator(vehicle_id)
                else: self.disable_indicator(vehicle_id)
            else: self.disable_indicator(vehicle_id)
        self.callback = BigWorld.callback(0.5, self.refresh_indicator)

    def check_nearest_target(self):
        return min(self.enemies_list.iterkeys(), key=(lambda key: self.enemies_list[key]['distance'])),

    @staticmethod
    def translation_points(vehicle_id, point):
        try: return Math.Matrix(BigWorld.entity(vehicle_id).model.matrix).applyPoint(point)
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
def hook_update_all(*args):
    hooked_update_all(*args)
    try:
        stat.start()
    except Exception as e:
        print('hook_update_all get stat', e)


def hook_vehicle_on_enter_world(self, vehicle):
    hooked_vehicle_on_enter_world(self, vehicle)
    if _config.data['enabled']: dir_ind.init_vehicle(vehicle.id)


def hook_vehicle_on_leave_world(self, vehicle):
    hooked_vehicle_on_leave_world(self, vehicle)
    if _config.data['enabled']: dir_ind.fin_vehicle(vehicle.id)


def hook_start_battle(self):
    hooked_start_battle(self)
    dir_ind.start_battle()


def hook_stop_battle(self):
    hooked_stop_battle(self)
    dir_ind.stop_battle()


#start mod
stat = Statistics()
_gui_config = _GUIConfig()
_config = _Config()
dir_ind = DirIndication()
_config.load()

#hooked
# noinspection PyProtectedMember
hooked_update_all = LobbyView._populate
hooked_vehicle_on_enter_world = PlayerAvatar.vehicle_onEnterWorld
hooked_vehicle_on_leave_world = PlayerAvatar.vehicle_onLeaveWorld
hooked_start_battle = Battle.afterCreate
hooked_stop_battle = Battle.beforeDelete

#hook
LobbyView._populate = hook_update_all
PlayerAvatar.vehicle_onEnterWorld = hook_vehicle_on_enter_world
PlayerAvatar.vehicle_onLeaveWorld = hook_vehicle_on_leave_world
Battle.afterCreate = hook_start_battle
Battle.beforeDelete = hook_stop_battle
