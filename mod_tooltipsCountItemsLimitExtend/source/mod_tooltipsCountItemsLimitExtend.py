# -*- coding: utf-8 -*-
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from gui.shared.tooltips import battle_booster
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers


def createStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType='', nationFlagIcon='', enabled=True, contextMenuId=''):
    b = []
    for priced in price['price']:
        b.append((priced[0], priced[1] * count))
    price['price'] = tuple(b)
    return {'id': itemID,
     'title': title,
     'description': description,
     'count': count,
     'price': price,
     'image': image,
     'imageAlt': imageAlt,
     'type': itemType,
     'nationFlagIcon': nationFlagIcon,
     'enabled': enabled,
     'contextMenuId': contextMenuId}
storage_helpers.createStorageDefVO = createStorageDefVO
ModuleTooltipBlockConstructor.MAX_INSTALLED_LIST_LEN = 1000
battle_booster._MAX_INSTALLED_LIST_LEN = 1000

print '[LOAD_MOD]:  [mod_tooltipsCountItemsLimitExtend 1.02 (18-08-2019), by spoter, gox]'