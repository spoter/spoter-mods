# -*- coding: utf-8 -*-
import os
import re
import json
import codecs
import datetime
import threading
import urllib
import urllib2
import string
import random

import BigWorld
from constants import AUTH_REALM
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.battle_control import g_sessionProvider
from Avatar import PlayerAvatar
from constants import BATTLE_EVENT_TYPE
import SoundGroups
from gui.app_loader import g_appLoader


class Config(object):
    def __init__(self):
        self.enable = True
        self.debug = False
        self.ru = True if 'RU' in AUTH_REALM else False
        self.version = 'v3.08(11.09.2015)'
        self.author = 'by spoter'
        self.description = 'spotted_extended_light'
        self.description_ru = 'Мод: "Маленький Светлячок"'
        self.author_ru = 'автор: spoter'
        self.name = 'spotted_extended_light'
        self.description_analytics = 'Мод: "Маленький Светлячок"'
        self.tid = 'UA-57975916-7'
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
                'enable': True, 'debug': False, 'sound': True, 'icon_size': [70, 24], 'language': 'Русский'
            }, 'sound': {
                '%s' % BATTLE_EVENT_TYPE.SPOTTED: '/GUI/notifications_FX/enemy_sighted_for_team', '%s' % BATTLE_EVENT_TYPE.RADIO_HIT_ASSIST: '/GUI/notifications_FX/gun_intuition',
                '%s' % BATTLE_EVENT_TYPE.RADIO_KILL_ASSIST: '/GUI/notifications_FX/cybersport_auto_search', '%s' % BATTLE_EVENT_TYPE.TRACK_ASSIST: '/GUI/notifications_FX/gun_intuition'

            }, 'language': {
                'Русский': {
                    'messages': {
                        '%s' % BATTLE_EVENT_TYPE.SPOTTED: 'Засвечены {icons}', '%s' % BATTLE_EVENT_TYPE.RADIO_HIT_ASSIST: 'Урон по засвету в {icons_names}',
                        '%s' % BATTLE_EVENT_TYPE.RADIO_KILL_ASSIST: 'Убили по засвету {full}', '%s' % BATTLE_EVENT_TYPE.TRACK_ASSIST: 'Ассист {icons_vehicles} за сбитые траки'
                    }
                }, 'English': {
                    'messages': {
                        '%s' % BATTLE_EVENT_TYPE.SPOTTED: 'Spotted {icons}', '%s' % BATTLE_EVENT_TYPE.RADIO_HIT_ASSIST: 'Radio hit assist to {icons_names}',
                        '%s' % BATTLE_EVENT_TYPE.RADIO_KILL_ASSIST: 'Radio kill assist to {full}', '%s' % BATTLE_EVENT_TYPE.TRACK_ASSIST: 'Tracks assist {icons_vehicles}'
                    }

                }, 'Deutsch': {
                    'messages': {
                        '%s' % BATTLE_EVENT_TYPE.SPOTTED: 'Gefunden {icons}', '%s' % BATTLE_EVENT_TYPE.RADIO_HIT_ASSIST: 'Schaden von Licht in {icons_names}',
                        '%s' % BATTLE_EVENT_TYPE.RADIO_KILL_ASSIST: 'Bei gluht getotet {full}', '%s' % BATTLE_EVENT_TYPE.TRACK_ASSIST: 'Assist {icons_vehicles} fur schwer verletzte tracks'
                    }
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


class Assist(object):
    def __init__(self):
        self.format_str = {'icons': '', 'names': '', 'vehicles': '', 'icons_names': '', 'icons_vehicles': '', 'full': ''}

    @staticmethod
    def check_macros(macros):
        if macros in config.language['messages']['0']: return True
        if macros in config.language['messages']['1']: return True
        if macros in config.language['messages']['2']: return True
        if macros in config.language['messages']['3']: return True

    def format_recreate(self):
        self.format_str = {'icons': '', 'names': '', 'vehicles': '', 'icons_names': '', 'icons_vehicles': '', 'full': ''}

    @staticmethod
    def sound(assist_type):
        if '%s' % assist_type in config.data['sound']:
            if config.data['sound'][assist_type] != '':
                sound = SoundGroups.g_instance.getSound2D(config.data['sound'][assist_type])
                if sound:
                    sound.play()

    def post_message(self, assist_type, vehicles_ids):
        if assist_type in config.language['messages']:
            self.format_recreate()
            for i in vehicles_ids:
                if i >> 32 & 4294967295L > 0: i = i >> 32 & 4294967295L
                else: i &= 4294967295L
                icon = '<img src="img://%s" width="%s" height="%s" />' % (
                    g_sessionProvider.getArenaDP().getVehicleInfo(i).vehicleType.iconPath.replace('..', 'gui'), config.data['config'].get('icon_size')[0], config.data['config'].get('icon_size')[1])
                target_info = g_sessionProvider.getCtx().getFullPlayerNameWithParts(vID=i)
                if self.check_macros('{icons}'): self.format_str['icons'] += icon
                if self.check_macros('{names}'): self.format_str['names'] += '[%s]' % target_info[1] if target_info[1] else icon
                if self.check_macros('{vehicles}'): self.format_str['vehicles'] += '[%s]' % target_info[4] if target_info[4] else icon
                if self.check_macros('{icons_names}'): self.format_str['icons_names'] += '%s[%s]' % (icon, target_info[1]) if target_info[1] else icon
                if self.check_macros('{icons_vehicles}'): self.format_str['icons_vehicles'] += '%s[%s]' % (icon, target_info[4]) if target_info[4] else icon
                if self.check_macros('{full}'):
                    full = g_sessionProvider.getCtx().getFullPlayerName(vID=i)
                    self.format_str['full'] += '%s[%s]' % (icon, full) if full else icon
            msg = config.language['messages'][assist_type].format(**self.format_str)
            g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', [msg + random.choice(string.ascii_letters), '%s' % msg.decode('utf-8-sig'), 'gold'])


# deformed functions:
def hook_update_all(self):
    hooked_update_all(self)
    config.analytics()


def hook_on_battle_event(self, event_type, details):
    if config.enable:
        assist_type = '%s' % event_type
        if config.data['config'].get('sound'): assist.sound(assist_type)
        assist.post_message(assist_type, details)
    return hooked_on_battle_event(self, event_type, details)


#hooked
# noinspection PyProtectedMember
hooked_update_all = Hangar._Hangar__updateAll
hooked_on_battle_event = PlayerAvatar.onBattleEvent

#hook
Hangar._Hangar__updateAll = hook_update_all
PlayerAvatar.onBattleEvent = hook_on_battle_event

#start mod
assist = Assist()
config = Config()
config.load_mod()
