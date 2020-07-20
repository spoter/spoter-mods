# -*- coding: utf-8 -*-
import BigWorld
import Math
# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject
from tutorial.control.battle.functional import _StaticObjectMarker3D as p__StaticObjectMarker3D
try:
    from gui.Scaleform.daapi.view.battle.battle_royale.battle_upgrade_panel import BattleUpgradePanel
    from gui.Scaleform.daapi.view.battle.battle_royale.minimap import plugins
    from gui.Scaleform.daapi.view.battle.battle_royale.minimap.settings import MarkersAs3Descr
    from shared_utils import findFirst

    from battleground.loot_object import LootObject
except StandardError:
    BattleUpgradePanel = False
from helpers import getLanguageCode


class Config(object):
    def __init__(self):
        self.ids = 'steelHunterAutoUpgrades2020'
        self.author = 'by spoter'
        self.version = 'v1.05 (2020-07-20)'
        self.version_id = 105
        self.versionI18n = 105
        lang = getLanguageCode().lower()
        self.data = {
            'version'                 : self.version_id,
            'enabled'                 : True,
            'selected_Varyag'         : 1,
            'selected_Walkure'        : 0,
            'selected_Raven'          : 0,
            'selected_Arlequin'       : 0,
            'selected_Harbinger_Mk_IV': 0,
            'Varyag'                  : [
                ['UI_Varyag_DPM_HP', 1, 1, 2, 2, 2, 1],  # DPM HP
                ['UI_Varyag_DPM_Armor', 1, 1, 2, 1, 1, 1],  # DPM Armor
                ['UI_Varyag_Double_Gun_HP', 1, 1, 1, 2, 2, 2],  # Double Gun HP
                ['UI_Varyag_Double_Gun_Armor', 1, 1, 1, 1, 1, 2],  # Double Gun Armor
                ['UI_Varyag_DPS_HP', 1, 1, 2, 2, 2, 3],  # DPS HP
                ['UI_Varyag_DPS_Armor', 1, 1, 2, 1, 2, 3],  # DPS Armor
            ],
            'Walkure'                 : [
                ['UI_Walkure_Machine_Gun_HP', 1, 1, 1, 2, 2, 1],  # Machine Gun HP
                ['UI_Walkure_Machine_Gun_Armor', 1, 1, 1, 1, 1, 1],  # Machine Gun Armor
                ['UI_Walkure_DPM_HP', 1, 1, 1, 2, 2, 2],  # DPM HP
                ['UI_Walkure_DPM_Armor', 1, 1, 1, 1, 1, 2],  # DPM Armor
                ['UI_Walkure_DPS_HP', 1, 1, 1, 2, 2, 3],  # DPS HP
                ['UI_Walkure_DPS_Armor', 1, 1, 1, 1, 2, 3],  # DPS Armor
            ],
            'Raven'                   : [
                ['UI_Raven_DPM_Rotation', 1, 2, 2, 2, 1, 1],  # DPM Rotation
                ['UI_Raven_DPM_Mobility', 1, 2, 2, 1, 1, 1],  # DPM Mobility
                ['UI_Raven_DPM_Armor', 1, 2, 2, 2, 2, 1],  # DPM Armor
                ['UI_Raven_Magazine_Rotation', 1, 2, 1, 2, 1, 2],  # Magazine Rotation
                ['UI_Raven_Magazine_Mobility', 1, 2, 1, 1, 1, 2],  # Magazine Mobility
                ['UI_Raven_Magazine_Speed_Mobility', 1, 1, 1, 1, 1, 2],  # Magazine Speed Mobility
                ['UI_Raven_Magazine_Armor', 1, 2, 1, 2, 2, 2],  # Magazine Armor
                ['UI_Raven_DPS_Mobility', 1, 2, 1, 1, 2, 3],  # DPS Mobility
                ['UI_Raven_DPS_Speed_Mobility', 1, 1, 1, 1, 2, 3],  # DPS Speed Mobility
                ['UI_Raven_DPS_Armor', 1, 2, 1, 2, 2, 3],  # DPS Armor
            ],
            'Arlequin'                : [
                ['UI_Arlequin_Machine_Gun_Dynamics', 1, 2, 2, 1, 1, 1],  # Dynamics Machine Gun
                ['UI_Arlequin_Machine_Gun_Speed_Mobility', 1, 1, 2, 1, 1, 1],  # Speed Mobility Machine Gun
                ['UI_Arlequin_Machine_Gun_HP', 1, 2, 2, 2, 2, 1],  # Machine Gun HP
                ['UI_Arlequin_Double_Gun_Dynamics', 1, 2, 1, 1, 1, 2],  # Double Gun Dynamics
                ['UI_Arlequin_Double_Gun_Speed_Mobility', 1, 1, 1, 1, 1, 2],  # Double Gun Speed Mobility
                ['UI_Arlequin_Double_Gun_HP', 1, 2, 1, 2, 2, 2],  # Double Gun HP
                ['UI_Arlequin_HE_Dynamics', 1, 2, 2, 1, 2, 3],  # HE Dynamics
                ['UI_Arlequin_HE_Speed_Mobility', 1, 1, 2, 1, 2, 3],  # HE Speed Mobility
                ['UI_Arlequin_HE_HP', 1, 2, 2, 2, 2, 3],  # HP HE
            ],
            'Harbinger_Mk_IV'         : [
                ['UI_Harbinger_Mk_IV_DPM_Rotation', 1, 2, 1, 2, 1, 1],  # DPM Rotation
                ['UI_Harbinger_Mk_IV_DPM_Mobility', 1, 2, 1, 1, 1, 1],  # DPM Mobility
                ['UI_Harbinger_Mk_IV_DPM_Armor', 1, 2, 1, 2, 2, 1],  # DPM Armor
                ['UI_Harbinger_Mk_IV_Autoreloader_Rotation', 1, 2, 1, 2, 1, 2],  # Rotation Autoreloader
                ['UI_Harbinger_Mk_IV_Autoreloader_Mobility', 1, 2, 1, 1, 1, 2],  # Mobility Autoreloader
                ['UI_Harbinger_Mk_IV_Autoreloader_Speed_Mobility', 1, 1, 1, 1, 1, 2],  # Speed Mobility Autoreloader
                ['UI_Harbinger_Mk_IV_Autoreloader_Armor', 1, 2, 1, 2, 2, 2],  # Armor Autoreloader
                ['UI_Harbinger_Mk_IV_DPS_Mobility', 1, 2, 1, 1, 2, 3],  # Mobility DPS
                ['UI_Harbinger_Mk_IV_DPS_Speed_Mobility', 1, 1, 1, 1, 2, 3],  # Speed Mobility DPS
                ['UI_Harbinger_Mk_IV_DPS_Armor', 1, 2, 1, 2, 2, 3],  # DPS Armor
            ]
        }
        self.i18n = {
            'version'                                       : self.versionI18n,
            'UI_name'                                       : 'Steel Hunter Auto Upgrades 2020',
            'UI_battleMessage'                              : 'Auto select %s Upgrade to level %s',
            'UI_Varyag_description'                         : 'Varyag',
            'UI_Walkure_description'                        : 'Walkure',
            'UI_Raven_description'                          : 'Raven',
            'UI_Arlequin_description'                       : 'Arlequin',
            'UI_Harbinger_Mk_IV_description'                : 'Harbinger Mk. IV',

            'UI_Varyag_DPM_HP'                              : 'DPM HP [1, 1, 2, 2, 2, 1]',
            'UI_Varyag_DPM_Armor'                           : 'DPM Armor [1, 1, 2, 1, 1, 1]',
            'UI_Varyag_Double_Gun_HP'                       : 'Double Gun HP [1, 1, 1, 2, 2, 2]',
            'UI_Varyag_Double_Gun_Armor'                    : 'Double Gun Armor [1, 1, 1, 1, 1, 2]',
            'UI_Varyag_DPS_HP'                              : 'DPS HP [1, 1, 2, 2, 2, 3]',
            'UI_Varyag_DPS_Armor'                           : 'DPS Armor [1, 1, 2, 1, 2, 3]',

            'UI_Walkure_Machine_Gun_HP'                     : 'Machine Gun HP [1, 1, 1, 2, 2, 1]',
            'UI_Walkure_Machine_Gun_Armor'                  : 'Machine Gun Armor [1, 1, 1, 1, 1, 1]',
            'UI_Walkure_DPM_HP'                             : 'DPM HP [1, 1, 1, 2, 2, 2]',
            'UI_Walkure_DPM_Armor'                          : 'DPM Armor [1, 1, 1, 1, 1, 2]',
            'UI_Walkure_DPS_HP'                             : 'DPS HP [1, 1, 1, 2, 2, 3]',
            'UI_Walkure_DPS_Armor'                          : 'DPS Armor [1, 1, 1, 1, 2, 3]',

            'UI_Raven_DPM_Rotation'                         : 'DPM Rotation [1, 2, 2, 2, 1, 1]',
            'UI_Raven_DPM_Mobility'                         : 'DPM Mobility [1, 2, 2, 1, 1, 1]',
            'UI_Raven_DPM_Armor'                            : 'DPM Armor [1, 2, 2, 2, 2, 1]',
            'UI_Raven_Magazine_Rotation'                    : 'Magazine Rotation [1, 2, 1, 2, 1, 2]',
            'UI_Raven_Magazine_Mobility'                    : 'Magazine Mobility [1, 2, 1, 1, 1, 2]',
            'UI_Raven_Magazine_Speed_Mobility'              : 'Magazine Speed Mobility [1, 1, 1, 1, 1, 2]',
            'UI_Raven_Magazine_Armor'                       : 'Magazine Armor [1, 2, 1, 2, 2, 2]',
            'UI_Raven_DPS_Mobility'                         : 'DPS Mobility [1, 2, 1, 1, 2, 3]',
            'UI_Raven_DPS_Speed_Mobility'                   : 'DPS Speed Mobility [1, 1, 1, 1, 2, 3]',
            'UI_Raven_DPS_Armor'                            : 'DPS Armor [1, 2, 1, 2, 2, 3]',

            'UI_Arlequin_Machine_Gun_Dynamics'              : 'Machine Gun Dynamics [1, 2, 2, 1, 1, 1]',
            'UI_Arlequin_Machine_Gun_Speed_Mobility'        : 'Machine Gun Speed Mobility [1, 1, 2, 1, 1, 1]',
            'UI_Arlequin_Machine_Gun_HP'                    : 'Machine Gun HP [1, 2, 2, 2, 2, 1]',
            'UI_Arlequin_Double_Gun_Dynamics'               : 'Double Gun Dynamics [1, 2, 1, 1, 1, 2]',
            'UI_Arlequin_Double_Gun_Speed_Mobility'         : 'Double Gun Speed Mobility [1, 1, 1, 1, 1, 2]',
            'UI_Arlequin_Double_Gun_HP'                     : 'Double Gun HP [1, 2, 1, 2, 2, 2]',
            'UI_Arlequin_HE_Dynamics'                       : 'HE Dynamics [1, 2, 2, 1, 2, 3]',
            'UI_Arlequin_HE_Speed_Mobility'                 : 'HE Speed Mobility [1, 1, 2, 1, 2, 3]',
            'UI_Arlequin_HE_HP'                             : 'HE HP [1, 2, 2, 2, 2, 3]',

            'UI_Harbinger_Mk_IV_DPM_Rotation'               : 'DPM Rotation [1, 2, 1, 2, 1, 1]',
            'UI_Harbinger_Mk_IV_DPM_Mobility'               : 'DPM Mobility [1, 2, 1, 1, 1, 1]',
            'UI_Harbinger_Mk_IV_DPM_Armor'                  : 'DPM Armor [1, 2, 1, 2, 2, 1]',
            'UI_Harbinger_Mk_IV_Autoreloader_Rotation'      : 'Autoreloader Rotation [1, 2, 1, 2, 1, 2]',
            'UI_Harbinger_Mk_IV_Autoreloader_Mobility'      : 'Autoreloader Mobility [1, 2, 1, 1, 1, 2]',
            'UI_Harbinger_Mk_IV_Autoreloader_Speed_Mobility': 'Autoreloader Speed Mobility [1, 1, 1, 1, 1, 2]',
            'UI_Harbinger_Mk_IV_Autoreloader_Armor'         : 'Autoreloader Armor [1, 2, 1, 2, 2, 2]',
            'UI_Harbinger_Mk_IV_DPS_Mobility'               : 'DPS Mobility [1, 2, 1, 1, 2, 3]',
            'UI_Harbinger_Mk_IV_DPS_Speed_Mobility'         : 'DPS Speed Mobility [1, 1, 1, 1, 2, 3]',
            'UI_Harbinger_Mk_IV_DPS_Armor'                  : 'DPS Armor [1, 2, 1, 2, 2, 3]',

        }
        if 'ru' in lang:
            self.i18n.update({
                'UI_name'                                       : 'Стальной Охотник Авто Улучшения 2020',
                'UI_Varyag_description'                         : 'Варяг',
                'UI_battleMessage'                              : 'Авто выбор %s Улучшения для уровня %s',
                'UI_Varyag_DPM_HP'                              : 'Уроний в ХП [1, 1, 2, 2, 2, 1]',
                'UI_Varyag_DPM_Armor'                           : 'Уроний в броню [1, 1, 2, 1, 1, 1]',
                'UI_Varyag_Double_Gun_HP'                       : 'Шотган в ХП [1, 1, 1, 2, 2, 2]',
                'UI_Varyag_Double_Gun_Armor'                    : 'Шотган в броню [1, 1, 1, 1, 1, 2]',
                'UI_Varyag_DPS_HP'                              : 'Скорострелка в ХП [1, 1, 2, 2, 2, 3]',
                'UI_Varyag_DPS_Armor'                           : 'Скорострелка в броню [1, 1, 2, 1, 2, 3]',

                'UI_Walkure_Machine_Gun_HP'                     : 'Барабан в ХП [1, 1, 1, 2, 2, 1]',
                'UI_Walkure_Machine_Gun_Armor'                  : 'Барабан в броню [1, 1, 1, 1, 1, 1]',
                'UI_Walkure_DPM_HP'                             : 'Уроний в ХП [1, 1, 1, 2, 2, 2]',
                'UI_Walkure_DPM_Armor'                          : 'Уроний в броню [1, 1, 1, 1, 1, 2]',
                'UI_Walkure_DPS_HP'                             : 'Скорострелка в ХП [1, 1, 1, 2, 2, 3]',
                'UI_Walkure_DPS_Armor'                          : 'Скорострелка в броню [1, 1, 1, 1, 2, 3]',

                'UI_Raven_DPM_Rotation'                         : 'Уроний в вёрткость [1, 2, 2, 2, 1, 1]',
                'UI_Raven_DPM_Mobility'                         : 'Уроний в подвижность [1, 2, 2, 1, 1, 1]',
                'UI_Raven_DPM_Armor'                            : 'Уроний в броню [1, 2, 2, 2, 2, 1]',
                'UI_Raven_Magazine_Rotation'                    : 'Барабан в вёрткость [1, 2, 1, 2, 1, 2]',
                'UI_Raven_Magazine_Mobility'                    : 'Барабан в подвижность [1, 2, 1, 1, 1, 2]',
                'UI_Raven_Magazine_Speed_Mobility'              : 'Барабан в скорость [1, 1, 1, 1, 1, 2]',
                'UI_Raven_Magazine_Armor'                       : 'Барабан в броню [1, 2, 1, 2, 2, 2]',
                'UI_Raven_DPS_Mobility'                         : 'Скорострелка в подвижность [1, 2, 1, 1, 2, 3]',
                'UI_Raven_DPS_Speed_Mobility'                   : 'Скорострелка в скорость [1, 1, 1, 1, 2, 3]',
                'UI_Raven_DPS_Armor'                            : 'Скорострелка в броню [1, 2, 1, 2, 2, 3]',

                'UI_Arlequin_Machine_Gun_Dynamics'              : 'Барабан в подвижность [1, 2, 2, 1, 1, 1]',
                'UI_Arlequin_Machine_Gun_Speed_Mobility'        : 'Барабан в скорость [1, 1, 2, 1, 1, 1]',
                'UI_Arlequin_Machine_Gun_HP'                    : 'Барабан в ХП [1, 2, 2, 2, 2, 1]',
                'UI_Arlequin_Double_Gun_Dynamics'               : 'Шотган в подвижность [1, 2, 1, 1, 1, 2]',
                'UI_Arlequin_Double_Gun_Speed_Mobility'         : 'Шотган в скорость [1, 1, 1, 1, 1, 2]',
                'UI_Arlequin_Double_Gun_HP'                     : 'Шотган в ХП [1, 2, 1, 2, 2, 2]',
                'UI_Arlequin_HE_Dynamics'                       : 'Фугаска в подвижность [1, 2, 2, 1, 2, 3]',
                'UI_Arlequin_HE_Speed_Mobility'                 : 'Фугаска в скорость [1, 1, 2, 1, 2, 3]',
                'UI_Arlequin_HE_HP'                             : 'Фугаска в ХП [1, 2, 2, 2, 2, 3]',

                'UI_Harbinger_Mk_IV_DPM_Rotation'               : 'Уроний вёрткость [1, 2, 1, 2, 1, 1]',
                'UI_Harbinger_Mk_IV_DPM_Mobility'               : 'Уроний в подвижность [1, 2, 1, 1, 1, 1]',
                'UI_Harbinger_Mk_IV_DPM_Armor'                  : 'Уроний в броню [1, 2, 1, 2, 2, 1]',
                'UI_Harbinger_Mk_IV_Autoreloader_Rotation'      : 'Барабан вёрткость [1, 2, 1, 2, 1, 2]',
                'UI_Harbinger_Mk_IV_Autoreloader_Mobility'      : 'Барабан подвижность [1, 2, 1, 1, 1, 2]',
                'UI_Harbinger_Mk_IV_Autoreloader_Speed_Mobility': 'Барабан в скорость [1, 1, 1, 1, 1, 2]',
                'UI_Harbinger_Mk_IV_Autoreloader_Armor'         : 'Барабан в броню [1, 2, 1, 2, 2, 2]',
                'UI_Harbinger_Mk_IV_DPS_Mobility'               : 'Скорострелка в подвижность [1, 2, 1, 1, 2, 3]',
                'UI_Harbinger_Mk_IV_DPS_Speed_Mobility'         : 'Скорострелка в скорость [1, 1, 1, 1, 2, 3]',
                'UI_Harbinger_Mk_IV_DPS_Armor'                  : 'Скорострелка в броню [1, 2, 1, 2, 2, 3]',
            })

        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_name'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
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
            'value'       : self.data['selected_' + name],
            'text'        : self.i18n['UI_%s_description' % name],
            'tooltip'     : '',
            'options'     : self.getLabels(name),
        }

    def getLabels(self, name):
        result = []
        for setting in self.data[name]:
            result.append({'label': '<p align="center">%s</p>' % (self.i18n[setting[0]] if setting[0] in self.i18n else str(setting))})
        return result

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


if BattleUpgradePanel:
    VEHICLES = {
        13057: 'Varyag',
        43793: 'Walkure',
        42785: 'Raven',
        13377: 'Arlequin',
        41553: 'Harbinger_Mk_IV',
    }
    p__config = Config()


    @inject.hook(BattleUpgradePanel, '_BattleUpgradePanel__onVehicleStateUpdated')
    @inject.log
    def onVehicleStateUpdated(func, *args):
        result = func(*args)
        if not p__config.data['enabled']:
            return result
        self = args[0]
        if self._BattleUpgradePanel__vehicleIsAlive and self._BattleUpgradePanel__localVisible and self._BattleUpgradePanel__isEnabled and self._BattleUpgradePanel__upgrades:
            vehicle = self._getVehicle()
            name = VEHICLES[vehicle.intCD]
            ids = p__config.data['selected_' + name]
            config = p__config.data[name][ids]
            level = self._BattleUpgradePanel__getCurrentLvl()
            selectedItem = config[level]
            self.selectVehicleModule(config[selectedItem] - 1)
            #inject.message(p__config.i18n['UI_battleMessage'] % (selectedItem, level))
        return result


    @inject.hook(plugins.BattleRoyaleRadarPlugin, '_addLootEntry')
    @inject.log
    def addLootEntry(func, *args):
        entryId = func(*args)
        if not p__config.data['enabled']:
            return entryId

        self, typeId, xzPosition = args
        try:
            found = entryId in self._lootEntriesModels
        except:
            self._lootEntriesModels = {}
            found = False

        vEntry = findFirst(lambda entry: entry.entryId == entryId, self._lootEntries)
        if vEntry is not None:
            matrix = self._RadarPlugin__getMatrixByXZ(xzPosition)
            position = matrix.translation
            testResTerrain = BigWorld.wg_collideSegment(BigWorld.player().spaceID, Math.Vector3(position.x, 1000.0, position.z), Math.Vector3(position.x, -1000, position.z), 128)
            if testResTerrain is not None:
                position.y = testResTerrain.closestPoint[1]
            if not found:
                lootTypeParam = self._BattleRoyaleRadarPlugin__getLootMarkerByTypeId(typeId)
                modelPath = 'objects/lootYellow.model'
                if 'improved' in lootTypeParam:
                    modelPath = 'objects/lootGreen.model'
                if 'airdrop' in lootTypeParam:
                    modelPath = 'objects/lootBlue.model'
                self._lootEntriesModels[entryId] = p__StaticObjectMarker3D({
                    'path': modelPath
                }, position)
                self._lootEntriesModels[entryId]._StaticObjectMarker3D__model.scale = Math.Vector3(1.0, 400, 1.0) * 0.1
            self._lootEntriesModels[entryId]._StaticObjectMarker3D__model.position = position
        return entryId


    @inject.hook(plugins.BattleRoyaleRadarPlugin, 'timeOutDone')
    @inject.log
    def timeOutDone(func, *args):
        result = func(*args)
        if p__config.data['enabled']:
            self = args[0]
            for entryId in self._lootEntriesModels:
                self._lootEntriesModels[entryId].clear()
            self._lootEntriesModels = {}
        return result