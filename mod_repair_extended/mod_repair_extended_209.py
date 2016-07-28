# -*- coding: utf-8 -*-

import threading
import urllib
import urllib2

import BigWorld

import BattleReplay
import Keys as Keys
import SoundGroups
from Avatar import PlayerAvatar
from b4it_core import inject as inject
from constants import AUTH_REALM
from constants import DAMAGE_INFO_CODES
from gui import InputHandler
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.app_loader import g_appLoader
from gui.mods.mod_mods_gui import g_gui, inject
from helpers import getLanguageCode

class Config(object):
    def __init__(self):
        self.ids = 'repair_extended'
        self.version = '2.09 (28.07.2016)'
        self.version_id = 209
        self.author = 'by spoter'
        self.buttons = {
            'button_fast_repair_all': [Keys.KEY_SPACE],
            'button_chassis_repair' : [[Keys.KEY_LALT, Keys.KEY_RALT]]
        }
        self.data = {
            'version'               : self.version_id,
            'enabled'               : True,
            'auto_repair'           : False,
            'auto_heal'             : False,
            'auto_extinguish'       : False,
            'fire_time'             : 0.3,
            'crew_time'             : 0.8,
            'device_time'           : 0.7,
            'use_gold_med_kit'      : True,
            'use_gold_repair_kit'   : True,
            'chassis_auto_repair'   : False,
            'button_chassis_repair' : self.buttons['button_chassis_repair'],
            'button_fast_repair_all': self.buttons['button_fast_repair_all'],
            'repair_priority'       : {
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
            'version'                                 : self.version_id,
            'UI_repair_name'                          : 'Auto or Quick repair device, heal crew, extinguish a fire ',
            'UI_repair_button_chassis_repair_text'    : 'Quick chassis repair Button',
            'UI_repair_button_chassis_repair_tooltip' : '',
            'UI_repair_button_fast_repair_all_text'   : 'Quick Button (heal, repair, extinguish) if auto disabled',
            'UI_repair_button_fast_repair_all_tooltip': '',
            'UI_repair_auto_repair_text'              : 'Enable auto repair device',
            'UI_repair_auto_repair_tooltip'           : '{HEADER}Enable auto repair devices{/HEADER}{BODY}If enabled, you may change priority in /res_mods/configs/xvm/b4it/{/BODY}',
            'UI_repair_auto_heal_text'                : 'Enable auto heal crew',
            'UI_repair_auto_heal_tooltip'             : '{HEADER}Enable auto heal crew{/HEADER}{BODY}If enabled, you may change priority in /res_mods/configs/xvm/b4it/{/BODY}',
            'UI_repair_auto_extinguish_text'          : 'Enable auto extinguish a fire',
            'UI_repair_auto_extinguish_tooltip'       : '',
            'UI_repair_chassis_auto_repair_text'      : 'Enable auto repair chassis',
            'UI_repair_chassis_auto_repair_tooltip'   : '{HEADER}Enable auto repair chassis{/HEADER}{BODY}if disable, LightTanks repair chassis for default.\nYou may change it in /res_mods/configs/xvm/b4it/{/BODY}',
            'UI_repair_use_gold_med_kit_text'         : 'Enable use Gold Med kit in heal crew',
            'UI_repair_use_gold_med_kit_tooltip'      : '',
            'UI_repair_use_gold_repair_kit_text'      : 'Enable use Gold Repair kit in repair device',
            'UI_repair_use_gold_repair_kit_tooltip'   : '',
            'UI_repair_device_time_text'              : 'Delay auto repair device (in millisecond)',
            'UI_repair_device_time_format'            : ' msec.',
            'UI_repair_crew_time_text'                : 'Delay auto heal crew (in millisecond)',
            'UI_repair_crew_time_format'              : ' msec.',
            'UI_repair_fire_time_text'                : 'Delay auto extinguish a fire (in millisecond)',
            'UI_repair_fire_time_format'              : ' msec.'
        }

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_repair_name'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_repair_button_fast_repair_all_text'],
                'tooltip'     : self.i18n['UI_repair_button_fast_repair_all_tooltip'],
                'value'       : self.data['button_fast_repair_all'],
                'defaultValue': self.buttons['button_fast_repair_all'],
                'varName'     : 'button_fast_repair_all'
            }, {
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_repair_button_chassis_repair_text'],
                'tooltip'     : self.i18n['UI_repair_button_chassis_repair_tooltip'],
                'value'       : self.data['button_chassis_repair'],
                'defaultValue': self.buttons['button_chassis_repair'],
                'varName'     : 'button_chassis_repair'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_auto_repair_text'],
                'value'  : self.data['auto_repair'],
                'tooltip': self.i18n['UI_repair_auto_repair_tooltip'],
                'varName': 'auto_repair'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_auto_heal_text'],
                'value'  : self.data['auto_heal'],
                'tooltip': self.i18n['UI_repair_auto_heal_tooltip'],
                'varName': 'auto_heal'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_auto_extinguish_text'],
                'value'  : self.data['auto_extinguish'],
                'tooltip': self.i18n['UI_repair_auto_extinguish_tooltip'],
                'varName': 'auto_extinguish'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_repair_chassis_auto_repair_text'],
                'value'  : self.data['chassis_auto_repair'],
                'tooltip': self.i18n['UI_repair_chassis_auto_repair_tooltip'],
                'varName': 'chassis_auto_repair'
            }],
            'column2'        : [{
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
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_repair_device_time_text'],
                'minimum'     : 500,
                'maximum'     : 1500,
                'snapInterval': 100,
                'value'       : self.data['device_time'],
                'format'      : '{{value}}%s' % self.i18n['UI_repair_device_time_format'],
                'varName'     : 'device_time'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_repair_crew_time_text'],
                'minimum'     : 500,
                'maximum'     : 1500,
                'snapInterval': 100,
                'value'       : self.data['crew_time'],
                'format'      : '{{value}}%s' % self.i18n['UI_repair_crew_time_format'],
                'varName'     : 'crew_time'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_repair_fire_time_text'],
                'minimum'     : 300,
                'maximum'     : 1500,
                'snapInterval': 100,
                'value'       : self.data['fire_time'],
                'format'      : '{{value}}%s' % self.i18n['UI_repair_fire_time_format'],
                'varName'     : 'fire_time'
            }]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings)
        g_gui.update(self.ids, self.template)

    def load(self):
        self.doConfig()
        print '[LOAD_MOD]:  [%s v%s, %s]' % (self.ids, self.version, self.author)

    def doConfig(self):
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n)
        g_gui.register(self.ids, self.template, self.data, self.apply)

class Repair(object):
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
        InputHandler.g_instance.onKeyDown += self.inject_handle_key_event
        InputHandler.g_instance.onKeyUp += self.inject_handle_key_event

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
            # noinspection PyProtectedMember
            self.ConsumablesPanel._ConsumablesPanel__handleEquipmentPressed(int_cd, entity_name)
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
                    if config.data['auto_extinguish'] and self.fired: self.auto_fired()
                if damage_code in self.v_DamageCodes:
                    if extra_name not in self.damaged and extra_name not in ['chassis', 'leftTrack', 'rightTrack']:
                        self.damaged.append(extra_name)
                    if damage_code in self.v_Destroyed_Codes and extra_name not in self.destroyed and extra_name in ['chassis', 'leftTrack', 'rightTrack']:
                        self.destroyed.append(extra_name)
                    if damage_code in self.v_RepairedCodes and extra_name in self.destroyed:
                        self.destroyed.remove(extra_name)
                    if config.data['auto_repair']: self.auto_repair()
            if extra_name in self.crew:
                if damage_code in self.m_DamageCodes:
                    if extra_name not in self.damaged:
                        self.damaged.append(extra_name)
                    if config.data['auto_heal']: self.auto_heal()

    def auto_fired(self):
        if BigWorld.time() - self.time < config.data['fire_time'] * 0.001:
            BigWorld.callback(0.1, self.auto_fired)
        else: self.fires()

    def fires(self):
        if self.fired and self.check_item('extinguisher'):
            self.use_item(self.int_cd['extinguisher'])
            self.fired = False

    def auto_heal(self):
        if BigWorld.time() - self.time < config.data['crew_time'] * 0.001:
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
        specific = config.data['repair_priority'].get(my_tank_class)

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

        elif config.data['use_gold_med_kit'] and self.check_item('g_med_kit'):
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
        if BigWorld.time() - self.time < config.data['device_time'] * 0.001:
            BigWorld.callback(0.1, self.auto_repair)
        else: self.repair()

    def repair(self):
        my_tank_class = self.check_class(BigWorld.player().vehicleTypeDescriptor.type.tags)
        specific = config.data['repair_priority'].get(my_tank_class)
        if self.check_item('repair_kit'):
            for device in specific['device']:
                if device == 'chassis' and config.data['chassis_auto_repair']:
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
        elif config.data['use_gold_repair_kit'] and self.check_item('g_repair_kit'):
            for device in specific['device']:
                if device == 'chassis' and config.data['chassis_auto_repair']:
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
        if config.data['chassis_auto_repair']:
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

    @inject.log
    def inject_handle_key_event(self, event):
        if g_appLoader.getDefBattleApp():
            if config.data['enabled']:
                if g_gui.get_key(config.data['button_chassis_repair']) and event.isKeyDown():
                    repair.repair_chassis()
                if g_gui.get_key(config.data['button_fast_repair_all']) and event.isKeyDown():
                    repair.fires()
                    repair.heal()
                    repair.repair()

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
                'tid': 'UA-57975916-11',
                'cid': self.user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Винтик"', # App name.
                'av' : 'Мод: "Винтик" %s' % config.version,
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
                'tid': 'UA-57975916-11',
                'cid': self.old_user, # Anonymous Client ID.
                't'  : 'screenview', # Screenview hit type.
                'an' : 'Мод: "Винтик"', # App name.
                'av' : 'Мод: "Винтик" %s' % config.version,
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, lang), # Screen name / content description.
                'ul' : '%s' % lang,
                'sc' : 'end'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=param).read()
            self.analytics_started = False

config = Config()
repair = Repair()
stat = Statistics()

@inject.log
def init():
    config.load()

@inject.log
def fini():
    stat.end()

@inject.hook(LobbyView, '_populate')
def hookLobbyViewPopulate(func, *args):
    func(*args)
    stat.start()

@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
def hookStartGUI(func, *args):
    func(*args)
    repair.clear()

@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
def hookDestroyGUI(func, *args):
    func(*args)
    repair.clear()

@inject.hook(PlayerAvatar, 'showVehicleDamageInfo')
def hookShowVehicleDamageInfo(func, *args):
    func(*args)
    self, vehicle_id, damage_index, extra_index, entity_id, equipment_id = args
    if config.data['enabled']:
        damage_code = DAMAGE_INFO_CODES[damage_index]
        extra = self.vehicleTypeDescriptor.extras[extra_index] if extra_index != 0 else None
        if vehicle_id == self.playerVehicleID or not self.isVehicleAlive and vehicle_id == self.inputHandler.ctrl.curVehicleID:
            if extra:
                repair.get_info(damage_code, extra)

@inject.hook(ConsumablesPanel, '_ConsumablesPanel__onEquipmentAdded')
def hookShowVehicleDamageInfo(func, *args):
    func(*args)
    self, int_cd, item = args
    if config.data['enabled']:
        repair.ConsumablesPanel = self
        repair.eq_add(int_cd, item)
