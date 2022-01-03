# -*- coding: utf-8 -*-

import BigWorld
import Keys
import Math
# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject
import VehicleGunRotator
from gui import InputHandler
from Avatar import PlayerAvatar
from AvatarInputHandler.aih_global_binding import CTRL_MODE_NAME
# noinspection PyProtectedMember
from tutorial.control.battle.functional import _StaticObjectMarker3D as StaticObjectMarker3D
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.gui_items import Vehicle


class Config(object):
    def __init__(self):
        self.ids = 'artySplash'
        self.version = 'v2.15 (2022-01-03)'
        self.author = 'by spoter'
        self.version_id = 215
        self.buttons = {
            'buttonShowDot'   : [Keys.KEY_C, [Keys.KEY_LALT, Keys.KEY_RALT]],
            'buttonShowSplash': [Keys.KEY_Z, [Keys.KEY_LALT, Keys.KEY_RALT]]
        }
        self.dataDefault = {
            'version'            : self.version_id,
            'enabled'            : True,
            'buttonShowDot'      : self.buttons['buttonShowDot'],
            'buttonShowSplash'   : self.buttons['buttonShowSplash'],
            'showSplashOnDefault': True,
            'showDotOnDefault'   : True,
            'showModeArcade'     : False,
            'showModeSniper'     : True,
            'showModeArty'       : True,
            'modelPathSplash'    : 'objects/artySplash.model',
            'modelPathDot'       : 'objects/artyDot.model'
        }
        self.i18n = {
            'version'                            : self.version_id,
            'UI_setting_name'                    : 'HE Splash',
            'UI_setting_buttonShowDot_text'      : 'Button: show/hide Dot',
            'UI_setting_buttonShowSplash_text'   : 'Button: show/hide Splash',
            'UI_setting_showSplashOnDefault_text': 'Show Splash on default',
            'UI_setting_showDotOnDefault_text'   : 'Show Dot on default',
            'UI_setting_showModeArcade_text'     : 'Arcade mode available',
            'UI_setting_showModeSniper_text'     : 'Sniper mode available',
            'UI_setting_showModeArty_text'       : 'Arty mode available',
            'UI_setting_messageSplashOn'         : 'HE Splash: Show Splash',
            'UI_setting_messageSplashOff'        : 'HE Splash: Hide Splash',
            'UI_setting_messageDotOn'            : 'HE Splash: Show Dot',
            'UI_setting_messageDotOff'           : 'HE Splash: Hide Dot',
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.dataDefault, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_setting_name'],
            'settingsVersion': self.version,
            'enabled'        : self.data['enabled'],
            'column1'        : [
                g_gui.optionCheckBox(*self.getI18nParam('showSplashOnDefault')),
                g_gui.optionCheckBox(*self.getI18nParam('showDotOnDefault')),
                g_gui.optionCheckBox(*self.getI18nParam('showModeArcade')),
                g_gui.optionCheckBox(*self.getI18nParam('showModeSniper')),
                g_gui.optionCheckBox(*self.getI18nParam('showModeArty')),
            ],
            'column2'        : [
                g_gui.optionButton(*self.getI18nParamButton('buttonShowSplash', 'Alt+Z')),
                g_gui.optionButton(*self.getI18nParamButton('buttonShowDot', 'Alt+C')),
            ]
        }

    def getI18nParam(self, name):
        # return varName, value, defaultValue, text, tooltip, defaultValueText
        tooltip = 'UI_setting_%s_tooltip' % name
        tooltip = self.i18n[tooltip] if tooltip in self.i18n else ''
        defaultValueText = 'UI_setting_%s_default' % name
        defaultValueText = self.i18n[defaultValueText] if defaultValueText in self.i18n else '%s' % self.dataDefault[name]
        return name, self.data[name], self.dataDefault[name], self.i18n['UI_setting_%s_text' % name], tooltip, defaultValueText

    def getI18nParamButton(self, name, defaultValueText):
        params = self.getI18nParam(name)
        return params[:5] + (defaultValueText,)

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


# noinspection PyProtectedMember
class ArtyBall(object):
    def __init__(self):
        self.modelSplash = None
        self.modelDot = None
        self.modelSplashCircle = None
        self.modelSplashVisible = False
        self.modelDotVisible = False
        self.modelSplashKeyPressed = False
        self.modelDotKeyPressed = False
        self.scaleSplash = None
        self.player = None

    def startBattle(self):
        InputHandler.g_instance.onKeyDown += self.injectButton
        # InputHandler.g_instance.onKeyUp += self.injectButton
        if config.data['enabled']:
            self.player = BigWorld.player()
            self.modelSplashVisible = config.data['showSplashOnDefault']
            self.modelDotVisible = config.data['showDotOnDefault']
            self.scaleSplash = None
            self.modelSplash = StaticObjectMarker3D({
                'path': config.data['modelPathSplash']
            }, (0, 0, 0))
            self.modelDot = StaticObjectMarker3D({
                'path': config.data['modelPathDot']
            }, (0, 0, 0))
            self.modelDot._StaticObjectMarker3D__model.scale = (0.1, 0.1, 0.1)
            if Vehicle.getVehicleClassTag(self.player.vehicleTypeDescriptor.type.tags) == VEHICLE_CLASS_NAME.SPG:
                self.modelDot._StaticObjectMarker3D__model.scale = (0.5, 0.5, 0.5)
            self.modelSplash._StaticObjectMarker3D__model.visible = False
            self.modelDot._StaticObjectMarker3D__model.visible = False
            # noinspection PyUnresolvedReferences
            self.modelSplashCircle = BigWorld.PyTerrainSelectedArea()
            self.modelSplashCircle.setup('content/Interface/CheckPoint/CheckPoint_yellow_black.model', Math.Vector2(2.0, 2.0), 0.5, 4294967295L)
            self.modelSplash._StaticObjectMarker3D__model.root.attach(self.modelSplashCircle)
            self.modelSplashCircle.enableAccurateCollision(False)

    def stopBattle(self):
        InputHandler.g_instance.onKeyDown -= self.injectButton
        # InputHandler.g_instance.onKeyUp -= self.injectButton
        self.modelSplashVisible = False
        self.modelDotVisible = False
        self.modelSplashKeyPressed = False
        self.modelDotKeyPressed = False
        if self.modelSplash is not None:
            if self.modelSplashCircle.attached:
                self.modelSplash._StaticObjectMarker3D__model.root.detach(self.modelSplashCircle)
            self.modelSplash.clear()
        if self.modelDot is not None:
            self.modelDot.clear()
        self.modelSplash = None
        self.modelDot = None
        self.scaleSplash = None
        self.modelSplashCircle = None

    def working(self):
        if not config.data['enabled'] or self.player is None:
            self.hideVisible()
            return
        if not hasattr(self.player, 'vehicleTypeDescriptor') or not hasattr(self.player, 'gunRotator'):
            self.hideVisible()
            return
        if Vehicle.getVehicleClassTag(self.player.getVehicleDescriptor().type.tags) != VEHICLE_CLASS_NAME.SPG:
            self.hideVisible()
            return
        shell = self.player.getVehicleDescriptor().shot.shell
        if 'HIGH_EXPLOSIVE' not in shell.kind:
            self.hideVisible()
            return
        if not config.data['showModeArcade'] and self.player.inputHandler.ctrlModeName == CTRL_MODE_NAME.ARCADE:
            self.hideVisible()
            return
        if not config.data['showModeSniper'] and self.player.inputHandler.ctrlModeName == CTRL_MODE_NAME.SNIPER:
            self.hideVisible()
            return
        if not config.data['showModeArty'] and self.player.inputHandler.ctrlModeName in [CTRL_MODE_NAME.STRATEGIC, CTRL_MODE_NAME.ARTY]:
            self.hideVisible()
            return

        if self.modelSplash is not None and self.modelSplash._StaticObjectMarker3D__model:
            if not self.scaleSplash or self.scaleSplash != shell.type.explosionRadius:
                self.scaleSplash = shell.type.explosionRadius
                self.modelSplash._StaticObjectMarker3D__model.scale = (self.scaleSplash, self.scaleSplash, self.scaleSplash)
            if not self.modelSplashKeyPressed:
                self.modelSplashVisible = config.data['showSplashOnDefault']
            self.modelSplash._StaticObjectMarker3D__model.position = self.player.gunRotator.markerInfo[0]
            self.modelSplashCircle.updateHeights()
        if self.modelDot is not None and self.modelDot._StaticObjectMarker3D__model:
            if not self.modelDotKeyPressed:
                self.modelDotVisible = config.data['showDotOnDefault']
            self.modelDot._StaticObjectMarker3D__model.position = self.player.gunRotator.markerInfo[0]
        self.setVisible()

    def setVisible(self):
        if self.modelSplash is not None and self.modelSplash._StaticObjectMarker3D__model:
            if self.modelSplash._StaticObjectMarker3D__model.visible != self.modelSplashVisible:
                self.modelSplash._StaticObjectMarker3D__model.visible = self.modelSplashVisible
        if self.modelDot is not None and self.modelDot._StaticObjectMarker3D__model:
            if self.modelDot._StaticObjectMarker3D__model.visible != self.modelDotVisible:
                self.modelDot._StaticObjectMarker3D__model.visible = self.modelDotVisible

    def hideVisible(self):
        if self.modelSplash is not None and self.modelSplash._StaticObjectMarker3D__model and self.modelSplash._StaticObjectMarker3D__model.visible:
            self.modelSplash._StaticObjectMarker3D__model.visible = False
        if self.modelDot is not None and self.modelDot._StaticObjectMarker3D__model and self.modelDot._StaticObjectMarker3D__model.visible:
            self.modelDot._StaticObjectMarker3D__model.visible = False

    @inject.log
    def injectButton(self, event):
        if g_gui.get_key(config.data['buttonShowSplash']) and event.isKeyDown():
            self.modelSplashKeyPressed = True
            self.modelSplashVisible = not self.modelSplashVisible
            message = config.i18n['UI_setting_messageSplashOn'] if self.modelSplashVisible else config.i18n['UI_setting_messageSplashOff']
            color = '#84DE40' if self.modelSplashVisible else '#FFA500'
            inject.message(message, color)
            self.setVisible()

        if g_gui.get_key(config.data['buttonShowDot']) and event.isKeyDown():
            self.modelDotKeyPressed = True
            self.modelDotVisible = not self.modelDotVisible
            message = config.i18n['UI_setting_messageDotOn'] if self.modelDotVisible else config.i18n['UI_setting_messageDotOff']
            color = '#84DE40' if self.modelDotVisible else '#FFA500'
            inject.message(message, color)
            self.setVisible()


config = Config()
artySplash = ArtyBall()


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    artySplash.startBattle()


@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
@inject.log
def hookDestroyGUI(func, *args):
    func(*args)
    artySplash.stopBattle()


@inject.hook(VehicleGunRotator.VehicleGunRotator, '_VehicleGunRotator__updateGunMarker')
@inject.log
def hookUpdateMarkerPos(func, *args):
    func(*args)
    artySplash.working()
