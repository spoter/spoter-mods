# -*- coding: utf-8 -*-
import codecs
import json
import os
import re
import threading
import urllib
import urllib2

import BigWorld

import BattleReplay
import SoundGroups
import game
from Avatar import PlayerAvatar
from constants import AUTH_REALM
from constants import DAMAGE_INFO_CODES
from gui import InputHandler
from gui.Scaleform.Battle import Battle
from gui.Scaleform.daapi.view.battle.ConsumablesPanel import ConsumablesPanel
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.app_loader import g_appLoader
from gui.battle_control import g_sessionProvider
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
        self.ids = 'repair_extended'
        self.version = '2.08 (11.03.2016)'
        self.author = 'by spoter'
        self.path_config = './res_mods/configs/spoter_mods/%s/' % self.ids
        self.path_lang = '%si18n/' % self.path_config
        self.data = {
            'enabled'                   : True,
            'auto_repair'               : False,
            'auto_heal'                 : False,
            'auto_extinguish'           : False,
            'fire_time'                 : 0.3,
            'crew_time'                 : 0.8,
            'device_time'               : 0.7,
            'use_gold_med_kit'          : True,
            'use_gold_repair_kit'       : True,
            'chassis_auto_repair'       : False,
            'key_chassis_repair'        : 56,
            'button_chassis_repair'     : 56,
            'button_chassis_repair_mod' : 0,
            'key_fast_repair_all'       : 57,
            'button_fast_repair_all'    : 57,
            'button_fast_repair_all_mod': 0,
            'repair_priority'           : {
                'lightTank' : {
                    'crew'  : ['driver', 'commander', 'gunner', 'loader'],
                    'device': ['engine', 'chassis', 'ammoBay', 'gun', 'turretRotator']
                },
                'mediumTank': {
                    'crew'  : ['loader', 'driver', 'commander', 'gunner'],
                    'device': ['turretRotator', 'engine', 'ammoBay', 'gun']
                },
                'heavyTank' : {
                    'crew'  : ['commander', 'loader', 'gunner', 'driver'],
                    'device': ['turretRotator', 'ammoBay', 'engine', 'gun']
                },
                'SPG'       : {
                    'crew'  : ['commander', 'loader', 'gunner', 'driver'],
                    'device': ['ammoBay', 'engine', 'gun', 'turretRotator']
                },
                'AT-SPG'    : {
                    'crew'  : ['loader', 'gunner', 'commander', 'driver'],
                    'device': ['ammoBay', 'gun', 'engine', 'turretRotator']
                }
            }
        }
        self.i18n = {
            'UI_repair_name'                              : 'Quick repair device, heal crew, extinguish a fire ',
            'UI_repair_button_chassis_repair_text'        : 'Quick chassis repair Button',
            'UI_repair_button_chassis_repair_tooltip'     : '',
            'UI_repair_button_fast_repair_all_text'       : 'Quick Button (heal, repair, extinguish) if auto disabled',
            'UI_repair_button_fast_repair_all_tooltip'    : '',
            'UI_repair_auto_repair_text'                  : 'Enable auto repair device',
            'UI_repair_auto_repair_tooltip'               : '{HEADER}Enable auto repair devices{/HEADER}{BODY}If enabled, you may change priority in configs/spoter_mods/repair_extended/repair_extended.json{/BODY}',
            'UI_repair_auto_heal_text'                    : 'Enable auto heal crew',
            'UI_repair_auto_heal_tooltip'                 : '{HEADER}Enable auto heal crew{/HEADER}{BODY}If enabled, you may change priority in configs/spoter_mods/repair_extended/repair_extended.json{/BODY}',
            'UI_repair_auto_extinguish_text'              : 'Enable auto extinguish a fire',
            'UI_repair_auto_extinguish_tooltip'           : '',
            'UI_repair_chassis_auto_repair_text'          : 'Enable auto repair chassis',
            'UI_repair_chassis_auto_repair_tooltip'       : '{HEADER}Enable auto repair chassis{/HEADER}{BODY}if disable, LightTanks repair chassis for default.\nYou may change it in configs/spoter_mods/repair_extended/repair_extended.json{/BODY}',
            'UI_repair_use_gold_med_kit_text'             : 'Enable use Gold Med kit in heal crew',
            'UI_repair_use_gold_med_kit_tooltip'          : '',
            'UI_repair_use_gold_repair_kit_text'          : 'Enable use Gold Repair kit in repair device',
            'UI_repair_use_gold_repair_kit_tooltip'       : '',
            'UI_repair_button_chassis_repair_mod_text'    : 'Quick chassis repair modifier',
            'UI_repair_button_chassis_repair_mod_tooltip' : '',
            'UI_repair_button_fast_repair_all_mod_text'   : 'Quick Button modifier',
            'UI_repair_button_fast_repair_all_mod_tooltip': '',
            'UI_repair_device_time_text'                  : 'Delay auto repair device (in millisecond)',
            'UI_repair_device_time_format'                : ' msec.',
            'UI_repair_crew_time_text'                    : 'Delay auto heal crew (in millisecond)',
            'UI_repair_crew_time_format'                  : ' msec.',
            'UI_repair_fire_time_text'                    : 'Delay auto extinguish a fire (in millisecond)',
            'UI_repair_fire_time_format'                  : ' msec.'
        }

        self.load_lang()
        self.no_gui = False
        self.json = {
            'repair_priority': {
                'lightTank' : {
                    'crew'  : ['driver', 'commander', 'gunner', 'loader'],
                    'device': ['engine', 'chassis', 'ammoBay', 'gun', 'turretRotator']
                },
                'mediumTank': {
                    'crew'  : ['loader', 'driver', 'commander', 'gunner'],
                    'device': ['turretRotator', 'engine', 'ammoBay', 'gun']
                },
                'heavyTank' : {
                    'crew'  : ['commander', 'loader', 'gunner', 'driver'],
                    'device': ['turretRotator', 'ammoBay', 'engine', 'gun']
                },
                'SPG'       : {
                    'crew'  : ['commander', 'loader', 'gunner', 'driver'],
                    'device': ['ammoBay', 'engine', 'gun', 'turretRotator']
                },
                'AT-SPG'    : {
                    'crew'  : ['loader', 'gunner', 'commander', 'driver'],
                    'device': ['ammoBay', 'gun', 'engine', 'turretRotator']
                }
            }
        }

        new_config = self.load_json(self.ids, self.json, self.path_config)
        for setting in new_config:
            if setting in self.json:
                self.json[setting] = new_config[setting]
        self.setup = {
            'MODIFIER': [{
                'label': 'MODIFIER_NONE',
                'data' : 0
            }, {
                'label': 'MODIFIER_SHIFT',
                'data' : 1
            }, {
                'label': 'MODIFIER_CTRL',
                'data' : 2
            }, {
                'label': 'MODIFIER_ALT',
                'data' : 4
            }],
            'KEY'     : [{
                'label': 'KEY_NONE',
                'data' : 0
            }, {
                'label': 'KEY_ESCAPE',
                'data' : 1
            }, {
                'label': 'KEY_1',
                'data' : 2
            }, {
                'label': 'KEY_2',
                'data' : 3
            }, {
                'label': 'KEY_3',
                'data' : 4
            }, {
                'label': 'KEY_4',
                'data' : 5
            }, {
                'label': 'KEY_5',
                'data' : 6
            }, {
                'label': 'KEY_6',
                'data' : 7
            }, {
                'label': 'KEY_7',
                'data' : 8
            }, {
                'label': 'KEY_8',
                'data' : 9
            }, {
                'label': 'KEY_9',
                'data' : 10
            }, {
                'label': 'KEY_0',
                'data' : 11
            }, {
                'label': 'KEY_MINUS',
                'data' : 12
            }, {
                'label': 'KEY_EQUALS',
                'data' : 13
            }, {
                'label': 'KEY_BACKSPACE',
                'data' : 14
            }, {
                'label': 'KEY_TAB',
                'data' : 15
            }, {
                'label': 'KEY_Q',
                'data' : 16
            }, {
                'label': 'KEY_W',
                'data' : 17
            }, {
                'label': 'KEY_E',
                'data' : 18
            }, {
                'label': 'KEY_R',
                'data' : 19
            }, {
                'label': 'KEY_T',
                'data' : 20
            }, {
                'label': 'KEY_Y',
                'data' : 21
            }, {
                'label': 'KEY_U',
                'data' : 22
            }, {
                'label': 'KEY_I',
                'data' : 23
            }, {
                'label': 'KEY_O',
                'data' : 24
            }, {
                'label': 'KEY_P',
                'data' : 25
            }, {
                'label': 'KEY_LBRACKET',
                'data' : 26
            }, {
                'label': 'KEY_RBRACKET',
                'data' : 27
            }, {
                'label': 'KEY_RETURN',
                'data' : 28
            }, {
                'label': 'KEY_LCONTROL',
                'data' : 29
            }, {
                'label': 'KEY_A',
                'data' : 30
            }, {
                'label': 'KEY_S',
                'data' : 31
            }, {
                'label': 'KEY_D',
                'data' : 32
            }, {
                'label': 'KEY_F',
                'data' : 33
            }, {
                'label': 'KEY_G',
                'data' : 34
            }, {
                'label': 'KEY_H',
                'data' : 35
            }, {
                'label': 'KEY_J',
                'data' : 36
            }, {
                'label': 'KEY_K',
                'data' : 37
            }, {
                'label': 'KEY_L',
                'data' : 38
            }, {
                'label': 'KEY_SEMICOLON',
                'data' : 39
            }, {
                'label': 'KEY_APOSTROPHE',
                'data' : 40
            }, {
                'label': 'KEY_GRAVE',
                'data' : 41
            }, {
                'label': 'KEY_LSHIFT',
                'data' : 42
            }, {
                'label': 'KEY_BACKSLASH',
                'data' : 43
            }, {
                'label': 'KEY_Z',
                'data' : 44
            }, {
                'label': 'KEY_X',
                'data' : 45
            }, {
                'label': 'KEY_C',
                'data' : 46
            }, {
                'label': 'KEY_V',
                'data' : 47
            }, {
                'label': 'KEY_B',
                'data' : 48
            }, {
                'label': 'KEY_N',
                'data' : 49
            }, {
                'label': 'KEY_M',
                'data' : 50
            }, {
                'label': 'KEY_COMMA',
                'data' : 51
            }, {
                'label': 'KEY_PERIOD',
                'data' : 52
            }, {
                'label': 'KEY_SLASH',
                'data' : 53
            }, {
                'label': 'KEY_RSHIFT',
                'data' : 54
            }, {
                'label': 'KEY_NUMPADSTAR',
                'data' : 55
            }, {
                'label': 'KEY_LALT',
                'data' : 56
            }, {
                'label': 'KEY_SPACE',
                'data' : 57
            }, {
                'label': 'KEY_CAPSLOCK',
                'data' : 58
            }, {
                'label': 'KEY_F1',
                'data' : 59
            }, {
                'label': 'KEY_F2',
                'data' : 60
            }, {
                'label': 'KEY_F3',
                'data' : 61
            }, {
                'label': 'KEY_F4',
                'data' : 62
            }, {
                'label': 'KEY_F5',
                'data' : 63
            }, {
                'label': 'KEY_F6',
                'data' : 64
            }, {
                'label': 'KEY_F7',
                'data' : 65
            }, {
                'label': 'KEY_F8',
                'data' : 66
            }, {
                'label': 'KEY_F9',
                'data' : 67
            }, {
                'label': 'KEY_F10',
                'data' : 68
            }, {
                'label': 'KEY_NUMLOCK',
                'data' : 69
            }, {
                'label': 'KEY_SCROLL',
                'data' : 70
            }, {
                'label': 'KEY_NUMPAD7',
                'data' : 71
            }, {
                'label': 'KEY_NUMPAD8',
                'data' : 72
            }, {
                'label': 'KEY_NUMPAD9',
                'data' : 73
            }, {
                'label': 'KEY_NUMPADMINUS',
                'data' : 74
            }, {
                'label': 'KEY_NUMPAD4',
                'data' : 75
            }, {
                'label': 'KEY_NUMPAD5',
                'data' : 76
            }, {
                'label': 'KEY_NUMPAD6',
                'data' : 77
            }, {
                'label': 'KEY_ADD',
                'data' : 78
            }, {
                'label': 'KEY_NUMPAD1',
                'data' : 79
            }, {
                'label': 'KEY_NUMPAD2',
                'data' : 80
            }, {
                'label': 'KEY_NUMPAD3',
                'data' : 81
            }, {
                'label': 'KEY_NUMPAD0',
                'data' : 82
            }, {
                'label': 'KEY_NUMPADPERIOD',
                'data' : 83
            }, {
                'label': 'KEY_OEM_102',
                'data' : 86
            }, {
                'label': 'KEY_F11',
                'data' : 87
            }, {
                'label': 'KEY_F12',
                'data' : 88
            }, {
                'label': 'KEY_F13',
                'data' : 100
            }, {
                'label': 'KEY_F14',
                'data' : 101
            }, {
                'label': 'KEY_F15',
                'data' : 102
            }, {
                'label': 'KEY_KANA',
                'data' : 112
            }, {
                'label': 'KEY_ABNT_C1',
                'data' : 115
            }, {
                'label': 'KEY_CONVERT',
                'data' : 121
            }, {
                'label': 'KEY_NOCONVERT',
                'data' : 123
            }, {
                'label': 'KEY_YEN',
                'data' : 125
            }, {
                'label': 'KEY_ABNT_C2',
                'data' : 126
            }, {
                'label': 'KEY_NUMPADEQUALS',
                'data' : 141
            }, {
                'label': 'KEY_PREVTRACK',
                'data' : 144
            }, {
                'label': 'KEY_AT',
                'data' : 145
            }, {
                'label': 'KEY_COLON',
                'data' : 146
            }, {
                'label': 'KEY_UNDERLINE',
                'data' : 147
            }, {
                'label': 'KEY_KANJI',
                'data' : 148
            }, {
                'label': 'KEY_STOP',
                'data' : 149
            }, {
                'label': 'KEY_AX',
                'data' : 150
            }, {
                'label': 'KEY_UNLABELED',
                'data' : 151
            }, {
                'label': 'KEY_NEXTTRACK',
                'data' : 153
            }, {
                'label': 'KEY_NUMPADENTER',
                'data' : 156
            }, {
                'label': 'KEY_RCONTROL',
                'data' : 157
            }, {
                'label': 'KEY_MUTE',
                'data' : 160
            }, {
                'label': 'KEY_CALCULATOR',
                'data' : 161
            }, {
                'label': 'KEY_PLAYPAUSE',
                'data' : 162
            }, {
                'label': 'KEY_MEDIASTOP',
                'data' : 164
            }, {
                'label': 'KEY_VOLUMEDOWN',
                'data' : 174
            }, {
                'label': 'KEY_VOLUMEUP',
                'data' : 176
            }, {
                'label': 'KEY_WEBHOME',
                'data' : 178
            }, {
                'label': 'KEY_NUMPADCOMMA',
                'data' : 179
            }, {
                'label': 'KEY_NUMPADSLASH',
                'data' : 181
            }, {
                'label': 'KEY_SYSRQ',
                'data' : 183
            }, {
                'label': 'KEY_RALT',
                'data' : 184
            }, {
                'label': 'KEY_PAUSE',
                'data' : 197
            }, {
                'label': 'KEY_HOME',
                'data' : 199
            }, {
                'label': 'KEY_UPARROW',
                'data' : 200
            }, {
                'label': 'KEY_PGUP',
                'data' : 201
            }, {
                'label': 'KEY_LEFTARROW',
                'data' : 203
            }, {
                'label': 'KEY_RIGHTARROW',
                'data' : 205
            }, {
                'label': 'KEY_END',
                'data' : 207
            }, {
                'label': 'KEY_DOWNARROW',
                'data' : 208
            }, {
                'label': 'KEY_PGDN',
                'data' : 209
            }, {
                'label': 'KEY_INSERT',
                'data' : 210
            }, {
                'label': 'KEY_DELETE',
                'data' : 211
            }, {
                'label': 'KEY_LWIN',
                'data' : 219
            }, {
                'label': 'KEY_RWIN',
                'data' : 220
            }, {
                'label': 'KEY_APPS',
                'data' : 221
            }, {
                'label': 'KEY_POWER',
                'data' : 222
            }, {
                'label': 'KEY_SLEEP',
                'data' : 223
            }, {
                'label': 'KEY_WAKE',
                'data' : 227
            }, {
                'label': 'KEY_WEBSEARCH',
                'data' : 229
            }, {
                'label': 'KEY_WEBFAVORITES',
                'data' : 230
            }, {
                'label': 'KEY_WEBREFRESH',
                'data' : 231
            }, {
                'label': 'KEY_WEBSTOP',
                'data' : 232
            }, {
                'label': 'KEY_WEBFORWARD',
                'data' : 233
            }, {
                'label': 'KEY_WEBBACK',
                'data' : 234
            }, {
                'label': 'KEY_MYCOMPUTER',
                'data' : 235
            }, {
                'label': 'KEY_MAIL',
                'data' : 236
            }, {
                'label': 'KEY_MEDIASELECT',
                'data' : 237
            }, {
                'label': 'KEY_IME_CHAR',
                'data' : 255
            }, {
                'label': 'KEY_LEFTMOUSE',
                'data' : 256
            }, {
                'label': 'KEY_RIGHTMOUSE',
                'data' : 257
            }, {
                'label': 'KEY_MIDDLEMOUSE',
                'data' : 258
            }, {
                'label': 'KEY_MOUSE3',
                'data' : 259
            }, {
                'label': 'KEY_MOUSE4',
                'data' : 260
            }, {
                'label': 'KEY_MOUSE5',
                'data' : 261
            }, {
                'label': 'KEY_MOUSE6',
                'data' : 262
            }, {
                'label': 'KEY_MOUSE7',
                'data' : 263
            }, {
                'label': 'KEY_DEBUG',
                'data' : 312
            }, {
                'label': 'KEY_LCDKB_LEFT',
                'data' : 320
            }, {
                'label': 'KEY_LCDKB_RIGHT',
                'data' : 321
            }, {
                'label': 'KEY_LCDKB_OK',
                'data' : 322
            }, {
                'label': 'KEY_LCDKB_CANCEL',
                'data' : 323
            }, {
                'label': 'KEY_LCDKB_UP',
                'data' : 324
            }, {
                'label': 'KEY_LCDKB_DOWN',
                'data' : 325
            }, {
                'label': 'KEY_LCDKB_MENU',
                'data' : 326
            }]
        }

    def load_lang(self):
        lang = str(getLanguageCode()).lower()
        new_config = self.load_json(lang, self.i18n, self.path_lang)
        for setting in new_config:
            if setting in self.i18n:
                self.i18n[setting] = new_config[setting]

    def template_settings(self):
        return {
            'modDisplayName' : self.i18n['UI_repair_name'],
            'settingsVersion': 207,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_repair_button_chassis_repair_text'],
                'tooltip'     : self.i18n['UI_repair_button_chassis_repair_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.setup['KEY'],
                'width'       : 200,
                'value'       : self.data['key_chassis_repair'],
                'varName'     : 'key_chassis_repair'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_repair_button_fast_repair_all_text'],
                'tooltip'     : self.i18n['UI_repair_button_fast_repair_all_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.setup['KEY'],
                'width'       : 200,
                'value'       : self.data['key_fast_repair_all'],
                'varName'     : 'key_fast_repair_all'
            },# {
            #    'type'   : 'CheckBox',
            #    'text'   : self.i18n['UI_repair_auto_repair_text'],
            #    'value'  : self.data,
            #    'tooltip': self.i18n['UI_repair_auto_repair_tooltip'],
            #    'varName': 'auto_repair'
            #}, {
            #    'type'   : 'CheckBox',
            #    'text'   : self.i18n['UI_repair_auto_heal_text'],
            #    'value'  : self.data['auto_heal'],
            #    'tooltip': self.i18n['UI_repair_auto_heal_tooltip'],
            #    'varName': 'auto_heal'
            #}, {
            #    'type'   : 'CheckBox',
            #    'text'   : self.i18n['UI_repair_auto_extinguish_text'],
            #    'value'  : self.data['auto_extinguish'],
            #    'tooltip': self.i18n['UI_repair_auto_extinguish_tooltip'],
            #    'varName': 'auto_extinguish'
            #}, {
            #    'type'   : 'CheckBox',
            #    'text'   : self.i18n['UI_repair_chassis_auto_repair_text'],
            #    'value'  : self.data['chassis_auto_repair'],
            #    'tooltip': self.i18n['UI_repair_chassis_auto_repair_tooltip'],
            #    'varName': 'chassis_auto_repair'
            #},
            {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_use_gold_med_kit_text'],
                'value'  : self.data['use_gold_med_kit'],
                'tooltip': self.i18n['UI_repair_use_gold_med_kit_tooltip'],
                'varName': 'use_gold_med_kit'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_use_gold_repair_kit_text'],
                'value'  : self.data['use_gold_repair_kit'],
                'tooltip': self.i18n['UI_repair_use_gold_repair_kit_tooltip'],
                'varName': 'use_gold_repair_kit'
            }],
            'column2'        : [{
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_repair_button_chassis_repair_mod_text'],
                    'tooltip'     : self.i18n['UI_repair_button_chassis_repair_mod_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : self.setup['MODIFIER'],
                    'width'       : 200,
                    'value'       : self.data['button_chassis_repair_mod'],
                    'varName'     : 'button_chassis_repair_mod'
                }, {
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_repair_button_fast_repair_all_mod_text'],
                    'tooltip'     : self.i18n['UI_repair_button_fast_repair_all_mod_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : self.setup['MODIFIER'],
                    'width'       : 200,
                    'value'       : self.data['button_fast_repair_all_mod'],
                    'varName'     : 'button_fast_repair_all_mod'
                }
                #, {
                #    'type'        : 'Slider',
                #    'text'        : self.i18n['UI_repair_device_time_text'],
                #    'minimum'     : 500,
                #    'maximum'     : 1500,
                #    'snapInterval': 100,
                #    'value'       : self.data['device_time'],
                #    'format'      : '{{value}}%s' % self.i18n['UI_repair_device_time_format'],
                #    'varName'     : 'device_time'
                #}, {
                #    'type'        : 'Slider',
                #    'text'        : self.i18n['UI_repair_crew_time_text'],
                #    'minimum'     : 500,
                #    'maximum'     : 1500,
                #    'snapInterval': 100,
                #    'value'       : self.data['crew_time'],
                #    'format'      : '{{value}}%s' % self.i18n['UI_repair_crew_time_format'],
                #    'varName'     : 'crew_time'
                #}, {
                #    'type'        : 'Slider',
                #    'text'        : self.i18n['UI_repair_fire_time_text'],
                #    'minimum'     : 300,
                #    'maximum'     : 1500,
                #    'snapInterval': 100,
                #    'value'       : self.data['fire_time'],
                #    'format'      : '{{value}}%s' % self.i18n['UI_repair_fire_time_format'],
                #    'varName'     : 'fire_time'
                #}
            ]
        }

    def apply_settings(self, settings):
        for setting in settings:
            if setting in self.data:
                self.data[setting] = settings[setting]
        self.data['button_chassis_repair'] = self.setup['KEY'][self.data['key_chassis_repair']]['data']
        self.data['button_fast_repair_all'] = self.setup['KEY'][self.data['key_fast_repair_all']]['data']
        _gui_config.update('%s' % self.ids, self.template_settings)

    def apply_json(self):
        repair_priority = {
            'lightTank' : {
                'crew'  : ['driver', 'commander', 'gunner', 'loader'],
                'device': ['engine', 'chassis', 'ammoBay', 'gun', 'turretRotator']
            },
            'mediumTank': {
                'crew'  : ['loader', 'driver', 'commander', 'gunner'],
                'device': ['turretRotator', 'engine', 'ammoBay', 'gun']
            },
            'heavyTank' : {
                'crew'  : ['commander', 'loader', 'gunner', 'driver'],
                'device': ['turretRotator', 'ammoBay', 'engine', 'gun']
            },
            'SPG'       : {
                'crew'  : ['commander', 'loader', 'gunner', 'driver'],
                'device': ['ammoBay', 'engine', 'gun', 'turretRotator']
            },
            'AT-SPG'    : {
                'crew'  : ['loader', 'gunner', 'commander', 'driver'],
                'device': ['ammoBay', 'gun', 'engine', 'turretRotator']
            }
        }

        if 'repair_priority' in self.json:
            repair_priority['lightTank'] = {
                'crew'  : self.json['repair_priority']['lightTank'].get('crew', self.data['repair_priority']['lightTank'].get('crew')),
                'device': self.json['repair_priority']['lightTank'].get('device', self.data['repair_priority']['lightTank'].get('device'))
            } if 'lightTank' in self.json['repair_priority'] else self.data['repair_priority']['lightTank']
            repair_priority['mediumTank'] = {
                'crew'  : self.json['repair_priority']['mediumTank'].get('crew', self.data['repair_priority']['mediumTank'].get('crew')),
                'device': self.json['repair_priority']['mediumTank'].get('device', self.data['repair_priority']['mediumTank'].get('device'))
            } if 'mediumTank' in self.json['repair_priority'] else self.data['repair_priority']['mediumTank']
            repair_priority['heavyTank'] = {
                'crew'  : self.json['repair_priority']['heavyTank'].get('crew', self.data['repair_priority']['heavyTank'].get('crew')),
                'device': self.json['repair_priority']['heavyTank'].get('device', self.data['repair_priority']['heavyTank'].get('device'))
            } if 'heavyTank' in self.json['repair_priority'] else self.data['repair_priority']['heavyTank']
            repair_priority['SPG'] = {
                'crew'  : self.json['repair_priority']['SPG'].get('crew', self.data['repair_priority']['SPG'].get('crew')),
                'device': self.json['repair_priority']['SPG'].get('device', self.data['repair_priority']['SPG'].get('device'))
            } if 'SPG' in self.json['repair_priority'] else self.data['repair_priority']['SPG']
            repair_priority['AT-SPG'] = {
                'crew'  : self.json['repair_priority']['AT-SPG'].get('crew', self.data['repair_priority']['AT-SPG'].get('crew')),
                'device': self.json['repair_priority']['AT-SPG'].get('device', self.data['repair_priority']['AT-SPG'].get('device'))
            } if 'AT-SPG' in self.json['repair_priority'] else self.data['repair_priority']['AT-SPG']

        for setting in repair_priority:
            if setting in self.data['repair_priority']:
                self.data['repair_priority'][setting] = repair_priority[setting]

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
        self.apply_json()
        if hasattr(BigWorld, 'mods_gui'):
            _gui_config.register(name='%s' % self.ids, template_func=self.template_settings, settings_dict=self.data, apply_func=self.apply_settings)
        else:
            if not self.no_gui:
                BigWorld.callback(1.0, self.do_config)


class Statistics(object):
    def __init__(self):
        self.analytics_started = False
        self._thread_analytics = None
        self.tid = 'UA-57975916-11'
        self.description_analytics = 'Мод: "Винтик"'

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


class _Repair(object):
    def __init__(self):
        self.items = {}
        self.damaged = []
        self.destroyed = []
        self.fired = False
        self.ConsumablesPanel = None
        self.int_cd = {
            'extinguisher': 251,
            'med_kit'     : 763,
            'repair_kit'  : 1275,
            'g_repair_kit': 1531,
            'g_med_kit'   : 1019
        }
        self.crew = ['_None', 'commander', 'radioman', 'driver', 'driver1', 'driver2', 'gunner', 'gunner1', 'gunner2', 'loader', 'loader1', 'loader2']
        self.device = ['_None', 'gun', 'engine', 'ammoBay', 'turretRotator', 'chassis', 'leftTrack', 'rightTrack', 'surveyingDevice', 'radio', 'fuelTank']
        self.v_FireCodes = ('FIRE', 'DEVICE_STARTED_FIRE_AT_SHOT', 'DEVICE_STARTED_FIRE_AT_RAMMING', 'FIRE_STOPPED')
        self.v_DamageCodes = (
            'DEVICE_CRITICAL', 'DEVICE_REPAIRED_TO_CRITICAL', 'DEVICE_CRITICAL_AT_SHOT', 'DEVICE_CRITICAL_AT_RAMMING', 'DEVICE_CRITICAL_AT_FIRE', 'DEVICE_CRITICAL_AT_WORLD_COLLISION', 'DEVICE_CRITICAL_AT_DROWNING', 'ENGINE_CRITICAL_AT_UNLIMITED_RPM',
            'DEVICE_DESTROYED', 'DEVICE_DESTROYED_AT_SHOT', 'DEVICE_DESTROYED_AT_RAMMING', 'DEVICE_DESTROYED_AT_FIRE', 'DEVICE_DESTROYED_AT_WORLD_COLLISION', 'DEVICE_DESTROYED_AT_DROWNING', 'ENGINE_DESTROYED_AT_UNLIMITED_RPM')
        self.v_RepairedCodes = ('DEVICE_REPAIRED_TO_CRITICAL',)
        self.v_Destroyed_Codes = ('DEVICE_DESTROYED', 'DEVICE_DESTROYED_AT_SHOT', 'DEVICE_DESTROYED_AT_RAMMING', 'DEVICE_DESTROYED_AT_FIRE', 'DEVICE_DESTROYED_AT_WORLD_COLLISION', 'DEVICE_DESTROYED_AT_DROWNING', 'ENGINE_DESTROYED_AT_UNLIMITED_RPM')
        self.m_DamageCodes = ('TANKMAN_HIT_AT_RAMMING', 'TANKMAN_HIT_AT_FIRE', 'TANKMAN_HIT_AT_EXPLOSION', 'TANKMAN_HIT', 'TANKMAN_HIT_AT_SHOT', 'TANKMAN_HIT_AT_WORLD_COLLISION', 'TANKMAN_HIT_AT_DROWNING', 'TANKMAN_HIT_AT_DROWNING')
        self.DeathCodes = ('DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE', 'DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT', 'DEATH_FROM_FIRE', 'DEATH_FROM_INACTIVE_CREW', 'DEATH_FROM_INACTIVE_CREW_AT_SHOT', 'DEATH_FROM_RAMMING', 'DEATH_FROM_SHOT')
        self.time = BigWorld.time()

    def clear(self):
        self.items = {}
        self.damaged = []
        self.destroyed = []
        self.fired = False

    def eq_add(self, int_cd, item):
        self.items[int_cd] = item

    def eq_upd(self, int_cd, item):
        self.items[int_cd] = item

    def check_item(self, int_cd):
        return int_cd in self.int_cd and self.int_cd[int_cd] in self.items and self.items[self.int_cd[int_cd]].getQuantity() > 0

    def use_item(self, int_cd, entity_name=None):
        replay_ctrl = BattleReplay.g_replayCtrl
        if int_cd != 0 and not replay_ctrl.isPlaying:
            # noinspection PyUnresolvedReferences,PyProtectedMember
            ConsumablesPanel._ConsumablesPanel__handleEquipmentPressed(self.ConsumablesPanel, int_cd, entity_name)
            sound = SoundGroups.g_instance.getSound2D('vo_flt_repair')
            BigWorld.callback(1.0, sound.play)

    @staticmethod
    def get_extra_name(extra):
        if extra.name == 'fire': return extra.name
        return extra.name[:-len('Health')]

    def get_info(self, damage_code, extra):
        extra_name = self.get_extra_name(extra)
        self.time = BigWorld.time()
        if damage_code not in self.DeathCodes:
            if extra_name in self.device:
                if damage_code in self.v_FireCodes and self.check_item('extinguisher'):
                    if damage_code == 'FIRE_STOPPED' or extra_name == '_None': self.fired = False
                    else: self.fired = True
                    if _config.data['auto_extinguish'] and self.fired: self.auto_fired()
                if damage_code in self.v_DamageCodes:
                    if extra_name not in self.damaged and extra_name not in ['chassis', 'leftTrack', 'rightTrack']:
                        self.damaged.append(extra_name)
                    if damage_code in self.v_Destroyed_Codes and extra_name not in self.destroyed and extra_name in ['chassis', 'leftTrack', 'rightTrack']:
                        self.destroyed.append(extra_name)
                    if damage_code in self.v_RepairedCodes and extra_name in self.destroyed:
                        self.destroyed.remove(extra_name)
                    if _config.data['auto_repair']: self.auto_repair()
            if extra_name in self.crew:
                if damage_code in self.m_DamageCodes:
                    if extra_name not in self.damaged:
                        self.damaged.append(extra_name)
                    if _config.data['auto_heal']: self.auto_heal()

    def auto_fired(self):
        if BigWorld.time() - self.time < _config.data['fire_time'] * 0.001:
            BigWorld.callback(0.1, self.auto_fired)
        else: self.fires()

    def fires(self):
        if self.fired and self.check_item('extinguisher'):
            self.use_item(self.int_cd['extinguisher'])
            self.fired = False

    def auto_heal(self):
        if BigWorld.time() - self.time < _config.data['crew_time'] * 0.001:
            BigWorld.callback(0.1, self.auto_heal)
        else: self.heal()

    @staticmethod
    def check_class(tank_class):
        if 'lightTank' in tank_class: return 'lightTank'
        if 'mediumTank' in tank_class: return 'mediumTank'
        if 'heavyTank' in tank_class: return 'heavyTank'
        if 'SPG' in tank_class: return 'SPG'
        if 'AT-SPG' in tank_class: return 'AT-SPG'

    def heal(self):
        my_tank_class = self.check_class(BigWorld.player().vehicleTypeDescriptor.type.tags)
        specific = _config.data['repair_priority'].get(my_tank_class)

        if self.check_item('med_kit'):
            for crew in specific['crew']:
                if crew in self.damaged:
                    self.use_item(self.int_cd['med_kit'], crew)
                    self.damaged.remove(crew)
                    break
                if crew == 'driver':
                    for module in ['driver', 'driver1', 'driver2']:
                        if module in self.damaged:
                            self.use_item(self.int_cd['med_kit'], module)
                            self.damaged.remove(module)
                            break
                if crew == 'gunner':
                    for module in ['gunner', 'gunner1', 'gunner2']:
                        if module in self.damaged:
                            self.use_item(self.int_cd['med_kit'], module)
                            self.damaged.remove(module)
                            break
                if crew == 'loader':
                    for module in ['loader', 'loader1', 'loader2']:
                        if module in self.damaged:
                            self.use_item(self.int_cd['med_kit'], module)
                            self.damaged.remove(module)
                            break

        elif _config.data['use_gold_med_kit'] and self.check_item('g_med_kit'):
            for crew in specific['crew']:
                if crew in self.damaged:
                    self.use_item(self.int_cd['g_med_kit'], crew)
                    for module in self.crew:
                        if module in self.damaged: self.damaged.remove(module)
                    break
                if crew == 'driver':
                    for module in ['driver', 'driver1', 'driver2']:
                        if module in self.damaged:
                            self.use_item(self.int_cd['g_med_kit'], module)
                            for module1 in self.crew:
                                if module1 in self.damaged: self.damaged.remove(module1)
                            break
                if crew == 'gunner':
                    for module in ['gunner', 'gunner1', 'gunner2']:
                        if module in self.damaged:
                            self.use_item(self.int_cd['g_med_kit'], module)
                            for module1 in self.crew:
                                if module1 in self.damaged: self.damaged.remove(module1)
                            break
                if crew == 'loader':
                    for module in ['loader', 'loader1', 'loader2']:
                        if module in self.damaged:
                            self.use_item(self.int_cd['g_med_kit'], module)
                            for module1 in self.crew:
                                if module1 in self.damaged: self.damaged.remove(module1)
                            break

    def auto_repair(self):
        if BigWorld.time() - self.time < _config.data['device_time'] * 0.001:
            BigWorld.callback(0.1, self.auto_repair)
        else: self.repair()

    def repair(self):
        my_tank_class = self.check_class(BigWorld.player().vehicleTypeDescriptor.type.tags)
        specific = _config.data['repair_priority'].get(my_tank_class)
        if self.check_item('repair_kit'):
            for device in specific['device']:
                if device == 'chassis' and _config.data['chassis_auto_repair']:
                    for device1 in ['chassis', 'leftTrack', 'rightTrack']:
                        if device1 in self.destroyed:
                            self.use_item(self.int_cd['repair_kit'], device1)
                            if device1 in self.destroyed: self.destroyed.remove(device1)
                            if device1 in self.damaged: self.damaged.remove(device1)
                            break
                elif device in self.damaged:
                    self.use_item(self.int_cd['repair_kit'], device)
                    self.damaged.remove(device)
                    break
        elif _config.data['use_gold_repair_kit'] and self.check_item('g_repair_kit'):
            for device in specific['device']:
                if device == 'chassis' and _config.data['chassis_auto_repair']:
                    for device1 in ['chassis', 'leftTrack', 'rightTrack']:
                        if device1 in self.destroyed:
                            self.use_item(self.int_cd['g_repair_kit'], device1)
                            for module in self.device:
                                if module in self.damaged: self.damaged.remove(module)
                                if module in self.destroyed: self.destroyed.remove(module)
                            break
                elif device in self.damaged:
                    self.use_item(self.int_cd['g_repair_kit'], device)
                    for module in self.device:
                        if module in self.damaged: self.damaged.remove(module)
                        if module in self.destroyed: self.destroyed.remove(module)
                    break
        if _config.data['chassis_auto_repair']:
            self.repair_chassis()

    def repair_chassis(self):
        if self.check_item('repair_kit'):
            for device in ['chassis', 'leftTrack', 'rightTrack']:
                if device in self.destroyed:
                    self.use_item(self.int_cd['repair_kit'], device)
                    if device in self.destroyed: self.destroyed.remove(device)
                    if device in self.damaged: self.damaged.remove(device)
                    break
        elif self.check_item('g_repair_kit'):
            for device in ['chassis', 'leftTrack', 'rightTrack']:
                if device in self.destroyed:
                    self.use_item(self.int_cd['g_repair_kit'], device)
                    for module in self.device:
                        if module in self.damaged: self.damaged.remove(module)
                        if module in self.destroyed: self.destroyed.remove(module)
                    break


# deformed functions:
def hook_update_all(self):
    hooked_update_all(self)
    try:
        stat.start()
    except Exception as e:
        print('%s hook_update_all get stat' % _config.ids, e)


def hook_handle_equipment_expanded(self, int_cd):
    if _config.data['enabled']:
        item = g_sessionProvider.getEquipmentsCtrl().getEquipment(int_cd)
        if not item: return
        for _, (_, _, entityState) in enumerate(item.getGuiIterator()):
            if entityState and entityState in ['destroyed', 'critical']: return hooked_handle_equipment_expanded(self, int_cd)
        return
    else: return hooked_handle_equipment_expanded(self, int_cd)


def hook_show_vehicle_damage_info(self, vehicle_id, damage_index, extra_index, entity_id, equipment_id):
    if _config.data['enabled']:
        damage_code = DAMAGE_INFO_CODES[damage_index]
        extra = self.vehicleTypeDescriptor.extras[extra_index] if extra_index != 0 else None
        if vehicle_id == self.playerVehicleID or not self.isVehicleAlive and vehicle_id == self.inputHandler.ctrl.curVehicleID:
            if extra: _repair.get_info(damage_code, extra)
    return hooked_show_vehicle_damage_info(self, vehicle_id, damage_index, extra_index, entity_id, equipment_id)


def inject_handle_key_event(event):
    is_down, key, mods, is_repeat = game.convertKeyEvent(event)
    is_in_battle = g_appLoader.getDefBattleApp()
    try:
        if is_in_battle:
            if _config.data['enabled']:
                if BigWorld.isKeyDown(_config.data['button_chassis_repair']) and is_down and mods == _config.data['button_chassis_repair_mod']:
                    _repair.repair_chassis()
                if BigWorld.isKeyDown(_config.data['button_fast_repair_all']) and is_down and mods == _config.data['button_fast_repair_all_mod']:
                    _repair.fires()
                    _repair.heal()
                    _repair.repair()
    except Exception as e:
        print('%s inject_handle_key_event' % _config.ids, e)


def hook_add_equipment_slot(self, int_cd, item):
    if _config.data['enabled']:
        _repair.ConsumablesPanel = self
        _repair.eq_add(int_cd, item)
    return hooked_add_equipment_slot(self, int_cd, item)


def hook_start_battle(self):
    hooked_start_battle(self)
    if _config.data['enabled']:
        _repair.clear()


def hook_stop_battle(self):
    hooked_stop_battle(self)
    if _config.data['enabled']:
        _repair.clear()


#start mod
stat = Statistics()
_gui_config = _GUIConfig()
_config = _Config()
_repair = _Repair()
_config.load()

#hooked

# noinspection PyProtectedMember
hooked_handle_equipment_expanded = ConsumablesPanel._ConsumablesPanel__handleEquipmentExpanded
hooked_show_vehicle_damage_info = PlayerAvatar.showVehicleDamageInfo

# noinspection PyProtectedMember
hooked_add_equipment_slot = ConsumablesPanel._ConsumablesPanel__onEquipmentAdded
# noinspection PyProtectedMember,PyProtectedMember
hooked_update_all = Hangar._Hangar__updateAll
hooked_start_battle = Battle.afterCreate
hooked_stop_battle = Battle.beforeDelete

#hook
Hangar._Hangar__updateAll = hook_update_all
ConsumablesPanel._ConsumablesPanel__handleEquipmentExpanded = hook_handle_equipment_expanded
ConsumablesPanel._ConsumablesPanel__onEquipmentAdded = hook_add_equipment_slot
PlayerAvatar.showVehicleDamageInfo = hook_show_vehicle_damage_info
Battle.afterCreate = hook_start_battle
Battle.beforeDelete = hook_stop_battle

#injected
InputHandler.g_instance.onKeyDown += inject_handle_key_event
InputHandler.g_instance.onKeyUp += inject_handle_key_event
