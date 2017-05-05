# -*- coding: utf-8 -*-

import codecs
import json
import os
import random
import re
import string
from functools import partial

import BigWorld
import Math
import GUI

from constants import VEHICLE_HIT_EFFECT
from gui import g_guiResetters
from gui.Scaleform import Minimap
from gui.Scaleform.Battle import Battle

from Vehicle import Vehicle
from VehicleEffects import DamageFromShotDecoder
from gui.app_loader import g_appLoader
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
        self.ids = 'armoring_extended'
        self.version = '2.04 (19.02.2016)'
        self.author = 'by spoter, reven86'
        self.path_config = './res_mods/configs/spoter_mods/%s/' % self.ids
        self.path_lang = '%si18n/' % self.path_config
        self.data = {
            'enabled'         : True,
            'activate_message': True,
            'only_HeavyTank'  : False,
            'show_text_shadow': True,
        }
        self.i18n = {
            'UI_description'                              : 'Armoring Extended',
            'UI_in_battle_main_text'                      : '<font size="14" color="#BDFA64"><font color="#fdf498">{NumDmg} Blocked <img align="top" src="img://gui/maps/icons/library/ClanBattleResultIcon-1.png" height="16" width="16" vspace="-3" '
                                                            '/><font '
                                                            'color="#fdf498">{AvgDmg}</font> damage</font>',
            'UI_in_battle_activate_message'               : 'Armoring Extended: Activated',
            'UI_in_battle_activate_message_only_HeavyTank': 'Armoring Extended: Activated, only Heavy Tanks',
            'UI_setting_activate_message_text'            : 'Show activation message in battle',
            'UI_setting_activate_message_tooltip'         : '{HEADER}Info:{/HEADER}{BODY}When battle start, show notification message about mode Armoring Extended{/BODY}',
            'UI_setting_heavy_tank_only_text'             : 'Enable mod only on Heavy Tank',
            'UI_setting_heavy_tank_only_tooltip'          : '{HEADER}Info:{/HEADER}{BODY}Enable mod only on Heavy Tank, all other not available{/BODY}',
            'UI_setting_show_text_shadow_text'            : 'Show shadows on text',
            'UI_setting_show_text_shadow_tooltip'         : '{HEADER}Info:{/HEADER}{BODY}Show shadow on text in battle flash{/BODY}',
        }

        self.load_lang()
        self.no_gui = False
        self.json = {
            'x': 100,
            'y': 100
        }

        new_config = self.load_json(self.ids, self.json, self.path_config)
        for setting in new_config:
            if setting in self.json:
                self.json[setting] = new_config[setting]

    def load_lang(self):
        lang = str(getLanguageCode()).lower()
        new_config = self.load_json(lang, self.i18n, self.path_lang)
        for setting in new_config:
            if setting in self.i18n:
                self.i18n[setting] = new_config[setting]

    def template_settings(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': 104,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_activate_message_text'],
                'value'  : self.data['activate_message'],
                'tooltip': self.i18n['UI_setting_activate_message_tooltip'],
                'varName': 'activate_message'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_heavy_tank_only_text'],
                'value'  : self.data['only_HeavyTank'],
                'tooltip': self.i18n['UI_setting_heavy_tank_only_tooltip'],
                'varName': 'only_HeavyTank'
            }],
            'column2'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_show_text_shadow_text'],
                'value'  : self.data['show_text_shadow'],
                'tooltip': self.i18n['UI_setting_show_text_shadow_tooltip'],
                'varName': 'show_text_shadow'
            }]
        }

    def apply_settings(self, settings):
        for setting in settings:
            if setting in self.data:
                self.data[setting] = settings[setting]
        _gui_config.update('%s' % self.ids, self.template_settings)

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
        if hasattr(BigWorld, 'mods_gui'):
            _gui_config.register(name='%s' % self.ids, template_func=self.template_settings, settings_dict=self.data, apply_func=self.apply_settings)
        else:
            if not self.no_gui:
                BigWorld.callback(1.0, self.do_config)


class _TextFlash(object):
    def __init__(self, parent_ui, battleWindow, name, tooltip):
        self.__parentUI = parent_ui
        self.__battleWindow = battleWindow
        self.__flashObject = None
        self.name = name
        self.tooltip = tooltip
        self.debug = False
        self.__battleWindow.addExternalCallback('%s.start' % self.name, self.start)
        self.__battleWindow.addExternalCallback('%s.log' % self.name, self.log)
        self.__battleWindow.addExternalCallback('%s.position' % self.name, self.position)
        self.__battleWindow.getRoot().loadSwf('Extended.swf', '%s' % self.name, None)
        self.text = {
            'x'                 : _config.json.get('x', 100),
            'y'                 : _config.json.get('y', 100),
            'alignX'            : 'center',
            'alignY'            : 'center',
            'default_font'      : '$IMELanguageBar',
            'default_font_size' : 14,
            'default_font_color': '#BDFA64'
        }
        self.shadow = {
            'enabled' : _config.data.get('show_text_shadow', True),
            'distance': 0,
            'angle'   : 90,
            'color'   : '#000000',
            'alpha'   : 100,
            'size'    : 3,
            'strength': 200

        }
        self.background = {
            'enabled': False,
            'image'  : '',
            'x'      : 218,
            'y'      : 448,
            'width'  : 250,
            'height' : 27,
            'alpha'  : 80

        }

    def start(self, *args):
        self.__flashObject = self.__parentUI.getMember('_level0.%s.battleFlash' % self.name)
        self.__flashObject.script = self
        g_guiResetters.add(self.as_onScreenResS)
        self.set_def_config()
        self.as_onScreenResS()

    def set_def_config(self):
        self.as_setTextS('')
        self.as_setToolTipS('%s' % self.tooltip)
        self.as_setPositionS(self.text['x'], self.text['y'])
        if self.shadow['enabled']:
            self.as_setShadowS(self.shadow['distance'], self.shadow['angle'], self.shadow['color'], self.shadow['alpha'], self.shadow['size'], self.shadow['strength'])
        if self.background['enabled']:
            self.as_setBgS(self.background['image'], self.background['x'], self.background['y'], self.background['width'], self.background['height'], self.background['alpha'])

    def destroy(self):
        g_guiResetters.discard(self.as_onScreenResS)
        self.__flashObject = None
        self.__battleWindow = None
        self.__parentUI = None

    def set_visible(self, boole):
        if self.__flashObject:
            self.as_setVisibleS(boole)

    def set_shadow(self, distance_shadow, angle_shadow, color_shadow, alpha_shadow, size_shadow, strength_shadow):
        if self.__flashObject:
            self.as_setShadowS(distance_shadow, angle_shadow, color_shadow, alpha_shadow, size_shadow, strength_shadow)

    def set_bg(self, image_bg, x_pos_bg, y_pos_bg, width_bg, height_bg, alpha_bg):
        if self.__flashObject:
            self.as_setBgS(image_bg, x_pos_bg, y_pos_bg, width_bg, height_bg, alpha_bg)

    def set_text_flash(self, text):
        _text = '<font size="%s" face="%s" color="%s" vspace="3" >%s</font>' % (self.text['default_font_size'], self.text['default_font'], self.text['default_font_color'], text)
        self.as_setTextS(_text)

    def set_text(self, text):
        if self.__flashObject:
            self.set_text_flash(text)

    @property
    def flashObject(self):
        return self.__flashObject

    def log(self, _, text):
        if self.debug:
            print('Extended.swf', '%s' % text)

    def position(self, _, posX, posY):
        self.text['x'] = posX
        self.text['y'] = posY
        _config.json['x'] = posX
        _config.json['y'] = posY
        _config.json = _config.load_json(_config.ids, _config.json, _config.path_config, True)
        self.log(None, 'updatePosition : %s / %s in %s' % (posX, posY, self.name))

    def as_onScreenResS(self):
        wRes, hRes = GUI.screenResolution()
        if self.flashObject:
            self.flashObject.as_onScreenRes(wRes, hRes)

    def as_setTextS(self, text):
        if self.flashObject:
            self.flashObject.as_setText(text)

    def as_setSizeS(self, width, height):
        if self.flashObject:
            self.flashObject.as_setSize(width, height)

    def as_setVisibleS(self, boole):
        if self.flashObject:
            self.flashObject.as_setVisible(boole)

    def as_setPositionS(self, posX, posY):
        if self.flashObject:
            self.flashObject.as_setPosition(posX, posY)

    def as_setToolTipS(self, text):
        if self.flashObject:
            self.flashObject.as_setToolTip(text)

    def as_setShadowS(self, distance, angle, color, alpha, size, strength):
        if self.flashObject:
            self.flashObject.as_setShadow(distance, angle, color, alpha, size, strength)

    def as_setBgS(self, image, posX, posY, width, height, alpha):
        if self.flashObject:
            self.flashObject.as_setBG(image, posX, posY, width, height, alpha)


class ArmoringExtended(object):
    def __init__(self):
        self.on_off = False
        self.flash = None
        self.num = 0
        self.avgDMG = 0
        self.SumAvgDmg = 0
        self.list = {}
        self.shots = 0

    def cleanup_battle_data(self):
        self.num = 0
        self.avgDMG = 0
        self.SumAvgDmg = 0
        self.list = {}
        self.shots = 0

    @staticmethod
    def message():
        app = g_appLoader.getDefBattleApp()
        if _config.data['only_HeavyTank']:
            app.call('battle.PlayerMessagesPanel.ShowMessage',
                ['%s%s' % (_config.i18n['UI_in_battle_activate_message_only_HeavyTank'], random.choice(string.ascii_letters)), _config.i18n['UI_in_battle_activate_message_only_HeavyTank'].decode('utf-8-sig'), 'gold'])
        else:
            app.call('battle.PlayerMessagesPanel.ShowMessage', ['%s%s' % (_config.i18n['UI_in_battle_activate_message'], random.choice(string.ascii_letters)), _config.i18n['UI_in_battle_activate_message'].decode('utf-8-sig'), 'gold'])

    def start_battle(self):
        if not _config.data['enabled']: return
        if _config.data['only_HeavyTank']:
            if 'heavyTank' in BigWorld.player().vehicleTypeDescriptor.type.tags:
                self.on_off = True
        else: self.on_off = True
        if _config.data['activate_message'] and self.on_off:
            BigWorld.callback(5.0, self.message)
        BigWorld.callback(5.0, self.shout_damage)

    def clear_data(self):
        self.avgDMG = 0

    @staticmethod
    def blocked_armor_hit(vehicle, decode_comp_name):
        can_hit_primary_armor = None
        comp_matrix = Math.Matrix(vehicle.appearance.modelsDesc[decode_comp_name.componentName]['model'].matrix)
        first_hit_dir_local = decode_comp_name.matrix.applyToAxis(2)
        first_hit_dir = comp_matrix.applyVector(first_hit_dir_local)
        first_hit_point = decode_comp_name.matrix.translation
        first_hit_pos = comp_matrix.applyPoint(first_hit_point)
        world_to_veh_matrix = Math.Matrix(vehicle.model.matrix)
        world_to_veh_matrix.invert()
        start_point = world_to_veh_matrix.applyPoint(first_hit_pos - first_hit_dir)
        end_point = world_to_veh_matrix.applyPoint(first_hit_pos + first_hit_dir.scale(10.0))
        for compDescr, comp_matrix, isAttached in vehicle.getComponents():
            if not isAttached: continue
            collisions = compDescr['hitTester'].localHitTest(comp_matrix.applyPoint(start_point), comp_matrix.applyPoint(end_point))
            if collisions is None: continue
            for dist, _, hitAngleCos, matKind in collisions:
                mat_info = compDescr['materials'].get(matKind)
                can_hit_primary_armor = True if mat_info is not None and mat_info.useArmorHomogenization else False
                if can_hit_primary_armor: break
            if can_hit_primary_armor: break
        return can_hit_primary_armor

    def shout_damage(self):
        if self.avgDMG != 0:
            self.num += 1
            self.SumAvgDmg += self.avgDMG
        format_str = {
            'NumDmg': BigWorld.wg_getIntegralFormat(self.num),
            'AvgDmg': BigWorld.wg_getIntegralFormat(self.SumAvgDmg)
        }
        text = '%s' % _config.i18n['UI_in_battle_main_text']
        self.flash.set_text(text.format(**format_str))
        self.clear_data()

    def shout_damage_hp(self, shots):
        if self.list[shots]:
            if self.list[shots]['isDamage']:
                self.list[shots] = None
                return
            if self.list[shots]['avgDMG'] != 0:
                self.num += 1
                self.SumAvgDmg += self.list[shots]['avgDMG']
            format_str = {
                'NumDmg': BigWorld.wg_getIntegralFormat(self.num),
                'AvgDmg': BigWorld.wg_getIntegralFormat(self.SumAvgDmg)
            }
            text = '%s' % _config.i18n['UI_in_battle_main_text']
            self.flash.set_text(text.format(**format_str))
            self.list[shots] = None

    def shot(self, vehicle, attacker_id, points, effects_index):
        if not (_config.data['enabled'] and self.on_off): return
        if not vehicle.isStarted: return
        if not vehicle.isPlayer: return
        if BigWorld.player().team == BigWorld.player().arena.vehicles.get(attacker_id)['team']: return
        if vehicle.health < 1: return
        self.shots += 1
        index_hit, decode_comp_name = DamageFromShotDecoder.decodeHitPoints(points, vehicle.typeDescriptor)
        #compName = decode_comp_name[0].componentName if decode_comp_name else None
        has_pierced_hit = index_hit >= VEHICLE_HIT_EFFECT.ARMOR_PIERCED
        is_blocked = self.blocked_armor_hit(vehicle, decode_comp_name[0]) if decode_comp_name else False
        if is_blocked:
            for shell in BigWorld.player().arena.vehicles.get(attacker_id)['vehicleType'].gun['shots']:
                if effects_index == shell['shell']['effectsIndex']:
                    type_shell = shell['shell']['kind']
                    if type_shell != 'HIGH_EXPLOSIVE':
                        self.avgDMG, _ = shell['shell']['damage']
                        if has_pierced_hit:
                            self.list[self.shots] = {
                                'id'      : attacker_id,
                                'avgDMG'  : self.avgDMG,
                                'isDamage': False,
                                'used'    : False
                            }
                            BigWorld.callback(0.15, partial(self.shout_damage_hp, self.shots))
                        else: self.shout_damage()
                    break
        else: self.clear_data()

    def heal(self, vehicle, new_health, attacker_id):
        if not (_config.data['enabled'] and self.on_off): return
        if not vehicle.isStarted or not vehicle.isPlayer: return
        is_damage = max(0, new_health)
        if is_damage:
            for shots in self.list:
                if self.list[shots] and 'id' in self.list[shots] and self.list[shots]['id'] == attacker_id and not self.list[shots]['used']:
                    self.list[shots]['isDamage'] = True
                    self.list[shots]['used'] = True
                    break


# deformed functions:

def hook_after_create(*args):
    hooked_afterCreate(*args)
    if _config.data['enabled']:
        armor.flash = _TextFlash(args[0].proxy, args[0], _config.ids, '')
        armor.cleanup_battle_data()


def hook_before_delete(*args):
    hooked_beforeDelete(*args)
    if _config.data['enabled']:
        armor.cleanup_battle_data()
        if armor.flash:
            armor.flash.destroy()
            armor.flash = None


def hook_vehicle_show_damage_from_shot(*args):
    hooked_vehicle_show_damage_from_shot(*args) #(self, attackerID, points, effectsIndex, damageFactor)
    if armor.on_off:
        armor.shot(args[0], args[1], args[2], args[3])


def hook_vehicle_on_health_changed(*args):
    hooked_vehicle_on_health_changed(*args) #(self, newHealth, attackerID, attackReasonID)
    if armor.on_off:
        armor.heal(args[0], args[1], args[2])


def hook_minimap_start(*args):
    hooked_minimap_start(*args)
    armor.start_battle()


#start mod
_gui_config = _GUIConfig()
_config = _Config()
armor = ArmoringExtended()
_config.load()

#hooked
hooked_afterCreate = Battle.afterCreate
hooked_beforeDelete = Battle.beforeDelete
# noinspection PyProtectedMember
hooked_vehicle_show_damage_from_shot = Vehicle.showDamageFromShot
hooked_vehicle_on_health_changed = Vehicle.onHealthChanged
hooked_minimap_start = Minimap.Minimap.start

#hook

Battle.afterCreate = hook_after_create
Battle.beforeDelete = hook_before_delete

# noinspection PyProtectedMember

Vehicle.showDamageFromShot = hook_vehicle_show_damage_from_shot
Vehicle.onHealthChanged = hook_vehicle_on_health_changed
Minimap.Minimap.start = hook_minimap_start