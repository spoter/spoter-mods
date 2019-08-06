# -*- coding: utf-8 -*-
import BattleReplay
import BigWorld
from aih_constants import GUN_MARKER_TYPE
from AvatarInputHandler.aih_global_binding import CTRL_MODE_NAME
from AvatarInputHandler.control_modes import ArcadeControlMode
from gui.Scaleform.daapi.view.battle.shared.crosshair import gm_components as _components
# noinspection PyProtectedMember
from gui.Scaleform.daapi.view.battle.shared.crosshair.gm_factory import _OptionalMarkersFactory
from gui.Scaleform.genConsts.GUN_MARKER_VIEW_CONSTANTS import GUN_MARKER_VIEW_CONSTANTS as _CONSTANTS
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID as _VIEW_ID


def hookedActivateAlternateMode(self, pos=None, bByScroll=False):
    ownVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
    if ownVehicle is not None and ownVehicle.isStarted and avatar_getter.isVehicleBarrelUnderWater() or BigWorld.player().isGunLocked:
        return
    elif self._aih.isSPG and bByScroll:
        self._cam.update(0, 0, 0, False, False)
        if BattleReplay.isPlaying() and BigWorld.player().isGunLocked:
            mode = BattleReplay.g_replayCtrl.getControlMode()
            pos = BattleReplay.g_replayCtrl.getGunMarkerPos()
            equipmentID = BattleReplay.g_replayCtrl.getEquipmentId()
        else:
            mode = CTRL_MODE_NAME.SNIPER
            equipmentID = None
            if pos is None:
                pos = self.camera.aimingSystem.getDesiredShotPoint()
                if pos is None:
                    pos = self._gunMarker.getPosition()
        self._aih.onControlModeChanged(mode, preferredPos=pos, aimingMode=self._aimingMode, saveZoom=not bByScroll, equipmentID=equipmentID)
        return
    else:
        return hookActivateAlternateMode(self, pos, bByScroll)


# noinspection PyUnusedLocal
def create(self, markersInfo, vehicleInfo, components=None):
    if vehicleInfo.isSPG():
        dataProvider = markersInfo.serverMarkerDataProvider if markersInfo.isServerMarkerActivated else markersInfo.clientMarkerDataProvider
        markerType = GUN_MARKER_TYPE.SERVER if markersInfo.isServerMarkerActivated else GUN_MARKER_TYPE.CLIENT
        component = self._findComponent(markerType, dataProvider, components, _CONSTANTS.SNIPER_GUN_MARKER_NAME)
        if component is None:
            component = _components.DefaultGunMarkerComponent(markerType, _VIEW_ID.SNIPER, _CONSTANTS.SNIPER_GUN_MARKER_NAME, _CONSTANTS.GUN_MARKER_LINKAGE, dataProvider)
        return component,
    elif markersInfo.isEnabledInVideoMode:
        return self._createVideoMarker(GUN_MARKER_TYPE.CLIENT, markersInfo.clientMarkerDataProvider, components),
    else:
        return tuple()


# noinspection PyProtectedMember
hookActivateAlternateMode = ArcadeControlMode._ArcadeControlMode__activateAlternateMode
ArcadeControlMode._ArcadeControlMode__activateAlternateMode = hookedActivateAlternateMode
_OptionalMarkersFactory.create = create

print '[LOAD_MOD]:  [sniperByScroll 2.05 (06-08-2019), by Kainenger, spoter, angelsoft]'
