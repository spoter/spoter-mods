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
import GUI
import Vehicle
import Math
from constants import AUTH_REALM
from Avatar import PlayerAvatar
from AvatarInputHandler import cameras
from BattleReplay import BattleReplay
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from tutorial.gui.Scaleform.battle import layout
from helpers import isPlayerAvatar
from gui.Scaleform.Battle import Battle


class Config(object):
    def __init__(self):
        self.enable = True
        self.debug = False
        self.ru = True if 'RU' in AUTH_REALM else False
        self.version = 'v3.09(18.11.2015)'
        self.author = 'by spoter'
        self.description = 'autoaim_extended'
        self.description_ru = 'Мод: "Индикатор'
        self.author_ru = 'автор: spoter'
        self.name = 'autoaim_extended'
        self.description_analytics = 'Мод: "Индикатор'
        self.tid = 'UA-57975916-6'
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
            # 
            import xvm_main
            self.xvm_installed = True
        except StandardError:
            pass

    def default_config(self):
        self.data = {
            'config': {
                'enable': True, 'debug': False, 'color': 'wg_enemy', 'indicators': {'model': True, 'direction': True, 'box': True}, 'language': 'Русский'
            }, 'language': {
                'Русский': {
                }, 'English': {

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


class AutoAim(object):
    def __init__(self):
        self.autoaim_vehicle = None
        self.view_edge_callback = None
        self.view_direction_callback = None
        self._box = None
        self._model = None
        self._model_blank = None
        self._direction = None
        self._create_config()
        self._load_config()

    def _create_config(self):
        self.indicatorModel = True
        self.indicatorEdge = False
        self.indicatorDirection = True
        self.indicatorBox = True
        self._path = 'objects/autoaim_extended/'
        self._box = None
        self._box_tex = '%swg_enemy/box.dds' % self._path
        self._model = None
        self._model_tex = '%swg_enemy/marker.model' % self._path
        self._model_blank = None
        self._model_blank_text = '%sempty/marker.model' % self._path
        self._direction = None
        self.angle_autoaim = math.radians(1.28915504)
        self._color = 'wg_enemy'
        self._autoaim = (0.8588235294, 0.01568627451, 0, 1)
        self._enemy = (1, 0, 0, 0.5)
        self._friend = (0, 1, 0, 0.5)
        self._flag = (1, 1, 1, 1)
        self._autoaim_def = (0.2, 0.2, 0.2, 0.5)
        self._enemy_def = (1, 0, 0, 0.5)
        self._friend_def = (0, 1, 0, 0.5)
        self._flag_def = (1, 1, 1, 1)
        self._config = {'colors': {}}
        self._config['colors']['blue'] = {'rgb': (0, 0, 255), 'edge': (0, 0, 1, 1), 'model': '%sblue/marker.model' % self._path, 'box': '%sblue/box.dds' % self._path}
        self._config['colors']['brown'] = {
            'rgb': (165, 42, 43), 'edge': (0.6470588235, 0.1647058824, 0.168627451, 1), 'model': '%sbrown/marker.model' % self._path, 'box': '%sbrown/box.dds' % self._path
        }
        self._config['colors']['chocolate'] = {
            'rgb': (211, 105, 30), 'edge': (0.8274509804, 0.4117647059, 0.1176470588, 1), 'model': '%schocolate/marker.model' % self._path, 'box': '%schocolate/box.dds' % self._path
        }
        self._config['colors']['cornflower_blue'] = {
            'rgb': (101, 149, 238), 'edge': (0.3960784314, 0.5843137255, 0.9333333333, 1), 'model': '%scornflower_blue/marker.model' % self._path, 'box': '%scornflower_blue/box.dds' % self._path
        }
        self._config['colors']['cream'] = {
            'rgb': (252, 245, 200), 'edge': (0.9882352941, 0.9607843137, 0.7843137255, 1), 'model': '%scream/marker.model' % self._path, 'box': '%scream/box.dds' % self._path
        }
        self._config['colors']['cyan'] = {'rgb': (0, 255, 255), 'edge': (0, 1, 1, 1), 'model': '%scyan/marker.model' % self._path, 'box': '%scyan/box.dds' % self._path}
        self._config['colors']['emerald'] = {
            'rgb': (40, 240, 156), 'edge': (0.1568627451, 0.9411764706, 0.6117647059, 1), 'model': '%semerald/marker.model' % self._path, 'box': '%semerald/box.dds' % self._path
        }
        self._config['colors']['gold'] = {'rgb': (255, 215, 0), 'edge': (1, 0.8431372549, 0, 1), 'model': '%sgold/marker.model' % self._path, 'box': '%sgold/box.dds' % self._path}
        self._config['colors']['green'] = {'rgb': (0, 128, 0), 'edge': (0, 0.5019607843, 0, 1), 'model': '%sgreen/marker.model' % self._path, 'box': '%sgreen/box.dds' % self._path}
        self._config['colors']['green_yellow'] = {
            'rgb': (173, 255, 46), 'edge': (0.6784313725, 1, 0.1803921569, 1), 'model': '%sgreen_yellow/marker.model' % self._path, 'box': '%sgreen_yellow/box.dds' % self._path
        }
        self._config['colors']['hot_pink'] = {
            'rgb': (255, 105, 181), 'edge': (1, 0.4117647059, 0.7098039216, 1), 'model': '%shot_pink/marker.model' % self._path, 'box': '%shot_pink/box.dds' % self._path
        }
        self._config['colors']['lime'] = {'rgb': (0, 255, 0), 'edge': (0, 1, 0, 1), 'model': '%slime/marker.model' % self._path, 'box': '%slime/box.dds' % self._path}
        self._config['colors']['orange'] = {'rgb': (255, 165, 0), 'edge': (1, 0.6470588235, 0, 1), 'model': '%sorange/marker.model' % self._path, 'box': '%sorange/box.dds' % self._path}
        self._config['colors']['pink'] = {'rgb': (255, 192, 203), 'edge': (1, 0.7529411765, 0.7960784314, 1), 'model': '%spink/marker.model' % self._path, 'box': '%spink/box.dds' % self._path}
        self._config['colors']['purple'] = {'rgb': (128, 0, 128), 'edge': (0.5019607843, 0, 0.5019607843, 1), 'model': '%spurple/marker.model' % self._path, 'box': '%spurple/box.dds' % self._path}
        self._config['colors']['red'] = {'rgb': (255, 0, 0), 'edge': (1, 0, 0, 1), 'model': '%sred/marker.model' % self._path, 'box': '%sred/box.dds' % self._path}
        self._config['colors']['wg_blur'] = {
            'rgb': (131, 120, 252), 'edge': (0.5137254902, 0.4705882353, 0.9882352941, 1), 'model': '%swg_blur/marker.model' % self._path, 'box': '%swg_blur/box.dds' % self._path
        }
        self._config['colors']['wg_enemy'] = {
            'rgb': (219, 4, 0), 'edge': (0.8588235294, 0.01568627451, 0, 1), 'model': '%swg_enemy/marker.model' % self._path, 'box': '%swg_enemy/box.dds' % self._path
        }
        self._config['colors']['wg_friend'] = {
            'rgb': (128, 214, 57), 'edge': (0.5019607843, 0.8392156863, 0.2235294118, 1), 'model': '%swg_friend/marker.model' % self._path, 'box': '%swg_friend/box.dds' % self._path
        }
        self._config['colors']['wg_squad'] = {
            'rgb': (255, 224, 65), 'edge': (1, 0.8784313725, 0.2549019608, 1), 'model': '%swg_squad/marker.model' % self._path, 'box': '%swg_squad/box.dds' % self._path
        }
        self._config['colors']['yellow'] = {'rgb': (255, 255, 0), 'edge': (1, 1, 0, 1), 'model': '%syellow/marker.model' % self._path, 'box': '%syellow/box.dds' % self._path}

    def _load_config(self):
        self._color = config.data['config'].get('color', 'wg_enemy')
        config_indicators = config.data['config'].get('indicators')
        self.indicatorModel = config_indicators.get('model', True)
        self.indicatorDirection = config_indicators.get('direction', True)
        self.indicatorBox = config_indicators.get('box', True)
        self._box_tex = self._config['colors'][self._color]['box']
        self._model_tex = self._config['colors'][self._color]['model']
        self._autoaim = self._config['colors'][self._color]['edge']

    def find_autoaim_target(self):
        auto_aim_vehicle = property(lambda self_other: BigWorld.entities.get(self_other.__autoAimVehID, None))
        print('find_autoaim_target', auto_aim_vehicle)
        if auto_aim_vehicle is None and BigWorld.target() is not None:
            return BigWorld.target()
        player = BigWorld.player()
        vehicles = player.arena.vehicles
        camera_dir, camera_pos = cameras.getWorldRayAndPoint(0, 0)
        camera_dir.normalise()
        result_len = None
        las_vehicle = None
        min_radian = 100000.0
        for vId, vData in vehicles.items():
            if vData['team'] == player.team:
                continue
            vehicle = BigWorld.entity(vId)
            if vehicle is None or not vehicle.isStarted or not vehicle.isAlive():
                continue
            temp1, radian = self._calc_radian(vehicle.position, self.angle_autoaim) #1.289 градуса в радианах

            if not temp1 and temp1 is not None:
                continue
            length = self._calc_length(vehicle.position, BigWorld.player().position)
            if radian:
                if result_len is None:
                    result_len = length
                    las_vehicle = vehicle
                if radian < min_radian and result_len >= length:
                    min_radian = radian
                    las_vehicle = vehicle
        result = las_vehicle
        if result is not None:
            if BigWorld.wg_collideSegment(BigWorld.player().spaceID, BigWorld.entity(result.id).appearance.modelsDesc['gun']['model'].position, camera_pos, False) is None:
                return result
        return BigWorld.target()

    @staticmethod
    def _calc_length(start_position, end_position):
        return (end_position - start_position).length

    @staticmethod
    def _calc_radian(target_position, angle):
        camera_dir, camera_pos = cameras.getWorldRayAndPoint(0, 0)
        camera_dir.normalise()
        camera_to_target = target_position - camera_pos
        a = camera_to_target.dot(camera_dir)
        if a < 0:
            return False, None
        target_radian = camera_to_target.lengthSquared
        radian = 1.0 - a * a / target_radian
        if radian > angle:
            return False, None
        return True, radian

    @staticmethod
    def get_battle_on():
        try:
            if BigWorld.player().arena: return True
        except StandardError: return False
        return hasattr(BigWorld.player(), 'arena')

    @staticmethod
    def get_is_live(vehicle_id):
        try: return BigWorld.player().arena.vehicles[vehicle_id]['isAlive']
        except StandardError: return False

    def get_is_friendly(self, vehicle_id):
        player = BigWorld.player()
        return self.get_battle_on() and player.arena.vehicles[player.playerVehicleID]['team'] == player.arena.vehicles[vehicle_id]['team']

    def create_indicators(self):
        if self.indicatorBox:
            self.create_box()
        if self.indicatorDirection:
            self.create_direction()
        if self.indicatorModel:
            self.create_model()

    def install_indicators(self):
        self.autoaim_vehicle = None
        self.create_indicators()

    def uninstall_indicators(self):
        self.delete_indicators()
        self.autoaim_vehicle = None
        self.view_edge_callback = None
        self.view_direction_callback = None

    def view_indicators(self):
        if isinstance(self.autoaim_vehicle, Vehicle.Vehicle) and self.autoaim_vehicle.isStarted and self.get_is_live(self.autoaim_vehicle.id) and not self.get_is_friendly(self.autoaim_vehicle.id):
            if self.indicatorBox:
                self.view_box()
            if self.indicatorEdge:
                self.view_edge_callback = BigWorld.callback(0.5, self.view_edge)
            if self.indicatorModel:
                self.view_model()
            if self.indicatorDirection:
                self.view_direction_callback = BigWorld.callback(0.5, self.view_direction)
        else:
            self.autoaim_vehicle = None

    def hide_indicators(self):
        if self.indicatorBox:
            self.hide_box()
        if self.indicatorEdge:
            if self.view_edge_callback:
                self.view_edge_callback = None
        if self.indicatorModel:
            self.hide_model()
        if self.indicatorDirection:
            if self.view_direction_callback:
                self.view_direction_callback = None
            self.hide_direction()
        self.autoaim_vehicle = None

    def create_box(self):
        self._box = GUI.BoundingBox(self._box_tex)
        self._box.size = (0.01, 0.01)
        self._box.visible = False
        GUI.addRoot(self._box)

    def create_model(self):
        if self._model:
            self.delete_model()
        if self._model_blank:
            self.delete_blank_model()
        if self.indicatorModel:
            self._model = BigWorld.Model(self._model_tex)
            self._model.visible = False
        elif self.indicatorEdge and not self.indicatorModel:
            self._model_blank = BigWorld.Model(self._model_blank_text)
            self._model_blank.visible = False

    def create_direction(self):
        if self.indicatorDirection:
            # noinspection PyProtectedMember
            self._direction = layout._DirectionIndicator()
            self._direction.component.visible = False
            self._direction.active(False)
            if self._color in ['cream', 'emerald', 'gold', 'green', 'green_yellow', 'lime', 'wg_friend', 'wg_squad', 'yellow']:
                self._direction.setShape('green')
            elif self._color in ['brown', 'chocolate', 'orange', 'pink', 'red', 'wg_enemy']:
                self._direction.setShape('red')
            elif self._color in ['blue', 'cornflower_blue', 'cyan', 'hot_pink', 'purple', 'wg_blur']:
                self._direction.setShape('purple')
            else:
                self._direction.setShape('red')

    def view_box(self):
        if hasattr(self.autoaim_vehicle, 'model') and self._box:
            self._box.source = self.autoaim_vehicle.model.bounds
            self._box.visible = True

    def view_model(self):
        if self._model:
            if hasattr(self.autoaim_vehicle, 'appearance'):
                self.autoaim_vehicle.appearance.modelsDesc['hull']['model'].node('HP_turretJoint').attach(self._model)
            self._model.visible = True
        if self._model_blank:
            if hasattr(self.autoaim_vehicle, 'appearance'):
                self.autoaim_vehicle.appearance.modelsDesc['hull']['model'].node('HP_turretJoint').attach(self._model_blank)
            self._model_blank.visible = True

    def view_edge(self):
        if hasattr(self.autoaim_vehicle, 'appearance') and hasattr(self.autoaim_vehicle, 'model') and self.autoaim_vehicle.isAlive():
            BigWorld.wgDelEdgeDetectEntity(self.autoaim_vehicle)
            if BigWorld.wg_collideSegment(BigWorld.player().spaceID, self.autoaim_vehicle.appearance.modelsDesc['gun']['model'].position, BigWorld.entity(BigWorld.player(

            ).playerVehicleID).appearance.modelsDesc['gun']['model'].position, False) is None:
                BigWorld.wgSetEdgeDetectColors((Math.Vector4(self._autoaim_def), Math.Vector4(self._enemy), Math.Vector4(self._friend), Math.Vector4(self._autoaim)))
                BigWorld.wgAddEdgeDetectEntity(self.autoaim_vehicle, 3, 0)
        self.view_edge_callback = BigWorld.callback(0.5, self.view_edge)

    def view_direction(self):
        try:
            if self.autoaim_vehicle is not None and self.get_is_live(self.autoaim_vehicle.id):
                self._direction.component.visible = True
                self._direction.active(True)
                matrix = self.autoaim_vehicle.matrix
                if matrix:
                    m = Math.Matrix(matrix)
                    pos = m.translation
                    length = (BigWorld.player().position - pos).length
                    self._direction.setPosition(pos)
                    self._direction.setDistance(length)
            self.view_direction_callback = BigWorld.callback(0.5, self.view_direction)
        except StandardError:
            self.view_direction_callback = None

    def hide_box(self):
        if self._box:
            self._box.source = None
            self._box.visible = False

    def hide_model(self):
        if self._model and self._model.visible:
            self._model.visible = False
            if hasattr(self.autoaim_vehicle, 'appearance'):
                turret_position = self.autoaim_vehicle.appearance.modelsDesc['hull']['model'].node('HP_turretJoint')
                if turret_position.attachments.length != 0:
                    turret_position.detach(self._model)
        if self._model_blank and self._model_blank.visible:
            self._model_blank.visible = False
            if hasattr(self.autoaim_vehicle, 'appearance'):
                turret_position = self.autoaim_vehicle.appearance.modelsDesc['hull']['model'].node('HP_turretJoint')
                if turret_position.attachments.length != 0:
                    turret_position.detach(self._model_blank)
        self.create_model()

    def hide_edge(self):
        if hasattr(self.autoaim_vehicle, 'appearance'):
            BigWorld.wgDelEdgeDetectEntity(self.autoaim_vehicle)
        BigWorld.wgSetEdgeDetectColors((Math.Vector4(self._autoaim_def), Math.Vector4(self._enemy_def), Math.Vector4(self._friend_def), Math.Vector4(self._flag_def)))

    def hide_direction(self):
        if self._direction:
            self._direction.component.visible = False
            self._direction.active(False)

    def delete_indicators(self):
        self.delete_direction()
        self.delete_box()
        self.delete_model()

    def delete_direction(self):
        if self._direction:
            self._direction = None

    def delete_box(self):
        if self._box:
            GUI.delRoot(self._box)
        self._box = None

    def delete_model(self):
        self._model = None

    def delete_blank_model(self):
        self._model_blank = None

    def start_battle(self):
        BigWorld.player().arena.onVehicleKilled += self.injected_on_vehicle_killed
        self.install_indicators()

    def stop_battle(self):
        BigWorld.player().arena.onVehicleKilled -= self.injected_on_vehicle_killed
        self.hide_indicators()
        self.uninstall_indicators()

    def injected_on_vehicle_killed(self, target_id, attacker_id, equipment_id, reason):
        _, _, _ = attacker_id, reason, equipment_id
        if self.autoaim_vehicle and target_id == self.autoaim_vehicle.id:
            self.hide_indicators()
        if target_id == BigWorld.player().playerVehicleID:
            self.hide_indicators()


# deformed functions:

def hook_update_all(self):
    hooked_UpdateAll(self)
    config.analytics()


def hook_auto_aim(self, target):
    if config.enable and not self.autoaim_extended.use:
        old_vehicle = autoaim_extended.autoaim_vehicle
        if autoaim_extended.autoaim_vehicle:
            autoaim_extended.hide_indicators()
        if old_vehicle != target:
            autoaim_extended.autoaim_vehicle = target
        autoaim_extended.view_indicators()
    return hooked_autoAim(self, target)


def hook_on_auto_aim_vehicle_lost(self):
    if config.enable:
        if autoaim_extended.autoaim_vehicle:
            autoaim_extended.hide_indicators()
    return hooked_onAutoAimVehicleLost(self)


def hook_on_lock_target(self, lock):
    if config.enable:
        player = BigWorld.player()
        if not isPlayerAvatar():
            return
        if self.isPlaying:
            if lock == 1:
                player.autoAim(autoaim_extended.find_autoaim_target())
            elif lock == 0:
                player.autoAim(None)
            else:
                player.autoAim(None)
        elif self.isRecording:
            self._BattleReplay__replayCtrl.onLockTarget(lock)
    else:
        hooked_onLockTarget(self, lock)


def hook_start_battle(self):
    hooked_start_battle(self)
    if config.enable:
        autoaim_extended.start_battle()


def hook_stop_battle(self):
    hooked_stop_battle(self)
    if config.enable:
        autoaim_extended.stop_battle()

class Autoaim_extended():
    def __init__(self):
        self.use = False
        self.target = autoaim_extended.autoaim_vehicle

    def start(self, target):
        if not self.use:
            self.use = True
        if config.enable:
            old_vehicle = autoaim_extended.autoaim_vehicle
            if autoaim_extended.autoaim_vehicle:
                autoaim_extended.hide_indicators()
            if old_vehicle != target:
                autoaim_extended.autoaim_vehicle = target
            autoaim_extended.view_indicators()
            return True
        return


    def stop(self):
        if not self.use:
            self.use = True
        if config.enable:
            if autoaim_extended.autoaim_vehicle:
                autoaim_extended.hide_indicators()
                return True
        return

#hooked
# noinspection PyProtectedMember
hooked_UpdateAll = Hangar._Hangar__updateAll
hooked_autoAim = PlayerAvatar.autoAim
hooked_onAutoAimVehicleLost = PlayerAvatar.onAutoAimVehicleLost
hooked_onLockTarget = BattleReplay.onLockTarget
hooked_start_battle = Battle.afterCreate
hooked_stop_battle = Battle.beforeDelete


#hook
Hangar._Hangar__updateAll = hook_update_all
PlayerAvatar.autoAim = hook_auto_aim
PlayerAvatar.onAutoAimVehicleLost = hook_on_auto_aim_vehicle_lost
BattleReplay.onLockTarget = hook_on_lock_target
Battle.afterCreate = hook_start_battle
Battle.beforeDelete = hook_stop_battle

#start mod
config = Config()
config.load_mod()
autoaim_extended = AutoAim()
PlayerAvatar.autoaim_extended = Autoaim_extended()