# -*- coding: utf-8 -*-
import BattleReplay
import BigWorld
from aih_constants import GUN_MARKER_TYPE
from AvatarInputHandler.aih_global_binding import CTRL_MODE_NAME
from AvatarInputHandler.control_modes import ArcadeControlMode, getShotTargetInfo
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID as _VIEW_ID
from gui.Scaleform.daapi.view.battle.shared.crosshair.gm_components import DefaultGunMarkerComponent
from gui.Scaleform.daapi.view.battle.shared.crosshair.gm_factory import _OptionalMarkersFactory
from gui.Scaleform.genConsts.GUN_MARKER_VIEW_CONSTANTS import GUN_MARKER_VIEW_CONSTANTS as _CONSTANTS
from gui.battle_control import avatar_getter


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
                vehicle = BigWorld.player().getVehicleAttached()
                hitPoint, _ = getShotTargetInfo(vehicle, pos, BigWorld.player().gunRotator)
                if vehicle.position.distTo(hitPoint) < vehicle.position.distTo(pos):
                    pos = hitPoint
        self._aih.onControlModeChanged(mode, preferredPos=pos, aimingMode=self._aimingMode, saveZoom=not bByScroll, equipmentID=equipmentID)
        return
    else:
        return hookActivateAlternateMode(self, pos, bByScroll)


# noinspection PyUnusedLocal
def create(self):
    if self._vehicleInfo.isSPG():
        return (self._createMarker(DefaultGunMarkerComponent, _VIEW_ID.SNIPER, GUN_MARKER_TYPE.CLIENT, self._getMarkerDataProvider(GUN_MARKER_TYPE.CLIENT), _CONSTANTS.SNIPER_GUN_MARKER_NAME),)
    return (self._createVideoMarker(),) if self._markersInfo.isEnabledInVideoMode else ()



# noinspection PyProtectedMember
hookActivateAlternateMode = ArcadeControlMode._ArcadeControlMode__activateAlternateMode
ArcadeControlMode._ArcadeControlMode__activateAlternateMode = hookedActivateAlternateMode
_OptionalMarkersFactory.create = create

print '[LOAD_MOD]:  [sniperByScroll 2.06 (11-10-2019), by Kainenger, spoter, angelsoft]'
