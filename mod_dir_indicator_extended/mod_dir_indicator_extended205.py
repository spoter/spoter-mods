# -*- coding: utf-8 -*-
import threading
import urllib
import urllib2

import BigWorld
import Math

from Avatar import PlayerAvatar
from constants import AUTH_REALM
# noinspection PyProtectedMember
from gui.Scaleform.daapi.view.battle.shared.indicators import _DirectionIndicator, _DIRECT_INDICATOR_SWF
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.battle_control import g_sessionProvider
from gui.mods.mod_mods_gui import g_gui, inject
from helpers import getLanguageCode

class _Config(object):
    def __init__(self):
        self.ids = 'dir_indicator_extended'
        self.version = '2.05 (28.07.2016)'
        self.version_id = 205
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
        self.data = g_gui.update_data(self.ids, settings)
        g_gui.update(self.ids, self.template)

    def load(self):
        self.do_config()
        print '[LOAD_MOD]:  [%s v%s, %s]' % (self.ids, self.version, self.author)

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
                'tid': 'UA-57975916-14',
                'cid': self.user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Тылы"', # App name.
                'av' : 'Мод: "Тылы" %s' % _config.version,
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
                'tid': 'UA-57975916-14',
                'cid': self.old_user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Тылы"', # App name.
                'av' : 'Мод: "Тылы" %s' % _config.version,
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, lang), # Screen name / content description.
                'ul' : '%s' % lang,
                'sc' : 'end'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=param).read()
            self.analytics_started = False

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
        if _config.data['enabled']:
            if self.get_is_live(vehicle_id):
                self.check_visible(vehicle_id)
                if not self.get_is_friendly(vehicle_id) and vehicle_id not in self.enemies_list:
                    self.enemies_list[vehicle_id] = {
                        'dir_indicator': _DirectionIndicator(_DIRECT_INDICATOR_SWF),
                        'distance'     : 10000
                    }
                    # noinspection PyProtectedMember
                    self.enemies_list[vehicle_id]['dir_indicator']._dObject.distance.x = -105

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
                # noinspection PyProtectedMember
                if self.enemies_list[vehicle_id]['dir_indicator']._dObject:
                    self.enemies_list[vehicle_id]['dir_indicator'].track(checkpoint)
                    msg = ''
                    if _config.data['distance_indicator']:
                        msg += '%sm. ' % self.enemies_list[vehicle_id]['distance']
                    if _config.data['tank_name_indicator']:
                        target_info = g_sessionProvider.getCtx().getPlayerFullNameParts(vehicle_id)
                        if target_info and target_info[4]:
                            msg += '%s' % target_info[4]
                    # noinspection PyProtectedMember
                    self.enemies_list[vehicle_id]['dir_indicator']._dObject.setMessage(msg)

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
                    self.enemies_list[vehicle_id]['distance'] = int((observe - checkpoint).length)
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

#start mod
_config = _Config()
stat = Statistics()
dir_ind = DirIndication()

@inject.log
def init():
    _config.load()

@inject.log
def fini():
    stat.end()

@inject.hook(LobbyView, '_populate')
def hookLobbyViewPopulate(func, *args):
    func(*args)
    stat.start()

@inject.hook(PlayerAvatar, 'vehicle_onEnterWorld')
def hook_PlayerAvatarVehicleOnEnterWorld(func, *args):
    func(*args)
    _, vehicle = args
    dir_ind.init_vehicle(vehicle.id)

@inject.hook(PlayerAvatar, 'vehicle_onLeaveWorld')
def hook_PlayerAvatarVehicleOnLeaveWorld(func, *args):
    func(*args)
    _, vehicle = args
    dir_ind.fin_vehicle(vehicle.id)

@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
def hook_PlayerAvatarStartGUI(func, *args):
    func(*args)
    dir_ind.start_battle()

@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
def hook_PlayerAvatarDestroyGUI(func, *args):
    func(*args)
    dir_ind.stop_battle()
