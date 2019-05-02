# -*- coding: utf-8 -*-

import BigWorld
import Keys
from gui.mods.mod_mods_gui import g_gui, inject
import VehicleGunRotator
from gui import InputHandler
from Avatar import PlayerAvatar
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME
# noinspection PyProtectedMember
from tutorial.control.battle.functional import _StaticObjectMarker3D as StaticObjectMarker3D
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.gui_items import Vehicle


class Config(object):
    def __init__(self):
        self.ids = 'artySplash'
        self.version = 'v2.10 (2019-05-02)'
        self.author = 'by spoter'
        self.version_id = 210
        self.buttons = {
            'buttonShowDot'   : [Keys.KEY_C, [Keys.KEY_LALT, Keys.KEY_RALT]],
            'buttonShowSplash': [Keys.KEY_Z, [Keys.KEY_LALT, Keys.KEY_RALT]]
        }
        self.data = {
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
            'version'                                  : self.version_id,
            'UI_artySplash_name'                       : 'HE Splash',
            'UI_artySplash_buttonShowDot_text'         : 'Button: show\hide Dot',
            'UI_artySplash_buttonShowDot_tooltip'      : '',
            'UI_artySplash_buttonShowSplash_text'      : 'Button: show\hide Splash',
            'UI_artySplash_buttonShowSplash_tooltip'   : '',
            'UI_artySplash_showSplashOnDefault_text'   : 'Show Splash on default',
            'UI_artySplash_showSplashOnDefault_tooltip': '',
            'UI_artySplash_showDotOnDefault_text'      : 'Show Dot on default',
            'UI_artySplash_showDotOnDefault_tooltip'   : '',
            'UI_artySplash_showModeArcade_text'        : 'Arcade mode available',
            'UI_artySplash_showModeArcade_tooltip'     : '',
            'UI_artySplash_showModeSniper_text'        : 'Sniper mode available',
            'UI_artySplash_showModeSniper_tooltip'     : '',
            'UI_artySplash_showModeArty_text'          : 'Arty mode available',
            'UI_artySplash_showModeArty_tooltip'       : '',
            'UI_artySplash_messageSplashOn'            : 'HE Splash: Show Splash',
            'UI_artySplash_messageSplashOff'           : 'HE Splash: Hide Splash',
            'UI_artySplash_messageDotOn'               : 'HE Splash: Show Dot',
            'UI_artySplash_messageDotOff'              : 'HE Splash: Hide Dot'
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_artySplash_name'],
            'settingsVersion': self.version,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_artySplash_showSplashOnDefault_text'],
                'value'  : self.data['showSplashOnDefault'],
                'tooltip': self.i18n['UI_artySplash_showSplashOnDefault_tooltip'],
                'varName': 'showSplashOnDefault'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_artySplash_showDotOnDefault_text'],
                'value'  : self.data['showDotOnDefault'],
                'tooltip': self.i18n['UI_artySplash_showDotOnDefault_tooltip'],
                'varName': 'showDotOnDefault'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_artySplash_showModeArcade_text'],
                'value'  : self.data['showModeArcade'],
                'tooltip': self.i18n['UI_artySplash_showModeArcade_tooltip'],
                'varName': 'showModeArcade'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_artySplash_showModeSniper_text'],
                'value'  : self.data['showModeSniper'],
                'tooltip': self.i18n['UI_artySplash_showModeSniper_tooltip'],
                'varName': 'showModeSniper'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_artySplash_showModeArty_text'],
                'value'  : self.data['showModeArty'],
                'tooltip': self.i18n['UI_artySplash_showModeArty_tooltip'],
                'varName': 'showModeArty'
            }],
            'column2'        : [{
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_artySplash_buttonShowSplash_text'],
                'tooltip'     : self.i18n['UI_artySplash_buttonShowSplash_tooltip'],
                'value'       : self.data['buttonShowSplash'],
                'defaultValue': self.buttons['buttonShowSplash'],
                'varName'     : 'buttonShowSplash'
            }, {
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_artySplash_buttonShowDot_text'],
                'tooltip'     : self.i18n['UI_artySplash_buttonShowDot_tooltip'],
                'value'       : self.data['buttonShowDot'],
                'defaultValue': self.buttons['buttonShowDot'],
                'varName'     : 'buttonShowDot'
            }]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


# noinspection PyProtectedMember
class ArtyBall(object):
    def __init__(self):
        self.modelSplash = None
        self.modelDot = None
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

    def stopBattle(self):
        InputHandler.g_instance.onKeyDown -= self.injectButton
        # InputHandler.g_instance.onKeyUp -= self.injectButton
        self.modelSplashVisible = False
        self.modelDotVisible = False
        self.modelSplashKeyPressed = False
        self.modelDotKeyPressed = False
        if self.modelSplash is not None:
            self.modelSplash.clear()
        if self.modelDot is not None:
            self.modelDot.clear()
        self.modelSplash = None
        self.modelDot = None
        self.scaleSplash = None

    def working(self):
        if not config.data['enabled'] or self.player is None:
            self.hideVisible()
            return
        if not hasattr(self.player, 'vehicleTypeDescriptor') or not hasattr(self.player, 'gunRotator'):
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
            message = config.i18n['UI_artySplash_messageSplashOn'] if self.modelSplashVisible else config.i18n['UI_artySplash_messageSplashOff']
            color = '#84DE40' if self.modelSplashVisible else '#FFA500'
            inject.message(message, color)
            self.setVisible()

        if g_gui.get_key(config.data['buttonShowDot']) and event.isKeyDown():
            self.modelDotKeyPressed = True
            self.modelDotVisible = not self.modelDotVisible
            message = config.i18n['UI_artySplash_messageDotOn'] if self.modelDotVisible else config.i18n['UI_artySplash_messageDotOff']
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
