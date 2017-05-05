# -*- coding: utf-8 -*-
import datetime
import re
import os
import json
import codecs
import urllib2
import urllib
import threading

import BattleReplay
import BigWorld
# noinspection PyProtectedMember
from gui.Scaleform.daapi.view.battle.BattleRibbonsPanel import BattleRibbonsPanel, _RIBBON_SOUNDS_ENABLED, _POS_COEFF
from gui.battle_control import battle_feedback
from account_helpers.settings_core.settings_constants import GAME
from account_helpers.settings_core.SettingsCore import g_settingsCore
import BigWorld
from constants import AUTH_REALM
from gui.Scaleform.daapi.view.lobby.hangar import Hangar
from debug_utils import LOG_ERROR


class Config(object):
    def __init__(self):
        self.enable = True
        self.debug = False
        self.ru = True if 'RU' in AUTH_REALM else False
        self.version = 'v1.02(30.08.2015)'
        self.author = 'by spoter'
        self.description = 'replay_flag_fix'
        self.description_ru = 'Мод: "Фикс: Лента Событий в реплеях"'
        self.author_ru = 'автор: spoter'
        self.name = 'replay_flag_fix'
        self.description_analytics = 'Мод: "Фикс: Лента Событий в реплеях"'
        self.tid = 'UA-57975916-2'
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
                'enable': True, 'debug': False, 'language': 'Русский'
            }, 'language': {
                'Русский': {
                }, 'English': {

                }, 'Deutsch': {
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


# deformed functions:


def hook_update_all(self):
    hooked_update_all(self)
    config.analytics()


def hook_start(self):
    self._BattleRibbonsPanel__flashObject = self._BattleRibbonsPanel__ui.getMember('_level0.ribbonsPanel')
    if BattleReplay.g_replayCtrl.isPlaying and config.enable: self._BattleRibbonsPanel__enabled = True
    else: self._BattleRibbonsPanel__enabled = bool(g_settingsCore.getSetting(GAME.SHOW_BATTLE_EFFICIENCY_RIBBONS))
    if self._BattleRibbonsPanel__flashObject:
        self._BattleRibbonsPanel__flashObject.resync()
        self._BattleRibbonsPanel__flashObject.script = self
        self._BattleRibbonsPanel__flashObject.setup(self._BattleRibbonsPanel__enabled, _RIBBON_SOUNDS_ENABLED, *_POS_COEFF)
        self._BattleRibbonsPanel__addListeners()
    else: LOG_ERROR('Display object is not found in the swf file.')


def hook_set_aim_position_updated(self, mode, x, y):
    battle_feedback.BattleFeedbackAdaptor.setAimPositionUpdated(self, mode, x, y)


def hook_set_player_shot_results(self, veh_hit_flags, enemy_id):
    battle_feedback.BattleFeedbackAdaptor.setPlayerShotResults(self, veh_hit_flags, enemy_id)


def hook_set_player_assist_result(self, assist_type, vehicle_id):
    battle_feedback.BattleFeedbackAdaptor.setPlayerAssistResult(self, assist_type, vehicle_id)


def hook_set_player_kill_result(self, target_id):
    battle_feedback.BattleFeedbackAdaptor.setPlayerKillResult(self, target_id)


def hook_set_vehicle_new_health(self, vehicle_id, new_health, attacker_id=0, attack_reason_id=-1):
    battle_feedback.BattleFeedbackAdaptor.setVehicleNewHealth(self, vehicle_id, new_health, attacker_id, attack_reason_id)


#start mod

config = Config()
config.load_mod()

#hooked
# noinspection PyProtectedMember
hooked_update_all = Hangar._Hangar__updateAll
hooked_start = BattleRibbonsPanel.start

#hook
# noinspection PyProtectedMember
Hangar._Hangar__updateAll = hook_update_all
BattleRibbonsPanel.start = hook_start
battle_feedback.BattleFeedbackPlayer.setAimPositionUpdated = hook_set_aim_position_updated
battle_feedback.BattleFeedbackPlayer.setPlayerShotResults = hook_set_player_shot_results
battle_feedback.BattleFeedbackPlayer.setPlayerAssistResult = hook_set_player_assist_result
battle_feedback.BattleFeedbackPlayer.setPlayerKillResult = hook_set_player_kill_result
battle_feedback.BattleFeedbackPlayer.setVehicleNewHealth = hook_set_vehicle_new_health

#Inject
