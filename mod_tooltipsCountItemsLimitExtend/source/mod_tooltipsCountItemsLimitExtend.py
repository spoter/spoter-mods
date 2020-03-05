# -*- coding: utf-8 -*-
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from gui.shared.tooltips import battle_booster
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from goodies.goodie_constants import GOODIE_STATE

oldCreateStorageDefVO = storage_helpers.createStorageDefVO

def createStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType='', nationFlagIcon='', enabled=True, available=True, contextMenuId='', additionalInfo='', active=GOODIE_STATE.INACTIVE, upgradable=False, upgradeButtonTooltip=''):
    result = oldCreateStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType, nationFlagIcon, enabled, available, contextMenuId, additionalInfo, active, upgradable, upgradeButtonTooltip)
    b = []
    for priced in result['price']['price']:
        b.append((priced[0], priced[1] * result['count']))
    result['price']['price'] = tuple(b)
    return result
storage_helpers.createStorageDefVO = createStorageDefVO
ModuleTooltipBlockConstructor.MAX_INSTALLED_LIST_LEN = 1000
battle_booster._MAX_INSTALLED_LIST_LEN = 1000

print '[LOAD_MOD]:  [mod_tooltipsCountItemsLimitExtend 1.03 (05-03-2020), by spoter, gox]'