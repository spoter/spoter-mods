# -*- coding: utf-8 -*-
import math

import BigWorld
from CurrentVehicle import g_currentVehicle
from goodies.goodie_constants import GOODIE_STATE
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.shared.items_parameters import formatters, functions
from gui.shared.tooltips import battle_booster, formatters as formatters1
from gui.shared.tooltips.module import CommonStatsBlockConstructor as CommonStatsBlockConstructor1, ModuleTooltipBlockConstructor
from gui.shared.tooltips.shell import CommonStatsBlockConstructor
from helpers import getLanguageCode
from helpers.i18n import makeString as p__makeString
from gui.shared.gui_items import GUI_ITEM_TYPE

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
    'UI_TOOLTIPS_modulesText_Text'             : "[Zu Modulen] <font color='#FFA500'>{}</font>",
    'UI_TOOLTIPS_modulesTextTooltip_Text'      : " [Zu Modulen]",
    'UI_TOOLTIPS_modulesTextTooltipBattle_Text': "%s, <font color='#FFA500'>[Zu Modulen] %s</font>",
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


def createStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType='', nationFlagIcon='', enabled=True, available=True, contextMenuId='', additionalInfo='', active=GOODIE_STATE.INACTIVE, upgradable=False, upgradeButtonTooltip=''):
    result = oldCreateStorageDefVO(itemID, title, description, count, price, image, imageAlt, itemType, nationFlagIcon, enabled, available, contextMenuId, additionalInfo, active, upgradable, upgradeButtonTooltip)
    try:
        b = []
        for priced in result['price']['price']:
            b.append((priced[0], priced[1] * result['count']))
        result['price']['price'] = tuple(b)
    except StandardError:
        pass
    return result


def makeShellTooltip(self, descriptor, piercingPower):
    player = BigWorld.player()
    result = oldMakeShellTooltip(self, descriptor, piercingPower)
    try:
        damage = str(int(descriptor.damage[0]))
        damageModule = i18n['UI_TOOLTIPS_modulesTextTooltipBattle_Text'] % (damage, int(descriptor.damage[1]))
        speed = ''
        for shot in player.vehicleTypeDescriptor.gun.shots:
            if descriptor.id == shot.shell.id:
                tracerSpeed = "\n%s %s <font color='#1CC6D9'>%s</font> %s" % (p__makeString('#menu:moduleInfo/params/flyDelayRange'), i18n['UI_TOOLTIPS_tracerSpeedText_Text'], int(shot.speed), i18n['UI_TOOLTIPS_speedMsec_Text'])
                shellSpeed = "\n%s %s <font color='#28F09C'>%s</font> %s" % (p__makeString('#menu:moduleInfo/params/flyDelayRange'), i18n['UI_TOOLTIPS_shellSpeedText_Text'], int(shot.speed / 0.8), i18n['UI_TOOLTIPS_speedMsec_Text'])
                speed = tracerSpeed + shellSpeed
                break
    except StandardError:
        return result
    return result.replace(damage, damageModule + speed)


def getFormattedParamsList(descriptor, parameters, excludeRelative=False):
    params = oldGetFormattedParamsList(descriptor, parameters, excludeRelative)
    result = []
    for param in params:
        if 'caliber' in param:
            result.append(param)
            try:
                for shot in g_currentVehicle.item.descriptor.gun.shots:
                    if descriptor.id == shot.shell.id:
                        result.append(('flyDelayRange', "%s <font color='#1CC6D9'>%s</font> %s" % (i18n['UI_TOOLTIPS_tracerSpeedText_Text'], int(shot.speed), i18n['UI_TOOLTIPS_speedMsec_Text'])))
                        result.append(('flyDelayRange', "%s <font color='#28F09C'>%s</font> %s" % (i18n['UI_TOOLTIPS_shellSpeedText_Text'], int(shot.speed / 0.8), i18n['UI_TOOLTIPS_speedMsec_Text'])))
                        break
                result.append(('avgDamage', i18n['UI_TOOLTIPS_modulesText_Text'].format(int(descriptor.damage[1]))))
            except StandardError:
                pass
        else:
            result.append(param)
    return result


def construct(self):
    result = old_construct(self)
    block = []

    for pack in result:
        if 'name' in pack['data'] and p__makeString('#menu:moduleInfo/params/' + 'caliber') in pack['data']['name']:
            block.append(pack)
            try:
                shell = self.shell
                for shot in g_currentVehicle.item.descriptor.gun.shots:
                    if shell.descriptor.id == shot.shell.id:
                        block.append(self._packParameterBlock(p__makeString('#menu:moduleInfo/params/flyDelayRange'), "<font color='#1CC6D9'>%s</font>" % int(shot.speed), '%s %s' % (i18n['UI_TOOLTIPS_tracerSpeedText_Text'], i18n['UI_TOOLTIPS_speedMsec_Text'])))
                        block.append(self._packParameterBlock(p__makeString('#menu:moduleInfo/params/flyDelayRange'), "<font color='#28F09C'>%s</font>" % int(shot.speed / 0.8), '%s %s' % (i18n['UI_TOOLTIPS_shellSpeedText_Text'], i18n['UI_TOOLTIPS_speedMsec_Text'])))
                        break
                block.append(self._packParameterBlock(p__makeString('#menu:moduleInfo/params/avgDamage'), "<font color='#FFA500'>%s</font>" % int(shell.descriptor.damage[1]), p__makeString(formatters.measureUnitsForParameter('avgDamage')) + i18n['UI_TOOLTIPS_modulesTextTooltip_Text']))
            except StandardError:
                pass
        else:
            block.append(pack)
    return block


def p__getAdditiveShotDispersionFactor(vehicle):
    additiveShotDispersionFactor = 1.0
    try:
        for crewman in vehicle.crew:
            if 'gunner_smoothTurret' in crewman[1].skillsMap:
                additiveShotDispersionFactor += crewman[1].skillsMap['gunner_smoothTurret'].level * 0.00075
            if 'driver_smoothDriving' in crewman[1].skillsMap:
                additiveShotDispersionFactor += crewman[1].skillsMap['driver_smoothDriving'].level * 0.0004
    except StandardError:
        pass
    # return additiveShotDispersionFactor
    for item in vehicle.equipment.battleBoosterConsumables:
        if item and 'imingStabilizer' in item.name:
            additiveShotDispersionFactor += 0.05
    for item in vehicle.optDevices:
        if item and 'imingStabilizer' in item.name:
            if 'pgraded' in item.name or 'mproved' in item.name:
                additiveShotDispersionFactor += 0.25
            else:
                additiveShotDispersionFactor += 0.2
    return additiveShotDispersionFactor


def p__getStabFactors(vehicle, module, inSettings=False):
    typeDescriptor = vehicle.descriptor
    factors = functions.getVehicleFactors(vehicle)
    additiveFactor = p__getAdditiveShotDispersionFactor(vehicle)
    chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation = typeDescriptor.chassis.shotDispersionFactors
    gunShotDispersionFactorsTurretRotation = module.descriptor.shotDispersionFactors['turretRotation']
    chassisShotDispersionFactorsMovement /= factors['vehicle/rotationSpeed']
    gunShotDispersionFactorsTurretRotation /= factors['turret/rotationSpeed']
    vehicleSpeed = vehicleRSpeed = turretRotationSpeed = 0
    maxTurretRotationSpeed = typeDescriptor.turret.rotationSpeed
    vehicleRSpeedMax = typeDescriptor.physics['rotationSpeedLimit']
    vehicleSpeedMax = typeDescriptor.siegeVehicleDescr.physics['speedLimits'][0] if typeDescriptor.isWheeledVehicle and hasattr(typeDescriptor, 'siegeVehicleDescr') else typeDescriptor.physics['speedLimits'][0]
    vehicleSpeedMax *= 3.6

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
    baseMovementSpeed = round(math.sqrt(vehicleMovementFactorMax), 2)
    baseRotatingVehicle = round(math.sqrt(vehicleRotationFactorMax), 2)
    baseRotatingTurret = round(math.sqrt(turretRotationFactorMax), 2)

    resultMax = round(math.sqrt(idealFactorMax * (additiveFactor ** 2)), 1)
    resultMovementSpeed = round(math.sqrt(vehicleMovementFactorMax * (additiveFactor ** 2)), 2)
    resultRotatingVehicle = round(math.sqrt(vehicleRotationFactorMax * (additiveFactor ** 2)), 2)
    resultRotatingTurret = round(math.sqrt(turretRotationFactorMax * (additiveFactor ** 2)), 2)
    bonuses = (i18n['UI_TOOLTIPS_StabBonus_Text'], '<font color="%s">+%.2f%%</font>' % (i18n['UI_TOOLTIPS_StabBonus_ColorPositive'] if additiveFactor > 1 else i18n['UI_TOOLTIPS_StabBonus_ColorNeutral'], additiveFactor / 0.01 - 100))
    if resultMax - baseMax > 0:
        bonuses1 = ('%s %.2f%% (<font color="%s">+%.2f%%</font>)' % (i18n['UI_TOOLTIPS_Stabilization_Text'], 100 - resultMax, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], resultMax - baseMax), '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_Stabilization_Color'], 100 - baseMax))
        bonuses2 = ('%s %.2f%% (<font color="%s">+%.2f%%</font>)' % (i18n['UI_TOOLTIPS_MovementSpeed_Text'], baseMovementSpeed, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], resultMovementSpeed - baseMovementSpeed), '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_MovementSpeed_Color'], resultMovementSpeed))
        bonuses3 = ('%s %.2f%% (<font color="%s">+%.2f%%</font>)' % (i18n['UI_TOOLTIPS_RotatingVehicle_Text'], baseRotatingVehicle, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], resultRotatingVehicle - baseRotatingVehicle), '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_RotatingVehicle_Color'], resultRotatingVehicle))
        bonuses4 = ('%s %.2f%% (<font color="%s">+%.2f%%</font>)' % (i18n['UI_TOOLTIPS_RotatingTurret_Text'], baseRotatingTurret, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], resultRotatingTurret - baseRotatingTurret), '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_RotatingTurret_Color'], resultRotatingTurret))
    else:
        bonuses1 = (i18n['UI_TOOLTIPS_Stabilization_Text'], '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_Stabilization_Color'], 100 - resultMax))
        bonuses2 = (i18n['UI_TOOLTIPS_MovementSpeed_Text'], '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_MovementSpeed_Color'], resultMovementSpeed))
        bonuses3 = (i18n['UI_TOOLTIPS_RotatingVehicle_Text'], '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_RotatingVehicle_Color'], resultRotatingVehicle))
        bonuses4 = (i18n['UI_TOOLTIPS_RotatingTurret_Text'], '<font color="%s">%.2f%%</font>' % (i18n['UI_TOOLTIPS_RotatingTurret_Color'], resultRotatingTurret))
    if inSettings:
        return resultMax
    if additiveFactor > 1:
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


oldCreateStorageDefVO = storage_helpers.createStorageDefVO
oldMakeShellTooltip = ConsumablesPanel._ConsumablesPanel__makeShellTooltip
oldGetFormattedParamsList = formatters.getFormattedParamsList
old_construct = CommonStatsBlockConstructor.construct
old1_construct = CommonStatsBlockConstructor1.construct

ModuleTooltipBlockConstructor.MAX_INSTALLED_LIST_LEN = 1000
battle_booster._MAX_INSTALLED_LIST_LEN = 1000
storage_helpers.createStorageDefVO = createStorageDefVO
ConsumablesPanel._ConsumablesPanel__makeShellTooltip = makeShellTooltip
formatters.getFormattedParamsList = getFormattedParamsList
CommonStatsBlockConstructor.construct = construct
CommonStatsBlockConstructor1.construct = construct1

print '[LOAD_MOD]:  [mod_tooltipsCountItemsLimitExtend 1.09 (04-07-2020), by spoter, gox, b4it]'
