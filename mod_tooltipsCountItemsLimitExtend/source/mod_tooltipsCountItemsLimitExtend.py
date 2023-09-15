# -*- coding: utf-8 -*-
import math

from CurrentVehicle import g_currentVehicle
from goodies.goodie_constants import GOODIE_STATE
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import formatters, functions
from gui.shared.items_parameters import params
from gui.shared.tooltips import formatters as formatters_tooltips
from gui.shared.tooltips import module
from gui.shared.tooltips.common import _CurrencySetting
from gui.shared.tooltips.module import CommonStatsBlockConstructor as CommonStatsBlockConstructor1
from gui.shared.tooltips.module import StatusBlockConstructor
from gui.shared.tooltips.shell import CommonStatsBlockConstructor
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import getLanguageCode
from helpers.i18n import makeString as p__makeString

# вентилятор и т.д.
#from gui.shared.tooltips.module import OptDeviceEffectsBlockConstructor
# аптечки
#from gui.shared.tooltips.module import EffectsBlockConstructor
# оборудка в исследованиях
#from gui.shared.tooltips.module import CommonStatsBlockConstructor

# стоимость одной текущей оборудки
#from gui.shared.tooltips.module import PriceBlockConstructor

# где на танках находится и сколько на складе лежит
#from gui.shared.tooltips.module import InventoryBlockConstructor



i18n = {
    'UI_TOOLTIPS_StabBonus_ColorPositive'      : '#28F09C',
    'UI_TOOLTIPS_StabBonus_ColorNeutral'       : '#7CD606',
    'UI_TOOLTIPS_Stabilization_Color'          : '#FFD700',
    'UI_TOOLTIPS_MovementSpeed_Color'          : '#8378FC',
    'UI_TOOLTIPS_RotatingVehicle_Color'        : '#1CC6D9',
    'UI_TOOLTIPS_RotatingTurret_Color'         : '#F200DA',
    'UI_TOOLTIPS_StabBonus_Text'               : 'Stabilization bonus',
    'UI_TOOLTIPS_Stabilization_Text'           : 'Total stabilization',
    'UI_TOOLTIPS_MovementSpeed_Text'           : 'When maximum speed',
    'UI_TOOLTIPS_RotatingVehicle_Text'         : 'When turning vehicle',
    'UI_TOOLTIPS_RotatingTurret_Text'          : 'When turning turret',
    'UI_TOOLTIPS_modulesText_Text'             : "[To modules] <font color='#FFA500'>{}</font>",
    'UI_TOOLTIPS_modulesTextTooltip_Text'      : " [To modules]",
    'UI_TOOLTIPS_modulesTextTooltipBattle_Text': "%s, <font color='#FFA500'>[To modules] %s</font>",
    'UI_TOOLTIPS_tracerSpeedText_Text'         : '[Tracer]',
    'UI_TOOLTIPS_shellSpeedText_Text'          : '[Shell]',
    'UI_TOOLTIPS_speedMsec_Text'               : 'm/sec.',
}
if 'ru' in getLanguageCode().lower():
    i18n = {
        'UI_TOOLTIPS_StabBonus_Text'               : 'Бонус стабилизации',
        'UI_TOOLTIPS_StabBonus_ColorPositive'      : '#28F09C',
        'UI_TOOLTIPS_StabBonus_ColorNeutral'       : '#7CD606',
        'UI_TOOLTIPS_Stabilization_Text'           : 'Общая стабилизация',
        'UI_TOOLTIPS_Stabilization_Color'          : '#FFD700',
        'UI_TOOLTIPS_MovementSpeed_Text'           : 'при макс. скорости',
        'UI_TOOLTIPS_MovementSpeed_Color'          : '#8378FC',
        'UI_TOOLTIPS_RotatingVehicle_Text'         : 'при развороте танка',
        'UI_TOOLTIPS_RotatingVehicle_Color'        : '#1CC6D9',
        'UI_TOOLTIPS_RotatingTurret_Text'          : 'при повороте башни',
        'UI_TOOLTIPS_RotatingTurret_Color'         : '#F200DA',
        'UI_TOOLTIPS_modulesText_Text'             : "[По модулям] <font color='#FFA500'>{}</font>",
        'UI_TOOLTIPS_modulesTextTooltip_Text'      : " [По модулям]",
        'UI_TOOLTIPS_modulesTextTooltipBattle_Text': "%s, <font color='#FFA500'>[По модулям] %s</font>",
        'UI_TOOLTIPS_tracerSpeedText_Text'         : '[Трассер]',
        'UI_TOOLTIPS_shellSpeedText_Text'          : '[Снаряд]',
        'UI_TOOLTIPS_speedMsec_Text'               : 'м/сек.',
    }
if 'de' in getLanguageCode().lower():
    i18n = {
    'UI_TOOLTIPS_StabBonus_ColorPositive'      : '#28F09C',
    'UI_TOOLTIPS_StabBonus_ColorNeutral'       : '#7CD606',
    'UI_TOOLTIPS_Stabilization_Color'          : '#FFD700',
    'UI_TOOLTIPS_MovementSpeed_Color'          : '#8378FC',
    'UI_TOOLTIPS_RotatingVehicle_Color'        : '#1CC6D9',
    'UI_TOOLTIPS_RotatingTurret_Color'         : '#F200DA',
    'UI_TOOLTIPS_StabBonus_Text'               : 'Stabilierungs Bonus',
    'UI_TOOLTIPS_Stabilization_Text'           : 'Totale Stabilisierung',
    'UI_TOOLTIPS_MovementSpeed_Text'           : 'bei max. Geschwindigkeit',
    'UI_TOOLTIPS_RotatingVehicle_Text'         : 'bei Wannendrehung',
    'UI_TOOLTIPS_RotatingTurret_Text'          : 'bei Turmdrehung',
    'UI_TOOLTIPS_modulesText_Text'             : "[An Modulen] <font color='#FFA500'>{}</font>",
    'UI_TOOLTIPS_modulesTextTooltip_Text'      : " [An Modulen]",
    'UI_TOOLTIPS_modulesTextTooltipBattle_Text': "%s, <font color='#FFA500'>[An Modulen] %s</font>",
    'UI_TOOLTIPS_tracerSpeedText_Text'         : '[Flugbahn]',
    'UI_TOOLTIPS_shellSpeedText_Text'          : '[Shell]',
    'UI_TOOLTIPS_speedMsec_Text'               : 'm/sek.',
}
if 'es' in getLanguageCode().lower():
    i18n = {
        'UI_TOOLTIPS_StabBonus_ColorPositive'      : '#28F09C',
        'UI_TOOLTIPS_StabBonus_ColorNeutral'       : '#7CD606',
        'UI_TOOLTIPS_Stabilization_Color'          : '#FFD700',
        'UI_TOOLTIPS_MovementSpeed_Color'          : '#8378FC',
        'UI_TOOLTIPS_RotatingVehicle_Color'        : '#1CC6D9',
        'UI_TOOLTIPS_RotatingTurret_Color'         : '#F200DA',
        'UI_TOOLTIPS_StabBonus_Text'               : 'Bono de estabilizacion',
        'UI_TOOLTIPS_Stabilization_Text'           : 'Estabilizacion total',
        'UI_TOOLTIPS_MovementSpeed_Text'           : 'Cuando velocidad max',
        'UI_TOOLTIPS_RotatingVehicle_Text'         : 'Al girar el tanque',
        'UI_TOOLTIPS_RotatingTurret_Text'          : 'Al girar la torreta',
        'UI_TOOLTIPS_modulesText_Text'             : "[A modulos] <font color='#FFA500'>{}</font>",
        'UI_TOOLTIPS_modulesTextTooltip_Text'      : " [A modulos]",
        'UI_TOOLTIPS_modulesTextTooltipBattle_Text': "%s, <font color='#FFA500'>[A modulos] %s</font>",
        'UI_TOOLTIPS_tracerSpeedText_Text'         : '[Trazador]',
        'UI_TOOLTIPS_shellSpeedText_Text'          : '[Bala]',
        'UI_TOOLTIPS_speedMsec_Text'               : 'm/seg.',
    }
if 'pl' in getLanguageCode().lower():
    i18n = {
    'UI_TOOLTIPS_StabBonus_ColorPositive'      : '#28F09C',
    'UI_TOOLTIPS_StabBonus_ColorNeutral'       : '#7CD606',
    'UI_TOOLTIPS_Stabilization_Color'          : '#FFD700',
    'UI_TOOLTIPS_MovementSpeed_Color'          : '#8378FC',
    'UI_TOOLTIPS_RotatingVehicle_Color'        : '#1CC6D9',
    'UI_TOOLTIPS_RotatingTurret_Color'         : '#F200DA',
    'UI_TOOLTIPS_StabBonus_Text'               : 'Bonus stabilizacyjna',
    'UI_TOOLTIPS_Stabilization_Text'           : 'Calkowita stabilizacja',
    'UI_TOOLTIPS_MovementSpeed_Text'           : 'Przy max predkosci',
    'UI_TOOLTIPS_RotatingVehicle_Text'         : 'Przy obracaniu zbiornika',
    'UI_TOOLTIPS_RotatingTurret_Text'          : 'Przy zawracaniu wiezy',
    'UI_TOOLTIPS_modulesText_Text'             : "[Do modulow] <font color='#FFA500'>{}</font>",
    'UI_TOOLTIPS_modulesTextTooltip_Text'      : " [Do modulow]",
    'UI_TOOLTIPS_modulesTextTooltipBattle_Text': "%s, <font color='#FFA500'>[Do modulow] %s</font>",
    'UI_TOOLTIPS_tracerSpeedText_Text'         : '[Tracer]',
    'UI_TOOLTIPS_shellSpeedText_Text'          : '[Kula]',
    'UI_TOOLTIPS_speedMsec_Text'               : 'm/sec.',
}
if 'hu' in getLanguageCode().lower():
    i18n = {
    'UI_TOOLTIPS_StabBonus_ColorPositive'      : '#28F09C',
    'UI_TOOLTIPS_StabBonus_ColorNeutral'       : '#7CD606',
    'UI_TOOLTIPS_Stabilization_Color'          : '#FFD700',
    'UI_TOOLTIPS_MovementSpeed_Color'          : '#8378FC',
    'UI_TOOLTIPS_RotatingVehicle_Color'        : '#1CC6D9',
    'UI_TOOLTIPS_RotatingTurret_Color'         : '#F200DA',
    'UI_TOOLTIPS_StabBonus_Text'               : 'Stabilizacios bonusz',
    'UI_TOOLTIPS_Stabilization_Text'           : 'Teljes stabilizacio',
    'UI_TOOLTIPS_MovementSpeed_Text'           : 'Amikor a max. sebesseg',
    'UI_TOOLTIPS_RotatingVehicle_Text'         : 'A tank megforditasakor',
    'UI_TOOLTIPS_RotatingTurret_Text'          : 'A torony forgatasakor',
    'UI_TOOLTIPS_modulesText_Text'             : "[A modulokhoz] <font color='#FFA500'>{}</font>",
    'UI_TOOLTIPS_modulesTextTooltip_Text'      : " [A modulokhoz]",
    'UI_TOOLTIPS_modulesTextTooltipBattle_Text': "%s, <font color='#FFA500'>[A modulokhoz] %s</font>",
    'UI_TOOLTIPS_tracerSpeedText_Text'         : '[Nyomjelzo]',
    'UI_TOOLTIPS_shellSpeedText_Text'          : '[Hej]',
    'UI_TOOLTIPS_speedMsec_Text'               : 'm/sec.',
}
if 'cn' in getLanguageCode().lower() or 'zh' in getLanguageCode().lower() :
    i18n = {
    'UI_TOOLTIPS_StabBonus_ColorPositive'      : '#28F09C',
    'UI_TOOLTIPS_StabBonus_ColorNeutral'       : '#7CD606',
    'UI_TOOLTIPS_Stabilization_Color'          : '#FFD700',
    'UI_TOOLTIPS_MovementSpeed_Color'          : '#8378FC',
    'UI_TOOLTIPS_RotatingVehicle_Color'        : '#1CC6D9',
    'UI_TOOLTIPS_RotatingTurret_Color'         : '#F200DA',
    'UI_TOOLTIPS_StabBonus_Text'               : 'Stabilization bonus',
    'UI_TOOLTIPS_Stabilization_Text'           : 'Total stabilization',
    'UI_TOOLTIPS_MovementSpeed_Text'           : 'When maximum speed',
    'UI_TOOLTIPS_RotatingVehicle_Text'         : 'When turning vehicle',
    'UI_TOOLTIPS_RotatingTurret_Text'          : 'When turning turret',
    'UI_TOOLTIPS_modulesText_Text'             : "[To modules] <font color='#FFA500'>{}</font>",
    'UI_TOOLTIPS_modulesTextTooltip_Text'      : " [To modules]",
    'UI_TOOLTIPS_modulesTextTooltipBattle_Text': "%s, <font color='#FFA500'>[To modules] %s</font>",
    'UI_TOOLTIPS_tracerSpeedText_Text'         : '[Tracer]',
    'UI_TOOLTIPS_shellSpeedText_Text'          : '[Shell]',
    'UI_TOOLTIPS_speedMsec_Text'               : 'm/sec.',
}
if 'tr' in getLanguageCode().lower():
    i18n = {
    'UI_TOOLTIPS_StabBonus_ColorPositive'      : '#28F09C',
    'UI_TOOLTIPS_StabBonus_ColorNeutral'       : '#7CD606',
    'UI_TOOLTIPS_Stabilization_Color'          : '#FFD700',
    'UI_TOOLTIPS_MovementSpeed_Color'          : '#8378FC',
    'UI_TOOLTIPS_RotatingVehicle_Color'        : '#1CC6D9',
    'UI_TOOLTIPS_RotatingTurret_Color'         : '#F200DA',
    'UI_TOOLTIPS_StabBonus_Text'               : 'Stabilizasyon Bonusu',
    'UI_TOOLTIPS_Stabilization_Text'           : 'Toplam stabilizasyon',
    'UI_TOOLTIPS_MovementSpeed_Text'           : 'Maksimum hızdayken',
    'UI_TOOLTIPS_RotatingVehicle_Text'         : 'Tank donerken',
    'UI_TOOLTIPS_RotatingTurret_Text'          : 'Taret donerken',
    'UI_TOOLTIPS_modulesText_Text'             : "[Modullere] <font color='#FFA500'>{}</font>",
    'UI_TOOLTIPS_modulesTextTooltip_Text'      : " [Modullere]",
    'UI_TOOLTIPS_modulesTextTooltipBattle_Text': "%s, <font color='#FFA500'>[Modullere] %s</font>",
    'UI_TOOLTIPS_tracerSpeedText_Text'         : '[Iz]',
    'UI_TOOLTIPS_shellSpeedText_Text'          : '[Mermi]',
    'UI_TOOLTIPS_speedMsec_Text'               : 'm/sn.',
}


def createStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType='', nationFlagIcon='', enabled=True, available=True, contextMenuId='', additionalInfo='', actionButtonLabel=None, active=GOODIE_STATE.INACTIVE, upgradable=False, upgradeButtonIcon=None, upgradeButtonTooltip='', extraParams=(), specializations=()):
    result = oldCreateStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType, nationFlagIcon, enabled, available, contextMenuId, additionalInfo, actionButtonLabel, active, upgradable, upgradeButtonIcon, upgradeButtonTooltip, extraParams, specializations)
    #if 'price' in result and 'count' in result:
    b = []
    for priced in result['price']['price']:
        b.append((priced[0], priced[1] * result['count']))
    result['price']['price'] = tuple(b)
    return result


def makeShellTooltip(*args):
    result = oldMakeShellTooltip(*args)
    descriptor = args[1]
    damage = backport.getNiceNumberFormat(descriptor.damage[0])
    damageModule = i18n['UI_TOOLTIPS_modulesTextTooltipBattle_Text'] % (damage, backport.getNiceNumberFormat(descriptor.damage[1]))
    return result.replace(damage, damageModule)


def getFormattedParamsList(descriptor, parameters, excludeRelative=False):
    params = oldGetFormattedParamsList(descriptor, parameters, excludeRelative)
    result = []
    for param in params:
        if 'caliber' in param:
            result.append(param)
            result.append(('avgDamage', i18n['UI_TOOLTIPS_modulesText_Text'].format(backport.getNiceNumberFormat(descriptor.damage[1]))))
        else:
            result.append(param)
    return result


def construct(self):
    result = old_construct(self)
    block = []
    avgDamage = backport.text(R.strings.menu.moduleInfo.params.dyn('avgDamage')())
    for pack in result:
        if 'name' in pack['data'] and avgDamage in pack['data']['name']:
            block.append(pack)
            block.append(self._packParameterBlock(avgDamage, "<font color='#FFA500'>%s</font>" % backport.getNiceNumberFormat(self.shell.descriptor.damage[1]), p__makeString(formatters.measureUnitsForParameter('avgDamage')) + i18n['UI_TOOLTIPS_modulesTextTooltip_Text']))
        else:
            block.append(pack)
    vehicle = g_currentVehicle.item
    module = vehicle.gun
    bonuses = p__getStabFactors(vehicle, module)
    for bonus in bonuses:
        block.append(self._packParameterBlock(bonus[0], bonus[1], ''))
    return block


def p__getAdditiveShotDispersionFactor(vehicle):
    additiveShotDispersionFactor = vehicle.descriptor.miscAttrs['additiveShotDispersionFactor']
    for crewman in vehicle.crew:
        if crewman[1] is None:
            continue
        if 'gunner_smoothTurret' in crewman[1].skillsMap:
            additiveShotDispersionFactor -= crewman[1].skillsMap['gunner_smoothTurret'].level * 0.00075
        if 'driver_smoothDriving' in crewman[1].skillsMap:
            additiveShotDispersionFactor -= crewman[1].skillsMap['driver_smoothDriving'].level * 0.0004
    # return additiveShotDispersionFactor
    for item in vehicle.battleBoosters.installed.getItems():
        if item and 'imingStabilizer' in item.name:
            additiveShotDispersionFactor -= 0.05
    for item in vehicle.optDevices.installed.getItems():
        if item and 'imingStabilizer' in item.name:
            if 'pgraded' in item.name:
                additiveShotDispersionFactor -= 0.25
            elif 'mproved' in item.name:
                additiveShotDispersionFactor -= 0.275
            else:
                additiveShotDispersionFactor -= 0.2
    return additiveShotDispersionFactor


def p__getStabFactors(vehicle, module, inSettings=False):
    typeDescriptor = vehicle.descriptor
    factors = functions.getVehicleFactors(vehicle)
    additiveFactor = p__getAdditiveShotDispersionFactor(vehicle)
    chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation = typeDescriptor.chassis.shotDispersionFactors
    gunShotDispersionFactorsTurretRotation = module.descriptor.shotDispersionFactors['turretRotation']
    chassisShotDispersionFactorsMovement /= factors['vehicle/rotationSpeed']
    gunShotDispersionFactorsTurretRotation /= factors['turret/rotationSpeed']
    vehicleRSpeed = turretRotationSpeed = 0
    maxTurretRotationSpeed = typeDescriptor.turret.rotationSpeed
    vehicleRSpeedMax = typeDescriptor.physics['rotationSpeedLimit']
    vehicleSpeed = typeDescriptor.siegeVehicleDescr.physics['speedLimits'][0] if typeDescriptor.isWheeledVehicle and hasattr(typeDescriptor, 'siegeVehicleDescr') else typeDescriptor.physics['speedLimits'][0]
    vehicleSpeed *= 3.6
    vehicleSpeedMax = 99.0 if typeDescriptor.isWheeledVehicle and hasattr(typeDescriptor, 'siegeVehicleDescr') else 70.0

    vehicleMovementFactor = vehicleSpeed * chassisShotDispersionFactorsMovement
    vehicleMovementFactor *= vehicleMovementFactor
    vehicleMovementFactorMax = vehicleSpeedMax * chassisShotDispersionFactorsMovement
    vehicleMovementFactorMax *= vehicleMovementFactorMax

    vehicleRotationFactorMax = vehicleRSpeedMax * chassisShotDispersionFactorsRotation
    vehicleRotationFactorMax *= vehicleRotationFactorMax
    vehicleRotationFactor = vehicleRSpeed * chassisShotDispersionFactorsRotation
    vehicleRotationFactor *= vehicleRotationFactor

    turretRotationFactorMax = maxTurretRotationSpeed * gunShotDispersionFactorsTurretRotation
    turretRotationFactorMax *= turretRotationFactorMax
    turretRotationFactor = turretRotationSpeed * gunShotDispersionFactorsTurretRotation
    turretRotationFactor *= turretRotationFactor

    idealFactorMax = vehicleMovementFactorMax + vehicleRotationFactorMax + turretRotationFactorMax

    baseMax = round(math.sqrt(idealFactorMax), 1)
    baseMovementSpeed = round(math.sqrt(vehicleMovementFactor), 2)
    baseRotatingVehicle = round(math.sqrt(vehicleRotationFactorMax), 2)
    baseRotatingTurret = round(math.sqrt(turretRotationFactorMax), 2)

    resultMax = round(math.sqrt(idealFactorMax * (additiveFactor ** 2)), 1)
    resultMovementSpeed = round(math.sqrt(vehicleMovementFactor * (additiveFactor ** 2)), 2)
    resultRotatingVehicle = round(math.sqrt(vehicleRotationFactorMax * (additiveFactor ** 2)), 2)
    resultRotatingTurret = round(math.sqrt(turretRotationFactorMax * (additiveFactor ** 2)), 2)
    bonuses = (i18n['UI_TOOLTIPS_StabBonus_Text'], '<font color="%s">+%.2f%%</font>' % (i18n['UI_TOOLTIPS_StabBonus_ColorPositive'] if additiveFactor < 1 else i18n['UI_TOOLTIPS_StabBonus_ColorNeutral'], 100 - additiveFactor / 0.01))
    if baseMax - resultMax > 0:
        bonuses1 = ('%s %.2f%% (<font color="%s">+%.2f%%</font>)' % (i18n['UI_TOOLTIPS_Stabilization_Text'], 100 - baseMax, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], baseMax - resultMax), '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_Stabilization_Color'], 100 - resultMax))
        bonuses2 = ('%s %.2f%% (<font color="%s">+%.2f%%</font>)' % (i18n['UI_TOOLTIPS_MovementSpeed_Text'], resultMovementSpeed, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], baseMovementSpeed - resultMovementSpeed), '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_MovementSpeed_Color'], baseMovementSpeed))
        bonuses3 = ('%s %.2f%% (<font color="%s">+%.2f%%</font>)' % (i18n['UI_TOOLTIPS_RotatingVehicle_Text'], resultRotatingVehicle, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], baseRotatingVehicle - resultRotatingVehicle), '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_RotatingVehicle_Color'], baseRotatingVehicle))
        bonuses4 = ('%s %.2f%% (<font color="%s">+%.2f%%</font>)' % (i18n['UI_TOOLTIPS_RotatingTurret_Text'], resultRotatingTurret, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], baseRotatingTurret - resultRotatingTurret), '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_RotatingTurret_Color'], baseRotatingTurret))
    else:
        bonuses1 = (i18n['UI_TOOLTIPS_Stabilization_Text'], '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_Stabilization_Color'], 100 - resultMax))
        bonuses2 = (i18n['UI_TOOLTIPS_MovementSpeed_Text'], '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_MovementSpeed_Color'], resultMovementSpeed))
        bonuses3 = (i18n['UI_TOOLTIPS_RotatingVehicle_Text'], '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_RotatingVehicle_Color'], resultRotatingVehicle))
        bonuses4 = (i18n['UI_TOOLTIPS_RotatingTurret_Text'], '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_RotatingTurret_Color'], resultRotatingTurret))
    if inSettings:
        return resultMax
    if additiveFactor < 1:
        return bonuses1, bonuses4, bonuses3, bonuses2, bonuses
    return bonuses1, bonuses4, bonuses3, bonuses2


def construct1(self):
    result = list(old1_construct(self))
    module = self.module
    vehicle = self.configuration.vehicle
    if module.itemTypeID == GUI_ITEM_TYPE.GUN:
        bonuses = p__getStabFactors(vehicle, module)
        for bonus in bonuses:
            result.append(formatters_tooltips.packTextParameterBlockData(name=bonus[0], value=bonus[1], valueWidth=self._valueWidth, padding=formatters_tooltips.packPadding(left=-5)))
    return result

# TODO: устарело, необходимо разобраться и восстановить позже
def _packBlocks(self, paramName):
    blocks = old_packBlocks(self, paramName)
    if paramName in ('relativePower', 'vehicleGunShotDispersion', 'aimingTime'):
        vehicle = g_currentVehicle.item
        module = vehicle.gun
        bonuses = p__getStabFactors(vehicle, module)
        result = []
        found = False
        for block in blocks:
            result.append(block)
            if 'blocksData' in block['data']:
                if found:
                    continue
                for linkage in block['data']['blocksData']:
                    if 'TooltipTextBlockUI' in linkage['linkage']:
                        found = True
                        for bonus in bonuses:
                            result.append(formatters_tooltips.packTextParameterBlockData(name='%s:&nbsp;%s' %(bonus[1], bonus[0]), value='', valueWidth=0, padding=formatters_tooltips.packPadding(left=59, right=20)))
                        break
        return result
    return blocks

def StatusBlockConstructor_getStatus(self):
    self.MAX_INSTALLED_LIST_LEN = 1000
    return old_StatusBlockConstructor_getStatus(self)

# Создаем испраленный конструктор для показа списка танков в подсказке
def InventoryBlockConstructorConstruct(self):
    block = []
    module = self.module
    inventoryCount = self.configuration.inventoryCount
    vehiclesCount = self.configuration.vehiclesCount
    if self.module.itemTypeID is GUI_ITEM_TYPE.EQUIPMENT and self.module.isBuiltIn:
        return
    else:
        items = self.itemsCache.items
        if inventoryCount:
            count = module.inventoryCount
            if count > 0:
                block.append(self._getInventoryBlock(count, self._inInventoryBlockData, self._inventoryPadding))
        if vehiclesCount:
            inventoryVehicles = items.getVehicles(REQ_CRITERIA.INVENTORY)
            installedVehicles = module.getInstalledVehicles(inventoryVehicles.itervalues())
            count = len(installedVehicles)
            if count > 0:
                totalInstalledVehicles = [x.shortUserName for x in installedVehicles]
                totalInstalledVehicles.sort()
                tooltipText = None
                visibleVehiclesCount = 0
                for installedVehicle in totalInstalledVehicles:
                    if tooltipText is None:
                        tooltipText = installedVehicle
                        visibleVehiclesCount = 1
                        continue
                    # изменённая строка
                    if len(tooltipText) + len(installedVehicle) + 2 > MAX_INSTALLED_LIST_LEN:
                        break
                    tooltipText = ', '.join((tooltipText, installedVehicle))
                    visibleVehiclesCount += 1

                if count > visibleVehiclesCount:
                    hiddenVehicleCount = count - visibleVehiclesCount
                    hiddenTxt = backport.text(R.strings.tooltips.moduleFits.already_installed.hiddenVehicleCount(), count=str(hiddenVehicleCount))
                    tooltipText = '... '.join((tooltipText, text_styles.stats(hiddenTxt)))
                self._onVehicleBlockData['text'] = tooltipText
                block.append(self._getInventoryBlock(count, self._onVehicleBlockData, self._inventoryPadding))
        return block

# добавляем показ стоимости продажи всего оборудования\расходников в ангаре и на технике в подсказке
def PriceBlockConstructorConstruct(self):
    # выполняем изначальный код
    block = oldPriceBlockConstructorConstruct(self)
    module = self.module
    # получаем данные о текущем количестве на складе и на танках
    inventoryCount = self.configuration.inventoryCount and module.inventoryCount
    vehiclesCount = self.configuration.vehiclesCount and len(module.getInstalledVehicles(self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()))
    # проверка наличия и уточнение что цена в кредитах
    if (inventoryCount or vehiclesCount) and module.getBuyPrice().getCurrency() == 'credits' and module.sellPrices.itemPrice.price.credits:
        # тип Продажа
        settings = _CurrencySetting('#tooltips:vehicle/sell_price', icons.credits(), text_styles.credits, 'credits', iconYOffset=0)
        # считаем стоимость продажи ВСЕГО однотипного оборудования\расходников цена * (количество на складе + количество на танках)
        priceValue = settings.textStyle(backport.getIntegralFormat(module.sellPrices.itemPrice.price.credits * (inventoryCount + vehiclesCount)))
        # добавляем текстовую подсказку с количеством
        text = text_styles.concatStylesWithSpace(text_styles.main(settings.text), '(%s + %s)' %(inventoryCount, vehiclesCount))
        # вставляем сформированный результат в конце блока стоимости
        block.append(formatters_tooltips.packTextParameterWithIconBlockData(name=text, value=priceValue, icon=settings.frame, valueWidth=self._valueWidth, padding=formatters_tooltips.packPadding(left=-5), nameOffset=14, gap=0, iconYOffset=settings.iconYOffset))
    return block

# Добавляем показ параметров, которые изменит расходник (аптечка, кола и т.д.) если будет установлена на танк
def EffectsBlockConstructorConstruct(self):
    block = oldEffectsBlockConstructorConstruct(self)
    isInstalled = self.module.isInstalled(self.configuration.vehicle)
    if isInstalled:
        kpiArgs = {kpi.name: kpi.value for kpi in self.module.getKpi(self.configuration.vehicle)}
        currParams = params.VehicleParams(self.configuration.vehicle).getParamsDict()
        onUseStr = ''
        sets = {
            'crewLevel': ('reloadTimeSecs', 'clipFireRate', 'autoReloadTime', 'aimingTime', 'shotDispersionAngle',
                          'avgDamagePerMinute', 'circularVisionRadius'),
            'vehicleEnginePower': ('enginePowerPerTon', 'enginePower', 'turretRotationSpeed'),
            'vehicleFireChance': ('damagedModulesDetectionTimeSituational', 'damagedModulesDetectionTime'),
            'vehicleRepairSpeed': ('chassisRepairTime', 'repairSpeed'),
        }
        for datasheet in sets:
            if datasheet in kpiArgs:
                for param in sets[datasheet]:
                    if param in currParams and currParams[param]:
                        value = currParams[param]
                        if type(value) == int:
                            temp = '%s' % value
                        elif type(value) == float:
                            temp = '%.2f' % value
                        else:
                            temp = '%.2f' % value[0]
                        if 'clipFireRate' in param:
                            temp = '(%.2f/%.2f/%.2f)' % (value[0], value[1], value[2])
                        onUseStr += "<font face='$FieldFont' size='14' color='#80d43a'>%s</font> %s %s\n" % (text_styles.bonusAppliedText(temp), p__makeString(formatters.measureUnitsForParameter(param)), p__makeString('#menu:tank_params/%s' % param))
        block.append(formatters_tooltips.packImageTextBlockData(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.always())), desc=text_styles.main(onUseStr), padding=formatters_tooltips.packPadding(top=5)))
    return block


# хуки изначальной функции
oldCreateStorageDefVO = storage_helpers.createStorageDefVO
oldMakeShellTooltip = ConsumablesPanel._ConsumablesPanel__makeShellTooltip
oldGetFormattedParamsList = formatters.getFormattedParamsList
old_construct = CommonStatsBlockConstructor.construct
old1_construct = CommonStatsBlockConstructor1.construct
#old_packBlocks = VehicleAdvancedParametersTooltipData._packBlocks
old_StatusBlockConstructor_getStatus = StatusBlockConstructor._getStatus
# добавление в конструктор стоимости для оборудования\расходников
oldPriceBlockConstructorConstruct = module.PriceBlockConstructor.construct

#old_ModuleBlockTooltipData_packBlocks = ModuleBlockTooltipData._packBlocks
# добавление в конструктор подсказок для расходников, на что именно влияет и какие результирующие цифры будут
oldEffectsBlockConstructorConstruct = module.EffectsBlockConstructor.construct
# расширение списка танков, где установленно оборудование\расходники
MAX_INSTALLED_LIST_LEN = 1200 # оригинал 120

# хуки для назначения новых функций взамен старых
# # замена конструктора списка танков, на которых установлено оборудование\расходники
module.InventoryBlockConstructor.construct = InventoryBlockConstructorConstruct
# добавление в конструктор стоимости для оборудования\расходников
module.PriceBlockConstructor.construct = PriceBlockConstructorConstruct
# добавление в конструктор подсказок для расходников, на что именно влияет и какие результирующие цифры будут
module.EffectsBlockConstructor.construct = EffectsBlockConstructorConstruct

storage_helpers.createStorageDefVO = createStorageDefVO
ConsumablesPanel._ConsumablesPanel__makeShellTooltip = makeShellTooltip
formatters.getFormattedParamsList = getFormattedParamsList
CommonStatsBlockConstructor.construct = construct
CommonStatsBlockConstructor1.construct = construct1
#VehicleAdvancedParametersTooltipData._packBlocks = _packBlocks
StatusBlockConstructor._getStatus = StatusBlockConstructor_getStatus


print('[LOAD_MOD]:  [mod_tooltipsCountItemsLimitExtend 2.06 (14-09-2023), by spoter]')

