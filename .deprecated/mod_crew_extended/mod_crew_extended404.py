# -*- coding: utf-8 -*-
import os
import re
import json
import codecs
import datetime
import threading
import urllib
import urllib2
import math

import BigWorld
from gui.shared.gui_items.dossier import TankmanDossier
from constants import AUTH_REALM
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from items.tankmen import MAX_SKILL_LEVEL
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.Scaleform.daapi.view.meta.BarracksMeta import BarracksMeta
from gui.Scaleform.locale.MENU import MENU
from helpers import i18n
from gui.shared import g_itemsCache


class Config(object):
    def __init__(self):
        self.enable = True
        self.debug = False
        self.ru = True if 'RU' in AUTH_REALM else False
        self.version = 'v4.04(18.11.2015)'
        self.author = 'by spoter'
        self.description = 'crew_extended'
        self.description_ru = 'Мод: "Экипаж"'
        self.author_ru = 'автор: spoter'
        self.name = 'crew_extended'
        self.description_analytics = 'Мод: "Экипаж"'
        self.tid = 'UA-57975916-10'
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
                'enable': True, 'debug': False, 'hangar_crew': True, 'barracks_crew': True, 'language': 'Русский'
            }, 'language': {
                'Русский': {
                }, 'English': {

                }, 'Deutsch': {
                }
            }
        }
        self.data['language']['Русский']['personal_file'] = {}
        self.data['language']['Русский']['personal_file']['premium_bonus_on'] = 'Премиум бонус на опыт: Активирован'
        self.data['language']['Русский']['personal_file']['premium_bonus_off'] = 'Премиум бонус на опыт: Неактивен'
        self.data['language']['Русский']['personal_file']['value_to'] = 'Опыта до'
        self.data['language']['Русский']['personal_file']['skill_number'] = 'Навык'
        self.data['language']['Русский']['personal_file']['basic_skill'] = 'Базовый навык'
        self.data['language']['Русский']['personal_file']['relearn'] = 'Переобучение'
        self.data['language']['Русский']['personal_file']['relearn_need'] = 'за кредиты надо'
        self.data['language']['Русский']['personal_file']['relearn_ready'] = 'за кредиты Готово!'
        self.data['language']['Русский']['personal_file']['relearn_not_ready'] = 'за кредиты не доступно'
        self.data['language']['Русский']['personal_file']['skill_drop'] = 'Уровень умения, после сброса за кредиты'
        self.data['language']['Русский']['personal_file']['skill_drop_ready'] = 'Возможен сброс умений за кредиты'
        self.data['language']['Русский']['hangar_crew'] = {}
        self.data['language']['Русский']['hangar_crew']['rank_string'] = u'[{exp-step-battles}|{exp-step}] {rank}'
        self.data['language']['Русский']['hangar_crew']['lastname_string'] = u'{lastname}'
        self.data['language']['Русский']['hangar_crew']['firstname_string'] = u'{firstname}'
        self.data['language']['Русский']['hangar_crew'][
            'role_string'] = u'[<font color="#00FF00">{training-battles}</font><img align="top" src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3"/><font ' \
                             u'color="#FFFF00">{exp-total}</font><img align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"/>]{role}'
        self.data['language']['Русский']['hangar_crew']['vehicle_type_string'] = u'{vehicleType}'
        self.data['language']['Русский']['barracks_crew'] = {}
        self.data['language']['Русский']['barracks_crew']['rank_string'] = u'{role}'
        self.data['language']['Русский']['barracks_crew']['lastname_string'] = u'{lastname}'
        self.data['language']['Русский']['barracks_crew']['firstname_string'] = u'[{training-battles}|{exp-total}] {firstname}'
        self.data['language']['Русский']['barracks_crew']['role_string'] = u'{skill_icons}{training-progress}%'
        self.data['language']['Русский']['barracks_crew']['vehicle_type_string'] = u'{vehicleType}'
        self.data['language']['Русский']['ordinator'] = {}
        self.data['language']['Русский']['ordinator']['none'] = '-й'

        self.data['language']['Deutsch']['personal_file'] = {}
        self.data['language']['Deutsch']['personal_file']['premium_bonus_on'] = u'Erfahrungsbonus'
        self.data['language']['Deutsch']['personal_file']['premium_bonus_off'] = u'Kein Erfahrungsbonus'
        self.data['language']['Deutsch']['personal_file']['value_to'] = u'f%sr' % (unichr(252))
        self.data['language']['Deutsch']['personal_file']['skill_number'] = u'Fertigkeit'
        self.data['language']['Deutsch']['personal_file']['basic_skill'] = u'Grundfertigkeit'
        self.data['language']['Deutsch']['personal_file']['relearn'] = u'Umschulung f%sr Kreditpunkte' % (unichr(252))
        self.data['language']['Deutsch']['personal_file']['relearn_need'] = u'ben%stigt weitere' % (unichr(246))
        self.data['language']['Deutsch']['personal_file']['relearn_ready'] = u'verf%sgbar!' % (unichr(252))
        self.data['language']['Deutsch']['personal_file']['relearn_not_ready'] = u'nicht verf%sgbar!' % (unichr(252))
        self.data['language']['Deutsch']['personal_file']['skill_drop'] = u'Neue Ausbildungsstufe nach verlernen'
        self.data['language']['Deutsch']['personal_file']['skill_drop_ready'] = u'Verlernen f%sr Kreditpunkte verf%sgbar!' % (unichr(252), unichr(252))
        self.data['language']['Deutsch']['hangar_crew'] = {}
        self.data['language']['Deutsch']['hangar_crew']['rank_string'] = u'[{exp-step-battles}|{exp-step}] {rank}'
        self.data['language']['Deutsch']['hangar_crew']['lastname_string'] = u'{lastname}'
        self.data['language']['Deutsch']['hangar_crew']['firstname_string'] = u'{firstname}'
        self.data['language']['Deutsch']['hangar_crew'][
            'role_string'] = u'[<font color="#00FF00">{training-battles}</font><img align="top" src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3"/><font ' \
                             u'color="#FFFF00">{exp-total}</font><img align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"/>]{role}'
        self.data['language']['Deutsch']['hangar_crew']['vehicle_type_string'] = u'{vehicleType}'
        self.data['language']['Deutsch']['barracks_crew'] = {}
        self.data['language']['Deutsch']['barracks_crew']['rank_string'] = u'{role}'
        self.data['language']['Deutsch']['barracks_crew']['lastname_string'] = u'{lastname}'
        self.data['language']['Deutsch']['barracks_crew']['firstname_string'] = u'[{training-battles}|{exp-total}] {firstname}'
        self.data['language']['Deutsch']['barracks_crew']['role_string'] = u'{skill_icons}{training-progress}%'
        self.data['language']['Deutsch']['barracks_crew']['vehicle_type_string'] = u'{vehicleType}'
        self.data['language']['Deutsch']['ordinator'] = {}
        self.data['language']['Deutsch']['ordinator']['none'] = '.'

        self.data['language']['English']['personal_file'] = {}
        self.data['language']['English']['personal_file']['premium_bonus_on'] = 'Premium XP bonus'
        self.data['language']['English']['personal_file']['premium_bonus_off'] = 'No premium XP bonus'
        self.data['language']['English']['personal_file']['value_to'] = 'to'
        self.data['language']['English']['personal_file']['skill_number'] = 'Skill'
        self.data['language']['English']['personal_file']['basic_skill'] = 'Basic skill'
        self.data['language']['English']['personal_file']['relearn'] = 'Retraining for credits'
        self.data['language']['English']['personal_file']['relearn_need'] = 'needs further'
        self.data['language']['English']['personal_file']['relearn_ready'] = 'ready!'
        self.data['language']['English']['personal_file']['relearn_not_ready'] = 'not ready!'
        self.data['language']['English']['personal_file']['skill_drop'] = 'New skill level after dropping skills'
        self.data['language']['English']['personal_file']['skill_drop_ready'] = 'Dropping skills for credits ready!'
        self.data['language']['English']['hangar_crew'] = {}
        self.data['language']['English']['hangar_crew']['rank_string'] = u'[{exp-step-battles}|{exp-step}] {rank}'
        self.data['language']['English']['hangar_crew']['lastname_string'] = u'{lastname}'
        self.data['language']['English']['hangar_crew']['firstname_string'] = u'{firstname}'
        self.data['language']['English']['hangar_crew'][
            'role_string'] = u'[<font color="#00FF00">{training-battles}</font><img align="top" src="img://gui/maps//icons/library/BattleResultIcon-1.png" height="14" width="14" vspace="-3"/><font ' \
                             u'color="#FFFF00">{exp-total}</font><img align="top" src="img://gui/maps//icons/library/XpIcon-1.png" height="16" width="16" vspace="-3"/>]{role}'
        self.data['language']['English']['hangar_crew']['vehicle_type_string'] = u'{vehicleType}'
        self.data['language']['English']['barracks_crew'] = {}
        self.data['language']['English']['barracks_crew']['rank_string'] = u'{role}'
        self.data['language']['English']['barracks_crew']['lastname_string'] = u'{lastname}'
        self.data['language']['English']['barracks_crew']['firstname_string'] = u'[{training-battles}|{exp-total}] {firstname}'
        self.data['language']['English']['barracks_crew']['role_string'] = u'{skill_icons}{training-progress}%'
        self.data['language']['English']['barracks_crew']['vehicle_type_string'] = u'{vehicleType}'
        self.data['language']['English']['ordinator'] = {}
        self.data['language']['English']['ordinator']['none'] = 'th'
        self.data['language']['English']['ordinator'][1] = 'st'
        self.data['language']['English']['ordinator'][2] = 'nd'
        self.data['language']['English']['ordinator'][3] = 'rd'

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


class PersonalFile(object):
    @staticmethod
    def __format_value_for_ui(value):
        if value is None: return '%s' % i18n.makeString(MENU.PROFILE_STATS_ITEMS_EMPTY)
        else: return BigWorld.wg_getIntegralFormat(value)

    def __pack_stat(self, name='empty', value=None, premium_value=None, image_type=None, image=None):
        if value and value < 1: value = 1
        if premium_value and premium_value < 1: value = 1
        value = self.__format_value_for_ui(value)
        new_premium_value = self.__format_value_for_ui(premium_value)
        return {'name': name, 'value': value, 'premiumValue': new_premium_value, 'imageType': image_type, 'image': image}

    # noinspection PyProtectedMember
    @staticmethod
    def second_label(vehicle, tankman):
        last_skill_number = tankman.descriptor.lastSkillNumber if not tankman.hasNewSkill else tankman.descriptor.lastSkillNumber + tankman.newSkillCount[0]
        ordinator = config.language['ordinator'][last_skill_number] if last_skill_number in config.language['ordinator'] else config.language['ordinator']['none']
        if vehicle.tmanDescr.roleLevel == MAX_SKILL_LEVEL:
            if vehicle._TankmanDossier__currentVehicleIsPremium: return '%s%s %s, x%s %s' % (
                last_skill_number, ordinator, config.language['personal_file']['skill_number'], vehicle._TankmanDossier__currentVehicleCrewXpFactor,
                config.language['personal_file']['premium_bonus_on'])
            else: return '%s%s %s, %s' % (last_skill_number, ordinator, config.language['personal_file']['skill_number'], config.language['personal_file']['premium_bonus_off'])
        else:
            if vehicle._TankmanDossier__currentVehicleIsPremium: return '%s, x%s %s' % (
                config.language['personal_file']['basic_skill'], vehicle._TankmanDossier__currentVehicleCrewXpFactor, config.language['personal_file']['premium_bonus_on'])
            else: return '%s, %s' % (config.language['personal_file']['basic_skill'], config.language['personal_file']['premium_bonus_off'])

    @staticmethod
    def nope():
        return {'name': 'empty', 'value': '', 'premiumValue': '', 'imageType': None, 'image': None}

    @staticmethod
    def title(tankman):
        next_skill_level = ((tankman.descriptor.lastSkillLevel if tankman.descriptor.roleLevel == MAX_SKILL_LEVEL else tankman.descriptor.roleLevel) if not tankman.hasNewSkill else
        tankman.newSkillCount[1]) + 1
        return {
            'name': 'empty', 'value': '%s %s%%' % (config.language['personal_file']['value_to'], next_skill_level), 'premiumValue': '%s 100%%' % config.language['personal_file']['value_to'],
            'imageType': None, 'image': None
        }

    @staticmethod
    def get_next_skill_battles_left(vehicle, tankman):
        if not vehicle.getBattlesCount(): result = None
        else:
            avg_exp = vehicle.getAvgXP()
            new_skill_ready = vehicle.tmanDescr.roleLevel == MAX_SKILL_LEVEL and (len(vehicle.tmanDescr.skills) == 0 or vehicle.tmanDescr.lastSkillLevel == MAX_SKILL_LEVEL)
            if avg_exp and not new_skill_ready: result = max(1, math.ceil(tankman.getNextSkillXpCost() / avg_exp))
            else: result = 0
        return result

    # noinspection PyProtectedMember
    def get_stats(self, vehicle, tankman, temp):
        temp[0]['stats'] = (temp[0]['stats'][0], temp[0]['stats'][1], self.__pack_stat('xp', tankman.descriptor.totalXP()))
        temp[1]['secondLabel'] = self.second_label(vehicle, tankman)
        temp[1]['isPremium'] = True
        next_skill_xp_left = self.__pack_stat('nextSkillXPLeft', tankman.getNextLevelXpCost(), tankman.getNextSkillXpCost(), image_type=temp[1]['stats'][0]['imageType'],
            image=temp[1]['stats'][0]['image'])
        if vehicle._TankmanDossier__currentVehicleIsPremium: next_skill_battles_left = self.__pack_stat('nextSkillBattlesLeft',
            vehicle._TankmanDossier__getBattlesLeftOnPremiumVehicle(vehicle._TankmanDossier__getNextSkillBattlesLeft(tankman)),
            vehicle._TankmanDossier__getBattlesLeftOnPremiumVehicle(self.get_next_skill_battles_left(vehicle, tankman)))
        else: next_skill_battles_left = self.__pack_stat('nextSkillBattlesLeft', vehicle._TankmanDossier__getNextSkillBattlesLeft(tankman), self.get_next_skill_battles_left(vehicle, tankman))
        temp[1]['stats'] = (self.title(tankman), next_skill_xp_left, next_skill_battles_left)
        return temp


class HangarCrew(object):
    def __init__(self):
        self.crew_dict = {}
        
    @staticmethod
    def fix_number(value):
        value = float(value)
        if value < 1000: return '%s' % int(value)
        elif value < 100000: return '{:0.1f}k'.format(value / 1000.0)
        elif value < 1000000: return '{0:d}k'.format(int(math.ceil(value / 1000.0)))
        else: return '{:0.1f}M'.format(value / 1000000.0)

    @staticmethod
    def check_macros(macros):
        if macros in config.language['hangar_crew']['firstname_string']: return True
        if macros in config.language['hangar_crew']['lastname_string']: return True
        if macros in config.language['hangar_crew']['role_string']: return True
        if macros in config.language['hangar_crew']['vehicle_type_string']: return True
        if macros in config.language['hangar_crew']['rank_string']: return True
        if macros in config.language['barracks_crew']['firstname_string']: return True
        if macros in config.language['barracks_crew']['lastname_string']: return True
        if macros in config.language['barracks_crew']['role_string']: return True
        if macros in config.language['barracks_crew']['vehicle_type_string']: return True
        if macros in config.language['barracks_crew']['rank_string']: return True
        return False

    @staticmethod
    def get_skill_icons(tankman):
        skill_icons = ''
        for skill in tankman.skills:
            skill_icons += "<img src='img://gui/maps/icons/tankmen/skills/small/%s' width='14' height='14' align='baseline' vspace='-3'>" % skill.icon
        if tankman.hasNewSkill:
            skill_icons += "<img src='img://gui/maps/icons/tankmen/skills/small/new_skill.png' width='14' height='14' align='baseline' vspace='-3'>"
        return skill_icons

    @staticmethod
    def is_in_tank_get_next_skill_battles_left(tankman):
        vehicle = g_itemsCache.items.getTankmanDossier(tankman.invID)
        current_vehicle_item = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
        current_vehicle_type = current_vehicle_item.descriptor.type if current_vehicle_item else None
        is_premium = current_vehicle_item and current_vehicle_item.isPremium
        if not vehicle.getBattlesCount(): result = None
        else:
            avg_exp = vehicle.getAvgXP()
            new_skill_ready = vehicle.tmanDescr.roleLevel == MAX_SKILL_LEVEL and (len(vehicle.tmanDescr.skills) == 0 or vehicle.tmanDescr.lastSkillLevel == MAX_SKILL_LEVEL)
            if avg_exp and not new_skill_ready: result = max(1, math.ceil(tankman.getNextSkillXpCost() / avg_exp))
            else: result = 0
        if is_premium:
            xp_factor_to_use = current_vehicle_type.crewXpFactor if current_vehicle_type else 1.0
            if result is not None:
                if result != 0:
                    return max(1, result / xp_factor_to_use)
                return 0
        return result

    @staticmethod
    def is_in_tank_get_next_level_battles_left(tankman):
        vehicle = g_itemsCache.items.getTankmanDossier(tankman.invID)
        current_vehicle_item = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
        current_vehicle_type = current_vehicle_item.descriptor.type if current_vehicle_item else None
        is_premium = current_vehicle_item and current_vehicle_item.isPremium
        if not vehicle.getBattlesCount(): result = None
        else:
            avg_exp = vehicle.getAvgXP()
            new_skill_ready = vehicle.tmanDescr.roleLevel == MAX_SKILL_LEVEL and (len(vehicle.tmanDescr.skills) == 0 or vehicle.tmanDescr.lastSkillLevel == MAX_SKILL_LEVEL)
            if avg_exp and not new_skill_ready: result = max(1, math.ceil(tankman.getNextLevelXpCost() / avg_exp))
            else: result = 0
        if is_premium:
            xp_factor_to_use = current_vehicle_type.crewXpFactor if current_vehicle_type else 1.0
            if result is not None:
                if result != 0:
                    return max(1, result / xp_factor_to_use)
                result = 0
        return result

    def training_battles(self, tankman):
        if tankman.isInTank:
            result = self.is_in_tank_get_next_skill_battles_left(tankman)
            return self.fix_number(result) if result > 0 else 1
        else:
            avg_xp = float(g_itemsCache.items.getTankmanDossier(tankman.invID).getAvgXP())
            if avg_xp > 0: return self.fix_number(math.ceil(tankman.getNextSkillXpCost() / avg_xp))
            else: return 1

    def exp_step_battles(self, tankman):
        if tankman.isInTank:
            result = self.is_in_tank_get_next_level_battles_left(tankman)
            return self.fix_number(result) if result > 0 else 1
        else:
            avg_xp = float(g_itemsCache.items.getTankmanDossier(tankman.invID).getAvgXP())
            if avg_xp > 0: return self.fix_number(math.ceil(tankman.getNextLevelXpCost() / avg_xp))
            else: return 1

    def create_format_str(self, tankman_id, tankman, vehicle_id):
        if tankman_id not in self.crew_dict:
            self.crew_dict[tankman_id] = {}
            self.crew_dict[tankman_id]['xp'] = 0
            self.crew_dict[tankman_id]['vehicle_id'] = vehicle_id
        update = False
        if self.crew_dict[tankman_id]['xp'] < tankman.descriptor.totalXP():
            update = True
        if self.crew_dict[tankman_id]['vehicle_id'] != vehicle_id:
            update = True
            self.crew_dict[tankman_id]['vehicle_id'] = vehicle_id
        self.crew_dict[tankman_id]['xp'] = tankman.descriptor.totalXP()
        format_str = {}
        if self.check_macros('{training-level}'):
            if 'training-level' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['raining-level'] = '%s' % tankman.realRoleLevel[0]
            format_str['training-level'] = self.crew_dict[tankman_id]['raining-level']
        if self.check_macros('{basic-training-level}'):
            if 'basic-training-level' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['basic-training-level'] = '%s' % tankman.efficiencyRoleLevel
            format_str['basic-training-level'] = self.crew_dict[tankman_id]['basic-training-level']
        if self.check_macros('{firstname}'):
            if 'firstname' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['firstname'] = '%s' % tankman.firstUserName
            format_str['firstname'] = self.crew_dict[tankman_id]['firstname']
        if self.check_macros('{lastname}'):
            if 'lastname' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['lastname'] = '%s' % tankman.lastUserName
            format_str['lastname'] = self.crew_dict[tankman_id]['lastname']
        if self.check_macros('{rank}'):
            if 'rank' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['rank'] = '%s' % tankman.rankUserName
            format_str['rank'] = self.crew_dict[tankman_id]['rank']
        if self.check_macros('{exp-total}'):
            if 'exp-total' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['exp-total'] = '%s' % self.fix_number(
                tankman.getNextSkillXpCost() + tankman.descriptor.freeXP)
            format_str['exp-total'] = self.crew_dict[tankman_id]['exp-total']
        if self.check_macros('{training-battles}'):
            if 'training-battles' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['training-battles'] = '%s' % self.training_battles(tankman)
            format_str['training-battles'] = self.crew_dict[tankman_id]['training-battles']
        if self.check_macros('{next_skill_level}'):
            if 'next_skill_level' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['next_skill_level'] = '%s' % (
                (tankman.descriptor.lastSkillLevel if tankman.descriptor.roleLevel == MAX_SKILL_LEVEL else tankman.descriptor.roleLevel) if not tankman.hasNewSkill else tankman.newSkillCount[1] + 1)
            format_str['next_skill_level'] = self.crew_dict[tankman_id]['next_skill_level']
        if self.check_macros('{skillsCnt}'):
            if 'skillsCnt' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id][
                'skillsCnt'] = '%s' % tankman.descriptor.lastSkillNumber if not tankman.hasNewSkill else tankman.descriptor.lastSkillNumber + tankman.newSkillCount[0]
            format_str['skillsCnt'] = self.crew_dict[tankman_id]['skillsCnt']
        if self.check_macros('{training-progress}'):
            if 'training-progress' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['training-progress'] = '%s' % (
                tankman.descriptor.lastSkillLevel if tankman.descriptor.roleLevel == MAX_SKILL_LEVEL else tankman.descriptor.roleLevel) if not tankman.hasNewSkill else tankman.newSkillCount[1]
            format_str['training-progress'] = self.crew_dict[tankman_id]['training-progress']
        if self.check_macros('{role}'):
            if 'role' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['role'] = '%s' % tankman.roleUserName
            format_str['role'] = self.crew_dict[tankman_id]['role']
        if self.check_macros('{current_exp}'):
            if 'current_exp' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['current_exp'] = '%s' % self.fix_number(tankman.descriptor.totalXP())
            format_str['current_exp'] = self.crew_dict[tankman_id]['current_exp']
        if self.check_macros('{vehicleType}'):
            if 'vehicleType' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['vehicleType'] = '%s' % g_itemsCache.items.getItemByCD(
                tankman.vehicleNativeDescr.type.compactDescr).shortUserName
            format_str['vehicleType'] = self.crew_dict[tankman_id]['vehicleType']
        if self.check_macros('{exp-step}'):
            if 'exp-step' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['exp-step'] = '%s' % self.fix_number(tankman.getNextLevelXpCost())
            format_str['exp-step'] = self.crew_dict[tankman_id]['exp-step']
        if self.check_macros('{exp-step-battles}'):
            if 'exp-step-battles' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['exp-step-battles'] = '%s' % self.exp_step_battles(tankman)
            format_str['exp-step-battles'] = self.crew_dict[tankman_id]['exp-step-battles']
        if self.check_macros('{exp-free}'):
            if 'exp-free' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['exp-free'] = '%s' % self.fix_number(tankman.descriptor.freeXP)
            format_str['exp-free'] = self.crew_dict[tankman_id]['exp-free']
        if self.check_macros('{lastSkillLevel}'):
            if 'lastSkillLevel' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['lastSkillLevel'] = '%s' % tankman.descriptor.lastSkillLevel
            format_str['lastSkillLevel'] = self.crew_dict[tankman_id]['lastSkillLevel']
        if self.check_macros('{skill_icons}'):
            if 'skill_icons' not in self.crew_dict[tankman_id] or update: self.crew_dict[tankman_id]['skill_icons'] = '%s' % self.get_skill_icons(tankman)
            format_str['skill_icons'] = self.crew_dict[tankman_id]['skill_icons']
        return format_str

    def change_data(self, data):
        for tankmenData in data['tankmen']:
            tankman = g_itemsCache.items.getTankman(tankmenData['tankmanID'])
            tankman_id = tankmenData['tankmanID']
            vehicle_id = tankmenData['typeID']
            format_str = self.create_format_str(tankman_id, tankman, vehicle_id)
            tankmenData['lastName'] = config.language['hangar_crew']['lastname_string'].format(**format_str)
            tankmenData['firstName'] = config.language['hangar_crew']['firstname_string'].format(**format_str)
            tankmenData['role'] = config.language['hangar_crew']['role_string'].format(**format_str)
            tankmenData['vehicleType'] = config.language['hangar_crew']['vehicle_type_string'].format(**format_str)
            tankmenData['rank'] = config.language['hangar_crew']['rank_string'].format(**format_str)
        return data

    def change_data_barracks(self, data):
        for tankmenData in data:
            if 'tankmanID' in tankmenData:
                tankman = g_itemsCache.items.getTankman(int(tankmenData['tankmanID']))
                tankman_id = tankmenData['tankmanID']
                vehicle_id = tankmenData['typeID']
                format_str = self.create_format_str(tankman_id, tankman, vehicle_id)
                tankmenData['lastname'] = config.language['barracks_crew']['lastname_string'].format(**format_str)
                tankmenData['firstname'] = config.language['barracks_crew']['firstname_string'].format(**format_str)
                tankmenData['role'] = config.language['barracks_crew']['role_string'].format(**format_str) if not config.xvm_installed else tankmenData['role']
                tankmenData['vehicleType'] = config.language['barracks_crew']['vehicle_type_string'].format(**format_str)
                tankmenData['rank'] = config.language['barracks_crew']['rank_string'].format(**format_str)
        return data


# deformed functions:
def hook_update_all(self):
    hooked_update_all(self)
    config.analytics()


def hook_get_stats(self, tankman):
    if config.enable:
        return personal_file.get_stats(self, tankman, hooked_get_stats(self, tankman))
    else: return hooked_get_stats(self, tankman)


def hook_as_tankmen_response_s(self, data):
    if config.enable and config.data['config'].get('hangar_crew'):
        return hooked_as_tankmen_response_s(self, hangar_crew.change_data(data))
    else: return hooked_as_tankmen_response_s(self, data)


def hook_as_set_tankmen_s(self, tankmen_count, tankmen_in_slots, places_count, tankmen_in_barracks, tankman_arr):
    if config.enable and config.data['config'].get('hangar_crew'):
        return hooked_as_set_tankmen_s(self, tankmen_count, tankmen_in_slots, places_count, tankmen_in_barracks, hangar_crew.change_data_barracks(tankman_arr))
    return hooked_as_set_tankmen_s(self, tankmen_count, tankmen_in_slots, places_count, tankmen_in_barracks, tankman_arr)


#start mod
personal_file = PersonalFile()
hangar_crew = HangarCrew()
config = Config()
config.load_mod()

#hooked
# noinspection PyProtectedMember
hooked_update_all = Hangar._Hangar__updateAll
hooked_get_stats = TankmanDossier.getStats
hooked_as_tankmen_response_s = CrewMeta.as_tankmenResponseS
hooked_as_set_tankmen_s = BarracksMeta.as_setTankmenS

#hook
# noinspection PyProtectedMember
Hangar._Hangar__updateAll = hook_update_all
TankmanDossier.getStats = hook_get_stats
CrewMeta.as_tankmenResponseS = hook_as_tankmen_response_s
BarracksMeta.as_setTankmenS = hook_as_set_tankmen_s
