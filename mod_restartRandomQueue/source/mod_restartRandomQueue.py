# -*- coding: utf-8 -*-
import BigWorld
import constants
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.lobby.battle_queue import QueueProvider
from gui.prb_control import prbEntityProperty
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from CurrentVehicle import g_currentVehicle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.prb_control.dispatcher import g_prbLoader
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items

class Mod:
    lobbyContext = dependency.descriptor(ILobbyContext)
    def __init__(self):
        g_playerEvents.onQueueInfoReceived += self.processQueueInfo
        self._count = 0
        self._exitCallback = None

    @prbEntityProperty
    def prbEntity(self):
        return None

    def processQueueInfo(self, _):
        if self.prbEntity is None:
            self._count = 0
            self._exitCallback = None
            return
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'requestQueueInfo'):
            prbDispatcher = g_prbLoader.getDispatcher()
            if prbDispatcher is not None and self.lobbyContext.isFightButtonPressPossible() and self.prbEntity.getQueueType() == constants.ARENA_GUI_TYPE.RANDOM and self._count:
                state = prbDispatcher.getFunctionalState()
                if battle_selector_items.getItems().update(state).isInSquad(state):
                    return
                vehicle = g_currentVehicle.item
                if vehicle is not None and vehicle.type != VEHICLE_CLASS_NAME.SPG:
                    self.prbEntity.exitFromQueue()
                    self.restartEnqueueRandom()
        self._count += 1

    def restartEnqueueRandom(self):
        if not self.prbEntity:
            return
        if not self.prbEntity.isInQueue():
            self.prbEntity.exitFromQueue()
            return
        self._exitCallback = BigWorld.callback(0.7, self.restartEnqueueRandom)

    def start(self):
        self._count = 0
        self._exitCallback = None


mod = Mod()


def newStart(self):
    oldStart(self)
    mod.start()


oldStart = QueueProvider.start
QueueProvider.start = newStart

VERSION_MOD = 'v1.12 (2025-02-24)'
print '[LOAD_MOD]:  [mod_restartRandomQueue {}, by spoter]'.format(VERSION_MOD)
