from gui.ClientHangarSpace import g_clientHangarSpaceOverride
import account_helpers
from gui.shared import g_itemsCache
from gui.Scaleform.daapi.view.lobby.hangar import Hangar

def hooked_update_all(self):
    hook_update_all(self)
    if account_helpers.isPremiumAccount(g_itemsCache.items.stats.attributes):
        g_clientHangarSpaceOverride.setPath('spaces/hangar_premium_v2_1')
    else:
        g_clientHangarSpaceOverride.setPath('spaces/hangar_v2_1')

hook_update_all = Hangar._Hangar__updateAll
Hangar._Hangar__updateAll = hooked_update_all

