# -*- coding: utf-8 -*-
from gui.Scaleform.daapi.view.lobby.missions.personal.personal_missions_map_view import PersonalMissionsMapView
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES

def hookedGetQuestStatusData(self, vehType, quest):
    data = hookGetQuestStatusData(self, vehType, quest)
    if data['state'] == PERSONAL_MISSIONS_ALIASES.REGION_COMPLETED:
        data['state'] = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_STATE
    return data

hookGetQuestStatusData = PersonalMissionsMapView._PersonalMissionsMapView__getQuestStatusData
PersonalMissionsMapView._PersonalMissionsMapView__getQuestStatusData = hookedGetQuestStatusData

print '[LOAD_MOD]:  [mod_personalMissionColored 1.01 (26-11-2017), by spoter]'
