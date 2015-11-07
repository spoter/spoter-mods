# -*- coding: utf-8 -*-

import BigWorld
import Keys
# noinspection PyProtectedMember
from tutorial.control.battle.functional import _StaticObjectMarker3D
from gui.Scaleform.Battle import Battle
from AvatarInputHandler.aims import Aim
from gui.app_loader import g_appLoader
from gui import InputHandler
from mods.modsettingsapi.ModSettingsAPI import g_modSettingsAPI

class _Config(object):
    def __init__(self):
        self.arty_ball = {'enabled': True, 'show_alt_mode': False, 'activated': True, 'show_only_strategic_mode': True}
        self.arty_ball_gui = None
        self.template_arty_ball()

    def template_arty_ball(self):
        settingsTemplate = {
            'modDisplayName': 'Arty splash sphere', 'settingsVersion': 1, 'enabled': True, 'column1': [{
                'type': 'CheckBox', 'text': 'Activate on start battle', 'value': True, 'tooltip': '', 'varName': 'activated'
            }, {
                'type': 'CheckBox', 'text': 'Show only in strategic mode', 'value': True, 'tooltip': '', 'varName': 'show_only_strategic_mode'
            }

            ], 'column2': [{
                'type': 'CheckBox', 'text': 'Show only if pressed ALT button', 'value': True, 'tooltip': '', 'varName': 'show_alt_mode'
            }]
        }
        self.arty_ball_gui = GuiSettings('arty_ball', settingsTemplate, self.arty_ball, self.apply_arty_ball)
        self.apply_arty_ball(self.arty_ball_gui.actual_settings)

    def apply_arty_ball(self, settings):
        for setting in settings:
            if setting in self.arty_ball:
                self.arty_ball[setting] = settings[setting]


class GuiSettings(object):
    def __init__(self, name, template, default_settings, function):
        self.saved_settings = None
        self.actual_settings = default_settings
        self.settings_name = name
        self.template = template
        self.default_settings = default_settings
        self.function = function
        self.start()

    def get_settings(self, linkage, settings):
        if linkage == self.settings_name:
            self.function(settings)

    def start(self):
        try:
            self.saved_settings = g_modSettingsAPI.getModSettings(self.settings_name)
            if self.saved_settings:
                self.actual_settings = g_modSettingsAPI.setModTemplate(self.settings_name, self.template, self.get_settings)
                g_modSettingsAPI.registerCallback(self.settings_name, self.get_settings)
            else:
                self.actual_settings = g_modSettingsAPI.setModTemplate(self.settings_name, self.template, self.get_settings)
        except:
            self.actual_settings = self.default_settings

    def update(self, settings):
        g_modSettingsAPI.updateModSettings(self.settings_name, settings)
        g_modSettingsAPI.saveConfig()


class _ArtyBall(object):
    def __init__(self):
        self.model_ball_visible = False
        self.model_ball_pressed_key = False
        self.model_ball = None
        self.model_circle = None
        self.target_id = None
        self.show_time = 0.0
        self.scale_ball = None
        self.player = None

    def clear(self):
        self.player = BigWorld.player()
        if not _config.arty_ball['show_alt_mode']:
            self.model_ball_visible = _config.arty_ball['activated']
        if self.model_ball:
            self.model_ball.clear()
            self.model_ball = None
        self.scale_ball = None

    def start(self):
        self.model_ball = _StaticObjectMarker3D({'path': 'objects/arty_splash.model'}, (0, 0, 0))
        # noinspection PyUnresolvedReferences
        self.model_ball._StaticObjectMarker3D__model.visible = False

    def working(self, function):
        if self.player is None:
            self.model_ball_visible = False
            self.set_visible()
            return

        if not hasattr(self.player, 'vehicleTypeDescriptor') or not hasattr(self.player, 'gunRotator'):
            self.model_ball_visible = False
            self.set_visible()
            return

        if 'HIGH_EXPLOSIVE' not in self.player.vehicleTypeDescriptor.shot['shell']['kind']:
            self.model_ball_visible = False
            self.set_visible()
            return

        if _config.arty_ball['show_only_strategic_mode'] and 'strategic' not in function.mode:
            self.model_ball_visible = False
            self.set_visible()
            return

        if self.model_ball and self.model_ball._StaticObjectMarker3D__model:
            if not self.scale_ball or self.scale_ball is not self.player.vehicleTypeDescriptor.shot['shell']['explosionRadius']:
                self.scale_ball = self.player.vehicleTypeDescriptor.shot['shell']['explosionRadius']
                self.model_ball._StaticObjectMarker3D__model.scale = (self.scale_ball, self.scale_ball, self.scale_ball)
            self.model_ball_visible = True
            if _config.arty_ball['show_alt_mode']:
                self.model_ball_visible = self.model_ball_pressed_key
            self.model_ball._StaticObjectMarker3D__model.position = self.player.gunRotator.markerInfo[0]
            self.set_visible()

    def set_visible(self):
        if self.model_ball and self.model_ball._StaticObjectMarker3D__model:
            if self.model_ball._StaticObjectMarker3D__model.visible is not self.model_ball_visible:
                self.model_ball._StaticObjectMarker3D__model.visible = self.model_ball_visible

    def handle_key(self):
        if _config.arty_ball['show_alt_mode']:
            if self.model_ball:
                if BigWorld.isKeyDown(Keys.KEY_LALT) or BigWorld.isKeyDown(Keys.KEY_RALT):
                    self.model_ball_pressed_key = True
                else:
                    self.model_ball_pressed_key = False


hooked_start_battle = Battle.afterCreate


def hook_start_battle(self):
    hooked_start_battle(self)
    if _config.arty_ball['enabled']:
        _arty_ball.clear()
        _arty_ball.start()


hooked_beforeDelete = Battle.beforeDelete


def hook_before_delete(self):
    hooked_beforeDelete(self)
    if _config.arty_ball['enabled']:
        _arty_ball.clear()


old_updateMarkerPos = Aim.updateMarkerPos


def new_updateMarkerPos(self, position, relaxTime):
    old_updateMarkerPos(self, position, relaxTime)
    if _config.arty_ball['enabled']:
        _arty_ball.working(self)


def inject_handle_key_event(event):
    if g_appLoader.getDefBattleApp():
        if _config.arty_ball['enabled']:
            _arty_ball.handle_key()


_config = _Config()
_arty_ball = _ArtyBall()

Battle.afterCreate = hook_start_battle
Battle.beforeDelete = hook_before_delete
Aim.updateMarkerPos = new_updateMarkerPos
InputHandler.g_instance.onKeyDown += inject_handle_key_event
InputHandler.g_instance.onKeyUp += inject_handle_key_event