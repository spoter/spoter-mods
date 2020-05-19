# -*- coding: utf-8 -*-
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from gui.shared.tooltips import battle_booster
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from goodies.goodie_constants import GOODIE_STATE
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
oldCreateStorageDefVO = storage_helpers.createStorageDefVO

def createStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType='', nationFlagIcon='', enabled=True, available=True, contextMenuId='', additionalInfo='', active=GOODIE_STATE.INACTIVE, upgradable=False, upgradeButtonTooltip=''):
    result = oldCreateStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType, nationFlagIcon, enabled, available, contextMenuId, additionalInfo, active, upgradable, upgradeButtonTooltip)
    b = []
    for priced in result['price']['price']:
        b.append((priced[0], priced[1] * result['count']))
    result['price']['price'] = tuple(b)
    return result
storage_helpers.createStorageDefVO = createStorageDefVO

oldMakeShellTooltip = ConsumablesPanel._ConsumablesPanel__makeShellTooltip

def makeShellTooltip(self, descriptor, piercingPower):
    result = oldMakeShellTooltip(self, descriptor, piercingPower)
    return result.replace(str(int(descriptor.damage[0])), '%s, to modules %s' %(str(int(descriptor.damage[0])), str(int(descriptor.damage[1]))))
ConsumablesPanel._ConsumablesPanel__makeShellTooltip = makeShellTooltip

ModuleTooltipBlockConstructor.MAX_INSTALLED_LIST_LEN = 1000
battle_booster._MAX_INSTALLED_LIST_LEN = 1000

print '[LOAD_MOD]:  [mod_tooltipsCountItemsLimitExtend 1.04 (19-05-2020), by spoter, gox]'