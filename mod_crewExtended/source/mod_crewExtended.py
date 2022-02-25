# -*- coding: utf-8 -*-
import math

# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

import BigWorld
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.barracks import barracks_data_provider
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.shared.gui_items.dossier import TankmanDossier
from items import tankmen


class Config(object):
    def __init__(self):
        self.ids = 'crewExtended'
        self.version = 'v6.04 (2022-02-25)'
        self.version_id = 604
        self.author = 'by spoter'
        self.dataDefault = {
            'version'                        : self.version_id,
            'enabled'                        : True,
            'personalFileTotalXP'            : True,
            'personalFileSkillXP'            : True,
            'personalFileSkillBattle'        : True,
            'currentCrewRankOnTop'           : True,
            'currentCrewRankBattle'          : True,
            'currentCrewRoleBattle'          : False,
            'currentCrewBattleIcon'          : True,
            'currentColorBattle'             : '#28F09C',
            'currentCrewRankExp'             : False,
            'currentCrewRoleExp'             : True,
            'currentCrewExpIcon'             : True,
            'currentCrewShowNewSkillPercent' : True,
            'currentCrewShowSkillResetStatus': True,
            'currentColorExp'                : '#00FFFF',
            'barracksEnable'                 : True,
            'barracksBattleOrExp'            : True,
            'barracksSkillIcons'             : True,
            'premiumSkillIcon'               : '<img align=\"top\" src=\"img://gui/maps//icons/library/referralCoin-1.png\" height=\"16\" width=\"16\" vspace=\"-3\"/>',
            'battleIcon'                     : '<img align=\"top\" src=\"img://gui/maps//icons/library/BattleResultIcon-1.png\" height=\"14\" width=\"14\" vspace=\"-3\"/>',
            'expIcon'                        : '<img align=\"top\" src=\"img://gui/maps//icons/library/XpIcon-1.png\" height=\"16\" width=\"16\" vspace=\"-3\"/>'

        }
        self.i18n = {
            'version'                                           : self.version_id,
            'UI_description'                                    : 'Crew: extended tank crew data - crew experience',
            'UI_setting_personalFileSilverXP_text'              : 'To reset main skill: {} experience',
            'UI_setting_personalFile_label'                     : 'Personal File :',
            'UI_setting_personalFileTotalXP_text'               : 'Show total exp',
            'UI_setting_personalFileTotalXP_tooltip'            : '{HEADER}Info:{/HEADER}{BODY}Show Total Experience to current tankman{/BODY}',
            'UI_setting_personalFileSkillXP_text'               : 'Show exp to 100%',
            'UI_setting_personalFileSkillXP_tooltip'            : '{HEADER}Info:{/HEADER}{BODY}Show Experience to current skill with format: to 1% (to 100%){/BODY}',
            'UI_setting_personalFileSkillBattle_text'           : 'Show battles to 100%',
            'UI_setting_personalFileSkillBattle_tooltip'        : '{HEADER}Info:{/HEADER}{BODY}Show Battles to current skill with format: 1 battle to 1% (100 battle to 100%){/BODY}',
            'UI_setting_currentCrew_label'                      : 'Current Crew :',
            'UI_setting_currentColorBattle_text'                : 'Change Battles color',
            'UI_setting_currentColorBattle_tooltip'             : '',
            'UI_setting_currentColorBattle_default'             : 'Default: %s' % self.dataDefault['currentColorBattle'],
            'UI_setting_currentCrewRankOnTop_text'              : 'Show Rank on Top',
            'UI_setting_currentCrewRankOnTop_tooltip'           : '{HEADER}Info:{/HEADER}{BODY}Default Role on top in current crew list in hangar, change it! :){/BODY}',
            'UI_setting_currentCrewRankBattle_text'             : 'Show Battles in Rank',
            'UI_setting_currentCrewRankBattle_tooltip'          : '{HEADER}Info:{/HEADER}{BODY}Show Battles to current skill in Rank field{/BODY}',
            'UI_setting_currentCrewRoleBattle_text'             : 'Show Battles in Role',
            'UI_setting_currentCrewRoleBattle_tooltip'          : '{HEADER}Info:{/HEADER}{BODY}Show Battles to current skill in Role field{/BODY}',
            'UI_setting_currentCrewBattleIcon_text'             : 'Show Battle Icon',
            'UI_setting_currentCrewBattleIcon_tooltip'          : '',
            'UI_setting_currentCrewRankExp_text'                : 'Show Exp in Rank',
            'UI_setting_currentCrewRankExp_tooltip'             : '{HEADER}Info:{/HEADER}{BODY}Show Exp to current skill in Rank field{/BODY}',
            'UI_setting_currentCrewRoleExp_text'                : 'Show Exp in Role',
            'UI_setting_currentCrewRoleExp_tooltip'             : '{HEADER}Info:{/HEADER}{BODY}Show Exp to current skill in Role field{/BODY}',
            'UI_setting_currentCrewExpIcon_text'                : 'Show Exp Icon',
            'UI_setting_currentCrewExpIcon_tooltip'             : '',
            'UI_setting_currentCrewShowNewSkillPercent_text'    : 'Show percentage new skills',
            'UI_setting_currentCrewShowNewSkillPercent_tooltip' : '',
            'UI_setting_currentCrewShowSkillResetStatus_text'   : 'Show skill reset without gold',
            'UI_setting_currentCrewShowSkillResetStatus_tooltip': '',
            'UI_setting_currentColorExp_text'                   : 'Change Exp color',
            'UI_setting_currentColorExp_tooltip'                : '',
            'UI_setting_currentColorExp_default'                : 'Default: %s' % self.dataDefault['currentColorExp'],
            'UI_setting_barracks_label'                         : 'Barracks :',
            'UI_setting_barracksEnable_text'                    : 'Show in Barracks',
            'UI_setting_barracksEnable_tooltip'                 : '',
            'UI_setting_barracksBattleOrExp_text'               : 'Show Battle or Exp',
            'UI_setting_barracksBattleOrExp_tooltip'            : '{HEADER}Info:{/HEADER}{BODY}Enabled: Show Battles to next skill level\nDisabled: Show Experience to next skill level{/BODY}',
            'UI_setting_barracksSkillIcons_text'                : 'Show Skill Icons',
            'UI_setting_barracksSkillIcons_tooltip'             : '',
            'UI_setting_premiumSkillIcon_text'                  : 'Icon: Premium crew member',
            'UI_setting_premiumSkillIcon_tooltip'               : '',
            'UI_setting_battleIcon_text'                        : 'Icon: Battle',
            'UI_setting_battleIcon_tooltip'                     : '',
            'UI_setting_expIcon_text'                           : 'Icon: Experience',
            'UI_setting_expIcon_tooltip'                        : '',

        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.dataDefault, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {'modDisplayName': self.i18n['UI_description'], 'settingsVersion': self.version_id, 'enabled': self.data['enabled'], 'column1': self._getLeftOptions(), 'column2': self._getRightOptions()}

    def _getLeftOptions(self):
        return [
            g_gui.optionLabel(self.i18n['UI_setting_currentCrew_label']),
            g_gui.optionCheckBox(*self.p__getI18nParam('currentCrewBattleIcon')),
            g_gui.optionCheckBox(*self.p__getI18nParam('currentCrewRankBattle')),
            g_gui.optionCheckBox(*self.p__getI18nParam('currentCrewRoleBattle')),
            g_gui.optionCheckBox(*self.p__getI18nParam('currentCrewShowNewSkillPercent')),
            g_gui.optionCheckBox(*self.p__getI18nParam('currentCrewRankOnTop')),
            g_gui.optionCheckBox(*self.p__getI18nParam('currentCrewExpIcon')),
            g_gui.optionCheckBox(*self.p__getI18nParam('currentCrewRankExp')),
            g_gui.optionCheckBox(*self.p__getI18nParam('currentCrewRoleExp')),
            g_gui.optionCheckBox(*self.p__getI18nParam('currentCrewShowSkillResetStatus')),
            g_gui.optionLabel(self.i18n['UI_setting_personalFile_label']),
            g_gui.optionCheckBox(*self.p__getI18nParam('personalFileTotalXP')),
            g_gui.optionCheckBox(*self.p__getI18nParam('personalFileSkillBattle')),
            g_gui.optionCheckBox(*self.p__getI18nParam('personalFileSkillXP')),
            g_gui.optionLabel(self.i18n['UI_setting_barracks_label']),
            g_gui.optionCheckBox(*self.p__getI18nParam('barracksEnable')),
            g_gui.optionCheckBox(*self.p__getI18nParam('barracksBattleOrExp')),
            g_gui.optionCheckBox(*self.p__getI18nParam('barracksSkillIcons')),
        ]

    def _getRightOptions(self):
        return [
            g_gui.optionColorHEX(*self.p__getI18nParam('currentColorBattle')),
            g_gui.optionColorHEX(*self.p__getI18nParam('currentColorExp')),
            g_gui.optionTextInput(*self.p__getI18nParam('premiumSkillIcon')),
            g_gui.optionTextInput(*self.p__getI18nParam('battleIcon')),
            g_gui.optionTextInput(*self.p__getI18nParam('expIcon')),
        ]

    def p__getI18nParam(self, name):
        # return varName, value, defaultValue, text, tooltip, defaultValueText
        tooltip = 'UI_setting_%s_tooltip' % name
        tooltip = self.i18n[tooltip] if tooltip in self.i18n else ''
        defaultValueText = 'UI_setting_%s_default' % name
        defaultValueText = self.i18n[defaultValueText] if defaultValueText in self.i18n else '%s' % self.dataDefault[name]
        return name, self.data[name], self.dataDefault[name], self.i18n['UI_setting_%s_text' % name], tooltip, defaultValueText

    def p__getI18nParamSlider(self, name, minValue, maxValue, step):
        # return varName, value, defaultValue, minValue, maxValue, step, text, formats, tooltip, defaultValueText
        params = self.p__getI18nParam(name)
        formats = 'UI_setting_%s_formats' % name
        formats = self.i18n[formats] if formats in self.i18n else ''
        return params[0], params[1], params[2], minValue, maxValue, step, params[3], formats, params[4], params[5]

    @inject.log
    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


@inject.log
def getLastSkillBattlesLeft(self, tankman):
    if not self.getBattlesCount():
        result = None
    else:
        avgExp = self.getAvgXP()
        newSkillReady = self.tmanDescr.roleLevel == tankmen.MAX_SKILL_LEVEL and (len(self.tmanDescr.skills) == 0 or self.tmanDescr.lastSkillLevel == tankmen.MAX_SKILL_LEVEL)
        if avgExp and not newSkillReady:
            result = max(1, int(math.ceil(tankman.getNextSkillXpCost() / avgExp)))
        else:
            result = 0
    return result


# noinspection PyProtectedMember
@inject.log
def changeStats(data, dossier, tankman):
    for index in data:
        if config.data['personalFileTotalXP'] and index['label'] == 'common':
            totalXP = dossier._TankmanDossier__packStat('xp', tankman.descriptor.totalXP())
            isMaxRoleLevel = tankman.roleLevel == 100
            if isMaxRoleLevel:
                silverXP = dossier._TankmanDossier__packStat('empty', 0)
                silverXP['value'] = config.i18n['UI_setting_personalFileSilverXP_text'].format(dossier._TankmanDossier__formatValueForUI(min(0, tankman.descriptor.freeXP - 39153)))
                silverXP['secondValue'] = ''
                index['stats'] += (totalXP, silverXP)
            else:
                index['stats'] += (totalXP,)
        if index['label'] == 'studying':
            for ids in index['stats']:
                if config.data['personalFileSkillXP'] and ids['name'] == 'nextSkillXPLeft':
                    ids['value'] = ' '
                    ids['secondValue'] = '%s (%s)' % (ids['secondValue'], dossier._TankmanDossier__formatValueForUI(tankman.getNextSkillXpCost()))
                if config.data['personalFileSkillBattle'] and ids['name'] == 'nextSkillBattlesLeft':
                    battles = dossier.getLastSkillBattlesLeft(tankman)
                    ids['value'] = '%s (%s)' % (ids['value'], dossier._TankmanDossier__formatValueForUI(battles))
                    ids['secondValue'] = '%s (%s)' % (ids['secondValue'], dossier._TankmanDossier__formatValueForUI(dossier._TankmanDossier__getBattlesLeftOnPremiumVehicle(battles)))
    return data


# noinspection PyProtectedMember
@inject.log
def changeTankman(data):
    for tankmenData in data['tankmen']:
        if tankmenData['tankmanID'] in g_currentVehicle.item.crewIndices:
            if config.data['currentCrewRankOnTop']:
                role, rank = (tankmenData['role'], tankmenData['rank'])
                tankmenData['role'], tankmenData['rank'] = (rank, role)
            tankman = g_currentVehicle.itemsCache.items.getTankman(tankmenData['tankmanID'])
            dossier = g_currentVehicle.itemsCache.items.getTankmanDossier(tankmenData['tankmanID'])
            exp = max(1, tankman.getNextSkillXpCost() if not None else 0)
            battles = max(1, dossier.getLastSkillBattlesLeft(tankman) if not None else 0)
            if g_currentVehicle.item.isPremium:
                battles = dossier._TankmanDossier__getBattlesLeftOnPremiumVehicle(battles)
            textBattle = generateTextString(dossier, 'Battle', battles, config.data['currentCrewRankOnTop'] and tankman.descriptor.freeSkillsNumber)
            textExp = generateTextString(dossier, 'Exp', exp, not config.data['currentCrewRankOnTop'] and tankman.descriptor.freeSkillsNumber)
            tankmenData['rank'] = textBattle[0] + textExp[0] + tankmenData['rank']
            tankmenData['role'] = textBattle[1] + textExp[1] + tankmenData['role']
            if config.data['currentCrewShowNewSkillPercent'] or config.data['currentCrewShowSkillResetStatus']:
                for skill in tankmenData['skills']:
                    if 'buyCount' in skill:
                        newSkillsCount, lastNewSkillLvl = tankman.newSkillCount
                        level = (newSkillsCount - 1) * 100 + lastNewSkillLvl
                        if level > 0 and level != 100:
                            skill['active'] = tankman.descriptor.freeXP > 39153 if config.data['currentCrewShowSkillResetStatus'] else True
                            skill['icon'] = u'new_skill.png'
                            skill['buy'] = False
                            tankmenData['lastSkillLevel'] = level if config.data['currentCrewShowNewSkillPercent'] else 100
    return data


def generateTextString(dossier, sign, value, premiumSkill):
    text = ''
    if premiumSkill:
        text = config.data['premiumSkillIcon']
    # noinspection PyProtectedMember
    text += '<font color="%s">%s </font>' % (config.data['currentColor%s' % sign], dossier._TankmanDossier__formatValueForUI(value))
    if config.data['currentCrew%sIcon' % sign]:
        if 'Battle' in sign:
            text += config.data['battleIcon']
        if 'Exp' in sign:
            text += config.data['expIcon']
    return text if config.data['currentCrewRank%s' % sign] else '', text if config.data['currentCrewRole%s' % sign] else ''


# noinspection PyUnresolvedReferences
def checkXVM():
    try:
        return BigWorld.XVMLoaded
    except StandardError:
        try:
            from xvm_main.python import PATH
            BigWorld.XVMLoaded = True
        except StandardError:
            BigWorld.XVMLoaded = False
    return BigWorld.XVMLoaded


def changeBarracksData(tankman, tankmenData):
    dossier = g_currentVehicle.itemsCache.items.getTankmanDossier(tankmenData['tankmanID'])
    if config.data['barracksBattleOrExp']:
        battles = max(1, dossier.getLastSkillBattlesLeft(tankman) if not None else 0)
        if g_currentVehicle.item.isPremium:
            # noinspection PyProtectedMember
            battles = dossier._TankmanDossier__getBattlesLeftOnPremiumVehicle(battles)
        text, _ = generateTextString(dossier, 'Battle', battles, tankman.descriptor.freeSkillsNumber)
    else:
        exp = max(1, tankman.getNextSkillXpCost() if not None else 0)
        _, text = generateTextString(dossier, 'Exp', exp, tankman.descriptor.freeSkillsNumber)
    skills = ''
    if config.data['barracksSkillIcons']:
        newSkillsCount, lastNewSkillLvl = tankman.newSkillCount
        level = (newSkillsCount - 1) * 100 + lastNewSkillLvl
        for skill in tankman.skills:
            if skill.isEnable:
                skills += '<img align=\"top\" src=\"img://gui/maps//icons/tankmen/skills/small/%s\" vspace=\"-3\"/>' % skill.icon
                if skill.level < 100 and not newSkillsCount:
                    skills += '%s%%' % skill.level
        if level > -1:
            skills += '<img align=\"top\" src=\"img://gui/maps//icons/tankmen/skills/small/new_skill.png\" vspace=\"-3\"/>%s%%' % level
    tankmenData['role'] = text + ' ' + tankmenData['role'] + skills
    return tankmenData


config = Config()
TankmanDossier.getLastSkillBattlesLeft = getLastSkillBattlesLeft


@inject.hook(TankmanDossier, 'getStats')
@inject.log
def getStats(func, *args):
    if config.data['enabled']:
        return changeStats(func(*args), *args)
    return func(*args)


@inject.hook(CrewMeta, 'as_tankmenResponseS')
@inject.log
def tankmanResponse(func, *args):
    import BigWorld
    BigWorld.tankmanResponse = args[0]
    if config.data['enabled']:
        return func(args[0], changeTankman(args[1]))
    return func(*args)


@inject.hook(barracks_data_provider, '_packTankmanData')
@inject.log
def _packTankmanData(func, *args):
    data = func(*args)
    if config.data['enabled'] and config.data['barracksEnable'] and not checkXVM():
        return changeBarracksData(args[0], data)
    return data
