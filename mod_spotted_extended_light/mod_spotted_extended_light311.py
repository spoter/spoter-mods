# -*- coding: utf-8 -*-
import threading
import urllib
import urllib2

import BigWorld

import SoundGroups
from Avatar import PlayerAvatar
from constants import AUTH_REALM
from gui.battle_control import g_sessionProvider
from gui.mods.mod_mods_gui import g_gui, inject
from helpers import getLanguageCode
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView

SOUND_LIST = ['soundSpotted', 'soundRadioHitAssist', 'soundRadioKillAssist', 'soundTrackAssist']
TEXT_LIST = ['UI_message_Spotted_text', 'UI_message_RadioHitAssist_text', 'UI_message_RadioKillAssist_text', 'UI_message_TrackAssist_text']
COLOR_MESSAGES = ['messageColorSpotted', 'messageColorRadioHitAssist', 'messageColorRadioKillAssist', 'messageColorTrackAssist']
COLOR = ['#0000FF', '#A52A2B', '#D3691E', '#6595EE', '#FCF5C8', '#00FFFF', '#28F09C', '#FFD700', '#008000', '#ADFF2E', '#FF69B5', '#00FF00', '#FFA500', '#FFC0CB', '#800080', '#FF0000', '#8378FC', '#DB0400', '#80D639', '#FFE041', '#FFFF00', '#FA8072']
MENU = ['UI_menu_blue', 'UI_menu_brown', 'UI_menu_chocolate', 'UI_menu_cornflower_blue', 'UI_menu_cream', 'UI_menu_cyan', 'UI_menu_emerald', 'UI_menu_gold', 'UI_menu_green', 'UI_menu_green_yellow', 'UI_menu_hot_pink', 'UI_menu_lime',
    'UI_menu_orange', 'UI_menu_pink', 'UI_menu_purple', 'UI_menu_red', 'UI_menu_wg_blur', 'UI_menu_wg_enemy', 'UI_menu_wg_friend', 'UI_menu_wg_squad', 'UI_menu_yellow', 'UI_menu_nice_red']

class Config(object):
    def __init__(self):
        self.ids = 'spotted_extended_light'
        self.version = '3.11 (02.08.2016)'
        self.version_id = 310
        self.author = 'by spoter'
        self.data = {
            'version'                    : self.version_id,
            'enabled'                    : True,
            'sound'                      : True,
            'iconSizeX'                  : 47,
            'iconSizeY'                  : 16,
            'soundSpotted'               : 'enemy_sighted_for_team',
            'soundRadioHitAssist'        : 'gun_intuition',
            'soundRadioKillAssist'       : 'cybersport_auto_search',
            'soundTrackAssist'           : 'gun_intuition',
            'messageColorSpotted'        : 7,
            'messageColorRadioHitAssist' : 10,
            'messageColorRadioKillAssist': 6,
            'messageColorTrackAssist'    : 11
        }
        self.i18n = {
            'version'                                       : self.version_id,
            'UI_description'                                : 'Spotted extended Light',
            'UI_setting_sound_text'                         : 'Use sound in battle',
            'UI_setting_sound_tooltip'                      : '{HEADER}<font color="#FFD700">Info:</font>{/HEADER}{BODY}Configure sounds in config file: <font '
                                                              'color="#FFD700">/res_mods/configs/spotted_extended_light/spotted_extended_light.json</font>{/BODY}',
            'UI_setting_iconSizeX_text'                     : 'Icon size X-coordinate',
            'UI_setting_iconSizeX_value'                    : ' px.',
            'UI_setting_iconSizeY_text'                     : 'Icon size Y-coordinate',
            'UI_setting_iconSizeY_value'                    : ' px.',
            'UI_setting_MessageColorSpotted_text'           : 'Color to message "Spotted',
            'UI_setting_MessageColorSpotted_tooltip'        : '',
            'UI_setting_MessageColorRadioHitAssist_text'    : 'Color to message "Radio Hit Assist"',
            'UI_setting_MessageColorRadioHitAssist_tooltip' : '',
            'UI_setting_MessageColorRadioKillAssist_text'   : 'Color to message "Radio Kill Assist"',
            'UI_setting_MessageColorRadioKillAssist_tooltip': '',
            'UI_setting_MessageColorTrackAssist_text'       : 'Color to message "Track Assist"',
            'UI_setting_MessageColorTrackAssist_tooltip'    : '',
            'UI_menu_blue'                                  : 'Blue',
            'UI_menu_brown'                                 : 'Brown',
            'UI_menu_chocolate'                             : 'Chocolate',
            'UI_menu_cornflower_blue'                       : 'Cornflower Blue',
            'UI_menu_cream'                                 : 'Cream',
            'UI_menu_cyan'                                  : 'Cyan',
            'UI_menu_emerald'                               : 'Emerald',
            'UI_menu_gold'                                  : 'Gold',
            'UI_menu_green'                                 : 'Green',
            'UI_menu_green_yellow'                          : 'Green Yellow',
            'UI_menu_hot_pink'                              : 'Hot Pink',
            'UI_menu_lime'                                  : 'Lime',
            'UI_menu_orange'                                : 'Orange',
            'UI_menu_pink'                                  : 'Pink',
            'UI_menu_purple'                                : 'Purple',
            'UI_menu_red'                                   : 'Red',
            'UI_menu_wg_blur'                               : 'WG Blur',
            'UI_menu_wg_enemy'                              : 'WG Enemy',
            'UI_menu_wg_friend'                             : 'WG Friend',
            'UI_menu_wg_squad'                              : 'WG Squad',
            'UI_menu_yellow'                                : 'Yellow',
            'UI_menu_nice_red'                              : 'Nice Red',
            'UI_message_Spotted_text'                       : 'Spotted {icons_vehicles}',
            'UI_message_RadioHitAssist_text'                : 'Radio hit assist to {icons_vehicles}',
            'UI_message_RadioKillAssist_text'               : 'Radio kill assist to {icons_vehicles}',
            'UI_message_TrackAssist_text'                   : 'Tracks assist {icons_vehicles}',
            'UI_message_macrosList'                         : 'Available macros in messages {icons}, {names}, {vehicles}, {icons_names}, {icons_vehicles}, {full}'
        }

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_sound_text'],
                'value'  : self.data['sound'],
                'tooltip': self.i18n['UI_setting_sound_tooltip'],
                'varName': 'sound'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_setting_iconSizeX_text'],
                'minimum'     : 5,
                'maximum'     : 150,
                'snapInterval': 1,
                'value'       : self.data['iconSizeX'],
                'format'      : '{{value}}%s [47]' % self.i18n['UI_setting_iconSizeX_value'],
                'varName'     : 'iconSizeX'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_setting_iconSizeY_text'],
                'minimum'     : 5,
                'maximum'     : 150,
                'snapInterval': 1,
                'value'       : self.data['iconSizeY'],
                'format'      : '{{value}}%s [16]' % self.i18n['UI_setting_iconSizeY_value'],
                'varName'     : 'iconSizeY'
            }],
            'column2'        : [{
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_MessageColorSpotted_text'],
                'tooltip'     : self.i18n['UI_setting_MessageColorSpotted_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['messageColorSpotted'],
                'varName'     : 'messageColorSpotted'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_MessageColorRadioHitAssist_text'],
                'tooltip'     : self.i18n['UI_setting_MessageColorRadioHitAssist_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['messageColorRadioHitAssist'],
                'varName'     : 'messageColorRadioHitAssist'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_MessageColorRadioKillAssist_text'],
                'tooltip'     : self.i18n['UI_setting_MessageColorRadioKillAssist_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['messageColorRadioKillAssist'],
                'varName'     : 'messageColorRadioKillAssist'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_MessageColorTrackAssist_text'],
                'tooltip'     : self.i18n['UI_setting_MessageColorTrackAssist_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['messageColorTrackAssist'],
                'varName'     : 'messageColorTrackAssist'
            }]
        }

    def generator_menu(self):
        res = []
        for i in xrange(0, len(COLOR)):
            res.append({
                'label': '<font color="%s">%s</font>' % (COLOR[i], self.i18n[MENU[i]])
            })
        return res

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
                'tid': 'UA-57975916-7',
                'cid': self.user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Маленький Светлячок"', # App name.
                'av' : 'Мод: "Маленький Светлячок" %s' % config.version,
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
                'tid': 'UA-57975916-7',
                'cid': self.old_user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Маленький Светлячок"', # App name.
                'av' : 'Мод: "Маленький Светлячок" %s' % config.version,
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, lang), # Screen name / content description.
                'ul' : '%s' % lang,
                'sc' : 'end'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=param).read()
            self.analytics_started = False

class Assist(object):
    def __init__(self):
        self.format_str = {}
        self.format_recreate()

    @staticmethod
    def check_macros(macros):
        for i in TEXT_LIST:
            if macros in config.i18n[i]:
                return True

    def format_recreate(self):
        self.format_str = {
            'icons'         : '',
            'names'         : '',
            'vehicles'      : '',
            'icons_names'   : '',
            'icons_vehicles': '',
            'full'          : ''
        }

    @staticmethod
    def sound(assist_type):
        if assist_type < 4:
            sound = SoundGroups.g_instance.getSound2D(config.data[SOUND_LIST[assist_type]])
            if sound:
                sound.stop()
                sound.play()

    def post_message(self, assist_type, vehicles_ids):
        if assist_type < 4:
            self.format_recreate()
            for i in vehicles_ids:
                if i >> 32 & 4294967295L > 0: i = i >> 32 & 4294967295L
                else: i &= 4294967295L
                icon = '<img src="img://%s" width="%s" height="%s" />' % (g_sessionProvider.getArenaDP().getVehicleInfo(i).vehicleType.iconPath.replace('..', 'gui'), config.data['iconSizeX'], config.data['iconSizeY'])
                target_info = g_sessionProvider.getCtx().getPlayerFullNameParts(vID=i)
                if self.check_macros('{icons}'): self.format_str['icons'] += icon
                if self.check_macros('{names}'): self.format_str['names'] += '[%s]' % target_info[1] if target_info[1] else icon
                if self.check_macros('{vehicles}'): self.format_str['vehicles'] += '[%s]' % target_info[4] if target_info[4] else icon
                if self.check_macros('{icons_names}'): self.format_str['icons_names'] += '%s[%s]' % (icon, target_info[1]) if target_info[1] else icon
                if self.check_macros('{icons_vehicles}'): self.format_str['icons_vehicles'] += '%s[%s]' % (icon, target_info[4]) if target_info[4] else icon
                if self.check_macros('{full}'):
                    self.format_str['full'] += '%s[%s]' % (icon, target_info) if target_info else icon
            msg = config.i18n[TEXT_LIST[assist_type]].format(**self.format_str)
            inject.message(msg, COLOR[config.data[COLOR_MESSAGES[assist_type]]])

#start mod
stat = Statistics()
config = Config()
assist = Assist()

@inject.log
def init():
    config.load()

@inject.log
def fini():
    stat.end()

@inject.hook(LobbyView, '_populate')
@inject.log
def hookLobbyViewPopulate(func, *args):
    func(*args)
    stat.start()

@inject.hook(PlayerAvatar, 'onBattleEvent')
@inject.log
def hook_PlayerAvatarVehicleOnEnterWorld(func, *args):
    if config.data['enabled']:
        self, event_type, details = args
        if config.data['sound']: assist.sound(event_type)
        assist.post_message(event_type, details)
    return func(*args)
