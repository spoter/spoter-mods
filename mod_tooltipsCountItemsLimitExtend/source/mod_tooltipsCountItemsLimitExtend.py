# -*- coding: utf-8 -*-
import math

from CurrentVehicle import g_currentVehicle
from goodies.goodie_constants import GOODIE_STATE
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.shared.items_parameters import formatters, functions
from gui.shared.tooltips import battle_booster, formatters as formatters1
from gui.shared.tooltips.vehicle import VehicleAdvancedParametersTooltipData
from gui.shared.tooltips.module import CommonStatsBlockConstructor as CommonStatsBlockConstructor1, ModuleTooltipBlockConstructor
from gui.shared.tooltips.shell import CommonStatsBlockConstructor
from helpers import getLanguageCode
from helpers.i18n import makeString as p__makeString
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.impl import backport
from gui.impl.gen import R

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


def createStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType='', nationFlagIcon='', enabled=True, available=True, contextMenuId='', additionalInfo='', active=GOODIE_STATE.INACTIVE, upgradable=False, upgradeButtonTooltip='', extraParams=(), specializations=()):
    result = oldCreateStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType, nationFlagIcon, enabled, available, contextMenuId, additionalInfo, active, upgradable, upgradeButtonTooltip, extraParams, specializations)
    try:
        b = []
        for priced in result['price']['price']:
            b.append((priced[0], priced[1] * result['count']))
        result['price']['price'] = tuple(b)
    except StandardError:
        pass
    return result


def makeShellTooltip(self, descriptor, piercingPower, shotSpeed):
    result = oldMakeShellTooltip(self, descriptor, piercingPower, shotSpeed)
    try:
        damage = backport.getNiceNumberFormat(descriptor.damage[0])
        damageModule = i18n['UI_TOOLTIPS_modulesTextTooltipBattle_Text'] % (damage, backport.getNiceNumberFormat(descriptor.damage[1]))
    except StandardError:
        return result
    return result.replace(damage, damageModule)


def getFormattedParamsList(descriptor, parameters, excludeRelative=False):
    params = oldGetFormattedParamsList(descriptor, parameters, excludeRelative)
    result = []
    try:
        for param in params:
            if 'caliber' in param:
                result.append(param)
                result.append(('avgDamage', i18n['UI_TOOLTIPS_modulesText_Text'].format(backport.getNiceNumberFormat(descriptor.damage[1]))))
            else:
                result.append(param)
    except StandardError:
        return params
    return result


def construct(self):
    result = old_construct(self)
    try:
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
    except StandardError:
        return result
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
    try:
        module = self.module
        vehicle = self.configuration.vehicle
        if module.itemTypeID == GUI_ITEM_TYPE.GUN:
            bonuses = p__getStabFactors(vehicle, module)
            for bonus in bonuses:
                result.append(formatters1.packTextParameterBlockData(name=bonus[0], value=bonus[1], valueWidth=self._valueWidth, padding=formatters1.packPadding(left=-5)))
    except StandardError:
        pass
    return result

def _packBlocks(self, paramName):
    blocks = old_packBlocks(self, paramName)
    try:
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
                                result.append(formatters1.packTextParameterBlockData(name='%s:&nbsp;%s' %(bonus[1], bonus[0]), value='', valueWidth=0, padding=formatters1.packPadding(left=59, right=20)))
                            break
            return result
    except StandardError:
        pass
    return blocks


oldCreateStorageDefVO = storage_helpers.createStorageDefVO
if hasattr(ConsumablesPanel, '_makeShellTooltip'):
    oldMakeShellTooltip = ConsumablesPanel._makeShellTooltip
else:
    oldMakeShellTooltip = ConsumablesPanel._ConsumablesPanel__makeShellTooltip
oldGetFormattedParamsList = formatters.getFormattedParamsList
old_construct = CommonStatsBlockConstructor.construct
old1_construct = CommonStatsBlockConstructor1.construct
old_packBlocks = VehicleAdvancedParametersTooltipData._packBlocks

ModuleTooltipBlockConstructor.MAX_INSTALLED_LIST_LEN = 1000
battle_booster._MAX_INSTALLED_LIST_LEN = 1000
storage_helpers.createStorageDefVO = createStorageDefVO
if hasattr(ConsumablesPanel, '_makeShellTooltip'):
    ConsumablesPanel._makeShellTooltip = makeShellTooltip
else:
    ConsumablesPanel._ConsumablesPanel__makeShellTooltip = makeShellTooltip
formatters.getFormattedParamsList = getFormattedParamsList
CommonStatsBlockConstructor.construct = construct
CommonStatsBlockConstructor1.construct = construct1
VehicleAdvancedParametersTooltipData._packBlocks = _packBlocks

print '[LOAD_MOD]:  [mod_tooltipsCountItemsLimitExtend 2.03 (26-09-2020), by spoter, gox, b4it]'
