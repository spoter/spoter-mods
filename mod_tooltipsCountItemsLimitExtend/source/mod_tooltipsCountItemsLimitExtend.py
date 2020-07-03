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
from helpers.i18n import makeString as _ms

isRU = 'ru' in getLanguageCode().lower()
modulesText = "[По модулям] <font color='#FFA500'>{}</font>" if isRU else "[To modules] <font color='#FFA500'>{}</font>"
modulesTextTooltip = " [По модулям]" if isRU else " [To modules]"
modulesTextTooltipBattle = "%s, <font color='#FFA500'>[По модулям] %s</font>" if isRU else "%s, <font color='#FFA500'>[To modules] %s</font>"
tracerSpeedText = '[Трассер]' if isRU else '[Tracer]'
shellSpeedText = '[Снаряд]' if isRU else '[Shell]'
speedMsec = 'м/сек.' if isRU else 'm/sec.'
if isRU:
    i18n = {
        'UI_TOOLTIPS_StabBonus_Text'         : 'Бонус стабилизации',
        'UI_TOOLTIPS_StabBonus_ColorPositive': '#28F09C',
        'UI_TOOLTIPS_StabBonus_ColorNeutral' : '#7CD606',
        'UI_TOOLTIPS_Stabilization_Text'     : 'Стабилизация',
        'UI_TOOLTIPS_Stabilization_Color'    : '#FFD700',
        'UI_TOOLTIPS_MovementSpeed_Text'     : 'Разброс от скорости',
        'UI_TOOLTIPS_MovementSpeed_Color'    : '#8378FC',
        'UI_TOOLTIPS_RotatingVehicle_Text'   : 'Разброс от разворота',
        'UI_TOOLTIPS_RotatingVehicle_Color'  : '#1CC6D9',
        'UI_TOOLTIPS_RotatingTurret_Text'    : 'Разброс от башни',
        'UI_TOOLTIPS_RotatingTurret_Color'   : '#F200DA',
    }
else:
    i18n = {
        'UI_TOOLTIPS_StabBonus_Text'         : 'Stabilization bonus',
        'UI_TOOLTIPS_StabBonus_ColorPositive': '#28F09C',
        'UI_TOOLTIPS_StabBonus_ColorNeutral' : '#7CD606',
        'UI_TOOLTIPS_Stabilization_Text'     : 'Stabilization',
        'UI_TOOLTIPS_Stabilization_Color'    : '#FFD700',
        'UI_TOOLTIPS_MovementSpeed_Text'     : 'Dispersion on speed',
        'UI_TOOLTIPS_MovementSpeed_Color'    : '#8378FC',
        'UI_TOOLTIPS_RotatingVehicle_Text'   : 'Dispersion on rotate',
        'UI_TOOLTIPS_RotatingVehicle_Color'  : '#1CC6D9',
        'UI_TOOLTIPS_RotatingTurret_Text'    : 'Dispersion on turret',
        'UI_TOOLTIPS_RotatingTurret_Color'   : '#F200DA',
    }

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
    speed = ''
    for shot in player.vehicleTypeDescriptor.gun.shots:
        if descriptor.id == shot.shell.id:
            tracerSpeed = "\n%s %s <font color='#1CC6D9'>%s</font> %s" % (_ms('#menu:moduleInfo/params/flyDelayRange'), tracerSpeedText, int(shot.speed), speedMsec)
            shellSpeed = "\n%s %s <font color='#28F09C'>%s</font> %s" % (_ms('#menu:moduleInfo/params/flyDelayRange'), shellSpeedText, int(shot.speed / 0.8), speedMsec)
            speed = tracerSpeed + shellSpeed
            break
    return result.replace(damage, damageModule + speed)


def getFormattedParamsList(descriptor, parameters, excludeRelative=False):
    params = oldGetFormattedParamsList(descriptor, parameters, excludeRelative)
    result = []
    for param in params:
        if 'damage' in param and 'flyDelayRange' not in param:
            for shot in g_currentVehicle.item.descriptor.gun.shots:
                if descriptor.id == shot.shell.id:
                    result.append(('flyDelayRange', "%s <font color='#1CC6D9'>%s</font> %s" % (tracerSpeedText, int(shot.speed), speedMsec)))
                    result.append(('flyDelayRange', "%s <font color='#28F09C'>%s</font> %s" % (shellSpeedText, int(shot.speed / 0.8), speedMsec)))
                    break
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
                    block.append(self._packParameterBlock(_ms('#menu:moduleInfo/params/flyDelayRange'), "<font color='#1CC6D9'>%s</font>" % int(shot.speed), '%s %s' % (tracerSpeedText, speedMsec)))
                    block.append(self._packParameterBlock(_ms('#menu:moduleInfo/params/flyDelayRange'), "<font color='#28F09C'>%s</font>" % int(shot.speed / 0.8), '%s %s' % (shellSpeedText, speedMsec)))
                    break
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

if not hasattr(BigWorld, 'blankLogG'):

    def p__getAdditiveShotDispersionFactor():
        additiveShotDispersionFactor = 1.0
        # return additiveShotDispersionFactor
        for item in g_currentVehicle.item.equipment.battleBoosterConsumables:
            if item and 'imingStabilizer' in item.name:
                additiveShotDispersionFactor += 0.05
        for item in g_currentVehicle.item.optDevices:
            if item and 'imingStabilizer' in item.name:
                if 'pgraded' in item.name or 'mproved' in item.name:
                    additiveShotDispersionFactor += 0.25
                else:
                    additiveShotDispersionFactor += 0.2
        return additiveShotDispersionFactor


    def p__getStabFactors(inSettings=False):
        typeDescriptor = g_currentVehicle.item.descriptor
        factors = functions.getVehicleFactors(g_currentVehicle.item)
        additiveFactor = p__getAdditiveShotDispersionFactor()
        chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation = typeDescriptor.chassis.shotDispersionFactors
        gunShotDispersionFactorsTurretRotation = typeDescriptor.gun.shotDispersionFactors['turretRotation']
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
        bonuses = (i18n['UI_TOOLTIPS_StabBonus_Text'], '<font color="%s">%d%%</font>' % (i18n['UI_TOOLTIPS_StabBonus_ColorPositive'] if additiveFactor > 1 else i18n['UI_TOOLTIPS_StabBonus_ColorNeutral'], 100 - additiveFactor / 0.01))
        if resultMax - baseMax > 0:
            bonuses1 = ('%s %s%% (<font color="%s">-%s%%</font>)' % (i18n['UI_TOOLTIPS_Stabilization_Text'], 100 - baseMax, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], resultMax - baseMax), '<font color="%s">%s%%</font>' % (i18n['UI_TOOLTIPS_Stabilization_Color'], 100 - resultMax))
            bonuses2 = ('%s %s%% (<font color="%s">-%s%%</font>)' % (i18n['UI_TOOLTIPS_MovementSpeed_Text'], 100 - baseMovementSpeed, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], resultMovementSpeed - baseMovementSpeed), '<font color="%s">%s%%</font>' % (i18n['UI_TOOLTIPS_MovementSpeed_Color'], 100 - resultMovementSpeed))
            bonuses3 = ('%s %s%% (<font color="%s">-%s%%</font>)' % (i18n['UI_TOOLTIPS_RotatingVehicle_Text'], 100 - baseRotatingVehicle, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], resultRotatingVehicle - baseRotatingVehicle), '<font color="%s">%s%%</font>' % (i18n['UI_TOOLTIPS_RotatingVehicle_Color'], 100 - resultRotatingVehicle))
            bonuses4 = ('%s %s%% (<font color="%s">-%s%%</font>)' % (i18n['UI_TOOLTIPS_RotatingTurret_Text'], 100 - baseRotatingTurret, i18n['UI_TOOLTIPS_StabBonus_ColorPositive'], resultRotatingTurret - baseRotatingTurret), '<font color="%s">%s%%</font>' % (i18n['UI_TOOLTIPS_RotatingTurret_Color'], 100 - resultRotatingTurret))
        else:
            bonuses1 = (i18n['UI_TOOLTIPS_Stabilization_Text'], '<font color="%s">%s%%</font>' % (i18n['UI_TOOLTIPS_Stabilization_Color'], 100 - resultMax))
            bonuses2 = (i18n['UI_TOOLTIPS_MovementSpeed_Text'], '<font color="%s">%s%%</font>' % (i18n['UI_TOOLTIPS_MovementSpeed_Color'], 100 - resultMovementSpeed))
            bonuses3 = (i18n['UI_TOOLTIPS_RotatingVehicle_Text'], '<font color="%s">%s%%</font>' % (i18n['UI_TOOLTIPS_RotatingVehicle_Color'], 100 - resultRotatingVehicle))
            bonuses4 = (i18n['UI_TOOLTIPS_RotatingTurret_Text'], '<font color="%s">%s%%</font>' % (i18n['UI_TOOLTIPS_RotatingTurret_Color'], 100 - resultRotatingTurret))
        if inSettings:
            return 100 - resultMax
        return bonuses, bonuses1, bonuses2, bonuses3, bonuses4


    def construct1(self):
        result = list(old1_construct(self))
        founded = False
        for pack in result:
            if 'name' in pack['data'] and _ms('#menu:moduleInfo/params/' + 'circularVisionRadius') in pack['data']['name']:
                founded = True
        if founded:
            bonuses = p__getStabFactors()
            for bonus in bonuses:
                result.append(formatters1.packTextParameterBlockData(name=bonus[0], value=bonus[1], valueWidth=self._valueWidth, padding=formatters1.packPadding(left=-5)))
        return result

    old1_construct = CommonStatsBlockConstructor1.construct
    CommonStatsBlockConstructor1.construct = construct1

print '[LOAD_MOD]:  [mod_tooltipsCountItemsLimitExtend 1.07 (03-07-2020), by spoter, gox, b4it]'
