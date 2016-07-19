# -*- coding: utf-8 -*-
import threading
import urllib
import urllib2
import traceback

import BigWorld
import Math
import game

from Avatar import PlayerAvatar
from constants import AUTH_REALM
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.battle_control import g_sessionProvider
from helpers import getClientVersion
from helpers import getLanguageCode

CURR_CLIENT = getClientVersion()

if '0.9.15.0' in CURR_CLIENT:
    # noinspection PyUnresolvedReferences,PyProtectedMember
    from gui.scaleform.daapi.view.battle.indicators import _DirectionIndicatorMessage, _DIRECT_INDICATOR_SWF
else:
    # noinspection PyProtectedMember
    from gui.Scaleform.daapi.view.battle.shared.indicators import _DirectionIndicatorMessage, _DIRECT_INDICATOR_SWF

SHOW_DEBUG = True
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
        self.ids = 'dir_indicator_extended'
        self.version = '2.04 (07.07.2016)'
        self.version_id = 204
        self.author = 'by spoter, Thx to Lp()rtii'
        self.data = {
            'version'                          : self.version_id,
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
            'version'                                           : self.version_id,
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

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
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
                'tid': 'UA-57975916-14',
                'cid': self.p__user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Тылы"', # App name.
                'av' : 'Мод: "Тылы" %s' % _config.version,
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
                'tid': 'UA-57975916-14',
                'cid': self.p__old_user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Тылы"', # App name.
                'av' : 'Мод: "Тылы" %s' % _config.version,
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, p__lang), # Screen name / content description.
                'ul' : '%s' % p__lang,
                'sc' : 'end'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=p__param).read()
            self.p__analytics_started = False


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
                    'dir_indicator': _DirectionIndicatorMessage(_DIRECT_INDICATOR_SWF),
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
                    # noinspection PyProtectedMember
                    if self.enemies_list[vehicle_id]['dir_indicator']._dObject and target_info and target_info[4]:
                        # noinspection PyProtectedMember
                        if '0.9.15.0' in CURR_CLIENT:
                            # noinspection PyProtectedMember
                            self.enemies_list[vehicle_id]['dir_indicator']._dObject.setVName(target_info[4])
                        else:
                            # noinspection PyProtectedMember
                            self.enemies_list[vehicle_id]['dir_indicator']._dObject.setMessage(target_info[4])

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
        except StandardError: return
        return hasattr(BigWorld.player(), 'arena')

    def get_is_on_arena(self, vehicle_id):
        return self.get_battle_on() and vehicle_id in self.enemies_list

    @staticmethod
    def get_is_live(vehicle_id):
        try: return BigWorld.player().arena.vehicles[vehicle_id]['isAlive']
        except StandardError: return

    def get_is_friendly(self, vehicle_id):
        player = BigWorld.player()
        return self.get_battle_on() and player.arena.vehicles[player.playerVehicleID]['team'] == player.arena.vehicles[vehicle_id]['team']


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


def hook_vehicle_on_enter_world(self, vehicle):
    hooked_vehicle_on_enter_world(self, vehicle)
    try:
        if _config.data['enabled']:
            dir_ind.init_vehicle(vehicle.id)
    except Exception as e:
        log('hook_vehicle_on_enter_world', e)
        traceback.print_exc()


def hook_vehicle_on_leave_world(self, vehicle):
    hooked_vehicle_on_leave_world(self, vehicle)
    try:
        if _config.data['enabled']:
            dir_ind.fin_vehicle(vehicle.id)
    except Exception as e:
        log('hook_vehicle_on_leave_world', e)
        traceback.print_exc()


def hook_start_battle(self):
    hooked_start_battle(self)
    try:
        dir_ind.start_battle()
    except Exception as e:
        log('hook_start_battle', e)
        traceback.print_exc()


def hook_stop_battle(self):
    hooked_stop_battle(self)
    try:
        dir_ind.stop_battle()
    except Exception as e:
        log('hook_stop_battle', e)
        traceback.print_exc()


#start mod
p__stat = Statistics()
_config = _Config()
dir_ind = DirIndication()
_config.load()

#hooked
# noinspection PyProtectedMember
hooked_update_all = LobbyView._populate
hooked_fini = game.fini
hooked_vehicle_on_enter_world = PlayerAvatar.vehicle_onEnterWorld
hooked_vehicle_on_leave_world = PlayerAvatar.vehicle_onLeaveWorld
# noinspection PyProtectedMember
hooked_start_battle = PlayerAvatar._PlayerAvatar__startGUI
# noinspection PyProtectedMember
hooked_stop_battle = PlayerAvatar._PlayerAvatar__destroyGUI

#hook
LobbyView._populate = hook_update_all
game.fini = hook_fini
PlayerAvatar.vehicle_onEnterWorld = hook_vehicle_on_enter_world
PlayerAvatar.vehicle_onLeaveWorld = hook_vehicle_on_leave_world
PlayerAvatar._PlayerAvatar__startGUI = hook_start_battle
PlayerAvatar._PlayerAvatar__destroyGUI = hook_stop_battle
