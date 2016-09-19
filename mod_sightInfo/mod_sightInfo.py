# -*- coding: utf-8 -*-
from Avatar import PlayerAvatar
from gui.Scaleform.daapi.view.battle.shared.crosshair_panel import createAmmoSettings
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import SHELL_SET_RESULT

class SightInfo(object):
    def __init__(self):
        self.isReloading = False
        self.quantity = None
        self.quantityInClip = None
        self.guiSettings = None
        self.timeData = (0, 0, 0)

    def start(self):
        ctrl = g_sessionProvider.shared.ammo
        if ctrl is not None:
            self.setup(ctrl)
            ctrl.onGunReloadTimeSet += self.setReloadingState
            ctrl.onShellsUpdated += self.onShellsUpdated
            ctrl.onCurrentShellChanged += self.onCurrentShellChanged

    def stop(self):
        ctrl = g_sessionProvider.shared.ammo
        if ctrl is not None:
            ctrl.onGunReloadTimeSet -= self.setReloadingState
            ctrl.onShellsUpdated -= self.onShellsUpdated
            ctrl.onCurrentShellChanged -= self.onCurrentShellChanged

    def setup(self, ctrl):
        self.guiSettings = createAmmoSettings(ctrl.getGunSettings())
        self.quantity, self.quantityInClip = ctrl.getCurrentShells()
        self.isReloading = ctrl.getGunReloadingState()
        print 'quantity: %s, quantityInClip: %s, isReloading: %s' % (self.quantity, self.quantityInClip, self.isReloading)

    def setReloadingState(self, _, state):
        self.timeData = (state.getActualValue(), state.getBaseValue(), state.getTimePassed())
        self.isReloading = state.isReloading()
        print 'setReloadingState timeData: %s, isReloading: %s' % (self.timeData, self.isReloading)

    def onShellsUpdated(self, _, quantity, quantityInClip, result):
        if not result & SHELL_SET_RESULT.CURRENT:
            return
        isLow, state = self.guiSettings.getState(quantity, quantityInClip)
        print 'onShellsUpdated quantity: %s, quantityInClip: %s, isLow: %s, state: %s, CASSETTE_RELOAD: %s' % (quantity, quantityInClip, isLow, state, result & SHELL_SET_RESULT.CASSETTE_RELOAD > 0)

    def onCurrentShellChanged(self, _):
        ctrl = g_sessionProvider.shared.ammo
        if ctrl is not None:
            self.quantity, self.quantityInClip = ctrl.getCurrentShells()
            isLow, state = self.guiSettings.getState(self.quantity, self.quantityInClip)
            print 'onCurrentShellChanged quantity: %s, quantityInClip: %s, isLow: %s, state: %s, CASSETTE_RELOAD: %s' % (self.quantity, self.quantityInClip, isLow, state, False)

def hookStartGUI(self):
    hookedStartGUI(self)
    sightInfo.start()

def hookDestroyGUI(self):
    hookedDestroyGUI(self)
    sightInfo.stop()

sightInfo = SightInfo()

# noinspection PyProtectedMember
hookedStartGUI = PlayerAvatar._PlayerAvatar__startGUI
# noinspection PyProtectedMember
hookedDestroyGUI = PlayerAvatar._PlayerAvatar__destroyGUI

PlayerAvatar._PlayerAvatar__startGUI = hookStartGUI
PlayerAvatar._PlayerAvatar__destroyGUI = hookDestroyGUI
print '[LOAD_MOD]:  [%s %s, %s]' % ('mod_sightInfo', '19.09.2016', 'by spoter')
