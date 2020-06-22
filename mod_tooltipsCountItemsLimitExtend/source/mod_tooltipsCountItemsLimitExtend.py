# -*- coding: utf-8 -*-
from CurrentVehicle import g_currentVehicle
from goodies.goodie_constants import GOODIE_STATE
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.shared.items_parameters import formatters
from gui.shared.tooltips import battle_booster
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from gui.shared.tooltips.shell import CommonStatsBlockConstructor
from helpers import getLanguageCode
from helpers.i18n import makeString as _ms
import BigWorld

isRU = 'ru' in getLanguageCode().lower()
modulesText = "[По модулям] <font color='#FFA500'>{}</font>" if isRU else "[To modules] <font color='#FFA500'>{}</font>"
modulesTextTooltip = " [По модулям]" if isRU else " [To modules]"
modulesTextTooltipBattle = "%s, <font color='#FFA500'>[По модулям] %s</font>" if isRU else "%s, <font color='#FFA500'>[To modules] %s</font>"


def createStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType='', nationFlagIcon='', enabled=True, available=True, contextMenuId='', additionalInfo='', active=GOODIE_STATE.INACTIVE, upgradable=False, upgradeButtonTooltip=''):
    result = oldCreateStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType, nationFlagIcon, enabled, available, contextMenuId, additionalInfo, active, upgradable, upgradeButtonTooltip)
    b = []
    for priced in result['price']['price']:
        b.append((priced[0], priced[1] * result['count']))
    result['price']['price'] = tuple(b)
    return result


def makeShellTooltip(self, descriptor, piercingPower):
    player = BigWorld.player()
    result = oldMakeShellTooltip(self, descriptor, piercingPower)
    damage = str(int(descriptor.damage[0]))
    damageModule = modulesTextTooltipBattle % (damage, int(descriptor.damage[1]))
    shellSpeed = ''
    for shot in player.vehicleTypeDescriptor.gun.shots:
        if descriptor.id == shot.shell.id:
            shellSpeed = "\n%s<font color='#1CC6D9'>%s</font>" % (_ms('#menu:moduleInfo/params/flyDelayRange'), int(shot.speed))
    return result.replace(damage, damageModule + shellSpeed)


def getFormattedParamsList(descriptor, parameters, excludeRelative=False):
    params = oldGetFormattedParamsList(descriptor, parameters, excludeRelative)
    result = []
    for param in params:
        if 'damage' in param and 'flyDelayRange' not in param:
            for shot in g_currentVehicle.item.descriptor.gun.shots:
                if descriptor.id == shot.shell.id:
                    result.append(('flyDelayRange', "<font color='#1CC6D9'>%s</font>" % int(shot.speed)))
            result.append(param)
            result.append(('avgDamage', modulesText.format(int(descriptor.damage[1]))))
        else:
            result.append(param)
    return result


def construct(self):
    result = old_construct(self)
    block = []

    for pack in result:
        if 'name' in pack['data'] and _ms('#menu:moduleInfo/params/' + 'damage') in pack['data']['name']:
            shell = self.shell
            for shot in g_currentVehicle.item.descriptor.gun.shots:
                if shell.descriptor.id == shot.shell.id:
                    block.append(self._packParameterBlock(_ms('#menu:moduleInfo/params/flyDelayRange'), "<font color='#1CC6D9'>%s</font>" % int(shot.speed), _ms(formatters.measureUnitsForParameter('flyDelayRange'))))
            block.append(pack)
            block.append(self._packParameterBlock(_ms('#menu:moduleInfo/params/avgDamage'), "<font color='#FFA500'>%s</font>" % int(shell.descriptor.damage[1]), _ms(formatters.measureUnitsForParameter('avgDamage')) + modulesTextTooltip))
        else:
            block.append(pack)
    return block


oldCreateStorageDefVO = storage_helpers.createStorageDefVO
oldMakeShellTooltip = ConsumablesPanel._ConsumablesPanel__makeShellTooltip
oldGetFormattedParamsList = formatters.getFormattedParamsList
old_construct = CommonStatsBlockConstructor.construct

ModuleTooltipBlockConstructor.MAX_INSTALLED_LIST_LEN = 1000
battle_booster._MAX_INSTALLED_LIST_LEN = 1000
storage_helpers.createStorageDefVO = createStorageDefVO
ConsumablesPanel._ConsumablesPanel__makeShellTooltip = makeShellTooltip
formatters.getFormattedParamsList = getFormattedParamsList
CommonStatsBlockConstructor.construct = construct

print '[LOAD_MOD]:  [mod_tooltipsCountItemsLimitExtend 1.05 (22-06-2020), by spoter, gox]'
