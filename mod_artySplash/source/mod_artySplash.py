# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
import BigWorld
# noinspection PyUnresolvedReferences
import Math
# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

import Keys
import VehicleGunRotator
from Avatar import PlayerAvatar
from AvatarInputHandler.aih_global_binding import CTRL_MODE_NAME
from gui import InputHandler
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME

OVER_TERRAIN_HEIGHT = 0.5
MARKER_HEIGHT = 5.0
COLOR_WHITE = 4294967295L

# Removed in wot ver. 1.26.00
class _StaticWorldObjectMarker3D(object):
    def __init__(self, data, position):
        self.__path = data.get('path')
        offset = data.get('offset', Math.Vector3(0, 0, 0))
        self.model = None
        self.__isMarkerVisible = True
        self.modelOwner = None
        self.__destroyed = False
        if self.__path is not None:
            modelPosition = Math.Vector3(position[:]) + offset
            refs = BigWorld.loadResourceListFG([self.__path])
            self.__onModelLoaded(refs, modelPosition)

    def addMarkerModel(self):
        if self.model is None or self.modelOwner is not None:
            return
        self.modelOwner = BigWorld.player()
        self.modelOwner.addModel(self.model)

    def clear(self):
        self.setVisible(False)
        self.model = None
        self.__destroyed = True

    def setVisible(self, isVisible):
        if not self.__isMarkerVisible and isVisible:
            self.__isMarkerVisible = True
            self.addMarkerModel()
        elif not isVisible:
            self.__isMarkerVisible = False
            if self.modelOwner is not None and not self.modelOwner.isDestroyed:
                self.modelOwner.delModel(self.model)
            self.modelOwner = None

    def __onModelLoaded(self, refs, position):
        if self.__destroyed:
            return
        if self.__path not in refs.failedIDs:
            self.model = refs[self.__path]
            self.model.position = position
            self.model.castsShadow = False
            if self.__isMarkerVisible:
                self.addMarkerModel()


class Config(object):
    def __init__(self):
        self.ids = 'artySplash'
        self.version = 'v2.17 (2025-10-16)'
        self.author = 'by spoter'
        self.version_id = 217
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
        print('[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author))

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
        if config.data['enabled']:
            self.player = BigWorld.player()
            self.modelSplashVisible = config.data['showSplashOnDefault']
            self.modelDotVisible = config.data['showDotOnDefault']
            self.scaleSplash = None
            self.modelSplash = _StaticWorldObjectMarker3D({'path': config.data['modelPathSplash']}, (0, 0, 0))
            self.modelDot = _StaticWorldObjectMarker3D({'path': config.data['modelPathDot']}, (0, 0, 0))
            self.modelDot.model.scale = (0.1, 0.1, 0.1)
            if Vehicle.getVehicleClassTag(self.player.vehicleTypeDescriptor.type.tags) == VEHICLE_CLASS_NAME.SPG:
                self.modelDot.model.scale = (0.5, 0.5, 0.5)
            self.modelSplash.model.visible = False
            self.modelDot.model.visible = False
            self.modelSplashCircle = BigWorld.PyTerrainSelectedArea()
            self.modelSplashCircle.setup('content/Interface/CheckPoint/CheckPoint_white.visual', Math.Vector2(2.0, 2.0), OVER_TERRAIN_HEIGHT, COLOR_WHITE, BigWorld.player().spaceID)
            self.modelSplash.model.root.attach(self.modelSplashCircle)
            self.modelSplashCircle.enableAccurateCollision(True)
            self.modelSplashCircle.enableWaterCollision(True)
            self.modelSplashCircle.setCutOffDistance(MARKER_HEIGHT)


    def stopBattle(self):
        InputHandler.g_instance.onKeyDown -= self.injectButton
        self.modelSplashVisible = False
        self.modelDotVisible = False
        self.modelSplashKeyPressed = False
        self.modelDotKeyPressed = False
        if self.modelSplash is not None:
            if self.modelSplashCircle.attached:
                self.modelSplash.model.root.detach(self.modelSplashCircle)
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
        explosionRadius = shell.type.explosionRadius  # shell.type.explosionRadius
        stunRadius = 0
        if shell.hasStun:
            stun = shell.stun
            stunRadius = stun.stunRadius
        if stunRadius > explosionRadius:
            explosionRadius = stunRadius
        if self.modelSplash is not None and self.modelSplash.model:
            if not self.scaleSplash or self.scaleSplash != explosionRadius:
                self.scaleSplash = explosionRadius
                self.modelSplash.model.scale = (self.scaleSplash, self.scaleSplash, self.scaleSplash)
            if not self.modelSplashKeyPressed:
                self.modelSplashVisible = config.data['showSplashOnDefault']
            self.modelSplash.model.position = self.player.gunRotator.markerInfo[0]
            self.modelSplashCircle.updateHeights()
        if self.modelDot is not None and self.modelDot.model:
            if not self.modelDotKeyPressed:
                self.modelDotVisible = config.data['showDotOnDefault']
            self.modelDot.model.position = self.player.gunRotator.markerInfo[0]
        self.setVisible()

    def setVisible(self):
        if self.modelSplash is not None and self.modelSplash.model:
            if self.modelSplash.model.visible != self.modelSplashVisible:
                self.modelSplash.model.visible = self.modelSplashVisible
        if self.modelDot is not None and self.modelDot.model:
            if self.modelDot.model.visible != self.modelDotVisible:
                self.modelDot.model.visible = self.modelDotVisible

    def hideVisible(self):
        if self.modelSplash is not None and self.modelSplash.model and self.modelSplash.model.visible:
            self.modelSplash.model.visible = False
        if self.modelDot is not None and self.modelDot.model and self.modelDot.model.visible:
            self.modelDot.model.visible = False

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
