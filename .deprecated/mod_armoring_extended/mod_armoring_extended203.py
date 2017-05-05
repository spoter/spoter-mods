# -*- coding: utf-8 -*-
import datetime
import re
import random
import string
import os
import json
import codecs
import urllib2
import urllib
import threading
import weakref
from functools import partial

import BigWorld
import Math
import GUI
import Keys
import game
from constants import AUTH_REALM, VEHICLE_HIT_EFFECT
from gui import InputHandler, g_guiResetters
from gui.Scaleform import Minimap
from gui.Scaleform.Flash import Flash
from gui.Scaleform.Battle import Battle
from gui.Scaleform.daapi.view.lobby.hangar import Hangar
from Vehicle import Vehicle
from VehicleEffects import DamageFromShotDecoder
from gui.app_loader import g_appLoader


class Config(object):
    def __init__(self):
        self.enable = True
        self.debug = False
        self.ru = True if AUTH_REALM == 'RU' else False
        self.version = 'v2.03(30.08.2015)'
        self.author = 'by spoter, reven86'
        self.description = 'armoring_extended'
        self.name = 'armoring_extended'
        self.description_analytics = 'Мод: "Броняня"'
        self.description_ru = 'Мод: "Броняня"'
        self.author_ru = 'авторы: spoter, reven86'
        self.tid = 'UA-57975916-9'
        self.setup = {'MODIFIER': {'MODIFIER_NONE': 0, 'MODIFIER_SHIFT': 1, 'MODIFIER_CTRL': 2, 'MODIFIER_ALT': 4}}
        self.sys_mes = {}
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
            # 
            import xvm_main
            self.xvm_installed = True
        except StandardError:
            pass

    def default_config(self):
        self.data = {
            'config': {
                'enable': True, 'debug': False, 'activate_message': True, 'only_HeavyTank': False, 'language': 'Русский'
            }, 'language': {
                'Русский': {
                    'main_text': 'Танканул <font color="#fdf498">{NumDmg}</font> раз(а) на <img align="top" src="img://gui/maps/icons/library/ClanBattleResultIcon-1.png" height="16" width="16" '
                                 'vspace="-3" /><font color="#fdf498">{AvgDmg}</font> урона', 'activate_message': 'Броняня: Активирована',
                    'activate_message_only_HeavyTank': 'Броняня: Активирована, режим ТТ'
                }, 'English': {
                    'main_text': '<font color="#fdf498">{NumDmg}</font> Blocked <img align="top" src="img://gui/maps/icons/library/ClanBattleResultIcon-1.png" height="16" width="16" vspace="-3" '
                                 '/><font color="#fdf498">{AvgDmg}</font> damage', 'activate_message': 'Armoring Extended: Activated',
                    'activate_message_only_HeavyTank': 'Armoring Extended: Activated, only Heavy Tanks'

                }, 'Deutsch': {
                    'main_text': '<font color="#fdf498">{NumDmg}</font> Blocked <img align="top" src="img://gui/maps/icons/library/ClanBattleResultIcon-1.png" height="16" width="16" vspace="-3" '
                                 '/><font color="#fdf498">{AvgDmg}</font> Schaden', 'activate_message': 'Armoring Extended: Aktiviert',
                    'activate_message_only_HeavyTank': 'Armoring Extended: Aktiviert, nur schwere Panzer'
                }
            }, 'flash': {
                'text': {
                    'x': 20, 'y': 450, 'alignX': 'left', 'alignY': 'top', 'default_font': '$IMELanguageBar', 'default_font_size': 14, 'default_font_color': '#BDFA64'
                }, 'background': {
                    'enable': False, 'image': 'img://../res_mods/configs/spoter_mods/%s/background.png' % self.name, 'x': 18, 'y': 448, 'width': 250, 'height': 27, 'alpha': 80

                }, 'shadow': {
                    'enable': True, 'distance': 0, 'angle': 0, 'color': '#000000', 'alpha': 60, 'size': 40, 'strength': 500

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
        if armor.flash:
            text = self.data['flash'].get('text')
            background = self.data['flash'].get('background')
            shadow = self.data['flash'].get('shadow')
            if text:
                armor.flash.data.set_text_config(text.get('x', 0), text.get('y', 0), text.get('alignX', 'left'), text.get('alignY', 'top'), text.get('default_font', '$IMELanguageBar'),
                    text.get('default_font_size', 14), text.get('default_font_color', '#BDFA64'))
            if background:
                armor.flash.data.set_background_config(background.get('enable'), background.get('image'), background.get('x'), background.get('y'), background.get('width'), background.get('height'),
                    background.get('alpha'))
            if shadow:
                armor.flash.data.set_shadow_config(shadow.get('enable'), shadow.get('distance'), shadow.get('angle'), shadow.get('color'), shadow.get('alpha'), shadow.get('size'),
                    shadow.get('strength'))

    def update_cord(self, text_x, text_y, back_x, back_y):
        flash = self.data['flash']
        text = flash.get('text')
        background = flash.get('background')
        text['x'] = text_x
        text['y'] = text_y
        background['x'] = back_x
        background['y'] = back_y

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

    def save_config_debug(self):
        new_config = self.load_json('armoring_extended', self.data, True)
        self.data = new_config
        self.do_config()

    def load_config_debug(self):
        new_config = self.load_json('armoring_extended', self.data)
        self.data = new_config
        self.do_config()
        if armor:
            armor.shout_damage()


class TextFlash(Flash):
    def __init__(self, parent_ui, flash_name):
        Flash.__init__(self, flash_name)
        self.parentUI = parent_ui
        self.isVisible = False
        self.movie.backgroundAlpha = 0.0
        self.component.wg_inputKeyMode = 2
        self.component.position.z = 0.5
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.flashSize = GUI.screenResolution()
        self.text = {}
        self.shadow = {}
        self.background = {}

    def start(self):
        self.active(True)
        self.visible_view(True)
        self.component.visible = False
        self.set_def_config()
        self.update_pos()

    def set_def_config(self):
        text = config.data['flash'].get('text')
        background = config.data['flash'].get('background')
        shadow = config.data['flash'].get('shadow')
        self.text['x'] = text['x']
        self.text['y'] = text['y']
        self.text['alignX'] = text['alignX']
        self.text['alignY'] = text['alignY']
        self.text['default_font'] = text['default_font']
        self.text['default_font_size'] = text['default_font_size']
        self.text['default_font_color'] = text['default_font_color']
        self.background['enable'] = background['enable']
        self.background['image'] = background['image']
        self.background['x'] = background['x']
        self.background['y'] = background['y']
        self.background['width'] = background['width']
        self.background['height'] = background['height']
        self.background['alpha'] = background['alpha']
        self.shadow['enable'] = shadow['enable']
        self.shadow['distance'] = shadow['distance']
        self.shadow['angle'] = shadow['angle']
        self.shadow['color'] = shadow['color']
        self.shadow['alpha'] = shadow['alpha']
        self.shadow['size'] = shadow['size']
        self.shadow['strength'] = shadow['strength']

    def set_text_config(self, x=None, y=None, align_x=None, align_y=None, default_font=None, default_font_size=None, default_font_color=None):
        if x is not None: self.text['x'] = int(x)
        if y is not None: self.text['y'] = int(y)
        if align_x is not None: self.text['alignX'] = '%s' % align_x
        if align_y is not None: self.text['alignY'] = '%s' % align_y
        if default_font is not None: self.text['default_font'] = '%s' % default_font
        if default_font_size is not None: self.text['default_font_size'] = int(default_font_size)
        if default_font_color is not None: self.text['default_font_color'] = '%s' % default_font_color

    def set_background_config(self, enable=None, image=None, x=None, y=None, width=None, height=None, alpha=None):
        if enable is not None: self.background['enable'] = enable
        if image is not None: self.background['image'] = '%s' % image
        if x is not None: self.background['x'] = int(x)
        if y is not None: self.background['y'] = int(y)
        if width is not None: self.background['width'] = int(width)
        if height is not None: self.background['height'] = int(height)
        if alpha is not None: self.background['alpha'] = int(alpha)

    def set_shadow_config(self, enable=None, distance_shadow=None, angle_shadow=None, color_shadow=None, alpha_shadow=None, size_shadow=None, strength_shadow=None):
        if enable is not None: self.shadow['enable'] = enable
        if distance_shadow is not None: self.shadow['distance'] = int(distance_shadow)
        if angle_shadow is not None: self.shadow['angle'] = int(angle_shadow)
        if color_shadow is not None: self.shadow['color'] = '%s' % color_shadow
        if alpha_shadow is not None: self.shadow['alpha'] = int(alpha_shadow)
        if size_shadow is not None: self.shadow['size'] = int(size_shadow)
        if strength_shadow is not None: self.shadow['strength'] = int(strength_shadow)

    def destroy(self):
        self.close()

    def visible_view(self, boole):
        self.isVisible = boole
        self.component.visible = boole

    def visible_tab(self, event):
        isdown, key, mods, is_repeat = game.convertKeyEvent(event)
        if not is_repeat and key == 15:
            boole = not isdown if self.isVisible else False
            self.component.visible = boole

    def update_pos_debug(self, mod_x, mod_y):
        self.text['x'] += mod_x
        self.text['y'] += mod_y
        self.background['x'] += mod_x
        self.background['y'] += mod_y

    def update_pos(self):
        screen_gui = GUI.screenResolution()
        screen_x = {'left': 0, 'center': screen_gui[0] / 2, 'right': screen_gui[0]}
        screen_y = {'top': 0, 'center': screen_gui[1] / 2, 'bottom': screen_gui[1]}
        if self.text['x'] + 10 > screen_gui[0]: self.text['x'] = screen_gui[0] - 10
        if self.text['y'] + 10 > screen_gui[1]: self.text['y'] = screen_gui[1] - 10
        x = self.text['x']
        y = self.text['y']
        align_x = self.text['alignX']
        align_y = self.text['alignY']
        elem_x = x + screen_x.get(align_x, 0)
        elem_y = y + screen_y.get(align_y, 0)
        self.set_position(elem_x, elem_y)
        if self.background['x'] + 10 > screen_gui[0]: self.background['x'] = screen_gui[0] - 10
        if self.background['y'] + 10 > screen_gui[1]: self.background['y'] = screen_gui[1] - 10
        if self.background['enable']:
            self.set_bg(self.background['image'], self.background['x'], self.background['y'], self.background['width'], self.background['height'], self.background['alpha'])
        else:
            self.set_bg(None, 0, 0, 0, 0, 0)
        config.update_cord(self.text['x'], self.text['y'], self.background['x'], self.background['y'])

    def set_position(self, pos_x, pos_y):
        self.flash_call('setPosition', [pos_x, pos_y])

    def set_visible(self, boole):
        self.flash_call('setVisible', [boole])

    def set_alpha(self, alpha):
        self.flash_call('setAlpha', [alpha])

    def set_shadow(self, distance_shadow, angle_shadow, color_shadow, alpha_shadow, size_shadow, strength_shadow):
        self.flash_call('setShadow', [distance_shadow, angle_shadow, color_shadow, alpha_shadow, size_shadow, strength_shadow])

    def set_bg(self, image_bg, x_pos_bg, y_pos_bg, width_bg, height_bg, alpha_bg):
        self.flash_call('setBG', [image_bg, x_pos_bg, y_pos_bg, width_bg, height_bg, alpha_bg])

    def set_text_flash(self, text):
        text = '<font size="%s" face="%s" color="%s" >%s</font>' % (self.text['default_font_size'], self.text['default_font'], self.text['default_font_color'], text)
        self.flash_call('setText', [text])

    def set_text(self, text):
        if self.isVisible:
            self.component.visible = True
            self.set_text_flash(text)
            if self.shadow['enable']:
                self.set_shadow(self.shadow['distance'], self.shadow['angle'], self.shadow['color'], self.shadow['alpha'], self.shadow['size'], self.shadow['strength'])
            else:
                self.set_shadow(0, 0, '#000000', 0, 0, 0)

    def flash_call(self, func_name, args=None):
        self.call('TextFlash.' + func_name, args)


class CustomFlash(object):
    def __init__(self, flash_name):
        self.data = TextFlash(weakref.proxy(self), flash_name)


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
        if config.data['config'].get('only_HeavyTank'):
            app.call('battle.PlayerMessagesPanel.ShowMessage',
                [config.language['activate_message_only_HeavyTank'] + random.choice(string.ascii_letters), config.language['activate_message_only_HeavyTank'].decode('utf-8-sig'), 'gold'])
        else:
            app.call('battle.PlayerMessagesPanel.ShowMessage',
                [config.language['activate_message'] + random.choice(string.ascii_letters), config.language['activate_message'].decode('utf-8-sig'), 'gold'])

    def start_battle(self):
        if not config.enable: return
        if config.data['config'].get('only_HeavyTank'):
            if 'heavyTank' in BigWorld.player().vehicleTypeDescriptor.type.tags:
                self.on_off = True
        else: self.on_off = True
        if config.data['config'].get('activate_message') and self.on_off:
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
        format_str = {'NumDmg': BigWorld.wg_getIntegralFormat(self.num), 'AvgDmg': BigWorld.wg_getIntegralFormat(self.SumAvgDmg)}
        self.flash.data.set_text(config.language['main_text'].format(**format_str))
        self.clear_data()

    def shout_damage_hp(self, shots):
        if self.list[shots]:
            if self.list[shots]['isDamage']:
                self.list[shots] = None
                return
            if self.list[shots]['avgDMG'] != 0:
                self.num += 1
                self.SumAvgDmg += self.list[shots]['avgDMG']
            format_str = {'NumDmg': BigWorld.wg_getIntegralFormat(self.num), 'AvgDmg': BigWorld.wg_getIntegralFormat(self.SumAvgDmg)}
            self.flash.data.set_text(config.language['main_text'].format(**format_str))
            self.list[shots] = None

    def shot(self, vehicle, attacker_id, points, effects_index):
        if not (config.enable and self.on_off): return
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
                            self.list[self.shots] = {'id': attacker_id, 'avgDMG': self.avgDMG, 'isDamage': False, 'used': False}
                            BigWorld.callback(0.15, partial(self.shout_damage_hp, self.shots))
                        else: self.shout_damage()
                    break
        else: self.clear_data()

    def heal(self, vehicle, new_health, attacker_id):
        if not (config.enable and self.on_off): return
        if not vehicle.isStarted or not vehicle.isPlayer: return
        is_damage = max(0, new_health)
        if is_damage:
            for shots in self.list:
                if self.list[shots] and 'id' in self.list[shots] and self.list[shots]['id'] == attacker_id and not self.list[shots]['used']:
                    self.list[shots]['isDamage'] = True
                    self.list[shots]['used'] = True
                    break


# deformed functions:

def hook_show_all(self_battle, old_hooked_show_all, is_show):
    old_hooked_show_all(self_battle, is_show)
    if config.enable:
        if armor.flash is None: return
        armor.flash.data.visible_view(is_show)


def hook_after_create(self):
    hooked_afterCreate(self)
    if config.enable:
        armor.flash = CustomFlash('%s.swf' % config.name)
        armor.flash.data.start()
        g_guiResetters.add(armor.flash.data.update_pos)
        config.do_config()
        armor.cleanup_battle_data()


def hook_before_delete(self):
    hooked_beforeDelete(self)
    if config.enable:
        armor.cleanup_battle_data()
        if armor.flash is None: return
        armor.flash.data.destroy()
        g_guiResetters.discard(armor.flash.data.update_pos)
        armor.flash.data = None
        armor.flash = None


def hook_update_all(self):
    hooked_update_all(self)
    config.analytics()


def inject_handle_key_event(event):
    if config.enable:
        is_down, key, mods, is_repeat = game.convertKeyEvent(event)
        if config.debug and armor.flash:
            if key == Keys.KEY_NUMPAD6 and is_down and mods == config.setup['MODIFIER']['MODIFIER_ALT']:
                armor.flash.data.update_pos_debug(10, 0)
                armor.flash.data.update_pos()
                config.save_config_debug()
                print 'position change x +10'
            if key == Keys.KEY_NUMPAD4 and is_down and mods == config.setup['MODIFIER']['MODIFIER_ALT']:
                armor.flash.data.update_pos_debug(-10, 0)
                armor.flash.data.update_pos()
                config.save_config_debug()
                print 'position change x -10'
            if key == Keys.KEY_NUMPAD8 and is_down and mods == config.setup['MODIFIER']['MODIFIER_ALT']:
                armor.flash.data.update_pos_debug(0, -10)
                armor.flash.data.update_pos()
                config.save_config_debug()
                print 'position change y -10'
            if key == Keys.KEY_NUMPAD2 and is_down and mods == config.setup['MODIFIER']['MODIFIER_ALT']:
                armor.flash.data.update_pos_debug(0, 10)
                armor.flash.data.update_pos()
                config.save_config_debug()
                print 'position change y +10'
            if key == Keys.KEY_NUMPADMINUS and is_down and mods == config.setup['MODIFIER']['MODIFIER_ALT']:
                config.load_config_debug()
                armor.flash.data.update_pos()
                print 'config reloaded'


def hook_vehicle_show_damage_from_shot(self, attacker_id, points, effects_index):
    hooked_vehicle_show_damage_from_shot(self, attacker_id, points, effects_index)
    if armor.on_off:
        armor.shot(self, attacker_id, points, effects_index)


def hook_vehicle_on_health_changed(self, new_health, attacker_id, attack_reason_id):
    hooked_vehicle_on_health_changed(self, new_health, attacker_id, attack_reason_id)
    if armor.on_off:
        armor.heal(self, new_health, attacker_id)


def hook_minimap_start(self):
    hooked_minimap_start(self)
    armor.start_battle()


#start mod
armor = ArmoringExtended()
config = Config()
config.load_mod()

#hooked
hooked_show_all = Battle.showAll
hooked_afterCreate = Battle.afterCreate
hooked_beforeDelete = Battle.beforeDelete
# noinspection PyProtectedMember
hooked_update_all = Hangar._Hangar__updateAll
hooked_vehicle_show_damage_from_shot = Vehicle.showDamageFromShot
hooked_vehicle_on_health_changed = Vehicle.onHealthChanged
hooked_minimap_start = Minimap.Minimap.start

#hook
Battle.showAll = lambda self_battle, is_show: hook_show_all(self_battle, hooked_show_all, is_show)
Battle.afterCreate = hook_after_create
Battle.beforeDelete = hook_before_delete

# noinspection PyProtectedMember
Hangar._Hangar__updateAll = hook_update_all
Vehicle.showDamageFromShot = hook_vehicle_show_damage_from_shot
Vehicle.onHealthChanged = hook_vehicle_on_health_changed
Minimap.Minimap.start = hook_minimap_start

#Inject
InputHandler.g_instance.onKeyDown += inject_handle_key_event
InputHandler.g_instance.onKeyUp += inject_handle_key_event
