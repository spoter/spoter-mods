# -*- coding: utf-8 -*-
import math

import BattleReplay
import BigWorld
import GUI
import Keys
from Avatar import PlayerAvatar
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from CurrentVehicle import g_currentVehicle
from Vehicle import Vehicle
from constants import ARENA_BONUS_TYPE
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, MARK_OF_MASTERY_RECORD, MARK_ON_GUN_RECORD
from gui import InputHandler, g_guiResetters
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.daapi.view.lobby.techtree.dumpers import NationObjDumper
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.app_loader import g_appLoader
from gui.battle_control.controllers import feedback_events
from gui.mods.mod_mods_gui import COMPONENT_ALIGN, COMPONENT_EVENT, COMPONENT_TYPE, g_gui, g_guiFlash, inject
from gui.shared.gui_items.dossier.achievements.MarkOnGunAchievement import MarkOnGunAchievement
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

DAMAGE_EVENTS = frozenset([BATTLE_EVENT_TYPE.RADIO_ASSIST, BATTLE_EVENT_TYPE.TRACK_ASSIST, BATTLE_EVENT_TYPE.STUN_ASSIST, BATTLE_EVENT_TYPE.DAMAGE, BATTLE_EVENT_TYPE.TANKING, BATTLE_EVENT_TYPE.RECEIVED_DAMAGE])
COLOR = ['#0000FF', '#A52A2B', '#D3691E', '#6595EE', '#FCF5C8', '#00FFFF', '#28F09C', '#FFD700', '#008000', '#ADFF2E', '#FF69B5', '#00FF00', '#FFA500', '#FFC0CB', '#800080', '#FF0000', '#8378FC', '#DB0400', '#80D639', '#FFE041', '#FFFF00', '#FA8072', '#FFFFFF']
MENU  = ['UI_menu_blue', 'UI_menu_brown', 'UI_menu_chocolate', 'UI_menu_cornflower_blue', 'UI_menu_cream', 'UI_menu_cyan', 'UI_menu_emerald', 'UI_menu_gold', 'UI_menu_green', 'UI_menu_green_yellow', 'UI_menu_hot_pink', 'UI_menu_lime',
        'UI_menu_orange', 'UI_menu_pink', 'UI_menu_purple', 'UI_menu_red', 'UI_menu_wg_blur', 'UI_menu_wg_enemy', 'UI_menu_wg_friend', 'UI_menu_wg_squad', 'UI_menu_yellow', 'UI_menu_nice_red', 'UI_menu_white']
RATING = {
    'neutral'  : '#FFFFFF',
    'very_bad' : '#FA8072',
    'bad'      : '#FE7903',
    'normal'   : '#F8F400',
    'good'     : '#60FF00',
    'very_good': '#02C9B3',
    'unique'   : '#D042F3'
}
statisticRating = [RATING['normal'], RATING['normal'], RATING['good'], RATING['very_good'], RATING['unique'], RATING['unique']]
techTreeRating  = [RATING['normal'], RATING['good'], RATING['very_good'], RATING['unique']]

battleDamageRating0   = RATING['very_bad']
battleDamageRating20  = RATING['very_bad']
battleDamageRating40  = RATING['bad']
battleDamageRating55  = RATING['bad']
battleDamageRating65  = RATING['normal']
battleDamageRating85  = RATING['good']
battleDamageRating95  = RATING['very_good']
battleDamageRating100 = RATING['unique']

battleDamageRating = [battleDamageRating0, battleDamageRating20, battleDamageRating40, battleDamageRating55, battleDamageRating65, battleDamageRating85, battleDamageRating95, battleDamageRating100]

LEVELS = [0.0, 20.0, 40.0, 55.0, 65.0, 85.0, 95.0, 100.0]


class Config(object):
    def __init__(self):
        self.ids = 'marksOnGunExtended'
        self.version = 'v5.02 (2018-11-02)'
        self.version_id = 502
        self.author = 'by spoter to b4it.org'
        self.buttons = {
            'buttonShow': [Keys.KEY_NUMPAD9, [Keys.KEY_LALT, Keys.KEY_RALT]],
        }
        self.data = {
            'version'                                      : self.version_id,
            'enabled'                                      : True,
            'buttonShow'                                   : self.buttons['buttonShow'],
            'showInBattle'                                 : True,
            'showInReplay'                                 : True,
            'showInStatistic'                              : True,
            'showInTechTree'                               : True,
            'showInTechTreeMastery'                        : False,
            'showInTechTreeMarkOfGunPercent'               : True,
            'showInTechTreeMarkOfGunTankNameColored'       : False,
            'showInTechTreeMarkOfGunPercentFirst'          : False,
            'techTreeMarkOfGunTankNameColoredOnlyMarkOfGun': True,
            'techTreeMasterySize'                          : 16,
            'techTreeMarkOfGunPercentSize'                 : 12,
            'upColor'                                      : 18,
            'downColor'                                    : 21,
            'unknownColor'                                 : 16,
            'font'                                         : '$IMELanguageBar',
            'background'                                   : True,
            'backgroundImage'                              : '../maps/icons/quests/inBattleHint.png',
            'backgroundData'                               : {'alpha': 1.0},
            'shadow'                                       : False,
            'panelSize'                                    : {'widthAlt': 163, 'heightAlt': 80, 'widthNormal': 163, 'heightNormal': 50},
            'panel'                                        : {'x': 230, 'y': -228, 'width': 163, 'height': 50, 'drag': True, 'border': True, 'alignX': COMPONENT_ALIGN.LEFT, 'alignY': COMPONENT_ALIGN.BOTTOM},
            'shadowText'                                   : {'distance': 0, 'angle': 0, 'color': 0x000000, "alpha": 1, 'blurX': 1, 'blurY': 1, 'strength': 1, 'quality': 1},
            'battleMessage'                                : '<font size=\"14\">{currentMarkOfGun}</font> <font size=\"10\">{damageCurrentPercent}</font><font size=\"14\"> ~ {c_nextMarkOfGun}</font> <font size=\"10\">{c_damageNextPercent}</font>\n'
                                                             '<font size=\"20\">{c_battleMarkOfGun}{status}</font><font size=\"14\">{c_damageCurrent}</font>',

            'battleMessageAlt'                             : '<font size=\"14\">{currentMarkOfGun}</font> <font size=\"10\">{damageCurrentPercent}</font><font size=\"14\"> ~ {c_nextMarkOfGun}</font> <font size=\"10\">{c_damageNextPercent}</font>\n'
                                                             '<font size=\"20\">{c_battleMarkOfGun}{status}</font><font size=\"14\">{c_damageCurrent}</font>\n'
                                                             '{c_damageToMark65}{c_damageToMark85}\n'
                                                             '{c_damageToMark95}{c_damageToMark100}',
            'battleMessage{status}Up'                      : '<img src=\"img://gui/maps/icons/messenger/status/24x24/chat_icon_user_is_online.png\" vspace=\"-5\"/>',
            'battleMessage{c_status}Up'                    : 'Δ',
            'battleMessage{status}Down'                    : '<img src=\"img://gui/maps/icons/messenger/status/24x24/chat_icon_user_is_busy.png\" vspace=\"-5\"/>',
            'battleMessage{c_status}Down'                  : 'V',
            'battleMessage{status}Unknown'                 : '<img src=\"img://gui/maps/icons/messenger/status/24x24/chat_icon_user_is_busy_violet.png\" vspace=\"-5\"/>',
            'battleMessage{c_status}Unknown'               : '~',
            'battleMessage{battleMarkOfGun}'               : '%.2f%%',
            'battleMessage{c_battleMarkOfGun}'             : '%s',
            'battleMessage{currentMarkOfGun}'              : '%.2f%%',
            'battleMessage{c_currentMarkOfGun}'            : '%s',
            'battleMessage{nextMarkOfGun}'                 : '%.1f%%',
            'battleMessage{c_nextMarkOfGun}'               : '%s',
            'battleMessage{damageCurrent}'                 : '[<b>%.0f</b>]',
            'battleMessage{c_damageCurrent}'               : '%s',
            'battleMessage{damageCurrentPercent}'          : '[<b>%.0f</b>]',
            'battleMessage{c_damageCurrentPercent}'        : '%s',
            'battleMessage{damageNextPercent}'             : '[<b>%.0f</b>]',
            'battleMessage{c_damageNextPercent}'           : '%s',
            'battleMessage{damageToMark65}'                : '<b>65%%:%.0f</b>, ',
            'battleMessage{c_damageToMark65}'              : '%s',
            'battleMessage{damageToMark85}'                : '<b>85%%:%.0f</b>',
            'battleMessage{c_damageToMark85}'              : '%s',
            'battleMessage{damageToMark95}'                : '<b>95%%:%.0f</b>, ',
            'battleMessage{c_damageToMark95}'              : '%s',
            'battleMessage{damageToMark100}'               : '<b>100%%:%.0f</b>',
            'battleMessage{c_damageToMark100}'             : '%s',
            'battleMessage{damageToMarkInfo}'              : '%s',
            'battleMessage{c_damageToMarkInfo}'            : '%s',
            'battleMessage{damageToMarkInfoLevel}'         : '%s%%',
            'battleMessage{c_damageToMarkInfoLevel}'       : '%s',
            'UI'                                           : 4
        }
        self.i18n = {
            'version'                                                         : self.version_id,
            'UI_description'                                                  : 'Marks of Excellence Extended',
            'UI_message'                                                      : 'MoE change visual %s',
            'UI_setting_buttonShow_text'                                      : 'Button: Change Style',
            'UI_setting_buttonShow_tooltip'                                   : '',
            'UI_setting_showInBattle_text'                                    : 'Battle: enabled',
            'UI_setting_showInBattle_tooltip'                                 : '',
            'UI_setting_showInReplay_text'                                    : 'Replay[test]: enabled',
            'UI_setting_showInReplay_tooltip'                                 : '{HEADER}Show in replay{/HEADER}{BODY}Not good, but useful for tests{/BODY}',
            'UI_setting_showInStatistic_text'                                 : 'Statistic: enabled',
            'UI_setting_showInStatistic_tooltip'                              : '',
            'UI_setting_upColor_text'                                         : 'Battle: color when % mark up',
            'UI_setting_upColor_tooltip'                                      : '',
            'UI_setting_downColor_text'                                       : 'Battle: color when % mark down',
            'UI_setting_downColor_tooltip'                                    : '',
            'UI_setting_unknownColor_text'                                    : 'Battle: color when % mark unknown',
            'UI_setting_unknownColor_tooltip'                                 : '',
            'UI_setting_background_text'                                      : 'Battle: show background',
            'UI_setting_background_tooltip'                                   : '',
            'UI_setting_showInTechTree_text'                                  : 'TechTree: enabled',
            'UI_setting_showInTechTree_tooltip'                               : '',
            'UI_setting_showInTechTreeMastery_text'                           : 'TechTree: show Mastery',
            'UI_setting_showInTechTreeMastery_tooltip'                        : '',
            'UI_setting_showInTechTreeMarkOfGunPercent_text'                  : 'TechTree: show MoE %',
            'UI_setting_showInTechTreeMarkOfGunPercent_tooltip'               : '',
            'UI_setting_showInTechTreeMarkOfGunTankNameColored_text'          : 'TechTree: MoE colorize vehicle name',
            'UI_setting_showInTechTreeMarkOfGunTankNameColored_tooltip'       : '',
            'UI_setting_showInTechTreeMarkOfGunPercentFirst_text'             : 'TechTree: show MoE % first then vehicle name',
            'UI_setting_showInTechTreeMarkOfGunPercentFirst_tooltip'          : '',
            'UI_setting_techTreeMarkOfGunTankNameColoredOnlyMarkOfGun_text'   : 'TechTree: MoE colorize vehicle name when get MoE',
            'UI_setting_techTreeMarkOfGunTankNameColoredOnlyMarkOfGun_tooltip': '',
            'UI_setting_techTreeMasterySize_text'                             : 'TechTree: Mastery icon size',
            'UI_setting_techTreeMasterySize_value'                            : '',
            'UI_setting_techTreeMarkOfGunPercentSize_text'                    : 'TechTree: MoE % font size',
            'UI_setting_techTreeMarkOfGunPercentSize_value'                   : '',
            'UI_setting_UI_text'                                              : 'UI in battle',
            'UI_setting_UI_tooltip'                                           : '{HEADER}UI in battle{/HEADER}{BODY}'
                                                                                'Extended:<br/><img src=\"img://objects/ui_extended.png\"></img><br/>'
                                                                                'Simple:<br/><img src=\"img://objects/ui_simple.png\"></img><br/>'
                                                                                'Config:<br/>/mods/configs/marksOnGunExtended/marksOnGunExtended.json<br/>'
                                                                                '{/BODY}',
            'UI_menu_UIMinimal'                                               : 'Minimal',
            'UI_menu_UINormal'                                                : 'Normal',
            'UI_menu_UIMaximum'                                               : 'Maximum 1',
            'UI_menu_UIMaximum2'                                              : 'Maximum 2',
            'UI_menu_UIConfig'                                                : 'Config',
            'UI_menu_blue'                                                    : 'Blue',
            'UI_menu_brown'                                                   : 'Brown',
            'UI_menu_chocolate'                                               : 'Chocolate',
            'UI_menu_cornflower_blue'                                         : 'Cornflower Blue',
            'UI_menu_cream'                                                   : 'Cream',
            'UI_menu_cyan'                                                    : 'Cyan',
            'UI_menu_emerald'                                                 : 'Emerald',
            'UI_menu_gold'                                                    : 'Gold',
            'UI_menu_green'                                                   : 'Green',
            'UI_menu_green_yellow'                                            : 'Green Yellow',
            'UI_menu_hot_pink'                                                : 'Hot Pink',
            'UI_menu_lime'                                                    : 'Lime',
            'UI_menu_orange'                                                  : 'Orange',
            'UI_menu_pink'                                                    : 'Pink',
            'UI_menu_purple'                                                  : 'Purple',
            'UI_menu_red'                                                     : 'Red',
            'UI_menu_wg_blur'                                                 : 'WG Blur',
            'UI_menu_wg_enemy'                                                : 'WG Enemy',
            'UI_menu_wg_friend'                                               : 'WG Friend',
            'UI_menu_wg_squad'                                                : 'WG Squad',
            'UI_menu_yellow'                                                  : 'Yellow',
            'UI_menu_nice_red'                                                : 'Nice Red',
            'UI_menu_white'                                                   : 'White',
            'UI_tooltips'                                                     : '<font color=\"#FFFFFF\" size=\"12\">{currentDamage} current total damage</font>\n'
                                                                                'To <font color=\"#FFFFFF\" size=\"12\">{nextPercent}% </font>   need <font color=\"#FFFFFF\" size=\"12\">{needDamage}</font> total damage\n'
                                                                                'This statistic available to last battle on this vehicle\n'
                                                                                'To <font color=\"#FFFFFF\" size=\"12\">20% </font>   need <font color=\"#F8F400\" size=\"12\">~{_20}</font> total damage\n'
                                                                                'To <font color=\"#FFFFFF\" size=\"12\">40% </font>   need <font color=\"#F8F400\" size=\"12\">~{_40}</font> total damage\n'
                                                                                'To <font color=\"#FFFFFF\" size=\"12\">55% </font>   need <font color=\"#F8F400\" size=\"12\">~{_55}</font> total damage\n'
                                                                                'To <font color=\"#FFFFFF\" size=\"12\">65% </font>   need <font color=\"#60FF00\" size=\"12\">~{_65}</font> total damage\n'
                                                                                'To <font color=\"#FFFFFF\" size=\"12\">85% </font>   need <font color=\"#02C9B3\" size=\"12\">~{_85}</font> total damage\n'
                                                                                'To <font color=\"#FFFFFF\" size=\"12\">95% </font>   need <font color=\"#D042F3\" size=\"12\">~{_95}</font> total damage\n'
                                                                                'To <font color=\"#FFFFFF\" size=\"12\">100% </font>  need <font color=\"#D042F3\" size=\"12\">~{_100}</font> total damage\n'
                                                                                'Used statistic after patch 0.8.8'
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        self.values = {}
        self.values = g_gui.register_data('%s_stats' % self.ids, self.values, {})[0]
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [
                {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showInStatistic_text'],
                    'value'  : self.data['showInStatistic'],
                    'tooltip': self.i18n['UI_setting_showInStatistic_tooltip'],
                    'varName': 'showInStatistic'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showInReplay_text'],
                    'value'  : self.data['showInReplay'],
                    'tooltip': self.i18n['UI_setting_showInReplay_tooltip'],
                    'varName': 'showInReplay'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showInBattle_text'],
                    'value'  : self.data['showInBattle'],
                    'tooltip': self.i18n['UI_setting_showInBattle_tooltip'],
                    'varName': 'showInBattle'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_background_text'],
                    'value'  : self.data['background'],
                    'tooltip': self.i18n['UI_setting_background_tooltip'],
                    'varName': 'background'
                }, {
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_setting_UI_text'],
                    'tooltip'     : self.i18n['UI_setting_UI_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : [
                        {'label': self.i18n['UI_menu_UIConfig']},
                        {'label': self.i18n['UI_menu_UIMinimal']},
                        {'label': self.i18n['UI_menu_UINormal']},
                        {'label': self.i18n['UI_menu_UIMaximum']},
                        {'label': self.i18n['UI_menu_UIMaximum2']},

                    ],
                    'width'       : 200,
                    'value'       : self.data['UI'],
                    'varName'     : 'UI'
                }, {
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_setting_upColor_text'],
                    'tooltip'     : self.i18n['UI_setting_upColor_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : self.generator_menu(),
                    'width'       : 200,
                    'value'       : self.data['upColor'],
                    'varName'     : 'upColor'
                }, {
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_setting_downColor_text'],
                    'tooltip'     : self.i18n['UI_setting_downColor_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : self.generator_menu(),
                    'width'       : 200,
                    'value'       : self.data['downColor'],
                    'varName'     : 'downColor'
                }, {
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_setting_unknownColor_text'],
                    'tooltip'     : self.i18n['UI_setting_unknownColor_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : self.generator_menu(),
                    'width'       : 200,
                    'value'       : self.data['unknownColor'],
                    'varName'     : 'unknownColor'
                }
            ],
            'column2'        : [
                {
                    'type'        : 'HotKey',
                    'text'        : self.i18n['UI_setting_buttonShow_text'],
                    'tooltip'     : self.i18n['UI_setting_buttonShow_tooltip'],
                    'value'       : self.data['buttonShow'],
                    'defaultValue': self.buttons['buttonShow'],
                    'varName'     : 'buttonShow'
                },
                {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showInTechTree_text'],
                    'value'  : self.data['showInTechTree'],
                    'tooltip': self.i18n['UI_setting_showInTechTree_tooltip'],
                    'varName': 'showInTechTree'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showInTechTreeMastery_text'],
                    'value'  : self.data['showInTechTreeMastery'],
                    'tooltip': self.i18n['UI_setting_showInTechTreeMastery_tooltip'],
                    'varName': 'showInTechTreeMastery'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showInTechTreeMarkOfGunPercent_text'],
                    'value'  : self.data['showInTechTreeMarkOfGunPercent'],
                    'tooltip': self.i18n['UI_setting_showInTechTreeMarkOfGunPercent_tooltip'],
                    'varName': 'showInTechTreeMarkOfGunPercent'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showInTechTreeMarkOfGunTankNameColored_text'],
                    'value'  : self.data['showInTechTreeMarkOfGunTankNameColored'],
                    'tooltip': self.i18n['UI_setting_showInTechTreeMarkOfGunTankNameColored_tooltip'],
                    'varName': 'showInTechTreeMarkOfGunTankNameColored'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showInTechTreeMarkOfGunPercentFirst_text'],
                    'value'  : self.data['showInTechTreeMarkOfGunPercentFirst'],
                    'tooltip': self.i18n['UI_setting_showInTechTreeMarkOfGunPercentFirst_tooltip'],
                    'varName': 'showInTechTreeMarkOfGunPercentFirst'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_techTreeMarkOfGunTankNameColoredOnlyMarkOfGun_text'],
                    'value'  : self.data['techTreeMarkOfGunTankNameColoredOnlyMarkOfGun'],
                    'tooltip': self.i18n['UI_setting_techTreeMarkOfGunTankNameColoredOnlyMarkOfGun_tooltip'],
                    'varName': 'techTreeMarkOfGunTankNameColoredOnlyMarkOfGun'
                }, {
                    'type'        : 'Slider',
                    'text'        : self.i18n['UI_setting_techTreeMasterySize_text'],
                    'minimum'     : 1,
                    'maximum'     : 48,
                    'snapInterval': 1,
                    'value'       : self.data['techTreeMasterySize'],
                    'format'      : '{{value}}%s' % self.i18n['UI_setting_techTreeMasterySize_value'],
                    'varName'     : 'techTreeMasterySize'
                }, {
                    'type'        : 'Slider',
                    'text'        : self.i18n['UI_setting_techTreeMarkOfGunPercentSize_text'],
                    'minimum'     : 1,
                    'maximum'     : 48,
                    'snapInterval': 1,
                    'value'       : self.data['techTreeMarkOfGunPercentSize'],
                    'format'      : '{{value}}%s' % self.i18n['UI_setting_techTreeMarkOfGunPercentSize_value'],
                    'varName'     : 'techTreeMarkOfGunPercentSize'
                }]
        }

    def generator_menu(self):
        res = []
        for i in xrange(len(COLOR)):
            res.append({
                'label': '<font color="%s">%s</font>' % (COLOR[i], self.i18n[MENU[i]])
            })
        return res

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class Worker(object):
    def __init__(self):
        InputHandler.g_instance.onKeyDown += self.keyPressed
        InputHandler.g_instance.onKeyUp += self.keyPressed
        self.altMode = False
        self.movingAvgDamage = 0.0
        self.damageRating = 0.0
        self.battleDamage = 0.0
        self.battleCount = 0
        self.RADIO_ASSIST = 0.0
        self.TRACK_ASSIST = 0.0
        self.STUN_ASSIST = 0.0
        self.TANKING = 0.0
        self.killed = False
        self.level = False
        self.values = [0, 0, 0, 0]
        self.name = ''
        self.dossier = None
        self.initiated = False
        self.replay = False
        self.formatStrings = {
            'status'                 : '',
            'battleMarkOfGun'        : '',
            'currentMarkOfGun'       : '',
            'nextMarkOfGun'          : '',
            'damageCurrent'          : '',
            'damageCurrentPercent'   : '',
            'damageNextPercent'      : '',
            'damageToMark65'         : '',
            'damageToMark85'         : '',
            'damageToMark95'         : '',
            'damageToMark100'        : '',
            'damageToMarkInfo'       : '',
            'damageToMarkInfoLevel'  : '',
            'c_status'               : '',
            'c_battleMarkOfGun'      : '',
            'c_currentMarkOfGun'     : '',
            'c__nextMarkOfGun'       : '',
            'c_damageCurrent'        : '',
            'c_damageCurrentPercent' : '',
            'c_damageNextPercent'    : '',
            'c_damageToMark65'       : '',
            'c_damageToMark85'       : '',
            'c_damageToMark95'       : '',
            'c_damageToMark100'      : '',
            'c_damageToMarkInfo'     : '',
            'c_damageToMarkInfoLevel': '',
            'colorOpen'              : '<font color="{color}">',
            'colorClose'             : '</font>',
            'color'                  : ''
        }
        self.messages = {
            'battleMessageMinimal'    : '<font size=\"20\">{c_battleMarkOfGun} ({currentMarkOfGun}){status}</font>\n',
            'battleMessageMinimalAlt' : '<font size=\"20\">{c_battleMarkOfGun} ({currentMarkOfGun}){status}</font>\n'
                                        '{c_damageCurrent} ({damageCurrentPercent})',

            'battleMessageNormal'     : '<font size=\"20\">{c_battleMarkOfGun}{c_damageCurrent}{status}</font>\n',
            'battleMessageNormalAlt'  : '<font size=\"20\">{c_battleMarkOfGun}{c_damageCurrent}{status}</font>\n'
                                        '<font size=\"15\">{currentMarkOfGun}{damageCurrentPercent}</font>',

            'battleMessageMaximum'    : '<font size=\"20\">{c_battleMarkOfGun}:{c_damageCurrent}{status}</font>\n'
                                        '<font size=\"15\">{c_nextMarkOfGun}:{c_damageNextPercent}</font>\n'
                                        '<font size=\"15\">{currentMarkOfGun}:{damageCurrentPercent}</font>',

            'battleMessageMaximumAlt' : '<font size=\"20\">{c_battleMarkOfGun}:{c_damageCurrent}{status}</font>\n'
                                        '<font size=\"15\">{c_nextMarkOfGun}:{c_damageNextPercent}</font>\n'
                                        '<font size=\"15\">{currentMarkOfGun}:{damageCurrentPercent}</font>\n'
                                        '{c_damageToMark65}{c_damageToMark85}\n'
                                        '{c_damageToMark95}{c_damageToMark100}',
            'battleMessageMaximum2'   : '<font size=\"14\">{currentMarkOfGun}</font> <font size=\"10\">{damageCurrentPercent}</font><font size=\"14\"> ~ {c_nextMarkOfGun}</font> <font size=\"10\">{c_damageNextPercent}</font>\n'
                                        '<font size=\"20\">{c_battleMarkOfGun}{status}</font><font size=\"14\">{c_damageCurrent}</font>',

            'battleMessageMaximum2Alt': '<font size=\"14\">{currentMarkOfGun}</font> <font size=\"10\">{damageCurrentPercent}</font><font size=\"14\"> ~ {c_nextMarkOfGun}</font> <font size=\"10\">{c_damageNextPercent}</font>\n'
                                        '<font size=\"20\">{c_battleMarkOfGun}{status}</font><font size=\"14\">{c_damageCurrent}</font>\n'
                                        '{c_damageToMark65}{c_damageToMark85}\n'
                                        '{c_damageToMark95}{c_damageToMark100}',
        }
        self.levels = []
        self.damages = []
        self.battleMessage = config.data['battleMessage'] if not self.altMode else config.data['battleMessageAlt']
        self.checkBattleMessage()
        self.health = {}
        self.battleDamageRatingIndex = []

    def checkBattleMessage(self):
        if not config.data['UI']:
            self.battleMessage = config.data['battleMessage'] if not self.altMode else config.data['battleMessageAlt']
        if config.data['UI'] == 1:
            self.battleMessage = self.messages['battleMessageMinimal'] if not self.altMode else self.messages['battleMessageMinimalAlt']

        if config.data['UI'] == 2:
            self.battleMessage = self.messages['battleMessageNormal'] if not self.altMode else self.messages['battleMessageNormalAlt']

        if config.data['UI'] == 3:
            self.battleMessage = self.messages['battleMessageMaximum'] if not self.altMode else self.messages['battleMessageMaximumAlt']

        if config.data['UI'] == 4:
            self.battleMessage = self.messages['battleMessageMaximum2'] if not self.altMode else self.messages['battleMessageMaximum2Alt']

    def clearData(self):
        self.altMode = False
        self.movingAvgDamage = 0.0
        self.damageRating = 0.0
        self.battleDamage = 0.0
        self.battleCount = 0
        self.RADIO_ASSIST = 0.0
        self.TRACK_ASSIST = 0.0
        self.STUN_ASSIST = 0.0
        self.TANKING = 0.0
        self.killed = False
        self.level = False
        self.values = [0, 0, 0, 0]
        self.name = ''
        self.initiated = False
        self.replay = False
        self.formatStrings = {
            'status'                 : '',
            'battleMarkOfGun'        : '',
            'currentMarkOfGun'       : '',
            'nextMarkOfGun'          : '',
            'damageCurrent'          : '',
            'damageCurrentPercent'   : '',
            'damageNextPercent'      : '',
            'damageToMark65'         : '',
            'damageToMark85'         : '',
            'damageToMark95'         : '',
            'damageToMark100'        : '',
            'damageToMarkInfo'       : '',
            'damageToMarkInfoLevel'  : '',
            'c_status'               : '',
            'c_battleMarkOfGun'      : '',
            'c_currentMarkOfGun'     : '',
            'c__nextMarkOfGun'       : '',
            'c_damageCurrent'        : '',
            'c_damageCurrentPercent' : '',
            'c_damageNextPercent'    : '',
            'c_damageToMark65'       : '',
            'c_damageToMark85'       : '',
            'c_damageToMark95'       : '',
            'c_damageToMark100'      : '',
            'c_damageToMarkInfo'     : '',
            'c_damageToMarkInfoLevel': '',
            'colorOpen'              : '<font color="{color}">',
            'colorClose'             : '</font>',
            'color'                  : ''
        }
        self.levels = []
        self.damages = []
        self.checkBattleMessage()
        self.health.clear()
        self.battleDamageRatingIndex = []

    @inject.log
    def getCurrentHangarData(self):
        if g_currentVehicle.item:
            self.damageRating = g_currentVehicle.getDossier().getRecordValue(ACHIEVEMENT_BLOCK.TOTAL, 'damageRating') / 100.0
            self.movingAvgDamage = g_currentVehicle.getDossier().getRecordValue(ACHIEVEMENT_BLOCK.TOTAL, 'movingAvgDamage')
            self.battleCount = g_currentVehicle.getDossier().getRandomStats().getBattlesCountVer2()
            self.level = g_currentVehicle.item.level > 4
            self.name = '%s' % g_currentVehicle.item.name
            if self.level and self.movingAvgDamage:
                dBid = self.check_player_thread()
                if dBid not in config.values:
                    config.values[dBid] = {}
                if self.name in config.values[dBid]:
                    self.requestCurData(self.damageRating, self.movingAvgDamage)
                else:
                    self.requestNewData(self.damageRating, self.movingAvgDamage)
                config.values = g_gui.update_data('%s_stats' % config.ids, config.values)

    def onBattleEvents(self, events):
        if not config.data['enabled']: return
        if not config.data['showInBattle']: return
        player = BigWorld.player()
        guiSessionProvider = player.guiSessionProvider
        if guiSessionProvider.shared.vehicleState.getControllingVehicleID() == player.playerVehicleID:
            for data in events:
                feedbackEvent = feedback_events.PlayerFeedbackEvent.fromDict(data)
                eventType = feedbackEvent.getBattleEventType()
                if eventType in DAMAGE_EVENTS:
                    extra = feedbackEvent.getExtra()
                    if extra:
                        if eventType == BATTLE_EVENT_TYPE.RADIO_ASSIST:
                            self.RADIO_ASSIST += float(extra.getDamage())
                        if eventType == BATTLE_EVENT_TYPE.TRACK_ASSIST:
                            self.TRACK_ASSIST += float(extra.getDamage())
                        if eventType == BATTLE_EVENT_TYPE.STUN_ASSIST:
                            self.STUN_ASSIST += float(extra.getDamage())
                        if eventType == BATTLE_EVENT_TYPE.TANKING:
                            self.TANKING += float(extra.getDamage())
                        if eventType == BATTLE_EVENT_TYPE.DAMAGE:
                            arenaDP = guiSessionProvider.getArenaDP()
                            if arenaDP.isEnemyTeam(arenaDP.getVehicleInfo(feedbackEvent.getTargetID()).team):
                                self.battleDamage += float(extra.getDamage())
            self.calc()

    def shots(self, avatar, newHealth, attackerID):
        if not config.data['enabled']: return
        if not config.data['showInBattle']: return
        if not avatar.isStarted:
            return
        if newHealth > 0 >= avatar.health:
            return
        player = BigWorld.player()
        if avatar.id not in self.health:
            self.health[avatar.id] = max(0, avatar.health)
        if not avatar.isPlayerVehicle and attackerID == player.playerVehicleID:
            arenaDP = player.guiSessionProvider.getArenaDP()
            vo = arenaDP.getVehicleInfo(avatar.id)
            if not arenaDP.isEnemyTeam(vo.team):
                self.battleDamage -= float(max(0, self.health[avatar.id] - newHealth))
                self.calc()
        self.health[avatar.id] = max(0, avatar.health)

    def initVehicle(self, avatar):
        if not avatar.isStarted:
            return
        self.health[avatar.id] = max(0, avatar.health)

    def requestNewData(self, damageRating, movingAvgDamage):
        p0 = 0
        d0 = 0
        p1 = damageRating
        d1 = movingAvgDamage
        self.values = [p0, d0, p1, d1]
        config.values[self.check_player_thread()][self.name] = self.values
        self.initiated = False

    def requestCurData(self, damageRating, movingAvgDamage):
        self.values = config.values[self.check_player_thread()][self.name]
        if movingAvgDamage not in self.values:
            p0 = self.values[2]
            d0 = self.values[3]
            p1 = damageRating
            d1 = movingAvgDamage
            if p0 == p1 and d0 == d1:
                d1 += 1
            self.values = [p0, d0, p1, d1]  # if p1 > p0 else [p1, d1, p0, d0]
            config.values[self.check_player_thread()][self.name] = self.values
        EDn = self.battleDamage + max(self.RADIO_ASSIST, self.TRACK_ASSIST, self.STUN_ASSIST)
        k = 0.0198019801980198022206547392443098942749202251434326171875  # 2 / (100.0 + 1)
        EMA = k * EDn + (1 - k) * self.movingAvgDamage
        p0, d0, p1, d1 = self.values
        result = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0) if p0 != 100.0 or p1 != 100.0 else 100.0
        nextMark = round(min(100.0, result), 2) if result > 0 else 0.0
        self.initiated = self.values[1] and not nextMark >= self.damageRating and not self.damageRating - nextMark > 3

    def getColor(self, percent, damage):
        a = filter(lambda x: x <= round(percent, 2), self.levels)
        i = self.levels.index(a[-1]) if a else 0
        n = max(2, min(i + 1, len(self.levels) - 1))
        idx = filter(lambda x: x >= damage, self.battleDamageRatingIndex)
        colorNowDamage = battleDamageRating[self.battleDamageRatingIndex.index(idx[0])] if idx else battleDamageRating[-1]
        idx = filter(lambda x: x >= self.damages[n], self.battleDamageRatingIndex)
        colorNextDamage = battleDamageRating[self.battleDamageRatingIndex.index(idx[0])] if idx else battleDamageRating[-1]
        idx = filter(lambda x: x >= percent, LEVELS)[0]
        colorNextPercent = battleDamageRating[LEVELS.index(idx)] if idx else battleDamageRating[-1]
        return self.levels[n], self.damages[n], colorNowDamage, colorNextDamage, colorNextPercent

    def calcBattlePercents(self):
        p0, d0, p1, d1 = self.values
        curPercent = p1
        nextPercent = float(int(curPercent + 1))
        halfPercent = nextPercent - curPercent >= 0.5
        EDn = 0
        k = 0.0198019801980198022206547392443098942749202251434326171875  # 2 / (100.0 + 1)
        EMA = k * EDn + (1 - k) * d1
        start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(start)
        self.damages.append(EDn)
        while start <= curPercent and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.formatStrings['damageCurrentPercent'] = config.data['battleMessage{damageCurrentPercent}'] % EDn  # if d0 and self.initiated or self.replay else '[--]'
        self.levels.append(curPercent)
        self.damages.append(EDn)
        if halfPercent:
            halfPercent = nextPercent - 0.5
            while start <= halfPercent and 0 <= start <= 100:
                EDn += 1
                EMA = k * EDn + (1 - k) * d1
                start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
            self.levels.append(halfPercent)
            self.damages.append(EDn)

        while start <= nextPercent and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent)
        self.damages.append(EDn)

        nextPercent_0_5 = nextPercent + 0.5
        while start <= nextPercent_0_5 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent_0_5)
        self.damages.append(EDn)

        nextPercent1 = nextPercent + 1.0
        while start <= nextPercent1 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent1)
        self.damages.append(EDn)

        nextPercent1_5 = nextPercent + 1.5
        while start <= nextPercent1_5 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent1_5)
        self.damages.append(EDn)

        nextPercent2 = nextPercent + 2.0
        while start <= nextPercent2 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent2)
        self.damages.append(EDn)

        nextPercent2_5 = nextPercent + 2.5
        while start <= nextPercent2_5 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent2_5)
        self.damages.append(EDn)

        nextPercent3 = nextPercent + 3.0
        while start <= nextPercent3 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent3)
        self.damages.append(EDn)

        nextPercent3_5 = nextPercent + 3.5
        while start <= nextPercent3_5 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent3_5)
        self.damages.append(EDn)

        nextPercent4 = nextPercent + 4.0
        while start <= nextPercent4 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent4)
        self.damages.append(EDn)

        nextPercent4_5 = nextPercent + 4.5
        while start <= nextPercent4_5 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent4_5)
        self.damages.append(EDn)

        nextPercent5 = nextPercent + 5.0
        while start <= nextPercent5 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent5)
        self.damages.append(EDn)

        nextPercent5_5 = nextPercent + 5.5
        while start <= nextPercent5_5 and 0 <= start <= 100:
            EDn += 1
            EMA = k * EDn + (1 - k) * d1
            start = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        self.levels.append(nextPercent5_5)
        self.damages.append(EDn)
        _, _, p20, p40, p55, p65, p85, p95, p100 = worker.calcStatistics(self.damageRating, self.movingAvgDamage)
        self.battleDamageRatingIndex = [0, p20, p40, p55, p65, p85, p95, p100]

        self.formatStrings['damageToMark65'] = config.data['battleMessage{damageToMark65}'] % p65
        self.formatStrings['c_damageToMark65'] = '<font color="%s">%s</font>' % (RATING['good'], self.formatStrings['damageToMark65'])

        self.formatStrings['damageToMark85'] = config.data['battleMessage{damageToMark85}'] % p85
        self.formatStrings['c_damageToMark85'] = '<font color="%s">%s</font>' % (RATING['very_good'], self.formatStrings['damageToMark85'])

        self.formatStrings['damageToMark95'] = config.data['battleMessage{damageToMark95}'] % p95
        self.formatStrings['c_damageToMark95'] = '<font color="%s">%s</font>' % (RATING['unique'], self.formatStrings['damageToMark95'])

        self.formatStrings['damageToMark100'] = config.data['battleMessage{damageToMark100}'] % p100
        self.formatStrings['c_damageToMark100'] = '<font color="%s">%s</font>' % (RATING['unique'], self.formatStrings['damageToMark100'])

        self.formatStrings['damageToMarkInfo'] = config.data['battleMessage{damageToMarkInfo}'] % self.formatStrings['damageToMark100']
        self.formatStrings['c_damageToMarkInfo'] = config.data['battleMessage{c_damageToMarkInfo}'] % self.formatStrings['damageToMarkInfo']
        self.formatStrings['damageToMarkInfoLevel'] = config.data['battleMessage{damageToMarkInfoLevel}'] % 100
        self.formatStrings['c_damageToMarkInfoLevel'] = config.data['battleMessage{c_damageToMarkInfo}'] % self.formatStrings['damageToMarkInfoLevel']

        for i in [65, 85, 95, 100]:
            if self.damageRating < i:
                self.formatStrings['damageToMarkInfo'] = config.data['battleMessage{damageToMarkInfo}'] % self.formatStrings['damageToMark%s' % i]
                self.formatStrings['c_damageToMarkInfo'] = config.data['battleMessage{c_damageToMarkInfo}'] % self.formatStrings['c_damageToMark%s' % i]
                self.formatStrings['damageToMarkInfoLevel'] = config.data['battleMessage{damageToMarkInfoLevel}'] % i
                self.formatStrings['c_damageToMarkInfoLevel'] = config.data['battleMessage{c_damageToMarkInfo}'] % self.formatStrings['damageToMarkInfoLevel']
                break

    def checkMark(self, nextMark):
        for i in [65.0, 85.0, 95.0, 100.0]:
            if self.damageRating < i <= nextMark:
                return True
        return

    def keyPressed(self, event):
        if not config.data['enabled']: return
        if not g_appLoader.getDefBattleApp(): return
        if self.level and self.movingAvgDamage:
            isKeyDownTrigger = event.isKeyDown()
            
            if event.key in [Keys.KEY_LALT, Keys.KEY_RALT]:
                if isKeyDownTrigger:
                    self.altMode = True
                    self.checkBattleMessage()
                    flash.setupSize()
                    self.calc()
                if event.isKeyUp():
                    self.altMode = False
                    self.checkBattleMessage()
                    flash.setupSize()
                    self.calc()
            if g_gui.get_key(config.data['buttonShow']) and isKeyDownTrigger:
                config.data['UI'] += 1
                if config.data['UI'] > 4:
                    config.data['UI'] = 1
                status = [config.i18n['UI_menu_UIConfig'], config.i18n['UI_menu_UIMinimal'], config.i18n['UI_menu_UINormal'], config.i18n['UI_menu_UIMaximum'], config.i18n['UI_menu_UIMaximum2']]
                message = config.i18n['UI_message'] % status[config.data['UI']]
                color = '#84DE40'
                inject.message(message, color)
                config.data = g_gui.update_data(config.ids, config.data, 'spoter')
                self.checkBattleMessage()
                flash.setupSize()
                self.calc()

    def calc(self):
        if not config.data['enabled']      : return
        if not config.data['showInBattle'] : return
        if not self.level                  : return
        if not self.movingAvgDamage        : return
        EDn = self.battleDamage + max(self.RADIO_ASSIST, self.TRACK_ASSIST, self.STUN_ASSIST)
        k = 0.0198019801980198022206547392443098942749202251434326171875  # 2 / (100.0 + 1)
        EMA = k * EDn + (1 - k) * self.movingAvgDamage
        p0, d0, p1, d1 = self.values
        result = p0 + (EMA - d0) / (d1 - d0) * (p1 - p0)
        nextMark = round(min(100.0, result), 2) if result > 0.0 else 0.0
        unknown = False
        if d0 and self.initiated or self.replay:
            if nextMark >= self.damageRating:
                self.formatStrings['color'] = '%s' % COLOR[config.data['upColor']]
                if self.checkMark(nextMark):
                    self.formatStrings['color'] = '#D042F3'
                self.formatStrings['status'] = config.data['battleMessage{status}Up']
                self.formatStrings['c_status'] = '%s%s%s' % (self.formatStrings['colorOpen'], config.data['battleMessage{c_status}Up'], self.formatStrings['colorClose'])
            else:
                self.formatStrings['color'] = '%s' % COLOR[config.data['downColor']]
                if self.checkMark(nextMark):
                    self.formatStrings['color'] = '#D042F3'
                self.formatStrings['status'] = config.data['battleMessage{status}Down']
                self.formatStrings['c_status'] = '%s%s%s' % (self.formatStrings['colorOpen'], config.data['battleMessage{c_status}Down'], self.formatStrings['colorClose'])
        else:
            self.formatStrings['color'] = '%s' % COLOR[config.data['unknownColor']]
            self.formatStrings['status'] = config.data['battleMessage{status}Unknown']
            self.formatStrings['c_status'] = '%s%s%s' % (self.formatStrings['colorOpen'], config.data['battleMessage{c_status}Unknown'], self.formatStrings['colorClose'])
            unknown = True
        self.formatStrings['battleMarkOfGun']        = config.data['battleMessage{battleMarkOfGun}'] % nextMark  # if d0 and self.initiated or self.replay else '--.--%'
        self.formatStrings['c_battleMarkOfGun']      = '%s%s%s' % (self.formatStrings['colorOpen'], self.formatStrings['battleMarkOfGun'], self.formatStrings['colorClose'])  # if d0 and self.initiated or self.replay else '--.--%'
        nextMarkOfGun, damage, colorNowDamage, colorNextDamage, colorNextPercent = self.getColor(nextMark, EDn)
        self.formatStrings['nextMarkOfGun']          = config.data['battleMessage{nextMarkOfGun}'] % nextMarkOfGun
        self.formatStrings['c_nextMarkOfGun']        = '%s%s%s' % ('<font color="%s">' % colorNextPercent if not unknown else self.formatStrings['colorOpen'], self.formatStrings['nextMarkOfGun'], self.formatStrings['colorClose'])
        self.formatStrings['damageCurrent']          = config.data['battleMessage{damageCurrent}'] % EDn  # if d0 and self.initiated or self.replay else '[--]'
        self.formatStrings['damageNextPercent']      = config.data['battleMessage{damageNextPercent}'] % damage  # if d0 and self.initiated or self.replay else '[--]'
        self.formatStrings['c_damageCurrent']        = '%s%s%s' % ('<font color="%s">' % colorNowDamage if not unknown else self.formatStrings['colorOpen'], self.formatStrings['damageCurrent'], self.formatStrings['colorClose'])
        self.formatStrings['c_damageCurrentPercent'] = '%s%s%s' % (self.formatStrings['colorOpen'], self.formatStrings['damageCurrentPercent'], self.formatStrings['colorClose'])
        self.formatStrings['c_damageNextPercent']    = '%s%s%s' % ('<font color="%s">' % colorNextDamage if not unknown else self.formatStrings['colorOpen'], self.formatStrings['damageNextPercent'], self.formatStrings['colorClose'])
        flash.setVisible(True)
        flash.set_text(self.battleMessage.format(**self.formatStrings).format(color=self.formatStrings['color']))

    @staticmethod
    def isAvailable():
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is None: return
        return vehicle.id == BigWorld.player().playerVehicleID

    def onVehicleKilled(self, target_id, attacker_id, equipment_id, reason):
        #_, _, _ = attacker_id, reason, equipment_id
        if target_id == BigWorld.player().playerVehicleID:
            self.killed = True
            self.calc()

    def startBattle(self):
        if not config.data['enabled']: return
        if not config.data['showInBattle']: return
        self.replay = BattleReplay.isPlaying()
        if self.replay and not config.data['showInReplay']: return
        BigWorld.callback(1.0, self.treadStartBattle)
        flash.setVisible(False)

    @inject.log
    def treadStartBattle(self):
        vehicle    = BigWorld.player().getVehicleAttached()
        dBid       = self.check_player_thread()
        self.name  = vehicle.typeDescriptor.name
        self.level = vehicle.typeDescriptor.level > 4
        if dBid not in config.values:
            config.values[dBid] = {}
        if self.replay:
            if self.name in config.values[dBid]:
                values = config.values[dBid][self.name]
                
                self.damageRating    = values[2]
                self.movingAvgDamage = values[3]
            else:
                self.damageRating    = 1.0
                self.movingAvgDamage = 100.0
                
                self.name = 'ReplayTest'
        if self.level and self.movingAvgDamage:
            BigWorld.player().arena.onVehicleKilled  += self.onVehicleKilled
            self.formatStrings['currentMarkOfGun']   = config.data['battleMessage{currentMarkOfGun}'] % self.damageRating
            self.formatStrings['c_currentMarkOfGun'] = '%s%s%s' % (self.formatStrings['colorOpen'], self.formatStrings['currentMarkOfGun'], self.formatStrings['colorClose'])
            if self.name in config.values[dBid]:
                self.requestCurData(self.damageRating, self.movingAvgDamage)
            else:
                self.requestNewData(self.damageRating, self.movingAvgDamage)
            self.calcBattlePercents()
            flash.setupSize()
            self.calc()
            if 'ReplayTest' not in self.name:
                config.values = g_gui.update_data('%s_stats' % config.ids, config.values)

    def endBattle(self):
        if not config.data['enabled']                      : return
        if not config.data['showInBattle']                 : return
        if self.replay and not config.data['showInReplay'] : return
        if self.level and self.movingAvgDamage:
            BigWorld.player().arena.onVehicleKilled -= self.onVehicleKilled

    @staticmethod
    def check_player_thread():
        player = BigWorld.player()
        if hasattr(player, 'databaseID'):
            return '%s' % player.databaseID
        return '%s' % player.arena.vehicles[player.playerVehicleID]['accountDBID']

    @staticmethod
    def getNormalizeDigits(value):
        return int(math.ceil(value))

    @staticmethod
    def calcPercent(ema, start, end, d, p):
        while start <= end:
            ema += 0.1
            start = ema / d * p
        return ema

    @staticmethod
    def getNormalizeDigitsCoeff(value):
        return int(math.ceil(math.ceil(value / 10.0)) * 10)

    def calcStatisticsCoeff(self, p, d):
        pC = math.floor(p) + 1
        dC = self.calcPercent(d, p, pC, d, p)
        
        p20 = self.calcPercent(0, 0.0, 20.0, d, p)
        p40 = self.calcPercent(p20, 20.0, 40.0, d, p)
        p55 = self.calcPercent(p40, 40.0, 55.0, d, p)
        p65 = self.calcPercent(p55, 55.0, 65.0, d, p)
        p85 = self.calcPercent(p65, 65.0, 85.0, d, p)
        p95 = self.calcPercent(p85, 85.0, 95.0, d, p)
        p100 = self.calcPercent(p95, 95.0, 100.0, d, p)
        
        data = [0, p20, p40, p55, p65, p85, p95, p100]
        
        idx = filter(lambda x: x >= p, LEVELS)[0]
        
        limit1 = data[LEVELS.index(idx) - 1]
        limit2 = data[LEVELS.index(idx)]
        
        check = LEVELS.index(idx)
        
        delta = limit2 - limit1
        
        for value in xrange(len(data)):
            if data[value] == limit1 or data[value] == limit2:
                continue
            if 0 < value < check:
                data[value] -= delta
            if value > check:
                data[value] += delta
        
        if pC == 101:
            pC = 100
            dC = data[7]
        
        return pC, dC, data[1], data[2], data[3], data[4], data[5], data[6], data[7]

    def calcStatistics(self, p, d):
        pC = math.floor(p) + 1
        dC = self.calcPercent(d, p, pC, d, p)
        
        p20 = self.calcPercent(0, 0.0, 20.0, d, p)
        p40 = self.calcPercent(0, 0.0, 40.0, d, p)
        p55 = self.calcPercent(0, 0.0, 55.0, d, p)
        p65 = self.calcPercent(0, 0.0, 65.0, d, p)
        p85 = self.calcPercent(0, 0.0, 85.0, d, p)
        p95 = self.calcPercent(0, 0.0, 95.0, d, p)
        p100 = self.calcPercent(0, 0.0, 100.0, d, p)
        
        data = [0, p20, p40, p55, p65, p85, p95, p100]
        
        idx = filter(lambda x: x >= p, LEVELS)[0]
        
        limit1 = dC
        limit2 = data[LEVELS.index(idx)]
        
        check = LEVELS.index(idx)
        
        delta = limit2 - limit1
        
        for value in xrange(len(data)):
            if data[value] == limit1 or data[value] == limit2:
                continue
            if value > check:
                data[value] = self.getNormalizeDigitsCoeff(data[value] + delta)
        
        if pC == 101:
            pC = 100
            dC = data[7]
        
        return pC, dC, data[1], data[2], data[3], data[4], data[5], data[6], data[7]


class Flash(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.name = {}
        self.data = {}

    def startBattle(self):
        if not config.data['enabled']                                   : return
        if not config.data['showInBattle']                              : return
        if BattleReplay.isPlaying() and not config.data['showInReplay'] : return
        self.setup()
        COMPONENT_EVENT.UPDATED += self.update
        self.createObject(COMPONENT_TYPE.PANEL)
        if config.data['background']:
            self.createObject(COMPONENT_TYPE.IMAGE)
            self.updateObject(COMPONENT_TYPE.IMAGE, self.data['backgroundData'])
        self.createObject(COMPONENT_TYPE.LABEL)
        if config.data['shadow']:
            self.updateObject(COMPONENT_TYPE.LABEL, self.data['shadow'])
        else:
            self.updateObject(COMPONENT_TYPE.LABEL, {'shadow': {"distance": 0, "angle": 0, "color": 0x000000, "alpha": 0, "blurX": 0, "blurY": 0, "strength": 0, "quality": 0}})
        g_guiResetters.add(self.screenResize)
        self.screenResize()

    def stopBattle(self):
        if not config.data['enabled']                                   : return
        if not config.data['showInBattle']                              : return
        if BattleReplay.isPlaying() and not config.data['showInReplay'] : return
        g_guiResetters.remove(self.screenResize)
        COMPONENT_EVENT.UPDATED -= self.update
        self.deleteObject(COMPONENT_TYPE.PANEL)
        if config.data['background']:
            self.deleteObject(COMPONENT_TYPE.IMAGE)
        self.deleteObject(COMPONENT_TYPE.LABEL)

    def deleteObject(self, name):
        g_guiFlash.deleteComponent(self.name[name])

    def createObject(self, name):
        g_guiFlash.createComponent(self.name[name], name, self.data[name])

    def updateObject(self, name, data):
        g_guiFlash.updateComponent(self.name[name], data)

    @inject.log
    def update(self, alias, props):
        # Component "testSprite" updated : {'y': 32.0, 'x': 256.0}
        if str(alias) == str(config.ids):
            x = int(props.get('x', config.data['panel']['x']))
            if x and x != int(config.data['panel']['x']):
                config.data['panel']['x'] = x
                self.data[COMPONENT_TYPE.PANEL]['x'] = x
            y = int(props.get('y', config.data['panel']['y']))
            if y and y != int(config.data['panel']['y']):
                config.data['panel']['y'] = y
                self.data[COMPONENT_TYPE.PANEL]['y'] = y
            self.screenResize()
            print '%s Flash coordinates updated : x = %i, y = %i, props: %s' % (alias, config.data['panel']['x'], config.data['panel']['y'], props)

    def setup(self):
        self.name = {
            COMPONENT_TYPE.PANEL: config.ids,
            COMPONENT_TYPE.IMAGE: '%s.%s' % (config.ids, 'image'),
            COMPONENT_TYPE.LABEL: '%s.%s' % (config.ids, 'text')
        }
        self.data = {
            COMPONENT_TYPE.PANEL: config.data.get('panel'),
            COMPONENT_TYPE.IMAGE: {'image': config.data.get('backgroundImage')},
            'backgroundData'    : config.data.get('backgroundData'),
            COMPONENT_TYPE.LABEL: {'text': '', 'index': 1, 'multiline': True},
            'shadow'            : {'shadow': config.data.get('shadowText')}
        }
        # for name in self.data:
        #    self.data[name]['width'] = config.data['panel'].get('width')
        #    self.data[name]['height'] = config.data['panel'].get('height')

    def setupSize(self):
        height = int(config.data['panelSize'].get('heightNormal', 50)) if not worker.altMode else int(config.data['panelSize'].get('heightAlt', 80))
        width = int(config.data['panelSize'].get('widthNormal', 163)) if not worker.altMode else int(config.data['panelSize'].get('widthAlt', 163))
        if config.data['UI'] == 1:
            height = 30 if not worker.altMode else 45
            width = 152 if not worker.altMode else 152
        if config.data['UI'] == 2:
            height = 30 if not worker.altMode else 50
            width = 130 if not worker.altMode else 130
        if config.data['UI'] == 3:
            height = 70 if not worker.altMode else 100
            width = 130 if not worker.altMode else 130
        if config.data['UI'] == 4:
            height = 50 if not worker.altMode else 80
            width = 163 if not worker.altMode else 163

        for name in self.data:
            self.data[name]['height'] = height
            self.data[name]['width'] = width
        data = {'height': height, 'width': width}
        self.updateObject(COMPONENT_TYPE.PANEL, data)
        self.updateObject(COMPONENT_TYPE.LABEL, data)
        if config.data['background']:
            self.updateObject(COMPONENT_TYPE.IMAGE, data)

    def set_text(self, text):
        self.updateObject(COMPONENT_TYPE.LABEL, {'text': '<font face="%s" color="#FFFFFF" vspace="-3" align="baseline" >%s</font>' % (config.data['font'], text)})

    def setVisible(self, status):
        data = {'visible': status}
        self.updateObject(COMPONENT_TYPE.PANEL, data)
        self.updateObject(COMPONENT_TYPE.LABEL, data)
        if config.data['background']:
            self.updateObject(COMPONENT_TYPE.IMAGE, data)

    @staticmethod
    def screenFix(screen, value, mod, align=1):
        if align == 1:  # положительное
            if value > screen:
                return int(screen - mod)
            if value < 0:
                return 0
        if align == -1:  # отрицательное
            if value < -screen:
                return int(-screen + mod)
            if value > 0:
                return 0
        if align == 0:  # центр
            scr = screen / 2
            if value < scr:
                return int(scr - mod)
            if value > -scr:
                return int(-scr)
        return None

    @inject.log
    def screenResize(self):
        curScr = GUI.screenResolution()
        scale = self.settingsCore.interfaceScale.get()
        xMo, yMo = curScr[0] / scale, curScr[1] / scale
        x = None
        if config.data['panel']['alignX'] == COMPONENT_ALIGN.LEFT:
            x = self.screenFix(xMo, config.data['panel']['x'], config.data['panel']['width'], 1)
        if config.data['panel']['alignX'] == COMPONENT_ALIGN.RIGHT:
            x = self.screenFix(xMo, config.data['panel']['x'], config.data['panel']['width'], -1)
        if config.data['panel']['alignX'] == COMPONENT_ALIGN.CENTER:
            x = self.screenFix(xMo, config.data['panel']['x'], config.data['panel']['width'], 0)
        if x is not None:
            if x != int(config.data['panel']['x']):
                config.data['panel']['x'] = x
                self.data[COMPONENT_TYPE.PANEL]['x'] = x
        y = None
        if config.data['panel']['alignY'] == COMPONENT_ALIGN.TOP:
            y = self.screenFix(yMo, config.data['panel']['y'], config.data['panel']['height'], 1)
        if config.data['panel']['alignY'] == COMPONENT_ALIGN.BOTTOM:
            y = self.screenFix(yMo, config.data['panel']['y'], config.data['panel']['height'], -1)
        if config.data['panel']['alignY'] == COMPONENT_ALIGN.CENTER:
            y = self.screenFix(yMo, config.data['panel']['y'], config.data['panel']['height'], 0)
        if y is not None:
            if y != int(config.data['panel']['y']):
                config.data['panel']['y'] = y
                self.data[COMPONENT_TYPE.PANEL]['y'] = y
        config.apply(config.data)
        self.updateObject(COMPONENT_TYPE.PANEL, self.data[COMPONENT_TYPE.PANEL])


config = Config()
flash = Flash()
worker = Worker()


# BigWorld.MoESetupSize = flash.setupSize
# BigWorld.MoEText = flash.set_text


@inject.hook(CrewMeta, 'as_tankmenResponseS')
@inject.log
def tankmanResponse(func, *args):
    worker.getCurrentHangarData()
    return func(*args)


@inject.hook(PlayerAvatar, 'onBattleEvents')
@inject.log
def onBattleEvents(func, *args):
    func(*args)
    if BigWorld.player().arena.bonusType == ARENA_BONUS_TYPE.REGULAR:
        worker.onBattleEvents(args[1])


@inject.hook(Vehicle, 'onHealthChanged')
@inject.log
def hookOnHealthChanged(func, self, newHealth, attackerID, attackReasonID):
    worker.shots(self, newHealth, attackerID)
    func(self, newHealth, attackerID, attackReasonID)


@inject.hook(Vehicle, 'startVisual')
@inject.log
def hookVehicleStartVisual(func, *args):
    func(*args)
    worker.initVehicle(args[0])


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    if BigWorld.player().arena.bonusType == ARENA_BONUS_TYPE.REGULAR:
        flash.startBattle()
        worker.startBattle()


@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
@inject.log
def hookDestroyGUI(func, *args):
    try:
        if BigWorld.player().arena.bonusType == ARENA_BONUS_TYPE.REGULAR:
            flash.stopBattle()
            worker.endBattle()
            worker.clearData()
    except StandardError:
        pass
    func(*args)


@inject.hook(MarkOnGunAchievement, 'getUserCondition')
@inject.log
def getUserCondition(func, *args):
    if config.data['enabled'] and config.data['showInStatistic']:
        if worker.dossier is not None:
            targetData = worker.dossier
            damageRating = targetData.getRecordValue(ACHIEVEMENT_BLOCK.TOTAL, 'damageRating') / 100.0
            movingAvgDamage = targetData.getRecordValue(ACHIEVEMENT_BLOCK.TOTAL, 'movingAvgDamage')
            damage = ProfileUtils.getValueOrUnavailable(ProfileUtils.getValueOrUnavailable(targetData.getRandomStats().getAvgDamage()))
            # noinspection PyProtectedMember
            track = ProfileUtils.getValueOrUnavailable(targetData.getRandomStats()._getAvgValue(targetData.getRandomStats().getBattlesCountVer2, targetData.getRandomStats().getDamageAssistedTrack))
            # noinspection PyProtectedMember
            radio = ProfileUtils.getValueOrUnavailable(targetData.getRandomStats()._getAvgValue(targetData.getRandomStats().getBattlesCountVer2, targetData.getRandomStats().getDamageAssistedRadio))
            stun = ProfileUtils.getValueOrUnavailable(targetData.getRandomStats().getAvgDamageAssistedStun())
            currentDamage = int(damage + max(track, radio, stun))
            if damageRating:
                pC, dC, p20, p40, p55, p65, p85, p95, p100 = worker.calcStatistics(damageRating, movingAvgDamage)
                color = ['#F8F400', '#F8F400', '#60FF00', '#02C9B3', '#D042F3', '#D042F3']
                levels = [p55, p65, p85, p95, p100, 10000000]
                data = {'nextPercent'  : '%.0f' % pC,
                        'needDamage'   : '<font color="%s">%s</font>' % (color[levels.index(filter(lambda x: x >= int(dC), levels)[0])], int(dC)),
                        'currentDamage': '<font color="%s">%s</font>' % (color[levels.index(filter(lambda x: x >= currentDamage, levels)[0])], currentDamage),
                        '_20'          : worker.getNormalizeDigits(p20),
                        '_40'          : worker.getNormalizeDigits(p40),
                        '_55'          : worker.getNormalizeDigits(p55),
                        '_65'          : worker.getNormalizeDigits(p65),
                        '_85'          : worker.getNormalizeDigits(p85),
                        '_95'          : worker.getNormalizeDigits(p95),
                        '_100'         : worker.getNormalizeDigits(p100)
                        }
                temp = config.i18n['UI_tooltips'].format(**data)
                return temp
    return func(*args)


@inject.hook(MarkOnGunAchievement, '__init__')
@inject.log
def initC(func, *args):
    func(*args)
    worker.dossier = args[1]


@inject.hook(NationObjDumper, '_getVehicleData')
@inject.log
def getExtraInfo(func, *args):
    result = func(*args)
    if config.data['enabled'] and config.data['showInTechTree']:
        dossier = None
        if len(args) > 2:
            item = args[2]
            dossier = g_currentVehicle.itemsCache.items.getVehicleDossier(item.intCD)
        else:
            try:
                # noinspection PyProtectedMember
                item = args[1]._RealNode__item
                dossier = g_currentVehicle.itemsCache.items.getVehicleDossier(item.intCD)
            except StandardError:
                pass
        if dossier:
            masteryStr = ''
            percentText = ''
            markOfGun = dossier.getTotalStats().getAchievement(MARK_ON_GUN_RECORD)
            markOfGunValue = markOfGun.getValue()
            mastery = dossier.getTotalStats().getAchievement(MARK_OF_MASTERY_RECORD)
            masteryValue = mastery.getValue()
            color = ['#F8F400', '#60FF00', '#02C9B3', '#D042F3']
            percent = float(dossier.getRecordValue(ACHIEVEMENT_BLOCK.TOTAL, 'damageRating') / 100.0)
            if config.data['showInTechTreeMastery'] and masteryValue and masteryValue < 5:
                masteryStr = '<img src="img://gui/%s" width="%s" height="%s" vspace="-%s"/>' % (mastery.getSmallIcon().replace('../', ''), config.data['techTreeMasterySize'], config.data['techTreeMasterySize'], config.data['techTreeMasterySize'])
            if config.data['showInTechTreeMarkOfGunPercent'] and percent:
                percentText = '<font size="%s" color="%s"> %s%%</font>' % (config.data['techTreeMarkOfGunPercentSize'], color[markOfGunValue], percent)
            if config.data['showInTechTreeMarkOfGunTankNameColored'] and percent:
                if config.data['techTreeMarkOfGunTankNameColoredOnlyMarkOfGun']:
                    if markOfGunValue:
                        result['nameString'] = '<font color="%s">%s</font>' % (color[markOfGunValue], result['nameString'])
                else:
                    result['nameString'] = '<font color="%s">%s</font>' % (color[markOfGunValue], result['nameString'])
            result['nameString'] = '%s%s%s' % (percentText if config.data['showInTechTreeMarkOfGunPercentFirst'] else result['nameString'], result['nameString'] if config.data['showInTechTreeMarkOfGunPercentFirst'] else percentText, masteryStr)

    return result
