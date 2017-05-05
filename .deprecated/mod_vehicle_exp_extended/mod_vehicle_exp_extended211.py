# -*- coding: utf-8 -*-
import textwrap
import datetime
import re
import os
import json
import codecs
import threading
import urllib
import urllib2
import math

import BigWorld
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.tooltips import getUnlockPrice
from gui.Scaleform.daapi.view.meta.ParamsMeta import ParamsMeta
from gui.server_events.EventsCache import g_eventsCache
from helpers import int2roman
import BigWorld
from constants import AUTH_REALM
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.shared import g_itemsCache
from CurrentVehicle import g_currentVehicle


class Config(object):
    def __init__(self):
        self.enable = True
        self.debug = False
        self.ru = True if 'RU' in AUTH_REALM else False
        self.version = 'v2.11(18.11.2015)'
        self.author = 'by spoter'
        self.description = 'vehicle_exp_extended'
        self.description_ru = 'Мод: "Танкопыт"'
        self.author_ru = 'автор: spoter'
        self.name = 'vehicle_exp_extended'
        self.description_analytics = 'Мод: "Танкопыт"'
        self.tid = 'UA-57975916-8'
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
                'enable': True, 'debug': False, 'free_xp_calculate': True, 'module_status': True, 'elite_status': True, 'next_tanks_status': True, 'tank_params': True, 'quest_status': True,
                'show_conditions_string': True, 'show_quest_title_string': False, 'short_numbers': False, 'language': 'Русский'

            }, 'language': {
                'Русский': {
                    'module_status_string1': 'Модули',
                    'module_status_string2': '<img align="top" src="img://gui/maps//icons/buttons/removeGold.png" height="15" width="13" vspace="-2"> <font color="#00FF00">{chk-exp}</font><img '
                                             'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> из <font color="#FF0000">{need-exp}</font><img '
                                             'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                             'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'module_status_ready_string1': 'Модули',
                    'module_status_ready_string2': '<img align="top" src="img://gui/maps//icons/buttons/removeGold.png" height="16" width="14" vspace="-2"> <font color="#00FF00">Все модули '
                                                   'доступны!</font>', 'elite_status_string1': '{tank-name}',
                    'elite_status_string2': '<img align="top" src="img://gui/maps//icons/library/EliteXpIcon-2.png" height="16" width="16" vspace="-3"> <font color="#00FF00">{chk-exp}</font><img '
                                            'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> из <font color="#FF0000">{need-exp}</font><img '
                                            'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                            'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'elite_status_ready_string1': '{tank-name}',
                    'elite_status_ready_string2': '<img align="top" src="img://gui/maps//icons/library/EliteXpIcon-2.png" height="16" width="16" vspace="-3"> <font color="#00FF00">Элитный статус '
                                                  'доступен!</font>', 'next_tanks_string1': '{tank-name}',
                    'next_tanks_string2': '<img align="top" src="img://gui/maps//icons/library/UnlockPrice.png" height="16" width="16" vspace="-2"> <font color="#00FF00">{chk-exp}</font><img '
                                          'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> из <font color="#FF0000">{need-exp}</font><img '
                                          'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                          'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'next_tanks_ready_string1': '{tank-name}',
                    'next_tanks_ready_string2': '<img align="top" src="img://gui/maps//icons/library/UnlockPrice.png" height="16" width="16" vspace="-2"> <font color="#00FF00">Исследование '
                                                'доступно!</font>', 'quest_title': '<b><font color="#FFE041">Текущие Личные Боевые Задачи</font></b>',
                    'text_quest_info': '<b><font color="#E8E0BD">{quest-name}</font></b> (мин. уровень #{quest-min-level})',
                    'text_main_condition': '<b><font color="#aefe57">{quest-main-condition}</font></b>', 'text_main_condition_extra': 'Осн. Условия',
                    'text_add_condition': '<font color="#aefe57">{quest-add-condition}</font>', 'text_add_condition_extra': 'Доп. условия'
                }, 'English': {
                    'module_status_string1': 'Modules',
                    'module_status_string2': '<img align="top" src="img://gui/maps//icons/buttons/removeGold.png" height="15" width="13" vspace="-2"> <font color="#00FF00">{chk-exp}</font><img '
                                             'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> of <font color="#FF0000">{need-exp}</font><img '
                                             'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                             'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'module_status_ready_string1': 'Modules',
                    'module_status_ready_string2': '<img align="top" src="img://gui/maps//icons/buttons/removeGold.png" height="16" width="14" vspace="-2"> <font color="#00FF00">Module research '
                                                   'available!</font>', 'elite_status_string1': '{tank-name}',
                    'elite_status_string2': '<img align="top" src="img://gui/maps//icons/library/EliteXpIcon-2.png" height="16" width="16" vspace="-3"> <font color="#00FF00">{chk-exp}</font><img '
                                            'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> of <font color="#FF0000">{need-exp}</font><img '
                                            'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                            'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'elite_status_ready_string1': '{tank-name}',
                    'elite_status_ready_string2': '<img align="top" src="img://gui/maps//icons/library/EliteXpIcon-2.png" height="16" width="16" vspace="-3"> <font color="#00FF00">Elite status '
                                                  'available!</font>', 'next_tanks_string1': '{tank-name}',
                    'next_tanks_string2': '<img align="top" src="img://gui/maps//icons/library/UnlockPrice.png" height="16" width="16" vspace="-2"> <font color="#00FF00">{chk-exp}</font><img '
                                          'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> of <font color="#FF0000">{need-exp}</font><img '
                                          'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                          'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'next_tanks_ready_string1': '{tank-name}',
                    'next_tanks_ready_string2': '<img align="top" src="img://gui/maps//icons/library/UnlockPrice.png" height="16" width="16" vspace="-2"> <font color="#00FF00">Research '
                                                'available!</font>', 'quest_title': '<b><font color="#FFE041">Personal Missions</font></b>',
                    'text_quest_info': '<b><font color="#E8E0BD">{quest-name}</b></font> (min lvl #{quest-min-level})',
                    'text_main_condition': '<b><font color="#aefe57">{quest-main-condition}</font></b>', 'text_main_condition_extra': 'Main Condition',
                    'text_add_condition': '<font color="#aefe57">{quest-add-condition}</font>', 'text_add_condition_extra': 'Add. Condition'
                }, 'Français': {
                    'module_status_string1': 'Tous Les Modules',
                    'module_status_string2': '<img align="top" src="img://gui/maps//icons/buttons/removeGold.png" height="15" width="13" vspace="-2"> <font color="#00FF00">{chk-exp}</font><img '
                                             'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> sur <font color="#FF0000">{need-exp}</font><img '
                                             'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                             'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'module_status_ready_string1': 'Tous Les Modules',
                    'module_status_ready_string2': '<img align="top" src="img://gui/maps//icons/buttons/removeGold.png" height="16" width="14" vspace="-2"> <font color="#00FF00">Modules '
                                                   'Disponible!</font>',
                    'elite_status_string1': '{tank-name}',
                    'elite_status_string2': '<img align="top" src="img://gui/maps//icons/library/EliteXpIcon-2.png" height="16" width="16" vspace="-3"> <font color="#00FF00">{chk-exp}</font><img '
                                            'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> sur <font color="#FF0000">{need-exp}</font><img '
                                            'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                            'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'elite_status_ready_string1': '{tank-name}',
                    'elite_status_ready_string2': '<img align="top" src="img://gui/maps//icons/library/EliteXpIcon-2.png" height="16" width="16" vspace="-3"> <font color="#00FF00">Status Elite '
                                                  'Disponible!</font>',
                    'next_tanks_string1': '{tank-name}',
                    'next_tanks_string2': '<img align="top" src="img://gui/maps//icons/library/UnlockPrice.png" height="16" width="16" vspace="-2"> <font color="#00FF00">{chk-exp}</font><img '
                                          'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> sur <font color="#FF0000">{need-exp}</font><img '
                                          'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                          'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'next_tanks_ready_string1': '{tank-name}',
                    'next_tanks_ready_string2': '<img align="top" src="img://gui/maps//icons/library/UnlockPrice.png" height="16" width="16" vspace="-2"> <font color="#00FF00">Recherche '
                                                'Disponible!</font>',
                    'quest_title': '<b><font color="#FFE041">Missions Personnel</font></b>', 'text_quest_info': '<b><font color="#E8E0BD">{quest-name}</b></font> (Mini Tier #{quest-min-level})',
                    'text_main_condition': '<b><font color="#aefe57">{quest-main-condition}</font></b>', 'text_main_condition_extra': 'Principale',
                    'text_add_condition': '<font color="#aefe57">{quest-add-condition}</font>', 'text_add_condition_extra': 'Secondaire'
                }, 'Deutsch': {
                    'module_status_string1': 'Alle Module erforschen',
                    'module_status_string2': '<img align="top" src="img://gui/maps//icons/buttons/removeGold.png" height="15" width="13" vspace="-2"> <font color="#00FF00">{chk-exp}</font><img '
                                             'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> von <font color="#FF0000">{need-exp}</font><img '
                                             'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                             'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'module_status_ready_string1': 'Alle Module erforschen',
                    'module_status_ready_string2': '<img align="top" src="img://gui/maps//icons/buttons/removeGold.png" height="16" width="14" vspace="-2"> <font color="#00FF00">Modulerforschung '
                                                   'verfügbar!</font>', 'elite_status_string1': '{tank-name}',
                    'elite_status_string2': '<img align="top" src="img://gui/maps//icons/library/EliteXpIcon-2.png" height="16" width="16" vspace="-3"> <font color="#00FF00">{chk-exp}</font><img '
                                            'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> von <font color="#FF0000">{need-exp}</font><img '
                                            'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                            'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'elite_status_ready_string1': '{tank-name}',
                    'elite_status_ready_string2': '<img align="top" src="img://gui/maps//icons/library/EliteXpIcon-2.png" height="16" width="16" vspace="-3"> <font color="#00FF00">Elitestatus '
                                                  'verfügbar!</font>', 'next_tanks_string1': '{tank-name}',
                    'next_tanks_string2': '<img align="top" src="img://gui/maps//icons/library/UnlockPrice.png" height="16" width="16" vspace="-2"> <font color="#00FF00">{chk-exp}</font><img '
                                          'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> von <font color="#FF0000">{need-exp}</font><img '
                                          'align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"> (~{battles-left}<img align="top" '
                                          'src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3">)', 'next_tanks_ready_string1': '{tank-name}',
                    'next_tanks_ready_string2': '<img align="top" src="img://gui/maps//icons/library/UnlockPrice.png" height="16" width="16" vspace="-2"> <font color="#00FF00">Forschung '
                                                'verfügbar!</font>', 'quest_title': '<b><font color="#FFE041">Persönliche Aufträge</font></b>',
                    'text_quest_info': '<b><font color="#E8E0BD">{quest-name}</b></font> (Min. Tierstufe #{quest-min-level})',
                    'text_main_condition': '<b><font color="#aefe57">{quest-main-condition}</font></b>', 'text_main_condition_extra': 'Hauptbedingung',
                    'text_add_condition': '<font color="#aefe57">{quest-add-condition}</font>', 'text_add_condition_extra': 'Nebenbedingung'
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


class VehExp(object):
    def __init__(self):
        self.quest_status = config.data['config'].get('quest_status')
        self.free_xp_calculate = config.data['config'].get('free_xp_calculate')
        self.module_status = config.data['config'].get('module_status')
        self.elite_status = config.data['config'].get('elite_status')
        self.next_tanks_status = config.data['config'].get('next_tanks_status')
        self.tank_params = config.data['config'].get('tank_params')
        self.short_numbers = config.data['config'].get('short_numbers')

    @staticmethod
    def fix_number(value):
        value = float(value)
        if value < 1000: return '%s' % int(value)
        elif value < 100000: return '{:0.1f}k'.format(value / 1000.0)
        elif value < 1000000: return '{0:d}k'.format(int(math.ceil(value / 1000.0)))
        else: return '{:0.1f}M'.format(value / 1000000.0)

    def change(self, data):
        result = {'params': []}
        result['params'].extend(self.vehicle_exp())
        if self.quest_status: result['params'].extend(self.quest())
        if self.tank_params: result['params'].extend(data['params'])
        return result

    @staticmethod
    def pack(text, html):
        return [{'selected': False, 'param': '%s' % text, 'text': '<h1>%s</h1>' % html}]

    def mark_text_main(self, texts):
        data = []
        format_str = {}
        text = texts.splitlines()
        for word in text:
            op = textwrap.wrap('%s' % word.decode('utf-8-sig'), 44, break_long_words=False)
            for sight in op:
                format_str['quest-main-condition'] = sight
                if not op.index(sight) and not text.index(word):
                    data.extend(self.pack(config.language['text_main_condition_extra'], config.language['text_main_condition'].format(**format_str)))
                else:
                    data.extend(self.pack('', config.language['text_main_condition'].format(**format_str)))
        return data

    def mark_text_seq(self, texts):
        data = []
        format_str = {}
        text = texts.splitlines()
        for word in text:
            op = textwrap.wrap('%s' % word.decode('utf-8-sig'), 44, break_long_words=False)
            for sight in op:
                format_str['quest-add-condition'] = sight
                if not op.index(sight) and not text.index(word):
                    data.extend(self.pack(config.language['text_add_condition_extra'], config.language['text_add_condition'].format(**format_str)))
                else:
                    data.extend(self.pack('', config.language['text_add_condition'].format(**format_str)))
        return data

    def quest(self):
        data = []
        player_quest = {}
        for player_quests in g_eventsCache.potapov.getSelectedQuests().itervalues():
            quest_class = player_quests.getVehicleClasses()
            if not quest_class or g_currentVehicle.item.type in quest_class:
                player_quest[player_quests.getID()] = player_quests
        if player_quest:
            for quest in player_quest:
                quest_level = player_quest[quest].getVehMinLevel()
                if g_currentVehicle.item.level >= quest_level:
                    format_str = {}
                    if config.data['config'].get('show_quest_title_string'):
                        data.extend(self.pack('', config.language['quest_title']))
                    if 'quest-name' in config.language['text_quest_info']:
                        format_str['quest-name'] = '%s' % player_quest[quest].getUserName().decode('utf-8-sig')
                    if 'quest-min-level' in config.language['text_quest_info']:
                        format_str['quest-min-level'] = '%s' % quest_level
                    if 'quest-min-level-roman' in config.language['text_quest_info']:
                        format_str['quest-min-level-roman'] = '%s' % int2roman(quest_level).decode('utf-8-sig')
                    data.extend(self.pack('', config.language['text_quest_info'].format(**format_str)))
                    if config.data['config'].get('show_conditions_string'):
                        data.extend(self.mark_text_main(player_quest[quest].getUserMainCondition()))
                        data.extend(self.mark_text_seq(player_quest[quest].getUserAddCondition()))
        return data

    def vehicle_exp(self):
        data = []
        vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.EMPTY)
        temp = self.create_exp_status(vehicles)
        if temp:
            exp = g_currentVehicle.item.xp
            free_exp = g_itemsCache.items.stats.freeXP #g_itemsCache.items.stats.actualFreeXP
            avg_xp = g_itemsCache.items.getVehicleDossier(g_currentVehicle.item.intCD).getRandomStats().getAvgXP()
            if not avg_xp: avg_xp = 0
            modules_exp_needed, elite_exp_need, research_vehicles, e_research, m_research = temp
            format_str = {
                'tank-name': '%s' % g_currentVehicle.item.shortUserName.decode('utf-8-sig'),
                'cur-tank-exp': '%s' % (self.fix_number(exp) if self.short_numbers else BigWorld.wg_getIntegralFormat(exp)).decode('utf-8-sig'),
                'freeXp': '%s' % (self.fix_number(free_exp) if self.short_numbers else BigWorld.wg_getIntegralFormat(free_exp)).decode('utf-8-sig')
            }

            if self.module_status:
                modules_exp = modules_exp_needed
                modules_exp_needed -= exp
                if self.free_xp_calculate: modules_exp_needed -= free_exp
                if modules_exp_needed > 0:
                    modules_battles = modules_exp_needed / avg_xp if avg_xp > 0 else 1
                    modules_battles = '%s' % (self.fix_number(modules_battles) if self.short_numbers else BigWorld.wg_getIntegralFormat(modules_battles)).decode('utf-8-sig')
                    format_str['need-exp'] = '%s' % (self.fix_number(modules_exp) if self.short_numbers else BigWorld.wg_getIntegralFormat(modules_exp)).decode('utf-8-sig')
                    format_str['chk-exp'] = '%s' % (self.fix_number(modules_exp_needed) if self.short_numbers else BigWorld.wg_getIntegralFormat(modules_exp_needed)).decode('utf-8-sig')
                    format_str['battles-left'] = modules_battles if avg_xp > 0 else 'X'
                    data.extend(self.pack(config.language['module_status_string1'].format(**format_str), config.language['module_status_string2'].format(**format_str)))
                elif m_research:
                    data.extend(self.pack(config.language['module_status_ready_string1'].format(**format_str), config.language['module_status_ready_string2'].format(**format_str)))

            if self.elite_status:
                elite_exp = elite_exp_need
                elite_exp_need -= exp
                if self.free_xp_calculate: elite_exp_need -= free_exp
                if elite_exp_need > 0:
                    elite_battles = elite_exp_need / avg_xp if avg_xp > 0 else 1
                    elite_battles = '%s' % (self.fix_number(elite_battles) if self.short_numbers else BigWorld.wg_getIntegralFormat(elite_battles)).decode('utf-8-sig')
                    format_str['need-exp'] = '%s' % (self.fix_number(elite_exp) if self.short_numbers else BigWorld.wg_getIntegralFormat(elite_exp)).decode('utf-8-sig')
                    format_str['chk-exp'] = '%s' % (self.fix_number(elite_exp_need) if self.short_numbers else BigWorld.wg_getIntegralFormat(elite_exp_need)).decode('utf-8-sig')
                    format_str['battles-left'] = elite_battles if avg_xp > 0 else 'X'
                    data.extend(self.pack(config.language['elite_status_string1'].format(**format_str), config.language['elite_status_string2'].format(**format_str)))
                elif e_research:
                    data.extend(self.pack(config.language['elite_status_ready_string1'].format(**format_str), config.language['elite_status_ready_string2'].format(**format_str)))

            if self.next_tanks_status:
                for vehicle_id in research_vehicles:
                    format_str['tank-name'] = '%s' % (research_vehicles[vehicle_id]['vehicle'].shortUserName.decode('utf-8-sig'))
                    research_vehicles[vehicle_id]['exp_need'] = research_vehicles[vehicle_id]['exp']
                    research_vehicles[vehicle_id]['exp'] -= exp
                    if self.free_xp_calculate: research_vehicles[vehicle_id]['exp'] -= free_exp
                    if research_vehicles[vehicle_id]['exp'] > 0:
                        research_vehicles[vehicle_id]['battles'] = research_vehicles[vehicle_id]['exp'] / avg_xp if avg_xp > 0 else 1
                        research_vehicles[vehicle_id]['battles'] = '%s' % (self.fix_number(research_vehicles[vehicle_id]['battles']) if self.short_numbers else BigWorld.wg_getIntegralFormat(
                            research_vehicles[vehicle_id]['battles'])).decode('utf-8-sig')
                        format_str['need-exp'] = '%s' % (
                            self.fix_number(research_vehicles[vehicle_id]['exp_need']) if self.short_numbers else BigWorld.wg_getIntegralFormat(research_vehicles[vehicle_id]['exp_need'])).decode(
                            'utf-8-sig')
                        format_str['chk-exp'] = '%s' % (
                            self.fix_number(research_vehicles[vehicle_id]['exp']) if self.short_numbers else BigWorld.wg_getIntegralFormat(research_vehicles[vehicle_id]['exp'])).decode('utf-8-sig')
                        format_str['battles-left'] = research_vehicles[vehicle_id]['battles'] if avg_xp > 0 else 'X'
                        data.extend(self.pack(config.language['next_tanks_string1'].format(**format_str), config.language['next_tanks_string2'].format(**format_str)))
                    else:
                        data.extend(self.pack(config.language['next_tanks_ready_string1'].format(**format_str), config.language['next_tanks_ready_string2'].format(**format_str)))
        return data

    @staticmethod
    def create_exp_status(vehicles):
        if not g_currentVehicle.isPresent(): return
        parent = g_currentVehicle.item.intCD if g_currentVehicle.item else None
        vehicles_id = vehicles.keys()
        modules_exp_needed = 0
        elite_exp_need = 0
        research_vehicles = {}
        e_research = False
        m_research = False
        for unlocks in g_currentVehicle.item.descriptor.type.unlocksDescrs:
            if unlocks[1] in vehicles_id:
                temp_vehicle = vehicles[unlocks[1]]
                if temp_vehicle and not temp_vehicle.isUnlocked:
                    is_available, cost, _ = getUnlockPrice(unlocks[1], parent)
                    research_vehicles[unlocks[1]] = {'exp': cost, 'battles': 1, 'vehicle': temp_vehicle}
                    elite_exp_need += cost
                    e_research = True
                    for research in unlocks:
                        if research in (unlocks[0], unlocks[1]): continue
                        is_available, cost, _ = getUnlockPrice(research, parent)
                        if not is_available:
                            research_vehicles[unlocks[1]]['exp'] += cost

            else:
                is_available, cost, _ = getUnlockPrice(unlocks[1], parent)
                if not is_available:
                    modules_exp_needed += cost
                    elite_exp_need += cost
                    e_research = True
                    m_research = True

        return modules_exp_needed, elite_exp_need, research_vehicles, e_research, m_research


# deformed functions:


def hook_update_all(self):
    hooked_update_all(self)
    config.analytics()


def hook_params_meta_values(self, data):
    if config.enable: return hooked_params_meta_values(self, veh_exp.change(data))
    return hooked_params_meta_values(self, data)


#start mod

config = Config()
config.load_mod()
veh_exp = VehExp()

#hooked
# noinspection PyProtectedMember
hooked_update_all = Hangar._Hangar__updateAll
hooked_params_meta_values = ParamsMeta.as_setValuesS

#hook
# noinspection PyProtectedMember
Hangar._Hangar__updateAll = hook_update_all
ParamsMeta.as_setValuesS = hook_params_meta_values
#Inject
