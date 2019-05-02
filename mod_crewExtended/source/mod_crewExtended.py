# -*- coding: utf-8 -*-
import math

from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui.Scaleform.daapi.view.lobby.barracks import Barracks
from gui.shared.gui_items.dossier import TankmanDossier
from items import tankmen
# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject


class Config(object):
    def __init__(self):
        self.ids = 'crewExtended'
        self.version = 'v6.00 (2019-05-02)'
        self.version_id = 600
        self.author = 'by spoter'
        self.data = {
            'version'                : self.version_id,
            'enabled'                : True,
            'personalFileTotalXP'    : True,
            'personalFileSkillXP'    : True,
            'personalFileSkillBattle': True,
            'currentCrewRankOnTop'   : True,
            'currentCrewRankBattle'  : True,
            'currentCrewRoleBattle'  : False,
            'currentCrewBattleIcon'  : True,
            'currentColorBattle'     : 6,
            'currentCrewRankExp'     : False,
            'currentCrewRoleExp'     : True,
            'currentCrewExpIcon'     : True,
            'currentColorExp'        : 5,
            'barracksEnable'         : True,
            'barracksBattleOrExp'    : True,
            'barracksSkillIcons'     : True,
            'colors'                 : ['0000FF', 'A52A2B', 'D3691E', '6595EE', 'FCF5C8', '00FFFF', '28F09C', 'FFD700', '008000', 'ADFF2E', 'FF69B5', '00FF00', 'FFA500', 'FFC0CB', '800080', 'FF0000', '8378FC', 'DB0400', '80D639', 'FFE041', 'FFFF00', 'FA8072'],
            'color_i18n'             : ['UI_menu_blue', 'UI_menu_brown', 'UI_menu_chocolate', 'UI_menu_cornflower_blue', 'UI_menu_cream', 'UI_menu_cyan', 'UI_menu_emerald', 'UI_menu_gold', 'UI_menu_green', 'UI_menu_green_yellow', 'UI_menu_hot_pink', 'UI_menu_lime', 'UI_menu_orange', 'UI_menu_pink', 'UI_menu_purple', 'UI_menu_red', 'UI_menu_wg_blur', 'UI_menu_wg_enemy', 'UI_menu_wg_friend', 'UI_menu_wg_squad', 'UI_menu_yellow', 'UI_menu_nice_red'],
            'premiumSkillIcon'       : '<img align=\"top\" src=\"img://gui/maps//icons/library/referralCoin-1.png\" height=\"16\" width=\"16\" vspace=\"-3\"/>',
            'battleIcon'             : '<img align=\"top\" src=\"img://gui/maps//icons/library/BattleResultIcon-1.png\" height=\"14\" width=\"14\" vspace=\"-3\"/>',
            'expIcon'                : '<img align=\"top\" src=\"img://gui/maps//icons/library/XpIcon-1.png\" height=\"16\" width=\"16\" vspace=\"-3\"/>'

        }
        self.i18n = {
            'version'                                   : self.version_id,
            'UI_description'                            : 'Crew Extended',
            'UI_setting_personalFileSilverXP_text'      : 'To reset main skill: {} experience',
            'UI_setting_personalFile_label'             : 'Personal File :',
            'UI_setting_personalFileTotalXP_text'       : 'Show total exp',
            'UI_setting_personalFileTotalXP_tooltip'    : '{HEADER}Info:{/HEADER}{BODY}Show Total Experience to current tankman{/BODY}',
            'UI_setting_personalFileSkillXP_text'       : 'Show exp to 100%',
            'UI_setting_personalFileSkillXP_tooltip'    : '{HEADER}Info:{/HEADER}{BODY}Show Experience to current skill with format: to 1% (to 100%){/BODY}',
            'UI_setting_personalFileSkillBattle_text'   : 'Show battles to 100%',
            'UI_setting_personalFileSkillBattle_tooltip': '{HEADER}Info:{/HEADER}{BODY}Show Battles to current skill with format: 1 battle to 1% (100 battle to 100%){/BODY}',
            'UI_setting_currentCrew_label'              : 'Current Crew :',
            'UI_setting_currentColorBattle_text'        : 'Change Battles color',
            'UI_setting_currentColorBattle_tooltip'     : '',
            'UI_setting_currentCrewRankOnTop_text'      : 'Show Rank on Top',
            'UI_setting_currentCrewRankOnTop_tooltip'   : '{HEADER}Info:{/HEADER}{BODY}Default Role on top in current crew list in hangar, change it! :){/BODY}',
            'UI_setting_currentCrewRankBattle_text'     : 'Show Battles in Rank',
            'UI_setting_currentCrewRankBattle_tooltip'  : '{HEADER}Info:{/HEADER}{BODY}Show Battles to current skill in Rank field{/BODY}',
            'UI_setting_currentCrewRoleBattle_text'     : 'Show Battles in Role',
            'UI_setting_currentCrewRoleBattle_tooltip'  : '{HEADER}Info:{/HEADER}{BODY}Show Battles to current skill in Role field{/BODY}',
            'UI_setting_currentCrewBattleIcon_text'     : 'Show Battle Icon',
            'UI_setting_currentCrewBattleIcon_tooltip'  : '',
            'UI_setting_currentCrewRankExp_text'        : 'Show Exp in Rank',
            'UI_setting_currentCrewRankExp_tooltip'     : '{HEADER}Info:{/HEADER}{BODY}Show Exp to current skill in Rank field{/BODY}',
            'UI_setting_currentCrewRoleExp_text'        : 'Show Exp in Role',
            'UI_setting_currentCrewRoleExp_tooltip'     : '{HEADER}Info:{/HEADER}{BODY}Show Exp to current skill in Role field{/BODY}',
            'UI_setting_currentCrewExpIcon_text'        : 'Show Exp Icon',
            'UI_setting_currentCrewExpIcon_tooltip'     : '',
            'UI_setting_currentColorExp_text'           : 'Change Exp color',
            'UI_setting_currentColorExp_tooltip'        : '',
            'UI_setting_barracks_label'                 : 'Barracks :',
            'UI_setting_barracksEnable_text'            : 'Show in Barracks',
            'UI_setting_barracksEnable_tooltip'         : '',
            'UI_setting_barracksBattleOrExp_text'       : 'Show Battle or Exp',
            'UI_setting_barracksBattleOrExp_tooltip'    : '{HEADER}Info:{/HEADER}{BODY}Enabled: Show Battles to next skill level\nDisabled: Show Experience to next skill level{/BODY}',
            'UI_setting_barracksSkillIcons_text'        : 'Show Skill Icons',
            'UI_setting_barracksSkillIcons_tooltip'     : '',
            'UI_menu_blue'                              : 'Blue',
            'UI_menu_brown'                             : 'Brown',
            'UI_menu_chocolate'                         : 'Chocolate',
            'UI_menu_cornflower_blue'                   : 'Cornflower Blue',
            'UI_menu_cream'                             : 'Cream',
            'UI_menu_cyan'                              : 'Cyan',
            'UI_menu_emerald'                           : 'Emerald',
            'UI_menu_gold'                              : 'Gold',
            'UI_menu_green'                             : 'Green',
            'UI_menu_green_yellow'                      : 'Green Yellow',
            'UI_menu_hot_pink'                          : 'Hot Pink',
            'UI_menu_lime'                              : 'Lime',
            'UI_menu_orange'                            : 'Orange',
            'UI_menu_pink'                              : 'Pink',
            'UI_menu_purple'                            : 'Purple',
            'UI_menu_red'                               : 'Red',
            'UI_menu_wg_blur'                           : 'WG Blur',
            'UI_menu_wg_enemy'                          : 'WG Enemy',
            'UI_menu_wg_friend'                         : 'WG Friend',
            'UI_menu_wg_squad'                          : 'WG Squad',
            'UI_menu_yellow'                            : 'Yellow',
            'UI_menu_nice_red'                          : 'Nice Red'

        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    @inject.log
    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'   : 'Label',
                'text'   : self.i18n['UI_setting_currentCrew_label'],
                'tooltip': '',
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_currentCrewBattleIcon_text'],
                'value'  : self.data['currentCrewBattleIcon'],
                'tooltip': self.i18n['UI_setting_currentCrewBattleIcon_tooltip'],
                'varName': 'currentCrewBattleIcon'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_currentCrewRankBattle_text'],
                'value'  : self.data['currentCrewRankBattle'],
                'tooltip': self.i18n['UI_setting_currentCrewRankBattle_tooltip'],
                'varName': 'currentCrewRankBattle'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_currentCrewRoleBattle_text'],
                'value'  : self.data['currentCrewRoleBattle'],
                'tooltip': self.i18n['UI_setting_currentCrewRoleBattle_tooltip'],
                'varName': 'currentCrewRoleBattle'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_currentColorBattle_text'],
                'tooltip'     : self.i18n['UI_setting_currentColorBattle_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['currentColorBattle'],
                'varName'     : 'currentColorBattle'
            }, {
                'type'   : 'Label',
                'text'   : self.i18n['UI_setting_personalFile_label'],
                'tooltip': '',
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_personalFileTotalXP_text'],
                'value'  : self.data['personalFileTotalXP'],
                'tooltip': self.i18n['UI_setting_personalFileTotalXP_tooltip'],
                'varName': 'personalFileTotalXP'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_personalFileSkillBattle_text'],
                'value'  : self.data['personalFileSkillBattle'],
                'tooltip': self.i18n['UI_setting_personalFileSkillBattle_tooltip'],
                'varName': 'personalFileSkillBattle'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_personalFileSkillXP_text'],
                'value'  : self.data['personalFileSkillXP'],
                'tooltip': self.i18n['UI_setting_personalFileSkillXP_tooltip'],
                'varName': 'personalFileSkillXP'
            }],
            'column2'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_currentCrewRankOnTop_text'],
                'value'  : self.data['currentCrewRankOnTop'],
                'tooltip': self.i18n['UI_setting_currentCrewRankOnTop_tooltip'],
                'varName': 'currentCrewRankOnTop'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_currentCrewExpIcon_text'],
                'value'  : self.data['currentCrewExpIcon'],
                'tooltip': self.i18n['UI_setting_currentCrewExpIcon_tooltip'],
                'varName': 'currentCrewExpIcon'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_currentCrewRankExp_text'],
                'value'  : self.data['currentCrewRankExp'],
                'tooltip': self.i18n['UI_setting_currentCrewRankExp_tooltip'],
                'varName': 'currentCrewRankExp'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_currentCrewRoleExp_text'],
                'value'  : self.data['currentCrewRoleExp'],
                'tooltip': self.i18n['UI_setting_currentCrewRoleExp_tooltip'],
                'varName': 'currentCrewRoleExp'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_currentColorExp_text'],
                'tooltip'     : self.i18n['UI_setting_currentColorExp_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['currentColorExp'],
                'varName'     : 'currentColorExp'
            }, {
                'type'   : 'Label',
                'text'   : self.i18n['UI_setting_barracks_label'],
                'tooltip': '',
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_barracksEnable_text'],
                'value'  : self.data['barracksEnable'],
                'tooltip': self.i18n['UI_setting_barracksEnable_tooltip'],
                'varName': 'barracksEnable'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_barracksBattleOrExp_text'],
                'value'  : self.data['barracksBattleOrExp'],
                'tooltip': self.i18n['UI_setting_barracksBattleOrExp_tooltip'],
                'varName': 'barracksBattleOrExp'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_barracksSkillIcons_text'],
                'value'  : self.data['barracksSkillIcons'],
                'tooltip': self.i18n['UI_setting_barracksSkillIcons_tooltip'],
                'varName': 'barracksSkillIcons'
            }]
        }

    @inject.log
    def generator_menu(self):
        res = []
        for i in xrange(0, len(self.data['colors'])):
            res.append({
                'label': '<font color="#%s">%s</font>' % (self.data['colors'][i], self.i18n[self.data['color_i18n'][i]])
            })
        return res

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
                silverXP['premiumValue'] = ''
                index['stats'] += (totalXP, silverXP)
            else:
                index['stats'] += (totalXP,)
        if index['label'] == 'studying':
            for ids in index['stats']:
                if config.data['personalFileSkillXP'] and ids['name'] == 'nextSkillXPLeft':
                    ids['value'] = ' '
                    ids['premiumValue'] = '%s (%s)' % (ids['premiumValue'], dossier._TankmanDossier__formatValueForUI(tankman.getNextSkillXpCost()))
                if config.data['personalFileSkillBattle'] and ids['name'] == 'nextSkillBattlesLeft':
                    battles = dossier.getLastSkillBattlesLeft(tankman)
                    ids['value'] = '%s (%s)' % (ids['value'], dossier._TankmanDossier__formatValueForUI(battles))
                    ids['premiumValue'] = '%s (%s)' % (ids['premiumValue'], dossier._TankmanDossier__formatValueForUI(dossier._TankmanDossier__getBattlesLeftOnPremiumVehicle(battles)))
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

    return data


def generateTextString(dossier, sign, value, premiumSkill):
    color = config.data['colors'][config.data['currentColor%s' % sign]]
    text = ''
    if premiumSkill:
        text = config.data['premiumSkillIcon']
    # noinspection PyProtectedMember
    text += '<font color="#%s">%s </font>' % (color, dossier._TankmanDossier__formatValueForUI(value))
    if config.data['currentCrew%sIcon' % sign]:
        if 'Battle' in sign:
            text += config.data['battleIcon']
        if 'Exp' in sign:
            text += config.data['expIcon']
    return text if config.data['currentCrewRank%s' % sign] else '', text if config.data['currentCrewRole%s' % sign] else ''


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
        for skill in tankman.skills:
            if skill.isEnable and skill.isActive:
                skills += '<img align=\"top\" src=\"img://gui/maps//icons/tankmen/skills/small/%s\" vspace=\"-3\"/>' % skill.icon
                if skill.level < 100:
                    skills += '%s%%' % skill.level
    tankmenData['role'] = text + tankmenData['role'] + skills
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
    if config.data['enabled']:
        return func(args[0], changeTankman(args[1]))
    return func(*args)


@inject.hook(Barracks, '_packTankmanData')
@inject.log
def _packTankmanData(func, *args):
    data = func(*args)
    if config.data['enabled'] and config.data['barracksEnable']:
        return changeBarracksData(args[0], data)
    return data
