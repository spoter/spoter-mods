# -*- coding: utf-8 -*-
import os
import re
import json
import codecs
import datetime
import threading
import urllib
import urllib2

import BigWorld
import BattleReplay
import game
from constants import AUTH_REALM, DAMAGE_INFO_CODES
from Avatar import PlayerAvatar
from gui import InputHandler
from gui.battle_control import g_sessionProvider
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.daapi.view.battle.ConsumablesPanel import ConsumablesPanel
import SoundGroups
from gui.Scaleform.Battle import Battle


class Config(object):
    def __init__(self):
        self.enable = True
        self.debug = False
        self.ru = True if 'RU' in AUTH_REALM else False
        self.version = 'v2.06(16.09.2015)'
        self.author = 'by spoter'
        self.description = 'repair_extended'
        self.description_ru = 'Мод: "Винтик"'
        self.author_ru = 'автор: spoter'
        self.name = 'repair_extended'
        self.description_analytics = 'Мод: "Винтик"'
        self.tid = 'UA-57975916-11'
        self.setup = {}
        self.sys_mes = {}
        self._thread_analytics = None
        self.analytics_started = False
        self.language = None
        self.xvm_installed = False
        self.xvm_check()
        self.res_mods = self.res_mods_init()
        self.data = {}
        self.setup = {}
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
                'enable': True, 'debug': False, 'button_expanded': True, 'use_extinguisher': True, 'use_gold_med_kit': True, 'use_gold_repair_kit': True, 'heal_crew': True, 'repair_device': True,
                'class_specific': True, 'play_sound': True, 'language': 'Русский'
            }, 'buttons': {
                'crew_only': {'KEY': 'KEY_NONE', 'MODIFIER': 'MODIFIER_NONE'}, 'device_only': {'KEY': 'KEY_NONE', 'MODIFIER': 'MODIFIER_NONE'},
                'chassis_only': {'KEY': 'KEY_LALT', 'MODIFIER': 'MODIFIER_NONE'}, 'universal': {'KEY': 'KEY_SPACE', 'MODIFIER': 'MODIFIER_NONE'}
            }, 'class_specific': {
                'None': {'crew': ['commander', 'driver', 'loader', 'gunner'], 'device': ['turretRotator', 'ammoBay', 'engine', 'gun', 'chassis']},
                'lightTank': {'crew': ['driver', 'commander', 'gunner', 'loader'], 'device': ['engine', 'chassis', 'ammoBay', 'gun', 'turretRotator']},
                'mediumTank': {'crew': ['loader', 'driver', 'commander', 'gunner'], 'device': ['turretRotator', 'engine', 'ammoBay', 'gun', 'chassis']},
                'heavyTank': {'crew': ['commander', 'loader', 'gunner', 'driver'], 'device': ['turretRotator', 'ammoBay', 'engine', 'gun', 'chassis']},
                'SPG': {'crew': ['commander', 'loader', 'gunner', 'driver'], 'device': ['ammoBay', 'engine', 'gun', 'turretRotator', 'chassis']},
                'AT-SPG': {'crew': ['loader', 'gunner', 'commander', 'driver'], 'device': ['ammoBay', 'gun', 'engine', 'turretRotator', 'chassis']}
            }, 'sound': {
                'fire': '/ingame_voice/notifications_VO/fire_stopped', 'commander': '/fortified_area/gui/transport_constrain', 'radioman': '/fortified_area/gui/transport_constrain',
                'driver': '/fortified_area/gui/transport_constrain', 'gunner': '/fortified_area/gui/transport_constrain', 'loader': '/fortified_area/gui/transport_constrain',
                'gun': '/fortified_area/gui/transport_constrain', 'engine': '/fortified_area/gui/transport_constrain', 'ammoBay': '/fortified_area/gui/transport_constrain',
                'turretRotator': '/fortified_area/gui/transport_constrain', 'chassis': '/ingame_voice/notifications_VO/track_functional', 'surveyingDevice': '/fortified_area/gui/transport_constrain',
                'radio': '/fortified_area/gui/transport_constrain', 'fuelTank': '/fortified_area/gui/transport_constrain', 'gold_med_kit': '/fortified_area/gui/transport_constrain',
                'gold_repair_kit': '/fortified_area/gui/transport_constrain'
            }, 'language': {
                'Русский': {
                }, 'English': {

                }
            }
        }

        self.setup = {
            'MODIFIER': {'MODIFIER_NONE': 0, 'MODIFIER_SHIFT': 1, 'MODIFIER_CTRL': 2, 'MODIFIER_ALT': 4},
            'KEY': {
                'KEY_NOT_FOUND': 0, 'KEY_NONE': 0, 'KEY_NULL': 0, 'KEY_ESCAPE': 1, 'KEY_1': 2, 'KEY_2': 3, 'KEY_3': 4, 'KEY_4': 5, 'KEY_5': 6, 'KEY_6': 7, 'KEY_7': 8, 'KEY_8': 9, 'KEY_9': 10,
                'KEY_0': 11, 'KEY_MINUS': 12, 'KEY_EQUALS': 13, 'KEY_BACKSPACE': 14, 'KEY_TAB': 15, 'KEY_Q': 16, 'KEY_W': 17, 'KEY_E': 18, 'KEY_R': 19, 'KEY_T': 20, 'KEY_Y': 21, 'KEY_U': 22,
                'KEY_I': 23, 'KEY_O': 24, 'KEY_P': 25, 'KEY_LBRACKET': 26, 'KEY_RBRACKET': 27, 'KEY_RETURN': 28, 'KEY_LCONTROL': 29, 'KEY_A': 30, 'KEY_S': 31, 'KEY_D': 32, 'KEY_F': 33, 'KEY_G': 34,
                'KEY_H': 35, 'KEY_J': 36, 'KEY_K': 37, 'KEY_L': 38, 'KEY_SEMICOLON': 39, 'KEY_APOSTROPHE': 40, 'KEY_GRAVE': 41, 'KEY_LSHIFT': 42, 'KEY_BACKSLASH': 43, 'KEY_Z': 44, 'KEY_X': 45,
                'KEY_C': 46, 'KEY_V': 47, 'KEY_B': 48, 'KEY_N': 49, 'KEY_M': 50, 'KEY_COMMA': 51, 'KEY_PERIOD': 52, 'KEY_SLASH': 53, 'KEY_RSHIFT': 54, 'KEY_NUMPADSTAR': 55, 'KEY_LALT': 56,
                'KEY_SPACE': 57, 'KEY_CAPSLOCK': 58, 'KEY_F1': 59, 'KEY_F2': 60, 'KEY_F3': 61, 'KEY_F4': 62, 'KEY_F5': 63, 'KEY_F6': 64, 'KEY_F7': 65, 'KEY_F8': 66, 'KEY_F9': 67, 'KEY_F10': 68,
                'KEY_NUMLOCK': 69, 'KEY_SCROLL': 70, 'KEY_NUMPAD7': 71, 'KEY_NUMPAD8': 72, 'KEY_NUMPAD9': 73, 'KEY_NUMPADMINUS': 74, 'KEY_NUMPAD4': 75, 'KEY_NUMPAD5': 76, 'KEY_NUMPAD6': 77,
                'KEY_ADD': 78, 'KEY_NUMPAD1': 79, 'KEY_NUMPAD2': 80, 'KEY_NUMPAD3': 81, 'KEY_NUMPAD0': 82, 'KEY_NUMPADPERIOD': 83, 'KEY_OEM_102': 86, 'KEY_F11': 87, 'KEY_F12': 88, 'KEY_F13': 100,
                'KEY_F14': 101, 'KEY_F15': 102, 'KEY_KANA': 112, 'KEY_ABNT_C1': 115, 'KEY_CONVERT': 121, 'KEY_NOCONVERT': 123, 'KEY_YEN': 125, 'KEY_ABNT_C2': 126, 'KEY_NUMPADEQUALS': 141,
                'KEY_PREVTRACK': 144, 'KEY_AT': 145, 'KEY_COLON': 146, 'KEY_UNDERLINE': 147, 'KEY_KANJI': 148, 'KEY_STOP': 149, 'KEY_AX': 150, 'KEY_UNLABELED': 151, 'KEY_NEXTTRACK': 153,
                'KEY_NUMPADENTER': 156, 'KEY_RCONTROL': 157, 'KEY_MUTE': 160, 'KEY_CALCULATOR': 161, 'KEY_PLAYPAUSE': 162, 'KEY_MEDIASTOP': 164, 'KEY_VOLUMEDOWN': 174, 'KEY_VOLUMEUP': 176,
                'KEY_WEBHOME': 178, 'KEY_NUMPADCOMMA': 179, 'KEY_NUMPADSLASH': 181, 'KEY_SYSRQ': 183, 'KEY_RALT': 184, 'KEY_PAUSE': 197, 'KEY_HOME': 199, 'KEY_UPARROW': 200, 'KEY_PGUP': 201,
                'KEY_LEFTARROW': 203, 'KEY_RIGHTARROW': 205, 'KEY_END': 207, 'KEY_DOWNARROW': 208, 'KEY_PGDN': 209, 'KEY_INSERT': 210, 'KEY_DELETE': 211, 'KEY_LWIN': 219, 'KEY_RWIN': 220,
                'KEY_APPS': 221, 'KEY_POWER': 222, 'KEY_SLEEP': 223, 'KEY_WAKE': 227, 'KEY_WEBSEARCH': 229, 'KEY_WEBFAVORITES': 230, 'KEY_WEBREFRESH': 231, 'KEY_WEBSTOP': 232, 'KEY_WEBFORWARD': 233,
                'KEY_WEBBACK': 234, 'KEY_MYCOMPUTER': 235, 'KEY_MAIL': 236, 'KEY_MEDIASELECT': 237, 'KEY_IME_CHAR': 255, 'KEY_MOUSE0': 256, 'KEY_LEFTMOUSE': 256, 'KEY_MOUSE1': 257,
                'KEY_RIGHTMOUSE': 257, 'KEY_MOUSE2': 258, 'KEY_MIDDLEMOUSE': 258, 'KEY_MOUSE3': 259, 'KEY_MOUSE4': 260, 'KEY_MOUSE5': 261, 'KEY_MOUSE6': 262, 'KEY_MOUSE7': 263, 'KEY_JOY0': 272,
                'KEY_JOY1': 273, 'KEY_JOY2': 274, 'KEY_JOY3': 275, 'KEY_JOY4': 276, 'KEY_JOY5': 277, 'KEY_JOY6': 278, 'KEY_JOY7': 279, 'KEY_JOY8': 280, 'KEY_JOY9': 281, 'KEY_JOY10': 282,
                'KEY_JOY11': 283, 'KEY_JOY12': 284, 'KEY_JOY13': 285, 'KEY_JOY14': 286, 'KEY_JOY15': 287, 'KEY_JOY16': 288, 'KEY_JOY17': 289, 'KEY_JOY18': 290, 'KEY_JOY19': 291, 'KEY_JOY20': 292,
                'KEY_JOY21': 293, 'KEY_JOY22': 294, 'KEY_JOY23': 295, 'KEY_JOY24': 296, 'KEY_JOY25': 297, 'KEY_JOY26': 298, 'KEY_JOY27': 299, 'KEY_JOY28': 300, 'KEY_JOY29': 301, 'KEY_JOY30': 302,
                'KEY_JOY31': 303, 'KEY_JOYDUP': 272, 'KEY_JOYDDOWN': 273, 'KEY_JOYDLEFT': 274, 'KEY_JOYDRIGHT': 275, 'KEY_JOYSTART': 276, 'KEY_JOYSELECT': 277, 'KEY_JOYBACK': 277,
                'KEY_JOYALPUSH': 278, 'KEY_JOYARPUSH': 279, 'KEY_JOYCROSS': 280, 'KEY_JOYA': 280, 'KEY_JOYCIRCLE': 281, 'KEY_JOYB': 281, 'KEY_JOYSQUARE': 282, 'KEY_JOYX': 282, 'KEY_JOYTRIANGLE': 283,
                'KEY_JOYY': 283, 'KEY_JOYL1': 284, 'KEY_JOYBLACK': 284, 'KEY_JOYR1': 285, 'KEY_JOYWHITE': 285, 'KEY_JOYL2': 286, 'KEY_JOYLTRIGGER': 286, 'KEY_JOYR2': 287, 'KEY_JOYRTRIGGER': 287,
                'KEY_JOYAHARD': 288, 'KEY_JOYBHARD': 289, 'KEY_JOYXHARD': 290, 'KEY_JOYYHARD': 291, 'KEY_JOYBLACKHARD': 292, 'KEY_JOYWHITEHARD': 293, 'KEY_JOYLTRIGGERHARD': 294,
                'KEY_JOYRTRIGGERHARD': 295, 'KEY_JOYALUP': 304, 'KEY_JOYALDOWN': 305, 'KEY_JOYALLEFT': 306, 'KEY_JOYALRIGHT': 307, 'KEY_JOYARUP': 308, 'KEY_JOYARDOWN': 309, 'KEY_JOYARLEFT': 310,
                'KEY_JOYARRIGHT': 311, 'KEY_DEBUG': 312, 'KEY_LCDKB_LEFT': 320, 'KEY_LCDKB_RIGHT': 321, 'KEY_LCDKB_OK': 322, 'KEY_LCDKB_CANCEL': 323, 'KEY_LCDKB_UP': 324, 'KEY_LCDKB_DOWN': 325,
                'KEY_LCDKB_MENU': 326
            },
            'buttons': {
                'crew_only': {'KEY': 0, 'MODIFIER': 0}, 'device_only': {'KEY': 0, 'MODIFIER': 0}, 'chassis_only': {'KEY': 56, 'MODIFIER': 0}, 'universal': {'KEY': 57, 'MODIFIER': 0}
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
        self.init_keys()

    def init_keys(self):
        buttons = self.data.get('buttons')
        if buttons['crew_only']['KEY']:
            if buttons['crew_only']['KEY'] in self.setup['KEY']:
                self.setup['buttons']['crew_only']['KEY'] = self.setup['KEY'][buttons['crew_only']['KEY']]
            if buttons['crew_only']['MODIFIER'] in self.setup['MODIFIER']:
                self.setup['buttons']['crew_only']['MODIFIER'] = self.setup['MODIFIER'][buttons['crew_only']['MODIFIER']]
        if buttons['device_only']['KEY']:
            if buttons['device_only']['KEY'] in self.setup['KEY']:
                self.setup['buttons']['device_only']['KEY'] = self.setup['KEY'][buttons['device_only']['KEY']]
            if buttons['device_only']['MODIFIER'] in self.setup['MODIFIER']:
                self.setup['buttons']['device_only']['MODIFIER'] = self.setup['MODIFIER'][buttons['device_only']['MODIFIER']]
        if buttons['chassis_only']['KEY']:
            if buttons['chassis_only']['KEY'] in self.setup['KEY']:
                self.setup['buttons']['chassis_only']['KEY'] = self.setup['KEY'][buttons['chassis_only']['KEY']]
            if buttons['chassis_only']['MODIFIER'] in self.setup['MODIFIER']:
                self.setup['buttons']['chassis_only']['MODIFIER'] = self.setup['MODIFIER'][buttons['chassis_only']['MODIFIER']]
        if buttons['universal']['KEY']:
            if buttons['universal']['KEY'] in self.setup['KEY']:
                self.setup['buttons']['universal']['KEY'] = self.setup['KEY'][buttons['universal']['KEY']]
            if buttons['universal']['MODIFIER'] in self.setup['MODIFIER']:
                self.setup['buttons']['universal']['MODIFIER'] = self.setup['MODIFIER'][buttons['universal']['MODIFIER']]

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


class Repair(object):
    def __init__(self):
        self.items = {}
        self.damaged = []
        self.destroyed = []
        self.fired = False
        self.ConsumablesPanel = None
        self.config = config.data.get('config')
        self.int_cd = {'extinguisher': 251, 'med_kit': 763, 'repair_kit': 1275, 'g_repair_kit': 1531, 'g_med_kit': 1019}
        self.crew = ['_None', 'commander', 'radioman', 'driver', 'driver1', 'driver2', 'gunner', 'gunner1', 'gunner2', 'loader', 'loader1', 'loader2']
        self.device = ['_None', 'gun', 'engine', 'ammoBay', 'turretRotator', 'chassis', 'leftTrack', 'rightTrack', 'surveyingDevice', 'radio', 'fuelTank']
        self.v_FireCodes = ('FIRE', 'DEVICE_STARTED_FIRE_AT_SHOT', 'DEVICE_STARTED_FIRE_AT_RAMMING', 'FIRE_STOPPED')
        self.v_DamageCodes = (
            'DEVICE_CRITICAL', 'DEVICE_REPAIRED_TO_CRITICAL', 'DEVICE_CRITICAL_AT_SHOT', 'DEVICE_CRITICAL_AT_RAMMING', 'DEVICE_CRITICAL_AT_FIRE', 'DEVICE_CRITICAL_AT_WORLD_COLLISION',
            'DEVICE_CRITICAL_AT_DROWNING', 'ENGINE_CRITICAL_AT_UNLIMITED_RPM', 'DEVICE_DESTROYED', 'DEVICE_DESTROYED_AT_SHOT', 'DEVICE_DESTROYED_AT_RAMMING', 'DEVICE_DESTROYED_AT_FIRE',
            'DEVICE_DESTROYED_AT_WORLD_COLLISION', 'DEVICE_DESTROYED_AT_DROWNING', 'ENGINE_DESTROYED_AT_UNLIMITED_RPM')
        self.v_RepairedCodes = ('DEVICE_REPAIRED_TO_CRITICAL',)
        self.v_Destroyed_Codes = (
            'DEVICE_DESTROYED', 'DEVICE_DESTROYED_AT_SHOT', 'DEVICE_DESTROYED_AT_RAMMING', 'DEVICE_DESTROYED_AT_FIRE', 'DEVICE_DESTROYED_AT_WORLD_COLLISION', 'DEVICE_DESTROYED_AT_DROWNING',
            'ENGINE_DESTROYED_AT_UNLIMITED_RPM')
        self.m_DamageCodes = (
            'TANKMAN_HIT_AT_RAMMING', 'TANKMAN_HIT_AT_FIRE', 'TANKMAN_HIT_AT_EXPLOSION', 'TANKMAN_HIT', 'TANKMAN_HIT_AT_SHOT', 'TANKMAN_HIT_AT_WORLD_COLLISION', 'TANKMAN_HIT_AT_DROWNING',
            'TANKMAN_HIT_AT_DROWNING')
        self.DeathCodes = (
            'DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE', 'DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT', 'DEATH_FROM_FIRE', 'DEATH_FROM_INACTIVE_CREW', 'DEATH_FROM_INACTIVE_CREW_AT_SHOT', 'DEATH_FROM_RAMMING',
            'DEATH_FROM_SHOT')
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

    @staticmethod
    def get_extra_name(extra):
        if extra.name == 'fire': return extra.name
        return extra.name[:-len('Health')]

    def get_info(self, damage_code, extra):
        extra_name = self.get_extra_name(extra)
        self.time = BigWorld.time()
        if damage_code not in self.DeathCodes:
            if extra_name in self.device:
                if damage_code in self.v_FireCodes and self.config['use_extinguisher'] and self.check_item('extinguisher'):
                    if damage_code == 'FIRE_STOPPED' or extra_name == '_None': self.fired = False
                    else: self.fired = True
                if damage_code in self.v_DamageCodes:
                    if extra_name not in self.damaged and extra_name not in ['chassis', 'leftTrack', 'rightTrack']:
                        self.damaged.append(extra_name)
                    if damage_code in self.v_Destroyed_Codes and extra_name not in self.destroyed and extra_name in ['chassis', 'leftTrack', 'rightTrack']:
                        self.destroyed.append(extra_name)
                    if damage_code in self.v_RepairedCodes and extra_name in self.destroyed:
                        self.destroyed.remove(extra_name)
            if extra_name in self.crew:
                if damage_code in self.m_DamageCodes:
                    if extra_name not in self.damaged:
                        self.damaged.append(extra_name)

    def fires(self):
        if self.config['use_extinguisher'] and self.fired and self.check_item('extinguisher'):
            self.use_item(self.int_cd['extinguisher'])
            self.fired = False
            self.play_sound('fire')


    @staticmethod
    def check_class(tank_class):
        if 'lightTank' in tank_class: return 'lightTank'
        if 'mediumTank' in tank_class: return 'mediumTank'
        if 'heavyTank' in tank_class: return 'heavyTank'
        if 'SPG' in tank_class: return 'SPG'
        if 'AT-SPG' in tank_class: return 'AT-SPG'

    def play_sound(self, module):
        if self.config['play_sound']:
            if module in config.data['sound']:
                SoundGroups.g_instance.playStinger(config.data['sound'][module], 1)
                #SoundGroups.g_instance.playSound2D(config.data['sound'][module])

    def heal(self):
        if self.config['heal_crew']:
            my_tank_class = self.check_class(BigWorld.player().vehicleTypeDescriptor.type.tags)
            if self.config['class_specific']:
                specific = config.data['class_specific'].get(my_tank_class)
            else:
                specific = config.data['class_specific'].get('None')
            if self.check_item('med_kit'):
                for crew in specific['crew']:
                    if crew in self.damaged:
                        self.use_item(self.int_cd['med_kit'], crew)
                        self.damaged.remove(crew)
                        self.play_sound(crew)
                        break
                    if crew == 'driver':
                        for module in ['driver', 'driver1', 'driver2']:
                            if module in self.damaged:
                                self.use_item(self.int_cd['med_kit'], module)
                                self.damaged.remove(module)
                                self.play_sound(module)
                                break
                    if crew == 'gunner':
                        for module in ['gunner', 'gunner1', 'gunner2']:
                            if module in self.damaged:
                                self.use_item(self.int_cd['med_kit'], module)
                                self.damaged.remove(module)
                                self.play_sound(module)
                                break
                    if crew == 'loader':
                        for module in ['loader', 'loader1', 'loader2']:
                            if module in self.damaged:
                                self.use_item(self.int_cd['med_kit'], module)
                                self.damaged.remove(module)
                                self.play_sound(module)
                                break

            elif self.check_item('g_med_kit'):
                for crew in specific['crew']:
                    if crew in self.damaged:
                        self.use_item(self.int_cd['g_med_kit'], crew)
                        for module in self.crew:
                            if module in self.damaged: self.damaged.remove(module)
                        self.play_sound('gold_med_kit')
                        break
                    if crew == 'driver':
                        for module in ['driver', 'driver1', 'driver2']:
                            if module in self.damaged:
                                self.use_item(self.int_cd['g_med_kit'], module)
                                for module1 in self.crew:
                                    if module1 in self.damaged: self.damaged.remove(module1)
                                self.play_sound('gold_med_kit')
                                break
                    if crew == 'gunner':
                        for module in ['gunner', 'gunner1', 'gunner2']:
                            if module in self.damaged:
                                self.use_item(self.int_cd['g_med_kit'], module)
                                for module1 in self.crew:
                                    if module1 in self.damaged: self.damaged.remove(module1)
                                self.play_sound('gold_med_kit')
                                break
                    if crew == 'loader':
                        for module in ['loader', 'loader1', 'loader2']:
                            if module in self.damaged:
                                self.use_item(self.int_cd['g_med_kit'], module)
                                for module1 in self.crew:
                                    if module1 in self.damaged: self.damaged.remove(module1)
                                self.play_sound('gold_med_kit')
                                break


    def repair(self):
        if self.config['repair_device']:
            my_tank_class = self.check_class(BigWorld.player().vehicleTypeDescriptor.type.tags)
            if self.config['class_specific']:
                specific = config.data['class_specific'].get(my_tank_class)
            else:
                specific = config.data['class_specific'].get('None')
            if self.check_item('repair_kit'):
                for device in specific['device']:
                    if device == 'chassis':
                        for device1 in ['chassis', 'leftTrack', 'rightTrack']:
                            if device1 in self.destroyed:
                                self.use_item(self.int_cd['repair_kit'], device1)
                                if device1 in self.destroyed: self.destroyed.remove(device1)
                                if device1 in self.damaged: self.damaged.remove(device1)
                                self.play_sound(device)
                                break
                    elif device in self.damaged:
                        self.use_item(self.int_cd['repair_kit'], device)
                        self.damaged.remove(device)
                        self.play_sound(device)
                        break
            elif self.check_item('g_repair_kit'):
                for device in specific['device']:
                    if device == 'chassis':
                        for device1 in ['chassis', 'leftTrack', 'rightTrack']:
                            if device1 in self.destroyed:
                                self.use_item(self.int_cd['g_repair_kit'], device1)
                                for module in self.device:
                                    if module in self.damaged: self.damaged.remove(module)
                                    if module in self.destroyed: self.destroyed.remove(module)
                                    self.play_sound('gold_repair_kit')
                                    self.play_sound(device)
                                break
                    elif device in self.damaged:
                        self.use_item(self.int_cd['g_repair_kit'], device)
                        for module in self.device:
                            if module in self.damaged: self.damaged.remove(module)
                            if module in self.destroyed: self.destroyed.remove(module)
                        self.play_sound('gold_repair_kit')
                        break

    def repair_chassis(self):
        if self.check_item('repair_kit'):
            for device in ['chassis', 'leftTrack', 'rightTrack']:
                if device in self.destroyed:
                    self.use_item(self.int_cd['repair_kit'], device)
                    if device in self.destroyed: self.destroyed.remove(device)
                    if device in self.damaged: self.damaged.remove(device)
                    self.play_sound('chassis')
                    break
        elif self.check_item('g_repair_kit'):
            for device in ['chassis', 'leftTrack', 'rightTrack']:
                if device in self.destroyed:
                    self.use_item(self.int_cd['g_repair_kit'], device)
                    for module in self.device:
                        if module in self.damaged: self.damaged.remove(module)
                        if module in self.destroyed: self.destroyed.remove(module)
                    self.play_sound('gold_repair_kit')
                    self.play_sound('chassis')
                    break


# deformed functions:
def hook_update_all(self):
    hooked_update_all(self)
    config.analytics()


def hook_handle_equipment_expanded(self, int_cd):
    if config.enable and config.data['config'].get('button_expanded'):
        item = g_sessionProvider.getEquipmentsCtrl().getEquipment(int_cd)
        if not item: return
        for _, (_, _, entityState) in enumerate(item.getGuiIterator()):
            if entityState and entityState in ['destroyed', 'critical']: return hooked_handle_equipment_expanded(self, int_cd)
        return
    else: return hooked_handle_equipment_expanded(self, int_cd)


def hook_show_vehicle_damage_info(self, vehicle_id, damage_index, extra_index, entity_id, equipment_id):
    if config.enable:
        damage_code = DAMAGE_INFO_CODES[damage_index]
        extra = self.vehicleTypeDescriptor.extras[extra_index] if extra_index != 0 else None
        if vehicle_id == self.playerVehicleID or not self.isVehicleAlive and vehicle_id == self.inputHandler.ctrl.curVehicleID:
            if extra: repair.get_info(damage_code, extra)
    return hooked_show_vehicle_damage_info(self, vehicle_id, damage_index, extra_index, entity_id, equipment_id)


def inject_handle_key_event(event):
    if config.enable:
        is_down, key, mods, is_repeat = game.convertKeyEvent(event)
        if key == config.setup['buttons']['crew_only']['KEY'] and is_down and mods == config.setup['buttons']['crew_only']['MODIFIER']:
            repair.heal()
        if key == config.setup['buttons']['device_only']['KEY'] and is_down and mods == config.setup['buttons']['device_only']['MODIFIER']:
            repair.repair()
        if key == config.setup['buttons']['chassis_only']['KEY'] and is_down and mods == config.setup['buttons']['chassis_only']['MODIFIER']:
            repair.repair_chassis()
        if key == config.setup['buttons']['universal']['KEY'] and is_down and mods == config.setup['buttons']['universal']['MODIFIER']:
            repair.fires()
            repair.heal()
            repair.repair()


def hook_add_equipment_slot(self, int_cd, item):
    if config.enable:
        repair.ConsumablesPanel = self
        repair.eq_add(int_cd, item)
    return hooked_add_equipment_slot(self, int_cd, item)


def hook_start_battle(self):
    hooked_start_battle(self)
    if config.enable:
        repair.clear()


def hook_stop_battle(self):
    hooked_stop_battle(self)
    if config.enable:
        repair.clear()


#start mod
config = Config()
config.load_mod()
repair = Repair()

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
