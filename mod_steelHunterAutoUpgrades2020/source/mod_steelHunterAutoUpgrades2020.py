# -*- coding: utf-8 -*-
from gui.mods.mod_mods_gui import g_gui as p__g_gui

try:
    from gui.Scaleform.daapi.view.battle.battle_royale.battle_upgrade_panel import BattleUpgradePanel
except StandardError:
    BattleUpgradePanel = False
from helpers import getLanguageCode as p__getLanguageCode


class p__Config(object):
    def __init__(self):
        self.p__id = 'steelHunterAutoUpgrades2020'
        self.p__version = 101
        self.p__versionI18n = 101
        lang = p__getLanguageCode().lower()
        self.p__data = {
            'version'                 : self.p__version,
            'enabled'                 : True,
            'selected_Varyag'         : 0,
            'selected_Walkure'        : 0,
            'selected_Raven'          : 0,
            'selected_Arlequin'       : 0,
            'selected_Harbinger_Mk_IV': 0,
            'Varyag'                  : [
                ['UI_Varyag_1', 1, 1, 1, 2, 2, 2],
                ['UI_Varyag_2', 1, 1, 1, 2, 2, 3],
            ],
            'Walkure'                 : [
                ['UI_Walkure_1', 1, 2, 1, 1, 1, 1],
                ['UI_Walkure_2', 1, 2, 1, 1, 1, 1],
            ],
            'Raven'                   : [
                ['UI_Raven_1', 1, 2, 1, 1, 1, 1],
                ['UI_Raven_2', 1, 2, 1, 1, 1, 1],
            ],
            'Arlequin'                : [
                ['UI_Arlequin_1', 1, 2, 1, 1, 1, 1],
                ['UI_Arlequin_2', 1, 2, 1, 1, 1, 1],
            ],
            'Harbinger_Mk_IV'         : [
                ['UI_Harbinger_Mk_IV_1', 1, 2, 1, 1, 1, 1],
                ['UI_Harbinger_Mk_IV_2', 1, 2, 1, 1, 1, 1],
            ]
        }
        self.p__i18n = {
            'version'                       : self.p__versionI18n,
            'UI_name'                       : 'Steel Hunter Auto Upgrades 2020',
            'UI_Varyag_description'         : 'Varyag',
            'UI_Walkure_description'        : 'Walkure',
            'UI_Raven_description'          : 'Raven',
            'UI_Arlequin_description'       : 'Arlequin',
            'UI_Harbinger_Mk_IV_description': 'Harbinger Mk. IV',

            'UI_Varyag_1'                   : 'Double Gun 1, 1, 1, 2, 2, 2',
            'UI_Varyag_2'                   : 'Damage per Shot 1, 1, 1, 2, 2, 3',

        }
        if 'ru' in lang:
            self.p__i18n.update({
                'UI_name': 'Стальной Охотник Авто Улучшения 2020',
            })

        self.p__data, self.p__i18n = p__g_gui.register_data(self.p__id, self.p__data, self.p__i18n, 'bait')
        p__g_gui.register(self.p__id, self.p__template, self.p__data, self.p__apply)

    def p__template(self):
        return {
            'modDisplayName' : self.p__i18n['UI_name'],
            'settingsVersion': self.p__version,
            'enabled'        : self.p__data['enabled'],
            'column1'        : [
                self.setDropdown('Varyag'),
                self.setDropdown('Walkure'),
                self.setDropdown('Raven'),
                self.setDropdown('Arlequin'),
                self.setDropdown('Harbinger_Mk_IV'),
            ],
            'column2'        : []
        }

    def setDropdown(self, name):
        return {
            'type'        : 'Dropdown',
            'itemRenderer': 'DropDownListItemRendererSound',
            'width'       : 400,
            'varName'     : 'selected_' + name,
            'value'       : self.p__data['selected_' + name],
            'text'        : self.p__i18n['UI_%s_description' % name],
            'tooltip'     : '',
            'options'     : self.p__getLabels(name),
        }

    def p__getLabels(self, name):
        result = []
        for setting in self.p__data[name]:
            result.append({'label': '<p align="center">%s</p>' % (self.p__i18n[setting[0]] if setting[0] in self.p__i18n else str(setting))})
        return result

    def p__apply(self, p__settings):
        self.p__data = p__g_gui.update_data(self.p__id, p__settings, 'spoter')
        p__g_gui.update(self.p__id, self.p__template)


if BattleUpgradePanel:
    VEHICLES = {
        13057: 'Varyag',
        43793: 'Walkure',
        42785: 'Raven',
        13377: 'Arlequin',
        41553: 'Harbinger_Mk_IV',
    }
    p__config = p__Config()


    def setUpgradeEnabled(self):
        result = oldSetUpgradeEnabled(self)
        vehicle = self._getVehicle()
        if vehicle:
            name = VEHICLES[vehicle.intCD]
            ids = 'selected_' + name
            config = self.p__data[name][ids]
            level = self._BattleUpgradePanel__getCurrentLvl() - 1
            self.selectVehicleModule(config[level])
        return result


    oldSetUpgradeEnabled = BattleUpgradePanel.setUpgradeEnabled
    BattleUpgradePanel.setUpgradeEnabled = setUpgradeEnabled
