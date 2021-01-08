# -*- coding: utf-8 -*-
import codecs as p__codecs
import collections as p__collections
import json as p__json
import os as p__os
import threading as p__threading
from Queue import Queue as p__Queue
from functools import partial as p__partial

import BattleReplay as p__BattleReplay
import BigWorld as p__BigWorld
import Event
import Keys as p__Keys
import ResMgr as p__ResMgr
from Avatar import PlayerAvatar as p__PlayerAvatar
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as p__BATTLE_EVENT_TYPE
from CurrentVehicle import g_currentVehicle as p__g_currentVehicle
from PlayerEvents import g_playerEvents as p__g_playerEvents
from constants import ARENA_BONUS_TYPE as p__ARENA_BONUS_TYPE
from gui import InputHandler as p__InputHandler
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView as p__LobbyView
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta as p__CrewMeta
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, g_entitiesFactories
from frameworks.wulf import WindowLayer as ViewTypes
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control.arena_info import vos_collections as p__vos_collections
from gui.battle_control.battle_constants import VEHICLE_DEVICE_IN_COMPLEX_ITEM, VEHICLE_VIEW_STATE
from gui.battle_control.controllers import feedback_events as p__feedback_events
from gui.mods.mod_mods_gui import COMPONENT_ALIGN as p__COMPONENT_ALIGN, COMPONENT_EVENT as p__COMPONENT_EVENT, COMPONENT_TYPE as p__COMPONENT_TYPE, g_gui as p__g_gui, g_guiFlash as p__g_flash
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.formatters import icons
from gui.shared.gui_items import Vehicle
from gui.shared.personality import ServicesLocator, ServicesLocator as p__ServicesLocator
from helpers import getLanguageCode as p__getLanguageCode
from messenger.formatters.service_channel import BattleResultsFormatter as p__BattleResultsFormatter

try:
    from gui import oldskool
    oldskoolCore = p__BigWorld.oldskoolCore
except:
    oldskoolCore = False
oldskoolCore = False

class flashInHangar():

    def __init__(self):
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__componentRegisteringHandler, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, self.__onAppInitialized, scope=EVENT_BUS_SCOPE.GLOBAL)

        g_entitiesFactories.addSettings(ViewSettings('creditCalc', FlashMeta, 'creditCalc.swf', ViewTypes.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE))

        self.onHeaderUpdate = Event.Event()
        self.onHangarLoaded = Event.Event()
        self.setPosition = Event.Event()
        self.setBackground = Event.Event()
        self.setText = Event.Event()

    def __onAppInitialized(self, event):
        if event.ns == APP_NAME_SPACE.SF_LOBBY:
            app = ServicesLocator.appLoader.getApp(event.ns)
            if app is None:
                return
            app.loadView(SFViewLoadParams('creditCalc'))

    def __componentRegisteringHandler(self, event):
        if event.alias == HANGAR_ALIASES.AMMUNITION_PANEL:
            if not p__config.p__data['hangar_show']:
                return
            self.setPosition(p__config.p__data['hangar_x'], p__config.p__data['hangar_y'])  # x and y
            self.setBackground(p__config.p__data['battle_background'], '0x000000', 0.4)  # change to false if dont want
            # self.setText('Test Test Test')  # text


class FlashMeta(View):

    def _populate(self):
        super(FlashMeta, self)._populate()
        p__flashInHangar.setText += self._setText
        p__flashInHangar.setPosition += self._setPosition
        p__flashInHangar.setBackground += self._setBackground

    def _dispose(self):
        super(FlashMeta, self)._dispose()

    def py_newPos(self, posX, posY):
        p__config.p__data['hangar_x'] = posX
        p__config.p__data['hangar_y'] = posY
        p__config.p__apply(p__config.p__data)

    def _setText(self, text):
        if self._isDAAPIInited():
            self.flashObject.as_setText(text)

    def _setPosition(self, x, y):
        if self._isDAAPIInited():
            self.flashObject.as_setPosition(x, y)

    def _setBackground(self, enabled, bgcolor, alpha):
        if self._isDAAPIInited():
            self.flashObject.as_setBackground(enabled, bgcolor, alpha)


p__CHASSIS_ALL_ITEMS = frozenset(VEHICLE_DEVICE_IN_COMPLEX_ITEM.keys() + VEHICLE_DEVICE_IN_COMPLEX_ITEM.values())
p__DAMAGE_EVENTS = frozenset([p__BATTLE_EVENT_TYPE.RADIO_ASSIST, p__BATTLE_EVENT_TYPE.TRACK_ASSIST, p__BATTLE_EVENT_TYPE.STUN_ASSIST, p__BATTLE_EVENT_TYPE.DAMAGE, p__BATTLE_EVENT_TYPE.TANKING, p__BATTLE_EVENT_TYPE.RECEIVED_DAMAGE])

p__DEBUG = True
p__DEBUG_COEFF = True


class p__Config(object):
    def __init__(self):
        self.p__ids = 'creditCalc'
        self.author = 'www.b4it.org'
        self.version = 'v2.07 (2021-01-09)'
        self.version_id = 207
        self.p__versionI18n = 3400
        lang = p__getLanguageCode().lower()
        self.p__data = {
            'version'   : self.version_id,
            'enabled'   : True,
            'battle_x'  : 60,
            'battle_y'  : -252,
            'hangar_x'  : 325.0,
            'hangar_y'  : 505.0,
            'battle_background': True,
            'battle_show': True,
            'hangar_background': True,
            'hangar_show': True,
        }
        self.p__i18n = {
            'version'                      : self.p__versionI18n,
            'UI_description'               : 'creditCalc',
            'UI_setting_label_text'        : 'Calc Credits in Battle, +1000 or -1000 silver difference: that\'s normal dispersion, if greater: Play one battle without damage.',
            'UI_setting_label_tooltip'     : '',
            'UI_setting_label1_text'       : 'Wait until the battle is complete without escape into the hangar. Income: Green Victory, Red Defeat, Outcome: ammo and consumables.',
            'UI_setting_label1_tooltip'    : '',
            'UI_setting_label2_text'       : 'Additional info in battle: Press Alt and Control buttons',
            'UI_setting_label2_tooltip'    : '',
            'UI_setting_battleBackground_text'   : 'Background in battle',
            'UI_setting_battleBackground_tooltip': '',
            'UI_setting_hangarBackground_text'   : 'Background in hangar',
            'UI_setting_hangarBackground_tooltip': '',
            'UI_setting_battleShow_text'   : 'Show in hangar',
            'UI_setting_battleShow_tooltip': '',
            'UI_setting_hangarShow_text'   : 'Show in battle',
            'UI_setting_hangarShow_tooltip': '',
        }
        if 'ru' in lang:
            self.p__i18n.update({
                'UI_setting_label_text'        : 'Калькуляция серебра в бою, +1000 или -1000 разницы: Нормальный разброс, если разброс больше, проведите один бой без урона',
                'UI_setting_label_tooltip'     : '',
                'UI_setting_label1_text'       : 'Дождитесь завершения боя без выхода в ангар. Доход: Зеленый победа, Красный поражение, Расходы: цена снарядов и расходников',
                'UI_setting_label1_tooltip'    : '',
                'UI_setting_label2_text'       : 'Дополнительная информация в бою: Нажмите кнопки АЛЬТ и КОНТРОЛ',
                'UI_setting_label2_tooltip'    : '',
                'UI_setting_battleBackground_text'   : 'Задний фон в бою',
                'UI_setting_battleBackground_tooltip': '',
                'UI_setting_hangarBackground_text'   : 'Задний фон в ангаре',
                'UI_setting_hangarBackground_tooltip': '',
                'UI_setting_battleShow_text'   : 'Показывать в ангаре',
                'UI_setting_battleShow_tooltip': '',
                'UI_setting_hangarShow_text'   : 'Показывать в бою',
                'UI_setting_hangarShow_tooltip': '',
            })
        if 'cn' in lang or 'zh' in lang:
            self.p__i18n.update({
                "UI_description"                     : "银币收益计算",
                "UI_setting_battleBackground_text"   : "在战斗中的消耗",
                "UI_setting_battleBackground_tooltip": "",
                "UI_setting_battleShow_text"         : "在机库中显示",
                "UI_setting_battleShow_tooltip"      : "",
                "UI_setting_hangarBackground_text"   : "机库的背景",
                "UI_setting_hangarBackground_tooltip": "",
                "UI_setting_hangarShow_text"         : "显示在战斗中",
                "UI_setting_hangarShow_tooltip"      : "",
                "UI_setting_label1_text"             : "等到战斗结束返回到机库. 收益：绿色为胜利, 红色为失败, 结果: 弹药和消耗品.",
                "UI_setting_label1_tooltip"          : "",
                "UI_setting_label2_text"             : "战斗中的详细情报:按Alt和Control按钮",
                "UI_setting_label2_tooltip"          : "",
                "UI_setting_label_text"              : "在战斗中的得分, +1000或-1000银币差额: 这是正常的分数, 如果更好的: 发挥战斗造成损伤.",
                "UI_setting_label_tooltip": "",
            })
        if p__g_gui:
            self.p__data, self.p__i18n = p__g_gui.register_data(self.p__ids, self.p__data, self.p__i18n, 'www.b4it.org')
            p__g_gui.register(self.p__ids, self.p__template, self.p__data, self.p__apply)
            print '[LOAD_MOD]:  [%s %s, %s]' % (self.p__ids, self.version, self.author)

    def p__template(self):
        return {
            'modDisplayName' : self.p__i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.p__data['enabled'],
            'column1'        : [
                {
                    'type'   : 'CheckBox',
                    'text'   : self.p__i18n['UI_setting_hangarShow_text'],
                    'value'  : self.p__data['hangar_show'],
                    'tooltip': self.p__i18n['UI_setting_battleShow_tooltip'],
                    'varName': 'hangar_show'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.p__i18n['UI_setting_battleShow_text'],
                    'value'  : self.p__data['battle_show'],
                    'tooltip': self.p__i18n['UI_setting_battleShow_tooltip'],
                    'varName': 'battle_show'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.p__i18n['UI_setting_hangarBackground_text'],
                    'value'  : self.p__data['hangar_background'],
                    'tooltip': self.p__i18n['UI_setting_battleBackground_tooltip'],
                    'varName': 'hangar_background'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.p__i18n['UI_setting_battleBackground_text'],
                    'value'  : self.p__data['battle_background'],
                    'tooltip': self.p__i18n['UI_setting_battleBackground_tooltip'],
                    'varName': 'battle_background'
                }, {
                    'type'   : 'Label',
                    'text'   : self.p__i18n['UI_setting_label_text'],
                    'tooltip': self.p__i18n['UI_setting_label_tooltip'],
                }, {
                    'type'   : 'Label',
                    'text'   : self.p__i18n['UI_setting_label1_text'],
                    'tooltip': self.p__i18n['UI_setting_label1_tooltip'],
                }, {
                    'type'   : 'Label',
                    'text'   : self.p__i18n['UI_setting_label2_text'],
                    'tooltip': self.p__i18n['UI_setting_label2_tooltip'],
                }
            ],
            'column2'        : []
        }

    def p__apply(self, settings):
        if p__g_gui:
            self.p__data = p__g_gui.update_data(self.p__ids, settings, 'www.b4it.org')
            p__g_gui.update(self.p__ids, self.p__template)


class p__MyJSONEncoder(p__json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(p__MyJSONEncoder, self).__init__(*args, **kwargs)
        self.current_indent = 0
        self.current_indent_str = ""
        self.indent = 4

    def encode(self, o):
        # Special Processing for lists
        if isinstance(o, (list, tuple)):
            primitives_only = True
            for item in o:
                if isinstance(item, (list, tuple, dict)):
                    primitives_only = False
                    break
            output = []
            if primitives_only:
                for item in o:
                    output.append(p__json.dumps(item, ensure_ascii=False, encoding='utf-8-sig'))
                return "[ " + ", ".join(output) + " ]"
            else:
                self.current_indent += self.indent
                self.current_indent_str = "".join([" " for x in range(self.current_indent)])
                for item in o:
                    output.append(self.current_indent_str + self.encode(item))
                self.current_indent -= self.indent
                self.current_indent_str = "".join([" " for x in range(self.current_indent)])
                return "[\n" + ",\n".join(output) + "\n" + self.current_indent_str + "]"
        elif isinstance(o, dict):
            output = []
            self.current_indent += self.indent
            self.current_indent_str = "".join([" " for x in range(self.current_indent)])
            for key, value in o.iteritems():
                output.append(self.current_indent_str + p__json.dumps(key, ensure_ascii=False, encoding='utf-8-sig') + ": " + self.encode(value))
            self.current_indent -= self.indent
            self.current_indent_str = "".join([" " for x in range(self.current_indent)])
            return "{\n" + ",\n".join(output) + "\n" + self.current_indent_str + "}"
        else:
            return p__json.dumps(o, ensure_ascii=False, encoding='utf-8-sig')


class p__CreditsCalculator(object):
    def __init__(self):
        self.p__coeffTable()
        self.p__COEFFICIENTS['USE_DATA'] = False
        self.p__AVERAGES = [(1.37, 1.37), (1.13, 1.28), (1.04, 1.35), (1.029, 1.42), (1.04, 1.5), (0.92, 1.3), (0.82, 1.4), (0.75, 1.5), (0.72, 0.72), (0.71, 0.72)]
        self.p__coeffDefaults = [0.53, 0.583, 0.6, 0.605, 0.62, 0.625, 0.63, 0.632, 0.633, 0.64, 0.65, 0.659, 0.66, 0.67, 0.6745, 0.68, 0.69, 0.7, 0.702, 0.708, 0.71, 0.711, 0.715, 0.72, 0.721, 0.724, 0.725, 0.73, 0.732, 0.734, 0.735, 0.745, 0.75, 0.751, 0.752, 0.753, 0.756, 0.759, 0.76, 0.764, 0.77, 0.774, 0.776, 0.777, 0.779, 0.78, 0.782, 0.783, 0.787, 0.788, 0.79, 0.791, 0.793, 0.795, 0.797, 0.798, 0.8, 0.802, 0.804, 0.805, 0.817, 0.82, 0.824, 0.825, 0.828, 0.83, 0.835, 0.836, 0.84, 0.847, 0.85, 0.854, 0.858, 0.861, 0.865, 0.868, 0.873, 0.874, 0.88, 0.883, 0.892, 0.894, 0.899, 0.9, 0.901, 0.906, 0.907, 0.909, 0.912, 0.9125, 0.915, 0.918, 0.922, 0.925, 0.928, 0.93, 0.931, 0.932, 0.935, 0.943, 0.945, 0.95, 0.964, 0.968, 0.969, 0.975, 0.976, 0.98, 0.987, 0.99, 0.997, 1.0, 1.0044, 1.0074, 1.012, 1.018, 1.02, 1.025, 1.026, 1.03, 1.0336, 1.044, 1.045, 1.046, 1.05, 1.053, 1.057, 1.07, 1.077, 1.08, 1.085, 1.086, 1.088, 1.089, 1.09, 1.0902, 1.093, 1.094, 1.1, 1.102, 1.104, 1.108, 1.109,
                                 1.11, 1.113, 1.115, 1.12, 1.122, 1.127, 1.128, 1.129, 1.14, 1.1425, 1.15, 1.154, 1.1585, 1.168, 1.17, 1.1782, 1.18, 1.199, 1.2, 1.21, 1.219, 1.22, 1.25, 1.253, 1.2558, 1.26, 1.27, 1.276, 1.3, 1.311, 1.3145, 1.33, 1.35, 1.36, 1.365, 1.38, 1.4, 1.419, 1.43, 1.437, 1.44, 1.445, 1.45, 1.46, 1.4734, 1.48, 1.485, 1.49, 1.5, 1.52, 1.53, 1.55, 1.56, 1.57, 1.575, 1.59, 1.6, 1.62, 1.63, 1.637, 1.64, 1.65, 1.67, 1.75, 1.81]
        resMgr = p__ResMgr.openSection('../version.xml')
        if resMgr is None:
            resMgr = p__ResMgr.openSection('version.xml')
            if resMgr is None:
                resMgr = p__ResMgr.openSection('./version.xml')
        ver = 'temp' if resMgr is None else resMgr.readString('version')
        i1 = ver.find('.')
        i2 = ver.find('#')
        self.p__PATH = ''.join(['./res_mods/', ver[i1 + 1:i2 - 1], '/system/'])
        self.p__readJson()
        self.p__PREMIUM_ACC = self.p__COEFFICIENTS['USE_DATA']
        self.p__iconCredits = '<img src=\"img://gui/maps/icons/quests/bonuses/big/credits.png\" vspace=\"-7\" width=\"20\" height=\"20\" />'
        self.p__textWin = ''
        self.p__textDEFEAT = ''
        self.p__tempResults = {}
        self.p__item = None
        self.p__altMode = False
        self.p__ctrlMode = False
        self.p__hangarOutcome = 0
        self.p__hangarItems = {}
        self.p__hangarAmmo = {}
        self.p__killed = False
        self.p__repairCost = 0
        self.p__costRepairs = {}
        self.p__usedItems = {}
        self.p__hangarHeader = ''

    def p__byte_ify(self, p__inputs):
        if p__inputs:
            if isinstance(p__inputs, dict):
                return {self.p__byte_ify(key): self.p__byte_ify(value) for key, value in p__inputs.iteritems()}
            elif isinstance(p__inputs, list):
                return [self.p__byte_ify(element) for element in p__inputs]
            elif isinstance(p__inputs, unicode):
                return p__inputs.encode('utf-8')
            else:
                return p__inputs
        return p__inputs

    def p__writeJson(self):
        if not p__os.path.exists(self.p__PATH):
            p__os.makedirs(self.p__PATH)
        with p__codecs.open(self.p__PATH + 'sw_templates.json', 'w', encoding='utf-8-sig') as p__json_file:
            p__data = p__json.dumps(p__collections.OrderedDict(sorted(self.p__COEFFICIENTS.items(), key=lambda t: t[0])), sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig', separators=(',', ': '), cls=p__MyJSONEncoder)
            p__json_file.write('%s' % self.p__byte_ify(p__data))
            p__json_file.close()

    def p__readJson(self):
        if p__os.path.isfile(self.p__PATH + 'sw_templates.json'):
            try:
                with p__codecs.open(self.p__PATH + 'sw_templates.json', 'r', encoding='utf-8-sig') as p__json_file:
                    p__data = p__json_file.read().decode('utf-8-sig')
                    self.p__COEFFICIENTS.update(self.p__byte_ify(p__json.loads(p__data)))
                    p__json_file.close()
            except Exception as e:
                self.p__writeJson()
        else:
            self.p__writeJson()

    def p__getHangarData(self, isPremium):
        if self.p__COEFFICIENTS['USE_DATA'] != isPremium:
            self.p__COEFFICIENTS['USE_DATA'] = isPremium
            self.p__writeJson()
        self.p__PREMIUM_ACC = isPremium

        # outcomeFull = 0
        outcome = 0
        for installedItem in p__g_currentVehicle.item.battleBoosters.installed.getItems():
            price = installedItem.buyPrices.getSum().price.credits
            # outcomeFull += price if not installedItem.inventoryCount else installedItem.getSellPrice().price.credits
            outcome += price if not installedItem.inventoryCount else 0
        self.p__hangarOutcome = outcome

        self.p__hangarItems = {}
        for installedItem in p__g_currentVehicle.item.consumables.installed.getItems():
            price = installedItem.buyPrices.getSum().price.credits
            self.p__hangarItems[installedItem.intCD] = [price if not installedItem.inventoryCount else 0, price if not installedItem.inventoryCount else installedItem.getSellPrice().price.credits]
        self.p__hangarAmmo = {}
        for ammo in p__g_currentVehicle.item.gun.defaultAmmo:
            self.p__hangarAmmo[ammo.intCD] = [ammo.buyPrices.getSum().price.credits if not ammo.inventoryCount else ammo.getSellPrice().price.credits, 0, 0]

        if p__DEBUG or p__DEBUG_COEFF:
            if p__g_currentVehicle.item:
                if self.p__item == p__g_currentVehicle.item.descriptor.type.compactDescr:
                    return
                vehicleCompDesc, balanceCoeff = self.p__deCode(p__g_currentVehicle.item.descriptor.type.compactDescr)
                if not balanceCoeff:
                    ids = 1 if 'premium' in p__g_currentVehicle.item.tags else 0
                    balanceCoeff = self.p__AVERAGES[p__g_currentVehicle.item.level - 1][ids]
                text = '<b>  {0} calcCredits {1} {0}\n '.format(icons.nutStat() * 3, 'to <font color=\"#6595EE\">oldskool.vip</font>' if oldskoolCore else 'by <font color=\"#6595EE\">www.b4it.org</font>')
                text += icons.makeImageTag(Vehicle.getTypeSmallIconPath(p__g_currentVehicle.item.type, p__g_currentVehicle.item.isPremium), width=30, height=30, vSpace=-7 if p__g_currentVehicle.item.isPremium else -5) + p__g_currentVehicle.item.shortUserName
                text += ' : %s %s%s%% %s</b>' % (icons.creditsBig(), 'coeff:', round(balanceCoeff * 100, 2), '')
                self.p__hangarHeader = text
                self.p__hangarMessage()
                self.p__item = p__g_currentVehicle.item.descriptor.type.compactDescr

    def p__timer(self):
        player = p__BigWorld.player()
        vehicle = player.getVehicleAttached()
        if vehicle:
            self.p__startBattle()
            return
        p__BigWorld.callback(0.1, self.p__timer)

    def p__code(self, p__compactDescr, p__balanceCoeff):
        test = '%s' % (p__compactDescr * 2847 * 122)
        self.p__COEFFICIENTS[test] = int(round(p__balanceCoeff * 10000.0)) * 1231 * 487
        self.p__writeJson()
        return test, self.p__COEFFICIENTS[test]

    def p__deCode(self, p__compactDescr):
        test = '%s' % (p__compactDescr * 2847 * 122)
        if test in self.p__COEFFICIENTS:
            return test, round(self.p__COEFFICIENTS[test] / 1231 / 487 * 0.0001, 6)
        return test, 0.0

    def p__startBattle(self):
        self.p__altMode = False
        self.p__ctrlMode = False
        player = p__BigWorld.player()
        p__InputHandler.g_instance.onKeyDown += self.p__keyPressed
        p__InputHandler.g_instance.onKeyUp += self.p__keyPressed
        player.arena.onVehicleKilled += self.p__onVehicleKilled
        # if player.guiSessionProvider.shared.vehicleState is not None:
        #    player.guiSessionProvider.shared.vehicleState.onVehicleStateUpdated += self.p__deviceTouched
        ammoCtrl = player.guiSessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded += self.p__onShellsAdded
            ammoCtrl.onShellsUpdated += self.p__onShellsUpdated
        p__flash.p__startBattle()
        p__flash.p__visible(False)
        vehicle = player.getVehicleAttached()
        self.p__costRepairs.update({
            'gun'            : vehicle.typeDescriptor.gun.maxRepairCost,
            'engine'         : vehicle.typeDescriptor.engine.maxRepairCost,
            'turretRotator'  : vehicle.typeDescriptor.turret.turretRotatorHealth.maxRepairCost,
            'surveyingDevice': vehicle.typeDescriptor.turret.surveyingDeviceHealth.maxRepairCost,
            'ammoBay'        : vehicle.typeDescriptor.hull.ammoBayHealth.maxRepairCost,
            'radio'          : vehicle.typeDescriptor.radio.maxRepairCost,
            'fuelTank'       : vehicle.typeDescriptor.fuelTank.maxRepairCost,
            'chassis'        : vehicle.typeDescriptor.chassis.maxRepairCost
        })
        self.p__costRepairs.update({name: vehicle.typeDescriptor.chassis.maxRepairCost for name in p__CHASSIS_ALL_ITEMS})
        if not self.p__hangarItems:
            self.p__hangarItems = {763: (3000, 3000), 1019: (20000, 20000), 1275: (3000, 3000), 1531: (20000, 20000), 1787: (5000, 5000), 4859: (20000, 20000), 4091: (20000, 20000), 2299: (20000, 20000), 2555: (20000, 20000), 3067: (20000, 20000), 251: (3000, 3000), 3323: (3000, 3000), 4347: (5000, 5000), 3579: (20000, 20000), 15867: (20000, 20000), 25851: (20000, 20000), 16123: (20000, 20000), 2043: (5000, 5000), 16379: (20000, 20000), 16635: (20000, 20000), 4603: (20000, 20000), 507: (20000, 20000)}
        self.p__usedItems = {}
        # vehicleName = player.guiSessionProvider.getCtx().getPlayerFullNameParts(vID=vehicle.id).vehicleName
        self.p__item = None
        self.p__name = vehicle.typeDescriptor.name
        self.p__vehicleName = player.guiSessionProvider.getCtx().getPlayerFullNameParts(vID=vehicle.id).vehicleName
        self.p__level = vehicle.typeDescriptor.level
        self.p__textWin = ''
        self.p__textDEFEAT = ''
        player = p__BigWorld.player()
        arenaDP = player.guiSessionProvider.getArenaDP()
        self.p__listAlly = p__vos_collections.AllyItemsCollection().ids(arenaDP)
        self.p__listAlly.remove(player.playerVehicleID)
        self.p__PREMIUM_ACC = self.p__COEFFICIENTS['USE_DATA']
        self.p__readJson()
        self.p__SPOT = 0
        self.p__ASSIST = 0
        self.p__DAMAGE_SELF_SPOT = 0  # 100% sure we're spotting
        self.p__DAMAGE_OTHER_SPOT = 0  # 100% sure someone else is spotting
        self.p__DAMAGE_UNKNOWN_SPOT = 0  # uncertanty who is spotting
        self.p__DAMAGE_STUN = 0
        self.p__DAMAGE_ASSIST = 0
        self.p__WinResult = 0
        self.p__WinResultMin = 0
        self.p__DefeatResult = 0
        self.p__DefeatResultMin = 0
        self.p__premium = 1.5 if self.p__PREMIUM_ACC else 1.0  # точно!
        self.p__compactDescr, self.p__balanceCoeff = self.p__deCode(vehicle.typeDescriptor.type.compactDescr)
        if not self.p__balanceCoeff:
            ids = 1 if 'premium' in vehicle.typeDescriptor.type.tags else 0
            self.p__balanceCoeff = self.p__AVERAGES[self.p__level - 1][ids]
        self.p__killed = False
        self.p__repairCost = 0
        self.p__calc()

    def p__canSpotTarget(self, targetVehicle):
        distSq = (targetVehicle.position - p__BigWorld.player().getOwnVehiclePosition()).lengthSquared
        # assume we can spot target 100% sure at 100m or at 75% of our vision radius
        if distSq < 10000:
            return True

        circularVisionRadius = p__BigWorld.player().guiSessionProvider.shared.feedback.getVehicleAttrs()['circularVisionRadius']
        if distSq < circularVisionRadius * circularVisionRadius * 0.75 * 0.75:
            return True

        return False

    def p__canNeverSpotTarget(self, targetVehicle):
        # we can's spot target outside of our vision radius
        distSq = (targetVehicle.position - p__BigWorld.player().getOwnVehiclePosition()).lengthSquared
        circularVisionRadius = p__BigWorld.player().guiSessionProvider.shared.feedback.getVehicleAttrs()['circularVisionRadius']
        if distSq > circularVisionRadius * circularVisionRadius:
            return True
        return False

    def p__onBattleEvents(self, events):
        player = p__BigWorld.player()
        guiSessionProvider = player.guiSessionProvider
        radio = 0
        track = 0
        stun = 0
        if guiSessionProvider.shared.vehicleState.getControllingVehicleID() == player.playerVehicleID:
            for p__data in events:
                feedbackEvent = p__feedback_events.PlayerFeedbackEvent.fromDict(p__data)
                eventType = feedbackEvent.getBattleEventType()
                targetID = feedbackEvent.getTargetID()
                if eventType == p__BATTLE_EVENT_TYPE.SPOTTED:
                    vehicle = p__BigWorld.entity(targetID)
                    self.p__SPOT += 1
                    if vehicle and 'SPG' in vehicle.typeDescriptor.type.tags:
                        self.p__SPOT += 1
                if eventType in p__DAMAGE_EVENTS:
                    extra = feedbackEvent.getExtra()
                    if extra:
                        if eventType == p__BATTLE_EVENT_TYPE.RADIO_ASSIST:
                            radio += extra.getDamage()
                        if eventType == p__BATTLE_EVENT_TYPE.TRACK_ASSIST:
                            track += extra.getDamage()
                        if eventType == p__BATTLE_EVENT_TYPE.STUN_ASSIST:
                            stun += extra.getDamage()
                        if eventType == p__BATTLE_EVENT_TYPE.DAMAGE:
                            arenaDP = guiSessionProvider.getArenaDP()
                            if arenaDP.isEnemyTeam(arenaDP.getVehicleInfo(targetID).team):
                                vehicle = p__BigWorld.entity(targetID)
                                if vehicle:
                                    if vehicle.stunInfo > 0.0:
                                        self.p__DAMAGE_STUN += extra.getDamage()
                                    elif self.p__canSpotTarget(vehicle):
                                        self.p__DAMAGE_SELF_SPOT += extra.getDamage()
                                    elif self.p__canNeverSpotTarget(vehicle):
                                        self.p__DAMAGE_OTHER_SPOT += extra.getDamage()
                                    else:
                                        self.p__DAMAGE_UNKNOWN_SPOT += extra.getDamage()
        data = [radio, track, stun]
        self.p__ASSIST += max(data)
        self.p__calc()

    def p__deviceTouched(self, state, value):
        if self.p__killed:
            return
        player = p__BigWorld.player()
        ctrl = player.guiSessionProvider.shared
        vehicle = player.getVehicleAttached()
        # self.p__repairCost = int(vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth + vehicle.health)
        # getMaxRepairCost = vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth
        self.p__repairCost = 0  # int(round(getMaxRepairCost - getMaxRepairCost * vehicle.health / round(vehicle.typeDescriptor.maxHealth)))
        if state == VEHICLE_VIEW_STATE.DEVICES:
            # print 'max:%s, maxHP:%s, hp:%s' % (vehicle.typeDescriptor.getMaxRepairCost(), vehicle.typeDescriptor.maxHealth, vehicle.health)
            # print 'repairCost1:%s' % self.p__repairCost
            self.p__repairCost = 0
            repairs = 0
            for equipment in ctrl.equipments.iterEquipmentsByTag('repairkit'):
                for itemName, deviceState in equipment[1].getEntitiesIterator():
                    if deviceState == 'destroyed':
                        if itemName in self.p__costRepairs:
                            # print 'module:%s, %s' % (itemName, deviceState)
                            repairs += self.p__costRepairs[itemName]
                    if deviceState == 'critical':
                        if itemName in self.p__costRepairs:
                            # print 'module:%s, %s' % (itemName, deviceState)
                            repairs += self.p__costRepairs[itemName] / 2
            self.p__repairCost += int(round(repairs))
            # print 'modules:%s' %(repairs)
            # print 'repairCost2:%s' % self.p__repairCost
            # print 'repairCost3:%s' % int(round(self.p__repairCost * self.p__balanceCoeff))
        self.p__calc()

    def p__onVehicleKilled(self, target_id, attacker_id, equipment_id, reason):
        player = p__BigWorld.player()
        vehicle = player.getVehicleAttached()
        if target_id == vehicle.id:
            self.p__killed = True
            self.p__calc()
            return
            # self.p__repairCost = int(vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth + vehicle.health)
            getMaxRepairCost = vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth
            self.p__repairCost = int(round(getMaxRepairCost - getMaxRepairCost * vehicle.health / round(vehicle.typeDescriptor.maxHealth)))
            ctrl = player.guiSessionProvider.shared
            repairs = 0
            for equipment in ctrl.equipments.iterEquipmentsByTag('repairkit'):
                for itemName, deviceState in equipment[1].getEntitiesIterator():
                    if deviceState == 'destroyed':
                        if itemName in self.p__costRepairs:
                            repairs += self.p__costRepairs[itemName]
                    if deviceState == 'critical':
                        if itemName in self.p__costRepairs:
                            repairs += self.p__costRepairs[itemName] / 2
            self.p__repairCost += int(repairs)
            self.p__calc()

    def p__battleOutcome(self):
        player = p__BigWorld.player()
        ctrl = player.guiSessionProvider.shared
        # priceFull = self.p__hangarOutcome[1]
        price = self.p__hangarOutcome  # + int(round(self.p__repairCost * self.p__balanceCoeff))
        if not self.p__killed:
            try:
                for item in ctrl.equipments.getOrderedEquipmentsLayout():
                    if item and item[0] in self.p__hangarItems:
                        prevQuantity = item[1].getPrevQuantity()
                        quantity = item[1].getQuantity()
                        if item[0] not in self.p__usedItems:
                            self.p__usedItems[item[0]] = [not prevQuantity and quantity < 65535, self.p__hangarItems[item[0]][1], self.p__hangarItems[item[0]][1]]
                        if prevQuantity > 0 and 1 < quantity < 65535:
                            self.p__usedItems[item[0]][0] = True
            except Exception as e:
                pass
        # print self.p__usedItems
        for equipment in self.p__usedItems:
            if self.p__usedItems[equipment][0]:
                price += self.p__usedItems[equipment][1]
        for ammo in self.p__hangarAmmo:
            if self.p__hangarAmmo[ammo][1]:
                price += self.p__hangarAmmo[ammo][0] * self.p__hangarAmmo[ammo][1]
        return int(round(price))

    def p__onShellsAdded(self, intCD, descriptor, quantity, _, gunSettings):
        if intCD in self.p__hangarAmmo:
            self.p__hangarAmmo[intCD][2] = quantity
            self.p__calc()

    def p__onShellsUpdated(self, intCD, quantity, *args):
        if intCD in self.p__hangarAmmo:
            self.p__hangarAmmo[intCD][1] = self.p__hangarAmmo[intCD][2] - quantity
            self.p__calc()

    def p__calc(self, hangar=False):
        if not p__config.p__data['enabled']:
            return
        if not (p__DEBUG or p__DEBUG_COEFF):
            return
        assistCoeff = 5
        spotCoeff = 100
        damageStunCoeff = 7.7
        damageSpottedCoeff = 7.5
        damageSelfCoeff = 10
        defeatCredits = self.p__level * 700
        winCredits = self.p__level * 1300

        assistCredits = self.p__ASSIST * assistCoeff
        spotCredits = self.p__SPOT * spotCoeff
        stunCredits = self.p__DAMAGE_STUN * damageStunCoeff

        damageMinCredits = self.p__DAMAGE_SELF_SPOT * damageSelfCoeff + (self.p__DAMAGE_UNKNOWN_SPOT + self.p__DAMAGE_OTHER_SPOT) * damageSpottedCoeff
        damageMaxCredits = (self.p__DAMAGE_SELF_SPOT + self.p__DAMAGE_UNKNOWN_SPOT) * damageSelfCoeff + self.p__DAMAGE_OTHER_SPOT * damageSpottedCoeff

        outcomeCredits = self.p__battleOutcome()

        self.p__DefeatResult = int(int(self.p__balanceCoeff * int(defeatCredits + assistCredits + spotCredits + damageMaxCredits + stunCredits) - 0.5) * self.p__premium + 0.5)
        self.p__DefeatResultMin = int(int(self.p__balanceCoeff * int(defeatCredits + assistCredits + spotCredits + damageMinCredits + stunCredits) - 0.5) * self.p__premium + 0.5)

        self.p__WinResult = int(int(self.p__balanceCoeff * int(winCredits + assistCredits + spotCredits + damageMaxCredits + stunCredits) - 0.5) * self.p__premium + 0.5)
        self.p__WinResultMin = int(int(self.p__balanceCoeff * int(winCredits + assistCredits + spotCredits + damageMinCredits + stunCredits) - 0.5) * self.p__premium + 0.5)

        if not hangar and p__flash:
            textWinner = self.p__correctedText(self.p__WinResultMin, self.p__WinResult, outcomeCredits)
            textDefeat = self.p__correctedText(self.p__DefeatResult, self.p__DefeatResult, outcomeCredits)
            colorWin = '#80D639'
            colorDefeat = '#FF6347'
            self.p__textWin = '<font size=\"20\" color=\"%s\">~%s%s</font>' % (colorWin, self.p__iconCredits, textWinner)
            self.p__textDEFEAT = '<font size=\"20\" color=\"%s\">~%s%s</font>' % (colorDefeat, self.p__iconCredits, textDefeat)
            if self.p__compactDescr not in self.p__tempResults:
                vehicle = p__BigWorld.player().getVehicleAttached()
                self.p__tempResults[self.p__compactDescr] = {
                    'descr'      : vehicle.typeDescriptor.type.compactDescr,
                    'premium'    : self.p__premium,
                    'damage'     : self.p__DAMAGE_SELF_SPOT + self.p__DAMAGE_UNKNOWN_SPOT + self.p__DAMAGE_OTHER_SPOT + self.p__DAMAGE_STUN,
                    'assist'     : self.p__ASSIST,
                    'spot'       : self.p__SPOT,
                    'level'      : self.p__level,
                    'name'       : self.p__name.replace(':', '_'),
                    'repairCost' : int(round(vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth)),
                    'clearRepair': False,
                }
            self.p__tempResults[self.p__compactDescr]['damage'] = self.p__DAMAGE_SELF_SPOT + self.p__DAMAGE_UNKNOWN_SPOT + self.p__DAMAGE_OTHER_SPOT + self.p__DAMAGE_STUN
            self.p__tempResults[self.p__compactDescr]['assist'] = self.p__ASSIST
            self.p__tempResults[self.p__compactDescr]['spot'] = self.p__SPOT
            if self.p__tempResults[self.p__compactDescr]['repairCost'] == self.p__repairCost:
                self.p__tempResults[self.p__compactDescr]['clearRepair'] = True
            else:
                self.p__tempResults[self.p__compactDescr]['clearRepair'] = False
            p__flash.p__visible(True)
            p__flash.setCreditsText(self.p__textWin if not self.p__altMode else self.p__textDEFEAT)

    def p__keyPressed(self, event):
        player = p__BigWorld.player()
        if not player.arena: return
        if player.arena.bonusType != p__ARENA_BONUS_TYPE.REGULAR: return
        isKeyDownTrigger = event.isKeyDown()
        if event.key in [p__Keys.KEY_LALT, p__Keys.KEY_RALT]:
            if isKeyDownTrigger:
                self.p__altMode = True
            if event.isKeyUp():
                self.p__altMode = False
            self.p__calc()
        if event.key in [p__Keys.KEY_LCONTROL, p__Keys.KEY_RCONTROL]:
            if isKeyDownTrigger:
                self.p__ctrlMode = True
            if event.isKeyUp():
                self.p__ctrlMode = False
            self.p__calc()

    def p__correctedText(self, min, max, outcome):
        out = '<font color=\"#FF0000\"> -%s</font>' % outcome if outcome else ''
        if min != max:
            if self.p__ctrlMode:
                return '%s[%s]%s' % (min, int(max * 1.05), out)  # add 5% to max credits range
            return '%s%s' % (min, out)
        return '%s%s' % (max, out)

    def p__getDebugText(self):
        debugText = 'Coeff: %s: %s\n' % ('MISS' if self.p__compactDescr not in self.p__COEFFICIENTS else 'FOUND', self.p__balanceCoeff)
        if self.p__compactDescr not in self.p__COEFFICIENTS:
            debugText += '\nCredit Calc need learn\non that vehicle\n'
            if not self.p__tempResults[self.p__compactDescr]['damage']:
                debugText += 'JUST SUICIDE FAST plz!\n'
                debugText += 'And wait until battle down\n'
            else:
                debugText += 'wrong battle! play again\n'
        return debugText

    def p__stopBattle(self):
        player = p__BigWorld.player()
        self.p__ctrlMode = False
        self.p__altMode = False
        player.arena.onVehicleKilled -= self.p__onVehicleKilled
        # if player.guiSessionProvider.shared.vehicleState is not None:
        #    player.guiSessionProvider.shared.vehicleState.onVehicleStateUpdated -= self.p__deviceTouched
        ammoCtrl = player.guiSessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded -= self.p__onShellsAdded
            ammoCtrl.onShellsUpdated -= self.p__onShellsUpdated
        p__InputHandler.g_instance.onKeyDown -= self.p__keyPressed
        p__InputHandler.g_instance.onKeyUp -= self.p__keyPressed
        p__flash.p__stopBattle()
        if p__DEBUG:
            if self.p__compactDescr not in self.p__tempResults:
                return
            self.p__compactDescr, self.p__balanceCoeff = self.p__deCode(self.p__tempResults[self.p__compactDescr]['descr'])
            print 'tempResults', self.p__tempResults[self.p__compactDescr]
            outcomeCredits = self.p__battleOutcome()
            textWinner = '~%s' % self.p__correctedText(self.p__WinResultMin, self.p__WinResult, outcomeCredits)
            textDefeat = '~%s' % self.p__correctedText(self.p__DefeatResultMin, self.p__DefeatResult, outcomeCredits)
            textWinnerPremium = ''
            textDefeatPremium = ''
            if p__BattleReplay.g_replayCtrl.isPlaying:
                textWinnerPremium = ', With Premium account: ~%s Credits' % self.p__correctedText(int(1.5 * self.p__WinResultMin), int(1.5 * self.p__WinResult), outcomeCredits)
                textDefeatPremium = ', With Premium account: ~%s Credits' % self.p__correctedText(int(1.5 * self.p__DefeatResultMin), int(1.5 * self.p__DefeatResult), outcomeCredits)
            price = self.p__hangarOutcome
            for equipment in self.p__usedItems:
                if self.p__usedItems[equipment][0]:
                    price += self.p__usedItems[equipment][1]
            for ammo in self.p__hangarAmmo:
                if self.p__hangarAmmo[ammo][1]:
                    price += self.p__hangarAmmo[ammo][0] * self.p__hangarAmmo[ammo][1]
            consumables = int(round(price))

            print '#' * 40
            print 'Credits Calculate mode'
            print 'VEHICLE: %s level:%s (id:%s)' % (self.p__tempResults[self.p__compactDescr]['name'], self.p__tempResults[self.p__compactDescr]['level'], self.p__compactDescr)
            print 'damage:%s, assist:%s, spot:%s, %s' % (self.p__tempResults[self.p__compactDescr]['damage'], self.p__tempResults[self.p__compactDescr]['assist'], self.p__tempResults[self.p__compactDescr]['spot'], 'clear repaired' if self.p__tempResults[self.p__compactDescr]['clearRepair'] else 'not cleared repair')
            print 'damage detail: selfSpot:%s, unkwnSpot:%s, othrSpot:%s, forStunned:%s, ' % (self.p__DAMAGE_SELF_SPOT, self.p__DAMAGE_UNKNOWN_SPOT, self.p__DAMAGE_OTHER_SPOT, self.p__DAMAGE_STUN)
            print 'coeff:%s, premCoeff:%s' % (self.p__balanceCoeff, self.p__tempResults[self.p__compactDescr]['premium'])
            print 'repairCost:%s[%s], consumables:%s' % (-int(round(self.p__repairCost * self.p__balanceCoeff)), -self.p__repairCost, -consumables)
            amm0 = ''
            for ammo in self.p__hangarAmmo:
                amm0 += '%s Credits (%s * %s) ' % (self.p__hangarAmmo[ammo][0] * self.p__hangarAmmo[ammo][1], self.p__hangarAmmo[ammo][0], self.p__hangarAmmo[ammo][1])
            if amm0:
                print 'Ammo: %s' % amm0
            print 'WINNER:%s Credits' % textWinner + textWinnerPremium
            print 'DEFEAT:%s Credits' % textDefeat + textDefeatPremium
            print '#' * 40
            print self.p__getDebugText()
        self.p__hangarOutcome = 0
        self.p__hangarItems = {}
        self.p__hangarAmmo = {}
        self.p__killed = False
        self.p__repairCost = 0
        self.p__costRepairs = {}
        self.p__usedItems = {}

    def p__hangarMessage(self):
        if not p__config.p__data['enabled']:
            return
        # if not (p__DEBUG or p__DEBUG_COEFF):
        #    return
        if p__ServicesLocator.hangarSpace is not None and p__ServicesLocator.hangarSpace.inited:
            self.p__recalculatedMessage = '<font size=\"20\" color=\"#FFE041\">%s</font>\n' % self.p__hangarHeader
            if self.p__textWin or self.p__textDEFEAT:
                textWinner = self.p__correctedText(self.p__WinResultMin, self.p__WinResult, 0)
                textDefeat = self.p__correctedText(self.p__DefeatResult, self.p__DefeatResult, 0)
                colorWin = '#80D639'
                colorDefeat = '#FF6347'
                self.p__textWin = '<font size=\"20\" color=\"%s\">~%s%s</font>' % (colorWin, self.p__iconCredits, textWinner)
                self.p__textDEFEAT = '<font size=\"20\" color=\"%s\">~%s%s</font>' % (colorDefeat, self.p__iconCredits, textDefeat)
                self.p__recalculatedMessage += '  ' + self.p__textWin + '<font size=\"20\" color=\"#FFE041\"> %s </font>' % self.p__vehicleName + self.p__textDEFEAT
            self.timerMessage()
            # p__SystemMessages.pushMessage(p__msg, p__SystemMessages.SM_TYPE.GameGreeting)

    def timerMessage(self):
        if not p__config.p__data['hangar_show']:
            return
        if p__g_currentVehicle.item:
            p__flashInHangar.setPosition(p__config.p__data['hangar_x'], p__config.p__data['hangar_y'])  # x and y
            p__flashInHangar.setBackground(p__config.p__data['battle_background'], '0x000000', 0.4)  # change to false if dont want
            p__flashInHangar.setText(self.p__recalculatedMessage)
            # p__SystemMessages.pushMessage(self.p__recalculatedMessage, p__SystemMessages.SM_TYPE.GameGreeting)
            return
        p__BigWorld.callback(1.0, self.timerMessage)

    def p__tester(self, credits, premiumCoeff, winCoeff, level, assist, spot):
        result = []
        winCoeff = 1300 if winCoeff else 700
        pool = {
            1: (99, 0.1),
            2: (999, 0.01),
            3: (9999, 0.001),
            4: (99999, 0.0001),
            5: (999999, 0.00001),
        }
        for ranged in pool:
            boosterCoeff = 0.0
            for i in xrange(pool[ranged][0]):
                boosterCoeff = round(boosterCoeff + pool[ranged][1], ranged)
                if credits == int(int(boosterCoeff * int(level * winCoeff + assist * 5 + spot * 100) - 0.5) * premiumCoeff + 0.5):
                    result.append(boosterCoeff)
            if result:
                if p__DEBUG:
                    print 'search pool: %s' % ranged, pool[ranged], boosterCoeff
                return result
        return result

    def p__sortValues(self, value, debug=False):
        try:
            index = self.p__coeffDefaults.index(filter(lambda x: value <= x + 0.0005, self.p__coeffDefaults)[0])
            if p__DEBUG or debug:
                print 'sortValues value: %s=>[%s]<%s' % (self.p__coeffDefaults[index], value, self.p__coeffDefaults[index + 1] if len(self.p__coeffDefaults) > index + 1 else self.p__coeffDefaults[index])
            return self.p__coeffDefaults[index]
        except Exception as e:
            if p__DEBUG or debug:
                print 'sortValues error not in range:%s' % value
            return value

    def p__sortResult(self, data1, data2, testCoeff):
        if data1 and data2:
            check1 = self.p__sortValues(round(sum(data1) / len(data1), 5), p__DEBUG_COEFF)
            check2 = self.p__sortValues(round(sum(data2) / len(data2), 5), p__DEBUG_COEFF)
            if check1 == testCoeff or check2 == testCoeff:
                return testCoeff
            if check1 == check2:
                return check1
            if check1 in data2:
                return check1
            if check2 in data1:
                return check2
        return 0.0

    def p__resultReCalc(self, typeCompDescr, isWin, credits, originalCredits, spot, assist, damage, repair):
        if p__DEBUG or p__DEBUG_COEFF:
            print '$$$$$ resultReCalc started'
        self.p__readJson()
        vehicleCompDesc, testCoeff = self.p__deCode(typeCompDescr)
        if vehicleCompDesc in self.p__tempResults:
            # if self.p__tempResults[vehicleCompDesc]['clearRepair'] and False:
            #    if p__DEBUG or p__DEBUG_COEFF:
            #        print '$$$$$$$$$$$$$$ CLEAR REPAIR MODE $$$$$$$$$$$$$$'
            #    calcRepair = int(round(self.p__tempResults[vehicleCompDesc]['repairCost'] * testCoeff))
            #    if p__DEBUG or p__DEBUG_COEFF:
            #        level = self.p__tempResults[vehicleCompDesc]['level']
            #        winCoeff = 1300 if isWin else 700
            #        print 'VEHICLE: %s level:%s (id:%s)' % (self.p__tempResults[vehicleCompDesc]['name'], self.p__tempResults[vehicleCompDesc]['level'], vehicleCompDesc)
            #        print 'level:%s, assist:%s, spot:%s, winCoeff:%s, balanceCoeff:%s' % (level, assist, spot, winCoeff, testCoeff)
            #        print 'repair:%s calcRepair:%s' % (repair, calcRepair)
            #    if repair != calcRepair:
            #        check = round(repair / round(self.p__tempResults[vehicleCompDesc]['repairCost']), 4)
            #        if p__DEBUG or p__DEBUG_COEFF:
            #            print 'repair / calcRepair = %s' % (repair / round(self.p__tempResults[vehicleCompDesc]['repairCost']))
            #            print 'possible coeffs:', check
            #            print '####2 resultReCalc SAVED coeff[%s]' % check
            #        self.p__compactDescr, self.p__balanceCoeff = self.p__code(typeCompDescr, check)
            #        self.p__readJson()
            #        if p__DEBUG or p__DEBUG_COEFF:
            #            print "####1 '%s': %s," % (self.p__compactDescr,self.p__balanceCoeff)
            #        if p__DEBUG or p__DEBUG_COEFF:
            #            self.p__recalculatedMessage = '<font size=\"20\" color=\"#FFE041\">Credits Calc to %s (id:%s)\nNew coeff:%s assigned, %s to %s</font>\n' % (self.p__tempResults[vehicleCompDesc]['name'], self.p__compactDescr, check, testCoeff, check)
            #            p__BigWorld.callback(1.0, self.timerMessage)
            #    return
            if not damage:
                if p__DEBUG or p__DEBUG_COEFF:
                    print '$$$$$$$$$$$$$$ NO DAMAGE MODE $$$$$$$$$$$$$$'
                checkCorrectedBattleData = credits / float(originalCredits)
                if p__DEBUG:
                    if checkCorrectedBattleData != 1.5:
                        print '$$$$ BATTLE DATA INCORRECT! PLAY AGAIN $$$$'
                # premiumCoeff = self.p__premium
                # if p__BattleReplay.g_replayCtrl.isPlaying:
                premiumCoeff = 1.0 if checkCorrectedBattleData < 1.01 else 1.5
                winCoeff = 1300 if isWin else 700
                level = self.p__tempResults[vehicleCompDesc]['level']
                result1 = self.p__tester(originalCredits, 1.0, isWin, level, assist, spot)
                result2 = self.p__tester(credits, 1.5, isWin, level, assist, spot)

                checkData = int(int(1.0 * int(level * winCoeff + assist * 5 + spot * 100) - 0.5) * premiumCoeff + 0.5)
                if premiumCoeff > 1.1:
                    coeff1 = round(checkData / originalCredits, 4)
                else:
                    coeff1 = round(originalCredits / checkData, 4)
                check = self.p__sortResult(result1, result2, coeff1)
                if p__DEBUG:
                    print 'VEHICLE: %s level:%s (id:%s)' % (self.p__tempResults[vehicleCompDesc]['name'], self.p__tempResults[vehicleCompDesc]['level'], vehicleCompDesc)
                    print 'level:%s, assist:%s, spot:%s, winCoeff:%s, balanceCoeff:%s' % (level, assist, spot, winCoeff, testCoeff)
                    print 'credits:%s originalCredits:%s, checkData:%s' % (credits, originalCredits, checkData)
                    print 'credits / originalCredits = %s' % checkCorrectedBattleData
                    print 'possible coeffs:', check
                checkOne = check
                # if check and testCoeff == check:
                #    return
                # if coeff1 == testCoeff:
                #    return
                if p__DEBUG:
                    print '#### resultReCalc coeff1[%s] and testCoeff[%s]' % (coeff1, testCoeff)
                    print 'result1 = ', result1
                    if result1:
                        print 'result1 coeff = %s' % round(sum(result1) / len(result1), 4)
                    print 'result2 = ', result2
                    if result2:
                        print 'result2 coeff = %s' % round(sum(result2) / len(result2), 4)
                if p__DEBUG_COEFF:
                    print '$$$$ 1 round coeff:%s' % round(sum(result1) / len(result1), 4), result1
                    print '$$$$ 2 round coeff:%s' % round(sum(result2) / len(result2), 4), result2
                    print '$$$$ VEHICLE: %s level:%s (id:%s)' % (self.p__tempResults[vehicleCompDesc]['name'], self.p__tempResults[vehicleCompDesc]['level'], vehicleCompDesc)
                    print '$$$$ originalCoeff: %s, possibleCoeff1: %s, possibleCoeff2: %s' % (testCoeff, checkOne, check)
                self.p__readJson()
                checkData *= premiumCoeff
                coeff2 = round(credits / checkData, 4)
                checkAgain = self.p__sortResult(result1, result2, coeff2)
                if checkAgain and check != checkAgain:
                    check = checkAgain
                if p__DEBUG:
                    print '#### resultReCalc coeff2[%s] and coeff1[%s] and check[%s]' % (coeff2, coeff1, check)
                if coeff1 == coeff2 and coeff1 != 1.0:
                    if p__DEBUG or p__DEBUG_COEFF:
                        print '####1 resultReCalc SAVED coeff[%s] ' % (coeff2)

                    self.p__compactDescr, self.p__balanceCoeff = self.p__code(typeCompDescr, coeff2)
                    self.p__readJson()
                    if p__DEBUG or p__DEBUG_COEFF:
                        print "####1 '%s': %s," % (self.p__compactDescr, self.p__balanceCoeff)
                else:
                    if check:
                        if p__DEBUG or p__DEBUG_COEFF:
                            print '####2 resultReCalc SAVED coeff[%s]' % check
                        self.p__compactDescr, self.p__balanceCoeff = self.p__code(typeCompDescr, check)
                        self.p__readJson()
                        if p__DEBUG or p__DEBUG_COEFF:
                            print "####2 '%s': %s," % (self.p__compactDescr, self.p__balanceCoeff)
                if p__DEBUG or p__DEBUG_COEFF:
                    self.p__recalculatedMessage = '<font size=\"20\" color=\"#FFE041\">Credits Calc to %s (id:%s)\nNew coeff:%s assigned, %s to %s</font>\n' % (self.p__tempResults[vehicleCompDesc]['name'], self.p__compactDescr, check, testCoeff, check)
                    p__BigWorld.callback(1.0, self.timerMessage)
            # del self.p__tempResults[vehicleCompDesc]

    def p__receiveBattleResult(self, isSuccess, battleResults):
        # print battleResults
        playerVehicles = battleResults['personal'].itervalues().next()
        if not playerVehicles:
            return
        assist = max(playerVehicles['damageAssistedRadio'], playerVehicles['damageAssistedTrack'], playerVehicles['damageAssistedStun'])
        spot = playerVehicles['spotted']
        damage = playerVehicles['damageDealt']
        repair = playerVehicles['repair']
        # 'subtotalCredits', 'factualCredits'
        # 'credits' - 'eventCredits'
        self.p__resultReCalc(playerVehicles['typeCompDescr'], battleResults['common']['winnerTeam'] == playerVehicles['team'], playerVehicles['factualCredits'], playerVehicles['originalCredits'], spot, assist, damage, repair)

    def p__coeffTable(self):
        self.p__COEFFICIENTS = {'4146125958': 8992455000, '10853840166': 8093209500, '11303985030': 7793461000, '11131707366': 8392958000, '11487377382': 9442077750, '1834270854': 5605296950, '511622982': 5994970000, '2990198406': 5917035390, '17850536262': 8992455000, '5568806022': 5994970000, '4857465990': 6474567600, '21557284710': 10491197500, '3790455942': 6294718500, '11215067526': 7793461000, '3434785926': 8392958000, '4323960966': 4496227500, '5035300998': 9352153200, '11031675174': 7793461000, '12715550406': 8992455000, '11159494086': 8992455000, '11587409574': 7313863400, '11915292870': 8872555600, '867292998': 4316378400, '3168033414': 5994970000, '11765244582': 7553662200, '10970544390': 7793461000, '4679630982': 4376328100, '12476584614': 7793461000, '10770480006': 8692706500, '5213136006': 5976985090, '12031997094': 8992455000, '12804467910': 7793461000, '11203952838': 8992455000, '5835558534': 8992455000, '11309542374': 8992455000, '5657723526': 7793461000, '11926407558': 9442077750, '10981659078': 7793461000, '21468367206': 8392958000, '5746641030': 8392958000, '4946383494': 4376328100, '22685425542': 8392958000, '12721107750': 8992455000, '10803824070': 9591952000, '9269997126': 8992455000, '12359880390': 7313863400, '13071220422': 7793461000, '12104242566': 8992455000, '12898942758': 8992455000, '11409574566': 7793461000, '11398459878': 9442077750, '11209510182': 9831750800, '11559622854': 8992455000, '12209832102': 8932505300, '422705478': 5994970000, '12093127878': 8992455000, '10764922662': 7193964000, '12298749606': 9591952000, '22413115686': 8992455000, '4412878470': 4676076600, '10859397510': 9711851400, '10787152038': 7493712500, '12365437734': 9292203500, '12893385414': 7793461000, '12270962886': 8992455000, '11676327078': 9442077750, '1034013318': 6294718500, '11042789862': 5994970000, '18773055366': 8093209500, '11248411590': 8992455000, '11059461894': 8992455000, '11053904550': 7493712500, '11654097702': 9352153200, '1745353350': 5581317070, '10892741574': 7193964000, '3079115910': 6150839220, '9092162118': 8392958000, '9625667142': 8992455000, '333787974': 6594467000, '11470705350': 7793461000, '12448797894': 8992455000, '11920850214': 9591952000, '11826375366': 8992455000, '3879373446': 6594467000, '13187924646': 5587312040, '11148379398': 8992455000, '11943079590': 8902530450, '21379449702': 7793461000, '11115035334': 8992455000, '9536749638': 8992455000, '4057208454': 7793461000, '4590713478': 5233608810, '12187602726': 8992455000, '12543272742': 8992455000, '12276520230': 8752656200, '13076777766': 8093209500, '12009767718': 8392958000, '11292870342': 8992455000, '11498492070': 8692706500, '5124218502': 4676076600, '12182045382': 8992455000, '689457990': 4795976000, '11837490054': 8692706500, '1300765830': 4244438760, '12120914598': 8932505300, '12454355238': 7193964000, '3968290950': 7193964000, '11381787846': 8832988798, '11320657062': 9292203500, '22863260550': 8992455000, '9803502150': 8992455000, '5302053510': 5143684260, '4501795974': 5185649050, '22596508038': 9442077750, '11476262694': 7793461000, '12987860262': 8992455000, '11326214406': 7793461000, '11659655046': 7793461000, '9003244614': 8662731650, '600540486': 5395473000, '22507590534': 9532002300, '13337972934': 7493712500, '12565502118': 9591952000, '12015325062': 7553662200, '11748572550': 7193964000, '11481820038': 7793461000, '956210502': 4376328100, '11415131910': 9352153200, '11126150022': 7793461000, '11737457862': 9112354400, '9447832134': 9591952000, '12537715398': 8093209500, '2278858374': 6294718500, '778375494': 4196479000, '10948315014': 9412102900, '12626632902': 8992455000, '22296411462': 8992455000, '11026117830': 9591952000, '4235043462': 4658091690, '11648540358': 9591952000, '13160137926': 8992455000, '9358914630': 8392958000, '5390971014': 5545347250, '9714584646': 8992455000, '22418673030': 8992455000, '3612620934': 3956680200, '12810025254': 7793461000, '155952966': 6594467000, '4768548486': 8992455000, '10953872358': 9442077750, '244870470': 6894215500, '11565180198': 9891700500, '12282077574': 5803130960, '12387667110': 9891700500, '11392902534': 7793461000, '9181079622': 8992455000, '67035462': 8392958000, '11298427686': 9891700500, '12921172134': 5994970000, '11120592678': 9352153200, '11854162086': 9292203500, '11231739558': 7793461000, '11570737542': 5395473000}
        self.p__COEFFICIENTS.update({
            # italy
            # lightTank
            '55920774'   : 8392958000,  # 161 italy_It04_Fiat_3000 lvl:1 coeff:1.4
            '144838278'  : 6594467000,  # 417 italy_It05_Carro_L6_40 lvl:2 coeff:1.1
            # mediumTank
            '233755782'  : 6894215500,  # 673 italy_It06_M14_41 lvl:2 coeff:1.15
            '322673286'  : 6594467000,  # 929 italy_It03_M15_42 lvl:3 coeff:1.1
            '411590790'  : 5994970000,  # 1185 italy_It07_P26_40 lvl:4 coeff:1.0
            '500508294'  : 5994970000,  # 1441 italy_It11_P43 lvl:5 coeff:1.0
            '589425798'  : 5395473000,  # 1697 italy_It10_P43_bis lvl:6 coeff:0.9
            '678343302'  : 4795976000,  # 1953 italy_It09_P43_ter lvl:7 coeff:0.8
            '767260806'  : 4196479000,  # 2209 italy_It14_P44_Pantera lvl:8 coeff:0.7
            '17839421574': 8992455000,  # 51361 italy_It13_Progetto_M35_mod_46 lvl:8 coeff:1.5 !!!!PREMIUM
            '856178310'  : 4316378400,  # 2465 italy_It12_Prototipo_Standard_B lvl:9 coeff:0.72
            '945095814'  : 4376328100,  # 2721 italy_It08_Progetto_M40_mod_65 lvl:10 coeff:0.73
        })
        self.p__COEFFICIENTS.update({
            # sweden
            # lightTank
            '44806086'   : 8392958000,  # 129 sweden_S05_Strv_M21_29 lvl:1 coeff:1.4
            '18006141894': 7193964000,  # 51841 sweden_S15_L_60 lvl:2 coeff:1.2 !!!!PREMIUM
            '133723590'  : 6606456940,  # 385 sweden_S03_Strv_M38 lvl:2 coeff:1.102
            '222641094'  : 6294718500,  # 641 sweden_S12_Strv_M40 lvl:3 coeff:1.05
            # mediumTank
            '311558598'  : 6294718500,  # 897 sweden_S04_Lago_I lvl:4 coeff:1.05
            '400476102'  : 6594467000,  # 1153 sweden_S02_Strv_M42 lvl:5 coeff:1.1
            '489393606'  : 5395473000,  # 1409 sweden_S07_Strv_74 lvl:6 coeff:0.9
            '17917224390': 7193964000,  # 51585 sweden_S01_Strv_74_A2 lvl:6 coeff:1.2 !!!!PREMIUM
            '578311110'  : 4795976000,  # 1665 sweden_S13_Leo lvl:7 coeff:0.8
            '1734238662' : 4196479000,  # 4993 sweden_S29_UDES_14_5 lvl:8 coeff:0.7
            '18272894406': 9591952000,  # 52609 sweden_S23_Strv_81_sabaton lvl:8 coeff:1.6 !!!!PREMIUM
            '18183976902': 9591952000,  # 52353 sweden_S23_Strv_81 lvl:8 coeff:1.6 !!!!PREMIUM
            '18450729414': 8992455000,  # 53121 sweden_S26_Lansen_C lvl:8 coeff:1.5 !!!!PREMIUM
            '1823156166' : 4316378400,  # 5249 sweden_S27_UDES_16 lvl:9 coeff:0.72
            '18717481926': 4376328100,  # 53889 sweden_S28_UDES_15_16_bob lvl:10 coeff:0.73
            '1912073670' : 4376328100,  # 5505 sweden_S28_UDES_15_16 lvl:10 coeff:0.73
            # heavyTank
            '667228614'  : 4795976000,  # 1921 sweden_S18_EMIL_1951_E1 lvl:8 coeff:0.8
            '18361811910': 8992455000,  # 52865 sweden_S25_EMIL_51 lvl:8 coeff:1.5 !!!!PREMIUM
            '756146118'  : 4376328100,  # 2177 sweden_S17_EMIL_1952_E2 lvl:9 coeff:0.73
            '845063622'  : 4256428700,  # 2433 sweden_S16_Kranvagn lvl:10 coeff:0.71
            # AT-SPG
            '933981126'  : 6294718500,  # 2689 sweden_S09_L_120_TD lvl:2 coeff:1.05
            '1022898630' : 5695221500,  # 2945 sweden_S20_Ikv_72 lvl:3 coeff:0.95
            '1111816134' : 5575322100,  # 3201 sweden_S19_Sav_M43 lvl:4 coeff:0.93
            '1200733638' : 5875070600,  # 3457 sweden_S14_Ikv_103 lvl:5 coeff:0.98
            '1289651142' : 5401467970,  # 3713 sweden_S08_Ikv_65_Alt_2 lvl:6 coeff:0.901
            '1378568646' : 4795976000,  # 3969 sweden_S06_Ikv_90_Typ_B_Bofors lvl:7 coeff:0.8
            '18095059398': 9591952000,  # 52097 sweden_S22_Strv_S1 lvl:8 coeff:1.6 !!!!PREMIUM
            '1467486150' : 4316378400,  # 4225 sweden_S21_UDES_03 lvl:8 coeff:0.72
            '1556403654' : 4196479000,  # 4481 sweden_S10_Strv_103_0_Series lvl:9 coeff:0.7
            '1645321158' : 3776831100,  # 4737 sweden_S11_Strv_103B lvl:10 coeff:0.63
        })
        self.p__COEFFICIENTS.update({
            # poland
            # lightTank
            '406033446'  : 8506862430,  # 1169 poland_Pl14_4TP lvl:1 coeff:1.419
            '494950950'  : 6594467000,  # 1425 poland_Pl09_7TP lvl:2 coeff:1.1
            '139280934'  : 7793461000,  # 401 poland_Pl01_TKS_20mm lvl:2 coeff:1.3 !!!!PREMIUM
            '583868454'  : 6594467000,  # 1681 poland_Pl06_10TP lvl:3 coeff:1.1
            '672785958'  : 6102879460,  # 1937 poland_Pl07_14TP lvl:4 coeff:1.018
            # mediumTank
            '761703462'  : 6021347868,  # 2193 poland_Pl12_25TP_KSUST_II lvl:5 coeff:1.0044
            '50363430'   : 7493712500,  # 145 poland_Pl03_PzV_Poland lvl:6 coeff:1.25 !!!!PREMIUM
            '850620966'  : 5395473000,  # 2449 poland_Pl10_40TP_Habicha lvl:6 coeff:0.9
            '17833864230': 7493712500,  # 51345 poland_Pl16_T34_85_Rudy lvl:6 coeff:1.25 !!!!PREMIUM
            # heavyTank
            '939538470'  : 5143684260,  # 2705 poland_Pl11_45TP_Habicha lvl:7 coeff:0.858
            '1028455974' : 4742021270,  # 2961 poland_Pl13_53TP_Markowskiego lvl:8 coeff:0.791
            '317115942'  : 8992455000,  # 913 poland_Pl08_50TP_prototyp lvl:8 coeff:1.5 !!!!PREMIUM
            '1117373478' : 4376328100,  # 3217 poland_Pl05_50TP_Tyszkiewicza lvl:9 coeff:0.73
            '1206290982' : 4256428700,  # 3473 poland_Pl15_60TP_Lewandowskiego lvl:10 coeff:0.71
        })
        self.p__COEFFICIENTS.update({
            # japan
            # lightTank
            '211526406'  : 7793461000,  # 609 japan_J01_NC27 lvl:1 coeff:1.3
            '1100701446' : 7791063012,  # 3169 japan_J02_Te_Ke lvl:2 coeff:1.2996 !!!!PREMIUM
            '300443910'  : 6594467000,  # 865 japan_J03_Ha_Go lvl:2 coeff:1.1
            '833948934'  : 6594467000,  # 2401 japan_J04_Ke_Ni lvl:3 coeff:1.1
            '1011783942' : 7193964000,  # 2913 japan_J06_Ke_Ho lvl:4 coeff:1.2
            # mediumTank
            '122608902'  : 7193964000,  # 353 japan_J15_Chi_Ni lvl:2 coeff:1.2
            '2078793990' : 6594467000,  # 5985 japan_J26_Type_89 lvl:2 coeff:1.1
            '745031430'  : 6594467000,  # 2145 japan_J07_Chi_Ha lvl:3 coeff:1.1
            '567196422'  : 6594467000,  # 1633 japan_J09_Chi_He lvl:4 coeff:1.1
            '478278918'  : 5994970000,  # 1377 japan_J08_Chi_Nu lvl:5 coeff:1.0
            '17906109702': 8992455000,  # 51553 japan_J12_Chi_Nu_Kai lvl:5 coeff:1.5 !!!!PREMIUM
            '656113926'  : 5095724500,  # 1889 japan_J10_Chi_To lvl:6 coeff:0.85
            '389361414'  : 4616126900,  # 1121 japan_J11_Chi_Ri lvl:7 coeff:0.77
            '18083944710': 8992455000,  # 52065 japan_J18_STA_2_3 lvl:8 coeff:1.5 !!!!PREMIUM
            '18350697222': 8992455000,  # 52833 japan_J30_Edelweiss lvl:8 coeff:1.5 !!!!PREMIUM
            '922866438'  : 4136529300,  # 2657 japan_J13_STA_1 lvl:8 coeff:0.69
            '1189618950' : 4496227500,  # 3425 japan_J14_Type_61 lvl:9 coeff:0.75
            '1278536454' : 4376328100,  # 3681 japan_J16_ST_B1 lvl:10 coeff:0.73
            # heavyTank
            '1634206470' : 6294718500,  # 4705 japan_J21_Type_91 lvl:3 coeff:1.05
            '1545288966' : 6294718500,  # 4449 japan_J22_Type_95 lvl:4 coeff:1.05
            '1989876486' : 6294718500,  # 5729 japan_J23_Mi_To lvl:5 coeff:1.05
            '18172862214': 7193964000,  # 52321 japan_J19_Tiger_I_Jpn lvl:6 coeff:1.2 !!!!PREMIUM
            '1900958982' : 5395473000,  # 5473 japan_J24_Mi_To_130_tons lvl:6 coeff:0.9
            '1812041478' : 4975825100,  # 5217 japan_J28_O_I_100 lvl:7 coeff:0.83
            '1723123974' : 4795976000,  # 4961 japan_J27_O_I_120 lvl:8 coeff:0.8
            '18261779718': 8992455000,  # 52577 japan_J29_Nameless lvl:8 coeff:1.5 !!!!PREMIUM
            '1456371462' : 4256428700,  # 4193 japan_J25_Type_4 lvl:9 coeff:0.71
            '1367453958' : 4376328100,  # 3937 japan_J20_Type_2605 lvl:10 coeff:0.73

            # lightTank
            # '17995027206': None, #51809 japan_J05_Ke_Ni_B lvl:3 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=51809 #ype 98 Ke-Ni Otsu, Этого танка нет ни у кого
        })
        self.p__COEFFICIENTS.update({
            # china
            # lightTank
            '461606886'  : 8506862430,  # 1329 china_Ch06_Renault_NC31 lvl:1 coeff:1.419
            '817276902'  : 6762326160,  # 2353 china_Ch07_Vickers_MkE_Type_BT26 lvl:2 coeff:1.128
            '1528616934' : 6039332778,  # 4401 china_Ch08_Type97_Chi_Ha lvl:3 coeff:1.0074
            '1084029414' : 6196400992,  # 3121 china_Ch09_M5 lvl:4 coeff:1.0336
            '1706451942' : 5545347250,  # 4913 china_Ch15_59_16 lvl:6 coeff:0.925
            '22513147878': 8093209500,  # 64817 china_Ch24_Type64 lvl:6 coeff:1.35 !!!!PREMIUM
            '1172946918' : 4676076600,  # 3377 china_Ch16_WZ_131 lvl:7 coeff:0.78
            '105936870'  : 8392958000,  # 305 china_Ch02_Type62 lvl:7 coeff:1.4 !!!!PREMIUM
            '1350781926' : 4043607265,  # 3889 china_Ch17_WZ131_1_WZ132 lvl:8 coeff:0.6745
            '21535055334': 8992455000,  # 62001 china_Ch42_WalkerBulldog_M41D lvl:8 coeff:1.5 !!!!PREMIUM
            '1973204454' : 4016629900,  # 5681 china_Ch28_WZ_132A lvl:9 coeff:0.67
            '2062121958' : 3956680200,  # 5937 china_Ch29_Type_62C_prot lvl:10 coeff:0.66
            # mediumTank
            '1617534438' : 6654416700,  # 4657 china_Ch21_T34 lvl:5 coeff:1.11
            '1795369446' : 5449427730,  # 5169 china_Ch20_Type58 lvl:6 coeff:0.909
            '372689382'  : 4676076600,  # 1073 china_Ch04_T34_1 lvl:7 coeff:0.78
            '22246395366': 9442077750,  # 64049 china_Ch14_T34_3 lvl:8 coeff:1.575 !!!!PREMIUM
            '17019366'   : 9442077750,  # 49 china_Ch01_Type59 lvl:8 coeff:1.575 !!!!PREMIUM
            '194854374'  : 9442077750,  # 561 china_Ch01_Type59_Gold lvl:8 coeff:1.575 !!!!PREMIUM
            '22157477862': 8992455000,  # 63793 china_Ch26_59_Patton lvl:8 coeff:1.5 !!!!PREMIUM
            '550524390'  : 4244438760,  # 1585 china_Ch05_T34_2 lvl:8 coeff:0.708
            '639441894'  : 4256428700,  # 1841 china_Ch18_WZ-120 lvl:9 coeff:0.71
            '22068560358': 4376328100,  # 63537 china_Ch25_121_mod_1971B lvl:10 coeff:0.73 !!!!PREMIUM
            '1439699430' : 4376328100,  # 4145 china_Ch19_121 lvl:10 coeff:0.73
            # heavyTank
            '1261864422' : 5239603780,  # 3633 china_Ch10_IS2 lvl:7 coeff:0.874
            '22602065382': 9442077750,  # 65073 china_Ch03_WZ_111_A lvl:8 coeff:1.575 !!!!PREMIUM
            '995111910'  : 4688066540,  # 2865 china_Ch11_110 lvl:8 coeff:0.782
            '283771878'  : 9442077750,  # 817 china_Ch03_WZ-111 lvl:8 coeff:1.575 !!!!PREMIUM
            '22424230374': 9292203500,  # 64561 china_Ch23_112 lvl:8 coeff:1.55 !!!!PREMIUM
            '728359398'  : 4196479000,  # 2097 china_Ch12_111_1_2_3 lvl:9 coeff:0.7
            '1884286950' : 4640106780,  # 5425 china_Ch22_113 lvl:10 coeff:0.774
            '2151039462' : 4616126900,  # 6193 china_Ch41_WZ_111_5A lvl:10 coeff:0.77
            # AT-SPG
            '2239956966' : 6294718500,  # 6449 china_Ch30_T-26G_FT lvl:2 coeff:1.05
            '2328874470' : 5695221500,  # 6705 china_Ch31_M3G_FT lvl:3 coeff:0.95
            '2417791974' : 5395473000,  # 6961 china_Ch32_SU-76G_FT lvl:4 coeff:0.9
            '2506709478' : 5695221500,  # 7217 china_Ch33_60G_FT lvl:5 coeff:0.95
            '2595626982' : 5395473000,  # 7473 china_Ch34_WZ131G_FT lvl:6 coeff:0.9
            '2684544486' : 4795976000,  # 7729 china_Ch35_T-34-2G_FT lvl:7 coeff:0.8
            '2773461990' : 4316378400,  # 7985 china_Ch36_WZ111_1G_FT lvl:8 coeff:0.72
            '21979642854': 8992455000,  # 63281 china_Ch39_WZ120_1G_FT lvl:8 coeff:1.5 !!!!PREMIUM
            '2862379494' : 4196479000,  # 8241 china_Ch37_WZ111G_FT lvl:9 coeff:0.7
            '2951296998' : 3716881400,  # 8497 china_Ch38_WZ113G_FT lvl:10 coeff:0.62

            # heavyTank
            # '21801807846': None, #62769 china_Ch22_113P lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=62769 #только КИТАЙ
            # '21712890342': None, #62513 china_Ch22_113_Beijing_Opera lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=62513 #только КИТАЙ
            # '21623972838': None, #62257 china_Ch41_WZ_111_QL lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=62257 #только КИТАЙ

            # AT-SPG
            # '21890725350': None, #63025 china_Ch40_WZ120G_FT lvl:9 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=63025 #только КИТАЙ
        })
        self.p__COEFFICIENTS.update({
            # czech
            # lightTank
            '39248742'   : 8392958000,  # 113 czech_Cz06_Kolohousenka lvl:1 coeff:1.4
            '128166246'  : 6594467000,  # 369 czech_Cz03_LT_vz35 lvl:2 coeff:1.1
            '217083750'  : 6294718500,  # 625 czech_Cz10_LT_vz38 lvl:3 coeff:1.05
            # mediumTank
            '306001254'  : 5994970000,  # 881 czech_Cz11_V_8_H lvl:4 coeff:1.0
            '394918758'  : 5994970000,  # 1137 czech_Cz09_T_24 lvl:5 coeff:1.0
            '17911667046': 7793461000,  # 51569 czech_Cz01_Skoda_T40 lvl:6 coeff:1.3 !!!!PREMIUM
            '483836262'  : 5395473000,  # 1393 czech_Cz08_T_25 lvl:6 coeff:0.9
            '572753766'  : 4616126900,  # 1649 czech_Cz05_T34_100 lvl:7 coeff:0.77
            '18000584550': 8992455000,  # 51825 czech_Cz13_T_27 lvl:8 coeff:1.5 !!!!PREMIUM
            '661671270'  : 4316378400,  # 1905 czech_Cz07_TVP_46 lvl:8 coeff:0.72
            '750588774'  : 4256428700,  # 2161 czech_Cz02_TVP_T50 lvl:9 coeff:0.71
            '839506278'  : 4376328100,  # 2417 czech_Cz04_T50_51 lvl:10 coeff:0.73
        })
        self.p__COEFFICIENTS.update({
            # uk
            # lightTank
            '1806484134' : 7187969030,  # 5201 uk_GB03_Cruiser_Mk_I lvl:2 coeff:1.199
            '205969062'  : 6594467000,  # 593 uk_GB14_M2 lvl:2 coeff:1.1
            '19056479910': 7791063012,  # 54865 uk_GB76_Mk_VIC lvl:2 coeff:1.2996 !!!!PREMIUM
            '2695659174' : 6534517300,  # 7761 uk_GB58_Cruiser_Mk_III lvl:2 coeff:1.09
            '2606741670' : 6528522330,  # 7505 uk_GB59_Cruiser_Mk_IV lvl:3 coeff:1.089
            '2428906662' : 6528522330,  # 6993 uk_GB69_Cruiser_Mk_II lvl:3 coeff:1.089
            '472721574'  : 5994970000,  # 1361 uk_GB15_Stuart_I lvl:3 coeff:1.0
            '2251071654' : 6456582690,  # 6481 uk_GB60_Covenanter lvl:4 coeff:1.077
            '1717566630' : 6150839220,  # 4945 uk_GB04_Valentine lvl:4 coeff:1.026
            '20745912486': 4675477103,  # 59729 uk_GB104_GSR_3301_Setter lvl:7 coeff:0.7799
            '20656994982': 4076579600,  # 59473 uk_GB102_LHMTV lvl:8 coeff:0.68
            '20301324966': 8992455000,  # 58449 uk_GB101_FV1066_Senlac lvl:8 coeff:1.5 !!!!PREMIUM
            '20390242470': 4017229397,  # 58705 uk_GB103_GSOR3301_AVR_FS lvl:9 coeff:0.6701
            '20479159974': 3956680200,  # 58961 uk_GB100_Manticore lvl:10 coeff:0.66
            # mediumTank
            '28134054'   : 9813765890,  # 81 uk_GB01_Medium_Mark_I lvl:1 coeff:1.637
            '117051558'  : 7511697410,  # 337 uk_GB05_Vickers_Medium_Mk_II lvl:2 coeff:1.253
            '828391590'  : 6528522330,  # 2385 uk_GB06_Vickers_Medium_Mk_III lvl:3 coeff:1.089
            '294886566'  : 6150839220,  # 849 uk_GB07_Matilda lvl:4 coeff:1.026
            '18345139878': 7553662200,  # 52817 uk_GB33_Sentinel_AC_I lvl:4 coeff:1.26 !!!!PREMIUM
            '561639078'  : 5994970000,  # 1617 uk_GB17_Grant_I lvl:4 coeff:1.0
            '739474086'  : 6336683290,  # 2129 uk_GB20_Crusader lvl:5 coeff:1.057
            '18611892390': 9172304100,  # 53585 uk_GB68_Matilda_Black_Prince lvl:5 coeff:1.53 !!!!PREMIUM
            '4474009254' : 5994970000,  # 12881 uk_GB50_Sherman_III lvl:5 coeff:1.0
            '19501067430': 7313863400,  # 56145 uk_GB35_Sentinel_AC_IV lvl:6 coeff:1.22 !!!!PREMIUM
            '383804070'  : 5587312040,  # 1105 uk_GB21_Cromwell lvl:6 coeff:0.932
            '19856737446': 7793461000,  # 57169 uk_GB95_Ekins_Firefly_M4A4 lvl:6 coeff:1.3 !!!!PREMIUM
            '19412149926': 7493712500,  # 55889 uk_GB85_Cromwell_Berlin lvl:6 coeff:1.25 !!!!PREMIUM
            '1272979110' : 5095724500,  # 3665 uk_GB19_Sherman_Firefly lvl:6 coeff:0.85
            '1895401638' : 4616126900,  # 5457 uk_GB22_Comet lvl:7 coeff:0.77
            '19767819942': 8992455000,  # 56913 uk_GB94_Centurion_Mk5-1_RAAC lvl:8 coeff:1.5 !!!!PREMIUM
            '5363184294' : 9292203500,  # 15441 uk_GB87_Chieftain_T95_turret lvl:8 coeff:1.55 !!!!PREMIUM
            '2073236646' : 4945850250,  # 5969 uk_GB23_Centurion lvl:8 coeff:0.825
            '19323232422': 9591952000,  # 55633 uk_GB70_N_FV4202_105 lvl:8 coeff:1.6 !!!!PREMIUM
            '1984319142' : 4376328100,  # 5713 uk_GB24_Centurion_Mk3 lvl:9 coeff:0.73
            '2517824166' : 4376328100,  # 7249 uk_GB86_Centurion_Action_X lvl:10 coeff:0.73
            '5185349286' : 4376328100,  # 14929 uk_GB70_FV4202_105 lvl:10 coeff:0.73
            # heavyTank
            '18878644902': 8392958000,  # 54353 uk_GB51_Excelsior lvl:5 coeff:1.4 !!!!PREMIUM
            '1006226598' : 6684391550,  # 2897 uk_GB08_Churchill_I lvl:5 coeff:1.115
            '18700809894': 8273058600,  # 53841 uk_GB63_TOG_II lvl:6 coeff:1.38 !!!!PREMIUM
            '1628649126' : 5875070600,  # 4689 uk_GB09_Churchill_VII lvl:6 coeff:0.98
            '1095144102' : 5011794920,  # 3153 uk_GB10_Black_Prince lvl:7 coeff:0.836
            '19145397414': 7793461000,  # 55121 uk_GB52_A45 lvl:7 coeff:1.3 !!!!PREMIUM
            '19678902438': 8992455000,  # 56657 uk_GB93_Caernarvon_AX lvl:8 coeff:1.5 !!!!PREMIUM
            '1361896614' : 4945850250,  # 3921 uk_GB11_Caernarvon lvl:8 coeff:0.825
            '1539731622' : 4508217440,  # 4433 uk_GB12_Conqueror lvl:9 coeff:0.752
            '5452101798' : 4466252650,  # 15697 uk_GB91_Super_Conqueror lvl:10 coeff:0.745
            '2162154150' : 4466252650,  # 6225 uk_GB13_FV215b lvl:10 coeff:0.745 !!!!PREMIUM
            '20123489958': 4376328100,  # 57937 uk_GB98_T95_FV4201_Chieftain lvl:10 coeff:0.73 !!!!PREMIUM
            '5274266790' : 4376328100,  # 15185 uk_GB84_Chieftain_Mk6 lvl:10 coeff:0.73 !!!!PREMIUM
            # AT-SPG
            '2873494182' : 6594467000,  # 8273 uk_GB39_Universal_CarrierQF2 lvl:2 coeff:1.1
            '2784576678' : 5395473000,  # 8017 uk_GB42_Valentine_AT lvl:3 coeff:0.9
            '3140246694' : 5665246650,  # 9041 uk_GB57_Alecto lvl:4 coeff:0.945
            '4651844262' : 5695221500,  # 13393 uk_GB44_Archer lvl:5 coeff:0.95
            '3051329190' : 5976985090,  # 8785 uk_GB73_AT2 lvl:5 coeff:0.997
            '3318081702' : 5395473000,  # 9553 uk_GB74_AT8 lvl:6 coeff:0.9
            '20034572454': 8572807100,  # 57681 uk_GB96_Excalibur lvl:6 coeff:1.43 !!!!PREMIUM
            '5007514278' : 5395473000,  # 14417 uk_GB45_Achilles_IIC lvl:6 coeff:0.9
            '3406999206' : 6066909640,  # 9809 uk_GB40_Gun_Carrier_Churchill lvl:6 coeff:1.012
            '18789727398': 8273058600,  # 54097 uk_GB71_AT_15A lvl:7 coeff:1.38 !!!!PREMIUM
            '3495916710' : 4766001150,  # 10065 uk_GB75_AT7 lvl:7 coeff:0.795
            '4918596774' : 4496227500,  # 14161 uk_GB41_Challenger lvl:7 coeff:0.75
            '20834829990': 8992455000,  # 59985 uk_GB99_Turtle_Mk1 lvl:8 coeff:1.5 !!!!PREMIUM
            '2962411686' : 4340358280,  # 8529 uk_GB72_AT15 lvl:8 coeff:0.724
            '5096431782' : 4256428700,  # 14673 uk_GB80_Charioteer lvl:8 coeff:0.71
            '4562926758' : 3896730500,  # 13137 uk_GB81_FV4004 lvl:9 coeff:0.65
            '18256222374': 4286403550,  # 52561 uk_GB32_Tortoise lvl:9 coeff:0.715
            '3229164198' : 3495067510,  # 9297 uk_GB48_FV215b_183 lvl:10 coeff:0.583 !!!!PREMIUM
            '4829679270' : 3596982000,  # 13905 uk_GB83_FV4005 lvl:10 coeff:0.6
            '5541019302' : 3495067510,  # 15953 uk_GB92_FV217 lvl:10 coeff:0.583
            # SPG
            '3673751718' : 6894215500,  # 10577 uk_GB25_Loyd_Gun_Carriage lvl:2 coeff:1.15
            '18967562406': 10850895700,  # 54609 uk_GB78_Sexton_I lvl:3 coeff:1.81 !!!!PREMIUM
            '1184061606' : 6534517300,  # 3409 uk_GB27_Sexton lvl:3 coeff:1.09
            '3762669222' : 6294718500,  # 10833 uk_GB26_Birch_Gun lvl:4 coeff:1.05
            '3851586726' : 6594467000,  # 11089 uk_GB28_Bishop lvl:5 coeff:1.1
            '4118339238' : 5994970000,  # 11857 uk_GB77_FV304 lvl:6 coeff:1.0
            '3940504230' : 4795976000,  # 11345 uk_GB29_Crusader_5inch lvl:7 coeff:0.8
            '4207256742' : 4496227500,  # 12113 uk_GB79_FV206 lvl:8 coeff:0.75
            '4029421734' : 4496227500,  # 11601 uk_GB30_FV3805 lvl:9 coeff:0.75
            '4296174246' : 4616126900,  # 12369 uk_GB31_Conqueror_Gun lvl:10 coeff:0.77

            # heavyTank
            # '20568077478': None, #59217 uk_GB105_Black_Prince_2019 lvl:6 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=59217 #A43 BP prototype, Этого танка нет ни у кого
            # '19589984934': None, #56401 uk_GB88_T95_Chieftain_turret lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=56401 #T95/Chieftain, Этого танка нет ни у кого
        })
        self.p__COEFFICIENTS.update({
            # france
            # lightTank
            '200411718'  : 9771801100,  # 577 france_F01_RenaultFT lvl:1 coeff:1.63
            '15049634886': 7193964000,  # 43329 france_F111_AM39_Gendron_Somua lvl:2 coeff:1.2 !!!!PREMIUM
            '5268709446' : 6594467000,  # 15169 france_F50_FCM36_20t lvl:2 coeff:1.1
            '556081734'  : 7649581720,  # 1601 france_F02_D1 lvl:2 coeff:1.276
            '5535461958' : 6594467000,  # 15937 france_F49_RenaultR35 lvl:2 coeff:1.1
            '467164230'  : 7307868430,  # 1345 france_F12_Hotchkiss_H35 lvl:2 coeff:1.219
            '15227469894': 6534517300,  # 43841 france_F42_AMR_35 lvl:2 coeff:1.09 !!!!PREMIUM
            '2067679302' : 6672401610,  # 5953 france_F13_AMX38 lvl:3 coeff:1.113
            '1000669254' : 6270738620,  # 2881 france_F14_AMX40 lvl:4 coeff:1.046
            '4913039430' : 5994970000,  # 14145 france_F62_ELC_AMX lvl:5 coeff:1.0
            '6246801990' : 5215623900,  # 17985 france_F109_AMD_Panhard_178B lvl:6 coeff:0.87
            '2245514310' : 5233608810,  # 6465 france_F15_AMX_12t lvl:6 coeff:0.873
            '1800926790' : 4939855280,  # 5185 france_F16_AMX_13_75 lvl:7 coeff:0.824
            '6335719494' : 4675477103,  # 18241 france_F107_Hotchkiss_EBR lvl:7 coeff:0.7799
            '21985200198': 8391759006,  # 63297 france_F69_AMX13_57_100_GrandFinal lvl:7 coeff:1.3998 !!!!PREMIUM
            '22163035206': 8392958000,  # 63809 france_F69_AMX13_57_100 lvl:7 coeff:1.4 !!!!PREMIUM
            '15138552390': 8992455000,  # 43585 france_F106_Panhard_EBR_75_Mle1954 lvl:8 coeff:1.5 !!!!PREMIUM
            '6068966982' : 4076579600,  # 17473 france_F87_Batignolles-Chatillon_12t lvl:8 coeff:0.68
            '6424636998' : 4076579600,  # 18497 france_F110_Lynx_6x6 lvl:8 coeff:0.68
            '21362777670': 8992455000,  # 61505 france_F97_ELC_EVEN_90 lvl:8 coeff:1.5 !!!!PREMIUM
            '1712009286' : 4016629900,  # 4929 france_F17_AMX_13_90 lvl:9 coeff:0.67
            '6513554502' : 4017229397,  # 18753 france_F100_Panhard_EBR_90 lvl:9 coeff:0.6701
            '5980049478' : 3956680200,  # 17217 france_F88_AMX_13_105 lvl:10 coeff:0.66
            '6602472006' : 3956680200,  # 19009 france_F108_Panhard_EBR_105 lvl:10 coeff:0.66
            # mediumTank
            '4557369414' : 5994970000,  # 13121 france_F44_Somua_S35 lvl:3 coeff:1.0
            '111494214'  : 6144844250,  # 321 france_F03_D2 lvl:3 coeff:1.025
            '5179791942' : 5994970000,  # 14913 france_F70_SARL42 lvl:4 coeff:1.0
            '1534174278' : 6294718500,  # 4417 france_F11_Renault_G1R lvl:5 coeff:1.05
            '21096025158': 7493712500,  # 60737 france_F113_Bretagne_Panther lvl:6 coeff:1.25 !!!!PREMIUM
            '22074117702': 8992455000,  # 63553 france_F68_AMX_Chasseur_de_char_46 lvl:8 coeff:1.5 !!!!PREMIUM
            '21896282694': 8992455000,  # 63041 france_F73_M4A1_Revalorise lvl:8 coeff:1.5 !!!!PREMIUM
            '21718447686': 9591952000,  # 62529 france_F19_Lorraine40t lvl:8 coeff:1.6 !!!!PREMIUM
            '1978761798' : 4897890490,  # 5697 france_F75_Char_de_25t lvl:9 coeff:0.817
            '5446544454' : 4496227500,  # 15681 france_F71_AMX_30_prototype lvl:9 coeff:0.75
            '5357626950' : 4376328100,  # 15425 france_F72_AMX_30 lvl:10 coeff:0.73
            '1267421766' : 4496227500,  # 3649 france_F18_Bat_Chatillon25t lvl:10 coeff:0.75
            # heavyTank
            '378246726'  : 6474567600,  # 1089 france_F04_B1 lvl:4 coeff:1.08
            '2334431814' : 6474567600,  # 6721 france_F05_BDR_G1B lvl:5 coeff:1.08
            '911751750'  : 5431442820,  # 2625 france_F06_ARL_44 lvl:6 coeff:0.906
            '2423349318' : 4766001150,  # 6977 france_F07_AMX_M4_1945 lvl:7 coeff:0.795
            '21629530182': 8992455000,  # 62273 france_F84_Somua_SM lvl:8 coeff:1.5 !!!!PREMIUM
            '5713296966' : 4795976000,  # 16449 france_F81_Char_de_65t lvl:8 coeff:0.8
            '21540612678': 9591952000,  # 62017 france_F74_AMX_M4_1949_Liberte lvl:8 coeff:1.6 !!!!PREMIUM
            '22251952710': 8662731650,  # 64065 france_F65_FCM_50t lvl:8 coeff:1.445 !!!!PREMIUM
            '1089586758' : 4754011210,  # 3137 france_F08_AMX_50_100 lvl:8 coeff:0.793
            '21807365190': 9591952000,  # 62785 france_F74_AMX_M4_1949 lvl:8 coeff:1.6 !!!!PREMIUM
            '1356339270' : 4208468940,  # 3905 france_F09_AMX_50_120 lvl:9 coeff:0.702
            '5802214470' : 4316378400,  # 16705 france_F83_AMX_M4_Mle1949_Bis lvl:9 coeff:0.72
            '2156596806' : 4496227500,  # 6209 france_F10_AMX_50B lvl:10 coeff:0.75
            '5891131974' : 4256428700,  # 16961 france_F82_AMX_M4_Mle1949_Ter lvl:10 coeff:0.71
            # AT-SPG
            '2690101830' : 5935020300,  # 7745 france_F30_RenaultFT_AC lvl:2 coeff:0.99
            '2867936838' : 5503382460,  # 8257 france_F52_RenaultUE57 lvl:3 coeff:0.918
            '822834246'  : 7793461000,  # 2369 france_F27_FCM_36Pak40 lvl:3 coeff:1.3 !!!!PREMIUM
            '3401441862' : 5809125930,  # 9793 france_F32_Somua_Sau_40 lvl:4 coeff:0.969
            '21273860166': 8692706500,  # 61249 france_F112_M10_RBFM lvl:5 coeff:1.45 !!!!PREMIUM
            '3490359366' : 5437437790,  # 10049 france_F33_S_35CA lvl:5 coeff:0.907
            '4023864390' : 5467412640,  # 11585 france_F34_ARL_V39 lvl:6 coeff:0.912
            '3757111878' : 4718041390,  # 10817 france_F35_AMX_AC_Mle1946 lvl:7 coeff:0.787
            '4201699398' : 4256428700,  # 12097 france_F36_AMX_AC_Mle1948 lvl:8 coeff:0.71
            '21451695174': 8992455000,  # 61761 france_F89_Canon_dassaut_de_105 lvl:8 coeff:1.5 !!!!PREMIUM
            '3846029382' : 4196479000,  # 11073 france_F37_AMX50_Foch lvl:9 coeff:0.7
            '4824121926' : 3177334100,  # 13889 france_F64_AMX_50Fosh_155 lvl:10 coeff:0.53 !!!!PREMIUM
            '6157884486' : 3176734603,  # 17729 france_F64_AMX_50Fosh_B lvl:10 coeff:0.5299
            # SPG
            '289329222'  : 6894215500,  # 833 france_F20_RenaultBS lvl:2 coeff:1.15
            '1178504262' : 6474567600,  # 3393 france_F21_Lorraine39_L_AM lvl:3 coeff:1.08
            '5090874438' : 6510537420,  # 14657 france_F66_AMX_Ob_Am105 lvl:4 coeff:1.086
            '1445256774' : 6618446880,  # 4161 france_F22_AMX_105AM lvl:5 coeff:1.104
            '733916742'  : 8093209500,  # 2113 france_F28_105_leFH18B2 lvl:5 coeff:1.35 !!!!PREMIUM
            '1623091782' : 6726356340,  # 4673 france_F23_AMX_13F3AM lvl:6 coeff:1.122
            '2512266822' : 5395473000,  # 7233 france_F24_Lorraine155_50 lvl:7 coeff:0.9
            '2601184326' : 4256428700,  # 7489 france_F25_Lorraine155_51 lvl:8 coeff:0.71
            '5001956934' : 3836780800,  # 14401 france_F67_Bat_Chatillon155_55 lvl:9 coeff:0.64
            '4112781894' : 4676076600,  # 11841 france_F38_Bat_Chatillon155_58 lvl:10 coeff:0.78

            # mediumTank
            # '21184942662': None, #60993 france_F85_M4A1_FL10 lvl:6 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=60993 #M4A1 FL 10, в разработке
            # '20918190150': None, #60225 france_F116_Bat_Chatillon_Bourrasque lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=60225 #в разработке
            # '21007107654': None, #60481 france_F114_Projet_4_1 lvl:9 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=60481 #Char Futur 4, в разработке

        })
        self.p__COEFFICIENTS.update({
            # usa
            # lightTank
            '14238262662': 8992455000,  # 40993 usa_A01_T1_Cunningham_bot lvl:1 coeff:1.5
            '189297030'  : 8183134050,  # 545 usa_A01_T1_Cunningham lvl:1 coeff:1.365
            '17883880326': 7613611900,  # 51489 usa_A19_T2_lt lvl:2 coeff:1.27 !!!!PREMIUM
            '18595220358': 8692706500,  # 53537 usa_A74_T1_E6 lvl:2 coeff:1.45 !!!!PREMIUM
            '14505015174': 8392958000,  # 41761 usa_A22_M5_Stuart_bootcamp lvl:2 coeff:1.4
            '19128725382': 7793461000,  # 55073 usa_A93_T7_Combat_Car lvl:2 coeff:1.3 !!!!PREMIUM
            '14416097670': 8992455000,  # 41505 usa_A03_M3_Stuart_bootcamp lvl:2 coeff:1.5
            '633884550'  : 6606456940,  # 1825 usa_A02_M2_lt lvl:2 coeff:1.102
            '100379526'  : 6414617900,  # 289 usa_A03_M3_Stuart lvl:3 coeff:1.07
            '18061715334': 7553662200,  # 52001 usa_A33_MTLS-1G14 lvl:3 coeff:1.26 !!!!PREMIUM
            '18328467846': 9412102900,  # 52769 usa_A43_M22_Locust lvl:3 coeff:1.57 !!!!PREMIUM
            '1789812102' : 6474567600,  # 5153 usa_A22_M5_Stuart lvl:4 coeff:1.08
            '3390327174' : 5994970000,  # 9761 usa_A34_M24_Chaffee lvl:5 coeff:1.0
            '1878729606' : 6594467000,  # 5409 usa_A23_M7_med lvl:5 coeff:1.1
            '5791099782' : 5095724500,  # 16673 usa_A94_T37 lvl:6 coeff:0.85
            '5257594758' : 5275573600,  # 15137 usa_A71_T21 lvl:6 coeff:0.88
            '5435429766' : 4676076600,  # 15649 usa_A103_T71E1 lvl:7 coeff:0.78
            '6858109830' : 4676076600,  # 19745 usa_A112_T71E2R lvl:7 coeff:0.78
            '6235687302' : 4076579600,  # 17953 usa_A97_M41_Bulldog lvl:8 coeff:0.68
            '20106817926': 8992455000,  # 57889 usa_A99_T92_LT lvl:8 coeff:1.5 !!!!PREMIUM
            '6324604806' : 4016629900,  # 18209 usa_A100_T49 lvl:9 coeff:0.67
            '6769192326' : 3956680200,  # 19489 usa_A116_XM551 lvl:10 coeff:0.66
            # mediumTank
            '1967647110' : 6756331190,  # 5665 usa_A24_T2_med lvl:2 coeff:1.127
            '14327180166': 8392958000,  # 41249 usa_A24_T2_med_bot lvl:2 coeff:1.4
            '1700894598' : 6258748680,  # 4897 usa_A25_M2_med lvl:3 coeff:1.044
            '1078472070' : 6648421730,  # 3105 usa_A04_M3_Grant lvl:4 coeff:1.109
            '18150632838': 9532002300,  # 52257 usa_A44_M4A2E4 lvl:5 coeff:1.59 !!!!PREMIUM
            '4368419718' : 8392958000,  # 12577 usa_A78_M4_Improved lvl:5 coeff:1.4 !!!!PREMIUM
            '367132038'  : 5803130960,  # 1057 usa_A05_M4_Sherman lvl:5 coeff:0.968
            '17972797830': 9292203500,  # 51745 usa_A62_Ram-II lvl:5 coeff:1.55 !!!!PREMIUM
            '20729240454': 7313863400,  # 59681 usa_A118_M4_Thunderbolt lvl:6 coeff:1.22 !!!!PREMIUM
            '456049542'  : 5203633960,  # 1313 usa_A06_M4A3E8_Sherman lvl:6 coeff:0.868
            '19484395398': 7313863400,  # 56097 usa_A104_M4A3E8A lvl:6 coeff:1.22 !!!!PREMIUM
            '3479244678' : 5119704380,  # 10017 usa_A36_Sherman_Jumbo lvl:6 coeff:0.854
            '4101667206' : 7793461000,  # 11809 usa_A86_T23E3 lvl:7 coeff:1.3 !!!!PREMIUM
            '20818157958': 7793461000,  # 59937 usa_A121_M26_Cologne lvl:7 coeff:1.3 !!!!PREMIUM
            '544967046'  : 4652096720,  # 1569 usa_A07_T20 lvl:7 coeff:0.776
            '811719558'  : 9591952000,  # 2337 usa_A08_T23 lvl:8 coeff:1.6
            '19928982918': 8992455000,  # 57377 usa_A111_T25_Pilot lvl:8 coeff:1.5 !!!!PREMIUM
            '5079759750' : 4016629900,  # 14625 usa_A90_T69 lvl:8 coeff:0.67
            '19840065414': 9442077750,  # 57121 usa_A63_M46_Patton_KR lvl:8 coeff:1.575 !!!!PREMIUM
            '4635172230' : 9442077750,  # 13345 usa_A80_T26_E4_SuperPershing lvl:8 coeff:1.575 !!!!PREMIUM
            '18684137862': 8992455000,  # 53793 usa_A81_T95_E2 lvl:8 coeff:1.5 !!!!PREMIUM
            '2056564614' : 4244438760,  # 5921 usa_A35_Pershing lvl:8 coeff:0.708
            '21618415494': 8992455000,  # 62241 usa_A127_TL_1_LPC lvl:8 coeff:1.5 !!!!PREMIUM
            '5346512262' : 4196479000,  # 15393 usa_A89_T54E1 lvl:9 coeff:0.7
            '3123574662' : 4502222470,  # 8993 usa_A63_M46_Patton lvl:9 coeff:0.751
            '5524347270' : 4376328100,  # 15905 usa_A92_M60 lvl:10 coeff:0.73 !!!!PREMIUM
            '4901924742' : 4400307980,  # 14113 usa_A120_M48A5 lvl:10 coeff:0.734
            # heavyTank
            '1167389574' : 6558497180,  # 3361 usa_A09_T1_hvy lvl:5 coeff:1.094
            '11462022'   : 9711851400,  # 33 usa_A21_T14 lvl:5 coeff:1.62 !!!!PREMIUM
            '278214534'  : 5587312040,  # 801 usa_A10_M6 lvl:6 coeff:0.932
            '1345224582' : 5011794920,  # 3873 usa_A11_T29 lvl:7 coeff:0.836
            '18239550342': 10011599900,  # 52513 usa_A45_M6A2E1 lvl:8 coeff:1.67 !!!!PREMIUM
            '20373570438': 8992455000,  # 58657 usa_A115_Chrysler_K_GF lvl:8 coeff:1.5 !!!!PREMIUM
            '1523059590' : 4963835160,  # 4385 usa_A12_T32 lvl:8 coeff:0.828
            '20551405446': 9442077750,  # 59169 usa_A117_T26E5_Patriot lvl:8 coeff:1.575 !!!!PREMIUM
            '989554566'  : 9442077750,  # 2849 usa_A13_T34_hvy lvl:8 coeff:1.575 !!!!PREMIUM
            '20462487942': 9442077750,  # 58913 usa_A117_T26E5 lvl:8 coeff:1.575 !!!!PREMIUM
            '3301409670' : 4406302950,  # 9505 usa_A66_M103 lvl:9 coeff:0.735
            '21440580486': 4675477103,  # 61729 usa_A125_AEP_1 lvl:9 coeff:0.7799 !!!!PREMIUM
            '3745997190' : 4406302950,  # 10785 usa_A69_T110E5 lvl:10 coeff:0.735
            '5168677254' : 4376328100,  # 14881 usa_A67_T57_58 lvl:10 coeff:0.73
            '21529497990': 8992455000, #61985 usa_A124_T54E2 lvl:8 coeff:1.5 !!!!PREMIUM https://premomer.org/tank.php?id=61985 #M54 Renegade
            # AT-SPG
            '2145482118' : 6294718500,  # 6177 usa_A46_T3 lvl:2 coeff:1.05
            '2234399622' : 5695221500,  # 6433 usa_A109_T56_GMC lvl:3 coeff:0.95
            '2678987142' : 5005799950,  # 7713 usa_A29_T40 lvl:4 coeff:0.835
            '3568162182' : 5389478030,  # 10273 usa_A57_M8A1 lvl:4 coeff:0.899
            '3657079686' : 5779151080,  # 10529 usa_A58_T67 lvl:5 coeff:0.964
            '2412234630' : 5851090720,  # 6945 usa_A30_M10_Wolverine lvl:5 coeff:0.976
            '4012749702' : 4783986060,  # 11553 usa_A41_M18_Hellcat lvl:6 coeff:0.798
            '2501152134' : 5161669170,  # 7201 usa_A31_M36_Slagger lvl:6 coeff:0.861
            '21262745478': 7792262006,  # 61217 usa_A123_T78 lvl:6 coeff:1.2998 !!!!PREMIUM
            '19573312902': 8093209500,  # 56353 usa_A101_M56 lvl:7 coeff:1.35 !!!!PREMIUM
            '19662230406': 8392958000,  # 56609 usa_A102_T28_concept lvl:7 coeff:1.4 !!!!PREMIUM
            '3212492166' : 4897890490,  # 9249 usa_A64_T25_AT lvl:7 coeff:0.817
            '3834914694' : 4388318040,  # 11041 usa_A72_T25_2 lvl:7 coeff:0.732
            '21707332998': 4783386563,  # 62497 usa_A130_Super_Hellcat lvl:7 coeff:0.7979 !!!!PREMIUM
            '20995992966': 8992455000,  # 60449 usa_A122_TS-5 lvl:8 coeff:1.5 !!!!PREMIUM
            '2856822150' : 4340358280,  # 8225 usa_A39_T28 lvl:8 coeff:0.724
            '3923832198' : 4262423670,  # 11297 usa_A68_T28_Prototype lvl:8 coeff:0.711
            '3034657158' : 4136529300,  # 8737 usa_A40_T95 lvl:9 coeff:0.69
            '900637062'  : 4322373370,  # 2593 usa_A14_T30 lvl:9 coeff:0.721
            '4813007238' : 3788821040,  # 13857 usa_A85_T110E3 lvl:10 coeff:0.632
            '4546254726' : 3746856250,  # 13089 usa_A83_T110E4 lvl:10 coeff:0.625
            # SPG
            '722802054'  : 7193964000,  # 2081 usa_A107_T1_HMC lvl:2 coeff:1.2
            '1256307078' : 6594467000,  # 3617 usa_A16_M7_Priest lvl:3 coeff:1.1
            '6413522310' : 6594467000,  # 18465 usa_A108_T18_HMC lvl:3 coeff:1.1
            '1611977094' : 6474567600,  # 4641 usa_A17_M37 lvl:4 coeff:1.08
            '6502439814' : 6594467000,  # 18721 usa_A27_T82 lvl:4 coeff:1.1
            '1434142086' : 7014114900,  # 4129 usa_A18_M41 lvl:5 coeff:1.17
            '5702182278' : 6114869400,  # 16417 usa_A87_M44 lvl:6 coeff:1.02
            '2767904646' : 4975825100,  # 7969 usa_A32_M12 lvl:7 coeff:0.83
            '2590069638' : 4196479000,  # 7457 usa_A37_M40M43 lvl:8 coeff:0.7
            '5613264774' : 4136529300,  # 16161 usa_A88_M53_55 lvl:9 coeff:0.69
            '2945739654' : 4795976000,  # 8481 usa_A38_T92 lvl:10 coeff:0.8

            # lightTank
            # '20017900422': None, #57633 usa_A112_T71E2 lvl:7 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=57633 #T71 CMCD P, только КИТАЙ

            # mediumTank
            # '19395477894': None, #55841 usa_A95_T95_E6 lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=55841 # T95E6 за глобалку

            # heavyTank
            # '21351662982': None, #61473 usa_A126_PzVI_Tiger_II_capt lvl:7 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=61473 #King Tiger (захваченный), TwichPrime
            # '20640322950': None, #59425 usa_A13_T34_hvy_BF lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=59425 #T34 Черный
            # '20907075462': None, #60193 usa_A115_Chrysler_K lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=60193 #Chrysler K
            # '21529497990': None, #61985 usa_A124_T54E2 lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=61985 #M54 Renegade
        })
        self.p__COEFFICIENTS.update({
            # germany
            # lightTank
            '1072914726' : 7859405670,  # 3089 germany_G12_Ltraktor lvl:1 coeff:1.311
            '717244710'  : 6535716294,  # 2065 germany_G06_PzII lvl:2 coeff:1.0902
            '272657190'  : 6552502210,  # 785 germany_G07_Pz35t lvl:2 coeff:1.093
            '18233992998': 5994970000,  # 52497 germany_G33_H39_captured lvl:2 coeff:1.0 !!!!PREMIUM
            '20990435622': 7193964000,  # 60433 germany_G108_PzKpfwII_AusfD lvl:2 coeff:1.2 !!!!PREMIUM
            '4451779878' : 7493712500,  # 12817 germany_G53_PzI lvl:2 coeff:1.25
            '16544560422': 7193964000,  # 47633 germany_G139_MKA lvl:2 coeff:1.2 !!!!PREMIUM
            '1695337254' : 6504542450,  # 4881 germany_G102_Pz_III lvl:3 coeff:1.085
            '4362862374' : 5994970000,  # 12561 germany_G63_PzI_ausf_C lvl:3 coeff:1.0
            '1161832230' : 5917035390,  # 3345 germany_G08_Pz38t lvl:3 coeff:0.987
            '17967240486': 7193964000,  # 51729 germany_G36_PzII_J lvl:3 coeff:1.2 !!!!PREMIUM
            '4540697382' : 5994970000,  # 13073 germany_G82_Pz_II_AusfG lvl:3 coeff:1.0
            '19034250534': 8992455000,  # 54801 germany_G50_T-15 lvl:3 coeff:1.5 !!!!PREMIUM
            '22057445670': 7791662509,  # 63505 germany_G117_Toldi_III lvl:3 coeff:1.2997 !!!!PREMIUM
            '2851264806' : 6312703410,  # 8209 germany_G52_Pz38_NA lvl:4 coeff:1.053
            '2139924774' : 6294718500,  # 6161 germany_G25_PzII_Luchs lvl:4 coeff:1.05
            '1873172262' : 6114869400,  # 5393 germany_G26_VK1602 lvl:5 coeff:1.02
            '3473687334' : 4945850250,  # 10001 germany_G66_VK2801 lvl:6 coeff:0.825
            '6585799974' : 4676076600,  # 18961 germany_G113_SP_I_C lvl:7 coeff:0.78
            '4985284902' : 8392958000,  # 14353 germany_G85_Auf_Panther lvl:7 coeff:1.4
            '7030387494' : 4076579600,  # 20241 germany_G126_HWK_12 lvl:8 coeff:0.68
            '22235280678': 8392958000,  # 64017 germany_G120_M41_90 lvl:8 coeff:1.4 !!!!PREMIUM
            '17700487974': 8392958000,  # 50961 germany_G120_M41_90_GrandFinal lvl:8 coeff:1.4 !!!!PREMIUM
            '16455642918': 8992455000,  # 47377 germany_G140_HWK_30 lvl:8 coeff:1.5 !!!!PREMIUM
            '6407964966' : 4016629900,  # 18449 germany_G103_RU_251 lvl:9 coeff:0.67
            '6941469990' : 3956680200,  # 19985 germany_G125_Spz_57_Rh lvl:10 coeff:0.66
            # mediumTank
            '18056157990': 7553662200,  # 51985 germany_G34_S35_captured lvl:3 coeff:1.26 !!!!PREMIUM
            '20723683110': 7313863400,  # 59665 germany_G100_Gtraktor_Krupp lvl:3 coeff:1.22 !!!!PREMIUM
            '5963377446' : 5994970000,  # 17169 germany_G83_Pz_IV_AusfA lvl:3 coeff:1.0
            '4718532390' : 6594467000,  # 13585 germany_G86_VK2001DB lvl:4 coeff:1.1
            '1517502246' : 6768321130,  # 4369 germany_G10_PzIII_AusfJ lvl:4 coeff:1.129
            '6052294950' : 6294718500,  # 17425 germany_G80_Pz_IV_AusfD lvl:4 coeff:1.05
            '17878322982': 8872555600,  # 51473 germany_G32_PzV_PzIV lvl:5 coeff:1.48 !!!!PREMIUM
            '18945333030': 9112354400,  # 54545 germany_G46_T-25 lvl:5 coeff:1.52 !!!!PREMIUM
            '2228842278' : 7002124960,  # 6417 germany_G28_PzIII_IV lvl:5 coeff:1.168
            '19123168038': 8392958000,  # 55057 germany_G70_PzIV_Hydro lvl:5 coeff:1.4 !!!!PREMIUM
            '6319047462' : 6594467000,  # 18193 germany_G81_Pz_IV_AusfH lvl:5 coeff:1.1
            '21346105638': 8392958000,  # 61457 germany_G107_PzKpfwIII_AusfK lvl:5 coeff:1.4 !!!!PREMIUM
            '21968528166': 8392358503,  # 63249 germany_G116_Turan_III_prot lvl:5 coeff:1.3999 !!!!PREMIUM
            '19923425574': 7553662200,  # 57361 germany_G77_PzIV_Schmalturm lvl:6 coeff:1.26 !!!!PREMIUM
            '4896367398' : 5395473000,  # 14097 germany_G87_VK3002DB_V1 lvl:6 coeff:0.9
            '2495594790' : 6102879460,  # 7185 germany_G27_VK3001P lvl:6 coeff:1.018
            '5518789926' : 5095724500,  # 15889 germany_G96_VK3002M lvl:6 coeff:0.85
            '20012343078': 9352153200,  # 57617 germany_G78_Panther_M10 lvl:7 coeff:1.56 !!!!PREMIUM
            '1428584742' : 4550182230,  # 4113 germany_G24_VK3002DB lvl:7 coeff:0.759
            '450492198'  : 4825950850,  # 1297 germany_G03_PzV_Panther lvl:7 coeff:0.805
            '2940182310' : 4742021270,  # 8465 germany_G64_Panther_II lvl:8 coeff:0.791
            '20901518118': 8992455000,  # 60177 germany_G106_PzKpfwPanther_AusfF lvl:8 coeff:1.5 !!!!PREMIUM
            '22324198182': 8992455000,  # 64273 germany_G119_Pz58_Mutz lvl:8 coeff:1.5 !!!!PREMIUM
            '22146363174': 5994970000,  # 63761 germany_G119_Panzer58 lvl:8 coeff:1.0 !!!!PREMIUM
            '4807449894' : 4016629900,  # 13841 germany_G88_Indien_Panzer lvl:8 coeff:0.67
            '3562604838' : 4670081630,  # 10257 germany_G54_E-50 lvl:9 coeff:0.779
            '5163119910' : 4496227500,  # 14865 germany_G91_Pro_Ag_A lvl:9 coeff:0.75
            '21168270630': 4795976000,  # 60945 germany_G105_T-55_NVA_DDR lvl:9 coeff:0.8 !!!!PREMIUM
            '5074202406' : 4496227500,  # 14609 germany_G89_Leopard1 lvl:10 coeff:0.75
            '4273944870' : 4376328100,  # 12305 germany_G73_E50_Ausf_M lvl:10 coeff:0.73
            # heavyTank
            '18145075494': 8153159200,  # 52241 germany_G35_B-1bis_captured lvl:4 coeff:1.36 !!!!PREMIUM
            '4629614886' : 6294718500,  # 13329 germany_G90_DW_II lvl:4 coeff:1.05
            '895079718'  : 6594467000,  # 2577 germany_G13_VK3001H lvl:5 coeff:1.1
            '20634765606': 8392958000,  # 59409 germany_G122_VK6501H lvl:5 coeff:1.4 !!!!PREMIUM
            '17078065446': 7193964000,  # 49169 germany_G136_Tiger_131 lvl:6 coeff:1.2 !!!!PREMIUM
            '806162214'  : 5581317070,  # 2321 germany_G15_VK3601H lvl:6 coeff:0.931
            '18322910502': 7193964000,  # 52753 germany_G137_PzVI_Tiger_217 lvl:6 coeff:1.2 !!!!PREMIUM
            '183739686'  : 5401467970,  # 529 germany_G04_PzVI_Tiger_I lvl:7 coeff:0.901
            '21879610662': 8992455000,  # 62993 germany_G118_VK4503 lvl:7 coeff:1.5 !!!!PREMIUM
            '3740439846' : 4819955880,  # 10769 germany_G57_PzVI_Tiger_P lvl:7 coeff:0.804
            '3651522342' : 5347513240,  # 10513 germany_G67_VK4502A lvl:8 coeff:0.892
            '6852552486' : 4975825100,  # 19729 germany_G115_Typ_205B lvl:8 coeff:0.83
            '18856415526': 9891700500,  # 54289 germany_G51_Lowe lvl:8 coeff:1.65 !!!!PREMIUM
            '1784254758' : 5119704380,  # 5137 germany_G16_PzVIB_Tiger_II lvl:8 coeff:0.854
            '16989147942': 8992455000,  # 48913 germany_G138_VK168_02 lvl:8 coeff:1.5 !!!!PREMIUM
            '16722395430': 8992455000,  # 48145 germany_G138_VK168_02_Mauerbrecher lvl:8 coeff:1.5 !!!!PREMIUM
            '19478838054': 8992455000,  # 56081 germany_G141_VK7501K lvl:8 coeff:1.5 !!!!PREMIUM
            '16277807910': 8992455000,  # 46865 germany_G143_E75_TS lvl:8 coeff:1.5 !!!!PREMIUM
            '6496882470' : 4556177200,  # 18705 germany_G110_Typ_205 lvl:9 coeff:0.76
            '2584512294' : 4724036360,  # 7441 germany_G58_VK4502P lvl:9 coeff:0.788
            '3384769830' : 4514212410,  # 9745 germany_G55_E-75 lvl:9 coeff:0.753
            '2406677286' : 5035774800,  # 6929 germany_G42_Maus lvl:10 coeff:0.84
            '3295852326' : 4580157080,  # 9489 germany_G56_E-100 lvl:10 coeff:0.764
            '6763634982' : 4376328100,  # 19473 germany_G134_PzKpfw_VII lvl:10 coeff:0.73
            '20368013094': 4376328100,  # 58641 germany_G92_VK7201 lvl:10 coeff:0.73 !!!!PREMIUM
            # AT-SPG
            '1250749734' : 5917035390,  # 3601 germany_G21_PanzerJager_I lvl:2 coeff:0.987
            '2317759782' : 5485397550,  # 6673 germany_G20_Marder_II lvl:3 coeff:0.915
            '6230129958' : 5095724500,  # 17937 germany_G101_StuG_III lvl:4 coeff:0.85
            '3918274854' : 5095724500,  # 11281 germany_G39_Marder_III lvl:4 coeff:0.85
            '628327206'  : 5470410125,  # 1809 germany_G09_Hetzer lvl:4 coeff:0.9125
            '361574694'  : 6021347868,  # 1041 germany_G05_StuG_40_AusfG lvl:5 coeff:1.0044
            '21079353126': 8992455000,  # 60689 germany_G104_Stug_IV lvl:5 coeff:1.5 !!!!PREMIUM
            '5607707430' : 5695221500,  # 16145 germany_G76_Pz_Sfl_IVc lvl:5 coeff:0.95
            '19834508070': 8093209500,  # 57105 germany_G41_DickerMax lvl:6 coeff:1.35 !!!!PREMIUM
            '539409702'  : 5875070600,  # 1553 germany_G17_JagdPzIV lvl:6 coeff:0.98
            '4096109862' : 5695221500,  # 11793 germany_G40_Nashorn lvl:6 coeff:0.95
            '3829357350' : 4496227500,  # 11025 germany_G43_Sturer_Emil lvl:7 coeff:0.75
            '21435023142': 7793461000,  # 61713 germany_G109_Steyr_WT lvl:7 coeff:1.3 !!!!PREMIUM
            '1339667238' : 4945850250,  # 3857 germany_G18_JagdPanther lvl:7 coeff:0.825
            '19301003046': 7793461000,  # 55569 germany_G48_E-25 lvl:7 coeff:1.3 !!!!PREMIUM
            '17433735462': 8992455000,  # 50193 germany_G114_Rheinmetall_Skorpian lvl:8 coeff:1.5 !!!!PREMIUM
            '21701775654': 8992455000,  # 62481 germany_G114_Skorpian lvl:8 coeff:1.5 !!!!PREMIUM
            '16811312934': 8992455000,  # 48401 germany_G112_KanonenJagdPanzer_105 lvl:8 coeff:1.5 !!!!PREMIUM
            '4007192358' : 4346353250,  # 11537 germany_G71_JagdPantherII lvl:8 coeff:0.725
            '5785542438' : 4316378400,  # 16657 germany_G99_RhB_Waffentrager lvl:8 coeff:0.72
            '19212085542': 9292203500,  # 55313 germany_G65_JagdTiger_SdKfz_185 lvl:8 coeff:1.55 !!!!PREMIUM
            '21523940646': 8992455000,  # 61969 germany_G112_KanonenJagdPanzer lvl:8 coeff:1.5 !!!!PREMIUM
            '2673429798' : 4346353250,  # 7697 germany_G37_Ferdinand lvl:8 coeff:0.725
            '5696624934' : 4196479000,  # 16401 germany_G97_Waffentrager_IV lvl:9 coeff:0.7
            '2762347302' : 4076579600,  # 7953 germany_G44_JagdTiger lvl:9 coeff:0.68
            '5874459942' : 3596982000,  # 16913 germany_G98_Waffentrager_E100 lvl:10 coeff:0.6
            '4185027366' : 3950685230,  # 12049 germany_G72_JagdPz_E100 lvl:10 coeff:0.659
            '6674717478' : 3596982000,  # 19217 germany_G121_Grille_15_L63 lvl:10 coeff:0.6
            # SPG
            '5252037414' : 7973310100,  # 15121 germany_G93_GW_Mk_VIe lvl:2 coeff:1.33
            '983997222'  : 7074064600,  # 2833 germany_G11_Bison_I lvl:3 coeff:1.18
            '2051007270' : 6474567600,  # 5905 germany_G19_Wespe lvl:3 coeff:1.08
            '1606419750' : 7074064600,  # 4625 germany_G22_Sturmpanzer_II lvl:4 coeff:1.18
            '5429872422' : 6174819100,  # 15633 germany_G95_Pz_Sfl_IVb lvl:4 coeff:1.03
            '1962089766' : 6714366400,  # 5649 germany_G23_Grille lvl:5 coeff:1.12
            '94822182'   : 7014114900,  # 273 germany_G02_Hummel lvl:6 coeff:1.17
            '3118017318' : 5095724500,  # 8977 germany_G49_G_Panther lvl:7 coeff:0.85
            '5340954918' : 4676076600,  # 15377 germany_G94_GW_Tiger_P lvl:8 coeff:0.78
            '3029099814' : 4196479000,  # 8721 germany_G45_G_Tiger lvl:9 coeff:0.7
            '3206934822' : 4915875400,  # 9233 germany_G61_G_E lvl:10 coeff:0.82

            # lightTank
            # '16633477926': None, #47889 germany_G85_Aufklarungspanzer_V lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=47889 #Aufklrungspanzer V, в разработке

            # mediumTank
            # '18767498022': None, #54033 germany_G32_PzV_PzIV_ausf_Alfa lvl:5 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=54033 #Pz.Kpfw. V/IV Alpha, Выдавался Альфа тестерам
            # '16188890406': None, #46609 germany_G142_M48RPz lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=46609 #M48A2 Rumpanzer Паттон с ковшом
            # '17344817958': None, #49937 germany_G119_Panzer58_BF lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=49937 #Schwarzpanzer 58
            # '16366725414': None, #47121 germany_G144_Kpz_50t lvl:9 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=47121 #Kampfpanzer 50 t, Награда за ранговые бои 2019

            # heavyTank
            # '21612858150': None, #62225 germany_G58_VK4502P7 lvl:7 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=62225 #VK 45.02 (P) Ausf. B7, Этого танка нет ни у кого
            # '17255900454': None, #49681 germany_G16_PzVIB_Tiger_II_F lvl:7 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=49681 #Tiger II (H), Этого танка нет ни у кого
            # '21790693158': None, #62737 germany_G115_Typ_205_4_Jun lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=62737 #VK 100.01 (P) Ausf. B, только КИТАЙ

            # AT-SPG
            # '17166982950': None, #49425 germany_G44_JagdTigerH lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=49425 #Jagdtiger (H), Этого танка нет ни у кого
            # '16900230438': None, #48657 germany_G98_Waffentrager_E100_P lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=48657 #Waffentrger auf E 100 (P), только КИТАЙ

        })
        self.p__COEFFICIENTS.update({
            # ussr
            # lightTank
            '1156274886' : 5503382460,  # 3329 ussr_R11_MS-1 lvl:1 coeff:0.918 #changed in 1.9 #fixed
            '356017350'  : 5695221500,  # 1025 ussr_R08_BT-2 lvl:2 coeff:0.95 #changed in 1.9 #fixed
            '14404982982': 10491197500,  # 41473 ussr_R86_LTP_bootcamp lvl:2 coeff:1.75
            '5335397574' : 4915875400,  # 15361 ussr_R42_T-60 lvl:2 coeff:0.82 #changed in 1.9 #fixed
            '1600862406' : 5347513240,  # 4609 ussr_R09_T-26 lvl:2 coeff:0.892 #changed in 1.9 #fixed
            '18939775686': 6534517300,  # 54529 ussr_R84_Tetrarch_LL lvl:2 coeff:1.09 !!!!PREMIUM
            # '17694930630': None, #50945 ussr_R125_T_45 lvl:2 coeff:0.0 !!!!PREMIUM
            '1067357382' : 5011794920,  # 3073 ussr_R22_T-46 lvl:3 coeff:0.836 #changed in 1.9 #fixed
            '267099846'  : 5845095750,  # 769 ussr_R03_BT-7 lvl:4 coeff:0.975  #changed in 1.9 #fixed
            '18317353158': 9591952000,  # 52737 ussr_R67_M3_LL lvl:3 coeff:1.6 !!!!PREMIUM
            '21162713286': 7793461000,  # 60929 ussr_R105_BT_7A lvl:3 coeff:1.3 !!!!PREMIUM
            '5246480070' : 5095724500,  # 15105 ussr_R43_T-70 lvl:3 coeff:0.85 #changed in 1.9 #fixed
            '18584105670': 7880388065,  # 53505 ussr_R56_T-127 lvl:3 coeff:1.3145 !!!!PREMIUM
            '18139518150': 7793461000,  # 52225 ussr_R34_BT-SV lvl:3 coeff:1.3 !!!!PREMIUM
            # '19651115718': None, #56577 ussr_R86_LTP lvl:3 coeff:0.0 !!!!PREMIUM
            # '15560910534': None, #44801 ussr_R161_T_116 lvl:3 coeff:0.0 !!!!PREMIUM
            #'711687366'  : 5917035390,  # 2049 ussr_R12_A-20 lvl:5 coeff:0.987 #changed in 1.9 #fixed
            '18228435654': 9442077750,  # 52481 ussr_R31_Valentine_LL lvl:4 coeff:1.575 !!!!PREMIUM
            '5513232582' : 6114869400,  # 15873 ussr_R44_T80 lvl:4 coeff:1.02 #changed in 1.9 #fixed
            '3379212486' : 8392958000,  # 9729 ussr_R70_T_50_2 lvl:5 coeff:1.4
            '3290294982' : 5779151080,  # 9473 ussr_R41_T-50 lvl:5 coeff:0.964 #changed in 1.9 #fixed
            '5779985094' : 4975825100,  # 16641 ussr_R101_MT25 lvl:6 coeff:0.83 #changed in 1.9 #fixed
            # '15738745542': None, #45313 ussr_R160_T_50_2 lvl:6 coeff:0.0 !!!!PREMIUM #changed in 1.9 #not fixed
            '6758077638' : 4676076600,  # 19457 ussr_R131_Tank_Gavalov lvl:7 coeff:0.78
            '15827663046': 8992455000,  # 45569 ussr_R158_LT_432 lvl:8 coeff:1.5 !!!!PREMIUM
            '6402407622' : 4076579600,  # 18433 ussr_R107_LTB lvl:8 coeff:0.68
            '6313490118' : 4016629900,  # 18177 ussr_R109_T54S lvl:9 coeff:0.67
            '6669160134' : 3956680200,  # 19201 ussr_R132_VNII_100LT lvl:10 coeff:0.66
            # mediumTank
            '16627920582': 7793461000,  # 47873 ussr_R143_T_29 lvl:3 coeff:1.3 !!!!PREMIUM
            '18406270662': 8614771890,  # 52993 ussr_R68_A-32 lvl:4 coeff:1.437 !!!!PREMIUM
            '533852358'  : 5976985090,  # 1537 ussr_R06_T-28 lvl:4 coeff:0.997 #changed in 1.9 #fixed
            '21340548294': 9112354400,  # 61441 ussr_R118_T28_F30 lvl:4 coeff:1.52 !!!!PREMIUM
            '347334'     : 6558497180,  # 1 ussr_R04_T-34 lvl:5 coeff:1.094  #changed in 1.9 #fixed
            '17872765638': 8992455000,  # 51457 ussr_R32_Matilda_II_LL lvl:5 coeff:1.5 !!!!PREMIUM
            '16361168070': 8692706500,  # 47105 ussr_R154_T_34E_1943 lvl:5 coeff:1.45 !!!!PREMIUM
            '20184620742': 7313863400,  # 58113 ussr_R108_T34_85M lvl:6 coeff:1.22 !!!!PREMIUM
            '4268387526' : 4975825100,  # 12289 ussr_R57_A43 lvl:6 coeff:0.83 #changed in 1.9 #fixed
            '889522374'  : 5431442820,  # 2561 ussr_R07_T-34-85 lvl:6 coeff:0.906 #changed in 1.9 #fixed
            '20629208262': 7493712500,  # 59393 ussr_R117_T34_85_Rudy lvl:6 coeff:1.25 !!!!PREMIUM
            # '16716838086': None, #48129 ussr_R140_M4_Loza lvl:6 coeff:0.0 !!!!PREMIUM
            '19828950726': 7493712500,  # 57089 ussr_R98_T44_85 lvl:7 coeff:1.25 !!!!PREMIUM
            '3112459974' : 5563332160,  # 8961 ussr_R46_KV-13 lvl:7 coeff:0.928
            '2312202438' : 5143684260,  # 6657 ussr_R23_T-43 lvl:7 coeff:0.858
            '4357305030' : 4616126900,  # 12545 ussr_R59_A44 lvl:7 coeff:0.77
            '4624057542' : 4016629900,  # 13313 ussr_R60_Object416 lvl:8 coeff:0.67
            '16539003078': 8992455000,  # 47617 ussr_R146_STG lvl:8 coeff:1.5 !!!!PREMIUM
            '20807043270': 8992455000,  # 59905 ussr_R112_T54_45 lvl:8 coeff:1.5 !!!!PREMIUM
            '21518383302': 8992455000,  # 61953 ussr_R122_T44_100 lvl:8 coeff:1.5 !!!!PREMIUM
            '16450085574': 8992455000,  # 47361 ussr_R146_STG_Tday lvl:8 coeff:1.5 !!!!PREMIUM
            '16983590598': 8992455000,  # 48897 ussr_R122_T44_100B lvl:8 coeff:1.5 !!!!PREMIUM
            '16094415558': 8992455000,  # 46337 ussr_R127_T44_100_U lvl:8 coeff:1.5 !!!!PREMIUM
            '21874053318': 8992455000,  # 62977 ussr_R127_T44_100_P lvl:8 coeff:1.5 !!!!PREMIUM
            '16005498054': 8992455000,  # 46081 ussr_R127_T44_100_K lvl:8 coeff:1.5 !!!!PREMIUM
            '1511944902' : 4807965940,  # 4353 ussr_R20_T-44 lvl:8 coeff:0.802
            '6135655110' : 4496227500,  # 17665 ussr_R104_Object_430_II lvl:9 coeff:0.75
            '2756789958' : 4915875400,  # 7937 ussr_R40_T-54 lvl:9 coeff:0.82
            '7558335174' : 4376328100,  # 21761 ussr_R144_K_91 lvl:10 coeff:0.73
            '5957820102' : 4376328100,  # 17153 ussr_R96_Object_430B lvl:10 coeff:0.73
            '4801892550' : 4676076600,  # 13825 ussr_R87_T62A lvl:10 coeff:0.78
            '5424315078' : 4376328100,  # 15617 ussr_R95_Object_907 lvl:10 coeff:0.73 !!!!PREMIUM
            # '7469417670': None, #21505 ussr_R96_Object_430 lvl:9 coeff:0.0

            '5868902598' : 4915875400,  # 16897 ussr_R97_Object_140 lvl:10 coeff:0.82
            '6935912646' : 4376328100,  # 19969 ussr_R148_Object_430_U lvl:10 coeff:0.73
            # heavyTank
            '6491325126' : 5467412640,  # 18689 ussr_R13_KV-1s lvl:6 coeff:0.912 #changed in 1.9 #fixed
            '18761940678': 8832988798,  # 54017 ussr_R38_KV-220 lvl:5 coeff:1.4734 !!!!PREMIUM
            '17961683142': 9442077750,  # 51713 ussr_R33_Churchill_LL lvl:5 coeff:1.575 !!!!PREMIUM
            '4090552518' : 5994970000,  # 11777 ussr_R80_KV1 lvl:5 coeff:1.0 #changed in 1.9 #fixed
            '3912717510' : 5527362340,  # 11265 ussr_R72_T150 lvl:6 coeff:0.922 #changed in 1.9 #fixed
            '978439878'  : 3495067510,  # 2817 ussr_R106_KV85 lvl:6 coeff:0.583 #changed in 1.9 #fixed
            '3645964998' : 5203633960,  # 10497 ussr_R77_KV2 lvl:6 coeff:0.868 #changed in 1.9 #fixed
            # '20895960774': None, #60161 ussr_R114_Object_244 lvl:6 coeff:0.0 !!!!PREMIUM
            # '22496475846': None, #64769 ussr_R152_KV2_W lvl:6 coeff:0.0 !!!!PREMIUM
            '17339260614': 8992455000,  # 49921 ussr_R133_KV_122 lvl:7 coeff:1.5 !!!!PREMIUM
            '20540290758': 8093209500,  # 59137 ussr_R71_IS_2B lvl:7 coeff:1.35 !!!!PREMIUM
            '16183333062': 8093209500,  # 46593 ussr_R156_IS_2M lvl:7 coeff:1.35 !!!!PREMIUM
            '178182342'  : 5605296950,  # 513 ussr_R01_IS lvl:7 coeff:0.935
            '2045449926' : 5359503180,  # 5889 ussr_R39_KV-3 lvl:7 coeff:0.894
            '3201377478' : 8992455000,  # 9217 ussr_R61_Object252 lvl:8 coeff:1.5 !!!!PREMIUM
            '21962970822': 8992455000,  # 63233 ussr_R128_KV4_Kreslavskiy lvl:8 coeff:1.5 !!!!PREMIUM
            '16894673094': 8992455000,  # 48641 ussr_R134_Object_252K lvl:8 coeff:1.5 !!!!PREMIUM
            '17250343110': 8992455000,  # 49665 ussr_R134_Object_252U lvl:8 coeff:1.5 !!!!PREMIUM
            '7113747654' : 4795976000,  # 20481 ussr_R139_IS_M lvl:8 coeff:0.8
            '20451373254': 8992455000,  # 58881 ussr_R113_Object_730 lvl:8 coeff:1.5 !!!!PREMIUM
            '3823800006' : 5527362340,  # 11009 ussr_R73_KV4 lvl:8 coeff:0.922
            '1867614918' : 4777991090,  # 5377 ussr_R19_IS-3 lvl:8 coeff:0.797
            '21785135814': 8992455000,  # 62721 ussr_R123_Kirovets_1 lvl:8 coeff:1.5 !!!!PREMIUM
            '18495188166': 8992455000,  # 53249 ussr_R54_KV-5 lvl:8 coeff:1.5 !!!!PREMIUM
            '20984878278': 8992455000,  # 60417 ussr_R115_IS-3_auto lvl:8 coeff:1.5 !!!!PREMIUM
            '6846995142' : 4616126900,  # 19713 ussr_R151_Object_257_2 lvl:9 coeff:0.77
            '7202665158' : 4616126900,  # 20737 ussr_R153_Object_705 lvl:9 coeff:0.77
            '3734882502' : 4532197320,  # 10753 ussr_R63_ST_I lvl:9 coeff:0.756
            '4001635014' : 4658091690,  # 11521 ussr_R81_IS8 lvl:9 coeff:0.777
            '2134367430' : 4694061510,  # 6145 ussr_R90_IS_4M lvl:10 coeff:0.783
            '2490037446' : 4724036360,  # 7169 ussr_R45_IS-7 lvl:10 coeff:0.788
            '7291582662' : 4376328100,  # 20993 ussr_R145_Object_705_A lvl:10 coeff:0.73
            '7647252678' : 4376328100,  # 22017 ussr_R155_Object_277 lvl:10 coeff:0.73
            '20273538246': 4196479000,  # 58369 ussr_R110_Object_260 lvl:10 coeff:0.7 !!!!PREMIUM
            '16272250566': 4196479000,  # 46849 ussr_R157_Object_279R lvl:10 coeff:0.7 !!!!PREMIUM
            # '7914005190': None, #22785 ussr_R170_IS_2_II lvl:8 coeff:0.0 https://premomer.org/tank.php?id=22785 #Двустволка8
            '15383075526': 8992455000,  # 44289 ussr_R165_Object_703_II lvl:8 coeff:1.5 !!!!PREMIUM
            # '7825087686': None, #22529 ussr_R171_IS_3_II lvl:9 coeff:0.0 https://premomer.org/tank.php?id=22529 #Двустволка9
            # '7736170182': None, #22273 ussr_R169_ST_II lvl:10 coeff:0.0 https://premomer.org/tank.php?id=22273 #Двустволка10
            # AT-SPG
            '1778697414' : 5779151080,  # 5121 ussr_R10_AT-1 lvl:2 coeff:0.964 #changed in 1.9 #fixed
            '14493900486': 10491197500,  # 41729 ussr_R50_SU76I_bootcamp lvl:2 coeff:1.75
            '18850858182': 7193964000,  # 54273 ussr_R50_SU76I lvl:3 coeff:1.2 !!!!PREMIUM
            '2223284934' : 4766001150,  # 6401 ussr_R24_SU-76 lvl:4 coeff:0.795 #changed in 1.9 #fixed
            '2401119942' : 4340358280,  # 6913 ussr_R25_GAZ-74b lvl:4 coeff:0.724 #changed in 1.9 #fixed
            '18673023174': 7793461000,  # 53761 ussr_R78_SU_85I lvl:5 coeff:1.3 !!!!PREMIUM #changed in 1.9 #not fixed
            '89264838'   : 5845095750,  # 257 ussr_R02_SU-85 lvl:5 coeff:0.975 #changed in 1.9 #fixed
            '19028693190': 8572807100,  # 54785 ussr_R49_SU100Y lvl:6 coeff:1.43 !!!!PREMIUM
            '1245192390' : 5119704380,  # 3585 ussr_R17_SU-100 lvl:6 coeff:0.854 #changed in 1.9 #fixed
            '800604870'  : 5077739590,  # 2305 ussr_R18_SU-152 lvl:7 coeff:0.847
            '3557047494' : 4316378400,  # 10241 ussr_R74_SU100M1 lvl:7 coeff:0.72
            '20718125766': 8093209500,  # 59649 ussr_R116_ISU122C_Berlin lvl:7 coeff:1.35 !!!!PREMIUM
            '19206528198': 8632756800,  # 55297 ussr_R89_SU122_44 lvl:7 coeff:1.44 !!!!PREMIUM
            '3468129990' : 4783986060,  # 9985 ussr_R58_SU-101 lvl:8 coeff:0.798
            '16805755590': 8992455000,  # 48385 ussr_R135_T_103 lvl:8 coeff:1.5 !!!!PREMIUM
            '20362455750': 5994970000,  # 58625 ussr_R111_ISU130 lvl:8 coeff:1.0 !!!!PREMIUM
            '2578954950' : 4262423670,  # 7425 ussr_R47_ISU-152 lvl:8 coeff:0.711
            # '15649828038': None, #45057 ussr_R159_SU_130PM lvl:8 coeff:0.0 !!!!PREMIUM
            '2845707462' : 3716881400,  # 8193 ussr_R53_Object_704 lvl:9 coeff:0.62
            '4179470022' : 4208468940,  # 12033 ussr_R75_SU122_54 lvl:9 coeff:0.702
            # '7380500166': None, #21249 ussr_R93_Object263 lvl:9 coeff:0.0
            '4979727558' : 3794816010,  # 14337 ussr_R93_Object263B lvl:10 coeff:0.633
            '7024830150' : 3776831100,  # 20225 ussr_R149_Object_268_4 lvl:10 coeff:0.63
            '4712975046' : 3626956850,  # 13569 ussr_R88_Object268 lvl:10 coeff:0.605
            # SPG
            '1334109894' : 5875070600,  # 3841 ussr_R16_SU-18 lvl:2 coeff:0.98 #changed in 1.9 #fixed
            '2667872454' : 5779151080,  # 7681 ussr_R66_SU-26 lvl:3 coeff:0.964 #changed in 1.9 #fixed
            '1689779910' : 6258748680,  # 4865 ussr_R14_SU-5 lvl:4 coeff:1.044 #changed in 1.9 #fixed
            '5691067590' : 6714366400,  # 16385 ussr_R100_SU122A lvl:5 coeff:1.12 #changed in 1.9 #fixed
            '1956532422' : 5994970000,  # 5633 ussr_R26_SU-8 lvl:6 coeff:1.0 #changed in 1.9 #fixed
            '5602150086' : 5665246650,  # 16129 ussr_R91_SU14_1 lvl:7 coeff:0.945
            '622769862'  : 5605296950,  # 1793 ussr_R15_S-51 lvl:7 coeff:0.935
            '1423027398' : 4676076600,  # 4097 ussr_R27_SU-14 lvl:8 coeff:0.78
            '2934624966' : 4076579600,  # 8449 ussr_R51_Object_212 lvl:9 coeff:0.68
            '3023542470' : 4556177200,  # 8705 ussr_R52_Object_261 lvl:10 coeff:0.76

            # lightTank
            # '19917868230': None, #57345 ussr_R98_T44_85M lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=57345 #Прошел тесты, но по каким-то причинам выпущен не был

            # mediumTank
            # '19740033222': None, #56833 ussr_R99_T44_122 lvl:7 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=56833 #Выдается Супер тестерам

            # '21073795782': None, #60673 ussr_R95_Object_907A lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=60673 #Эксклюзив 100%, только КИТАЙ
            # '21429465798': None, #61697 ussr_R120_T22SR_A22 lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=61697 #Награда за боевые задачи в рамках боёв в режиме "Бой до последнего"

            # heavyTank
            # '17783848134': None, #51201 ussr_R38_KV-220_beta lvl:5 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=51201 #Выдавался Бэта-тестерам
            # '10670447814': None, #30721 ussr_R165_Object_703_II_2 lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=30721 #Этого танка нет ни у кого
            # '17161425606': None, #49409 ussr_R61_Object252_BF lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=49409 #ИС-6 Черный
            # '15471993030': None, #44545 ussr_R119_Object_777 lvl:9 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=44545 #Объект 777 Вариант II, в разработке
            # '10581530310': None, #30465 ussr_R172_Object_752 lvl:9 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=30465 #Объект 752, в разработке
            # '21251630790': None, #61185 ussr_R119_Object_777C lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=61185 #Объект 777 Вариант II С, в разработке
            # '17517095622': None, #50433 ussr_R129_Object_257 lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=50433 #Объект 257 (П), только КИТАЙ

            # AT-SPG
            # '21607300806': None, #62209 ussr_R121_KV4_KTT lvl:8 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=62209 #КВ-4 КТТС По слухам полностью отмененный танк, но присутствует в ангаре у многих старых супер тестеров
            # '17606013126': None, #50689 ussr_R126_Object_730_5 lvl:10 coeff:0.0 !!!!PREMIUM https://premomer.org/tank.php?id=50689 #Объект 268 вариант 5, Этого танка нет ни у кого
        })


class p__Flash(object):
    def p__startBattle(self):
        if not p__config.p__data['battle_show']:
            return
        if not p__g_flash:
            return
        p__g_flash.createComponent('credits', p__COMPONENT_TYPE.PANEL, {
            'x'     : p__config.p__data['battle_x'],
            'y'     : p__config.p__data['battle_y'],
            'width' : 1,
            'height': 1,
            'drag'  : True, 'border': True, 'alignX': p__COMPONENT_ALIGN.LEFT, 'alignY': p__COMPONENT_ALIGN.BOTTOM})

        p__g_flash.createComponent('credits.text', p__COMPONENT_TYPE.LABEL, {
            'shadow': {"distance": 0, "angle": 0, "color": 0x000000, "alpha": 1, "blurX": 1, "blurY": 1, "strength": 1, "quality": 1},
            'text'  : '', 'width': 168, 'height': 25, 'index': 1, 'multiline': True, 'tooltip': '+1000 or -1000 it\'s normal calc\nIf calc incorrect, play battle without damage to fix it.\nFull time replays, no escape!!!'})
        if p__config.p__data['battle_background']:
            p__g_flash.createComponent('credits.image', p__COMPONENT_TYPE.IMAGE, {
                'width': 168, 'height': 25, 'index': 0, 'image': '../maps/icons/quests/inBattleHint.png'})
        p__COMPONENT_EVENT.UPDATED += self.p__update

    def p__stopBattle(self):
        if not p__config.p__data['battle_show']:
            return
        if not p__g_flash:
            return
        p__COMPONENT_EVENT.UPDATED -= self.p__update
        p__g_flash.deleteComponent('credits.text')
        if p__config.p__data['battle_background']:
            p__g_flash.deleteComponent('credits.image')
        p__g_flash.deleteComponent('credits')

    def p__update(self, alias, props):
        if not p__config.p__data['battle_show']:
            return
        if str(alias) == str('credits'):
            x = int(props.get('x', p__config.p__data['battle_x']))
            if x and x != int(p__config.p__data['battle_x']):
                p__config.p__data['battle_x'] = x
            y = int(props.get('y', p__config.p__data['battle_y']))
            if y and y != int(p__config.p__data['battle_y']):
                p__config.p__data['battle_y'] = y
            p__config.p__apply(p__config.p__data)
            # p__g_flash.updateComponent('credits.text', p__data)
            # print '%s Flash coordinates updated : y = %i, x = %i, props: %s' % (alias, p__config.p__data['battle_y'], p__config.p__data['battle_x'], props)

    def setCreditsText(self, text, width=0, height=0):
        if not p__config.p__data['battle_show']:
            return
        if not p__g_flash:
            return
        data = {'visible': True, 'text': text}
        if width:
            data['width'] = width
        if height:
            data['width'] = height
        p__g_flash.updateComponent('credits.text', data)

    def p__visible(self, status):
        if not p__config.p__data['battle_show']:
            return
        p__g_flash.updateComponent('credits', {'visible': status})


class p__BattleResultParser(object):
    def __init__(self):
        self.p__Threads = True
        self.p__ArenaIDQueue = p__Queue()
        self.ResultsCache = []
        self.ResultsAvailable = p__threading.Event()
        self.thread = p__threading.Thread(target=self.WaitResult)
        self.thread.setDaemon(True)
        self.thread.setName('WaitResult')
        self.thread.start()

    def CheckCallback(self, ArenaUniqueID, ErrorCode, battleResults):
        if ErrorCode in [-3, -5]:
            p__BigWorld.callback(1.0, lambda: self.p__ArenaIDQueue.put(ArenaUniqueID))
        elif ErrorCode >= 0:
            if ArenaUniqueID in self.ResultsCache: return
            p__calc.p__receiveBattleResult(True, battleResults)
            # print battleResults.get('arenaUniqueID')
            # print battleResults.get('personal')
            # print battleResults.get('common')

    def WaitResult(self):
        while self.p__Threads:
            ArenaUniqueID = self.p__ArenaIDQueue.get()
            self.ResultsAvailable.wait()
            try:
                p__BigWorld.player().battleResultsCache.get(ArenaUniqueID, p__partial(self.CheckCallback, ArenaUniqueID))
            except Exception as e:
                pass


p__config = p__Config()
p__flashInHangar = flashInHangar()
p__flash = p__Flash()
p__calc = p__CreditsCalculator()
p__results = p__BattleResultParser()


def p__hook_start_battle(*args):
    if p__BigWorld.player().arena.bonusType == p__ARENA_BONUS_TYPE.REGULAR:
        p__calc.p__timer()
    p__hooked_start_battle(*args)


def p__hook_before_delete(*args):
    if p__BigWorld.player().arena.bonusType == p__ARENA_BONUS_TYPE.REGULAR:
        p__calc.p__stopBattle()
    p__hooked_before_delete(*args)


def p__hook_CrewMeta_as_tankmenResponseS(self, p__data):
    if p__g_currentVehicle.item:
        try:
            status = p__g_currentVehicle.itemsCache.items.stats.activePremiumExpiryTime > 0
        except Exception as e:
            status = False
        try:
            p__calc.p__getHangarData(status)
        except Exception as e:
            print 'ERROR: creditCalc crew:', e

    return p__hooked_CrewMeta_as_tankmenResponseS(self, p__data)


def p__hook_onBattleEvents(self, events):
    p__hooked_onBattleEvents(self, events)
    if p__BigWorld.player().arena.bonusType == p__ARENA_BONUS_TYPE.REGULAR:
        p__calc.p__onBattleEvents(events)


def p__hook_LobbyPopulate(self):
    p__hooked_LobbyPopulate(self)
    p__BigWorld.callback(3.0, p__calc.p__hangarMessage)


def p__hook_BattleResultsFormatter_format(self, message, *args):
    arenaUniqueID = message.data.get('arenaUniqueID', 0)
    p__results.p__ArenaIDQueue.put(arenaUniqueID)
    return p__hooked_BattleResultsFormatter_format(self, message, *args)


def p__onAccountBecomePlayer():
    p__results.ResultsAvailable.set()


def p__IntoBattle():
    p__results.ResultsAvailable.clear()


p__hooked_start_battle = p__PlayerAvatar._PlayerAvatar__startGUI
p__hooked_before_delete = p__PlayerAvatar._PlayerAvatar__destroyGUI
p__hooked_onBattleEvents = p__PlayerAvatar.onBattleEvents
p__hooked_CrewMeta_as_tankmenResponseS = p__CrewMeta.as_tankmenResponseS
p__hooked_LobbyPopulate = p__LobbyView._populate
p__hooked_BattleResultsFormatter_format = p__BattleResultsFormatter.format

p__PlayerAvatar._PlayerAvatar__startGUI = p__hook_start_battle
p__PlayerAvatar._PlayerAvatar__destroyGUI = p__hook_before_delete
p__PlayerAvatar.onBattleEvents = p__hook_onBattleEvents
p__CrewMeta.as_tankmenResponseS = p__hook_CrewMeta_as_tankmenResponseS
p__LobbyView._populate = p__hook_LobbyPopulate
p__BattleResultsFormatter.format = p__hook_BattleResultsFormatter_format
p__g_playerEvents.onBattleResultsReceived += p__calc.p__receiveBattleResult
p__g_playerEvents.onAvatarReady += p__IntoBattle
p__g_playerEvents.onAccountBecomePlayer += p__onAccountBecomePlayer


def fini():
    p__results.p__Threads = False


def p__jsonGenerator(nations):
    from CurrentVehicle import g_currentVehicle as p__g_currentVehicle
    import ResMgr as p__ResMgr
    import os as p__os
    import codecs as p__codecs
    import json as p__json
    p__COEFFICIENTS = {}
    resMgr = p__ResMgr.openSection('../version.xml')
    if resMgr is None:
        resMgr = p__ResMgr.openSection('version.xml')
        if resMgr is None:
            resMgr = p__ResMgr.openSection('./version.xml')
    ver = 'temp' if resMgr is None else resMgr.readString('version')
    i1 = ver.find('.')
    i2 = ver.find('#')
    p__PATH = ''.join(['./res_mods/', ver[i1 + 1:i2 - 1], '/system/'])
    if p__os.path.isfile(p__PATH + 'sw_templates.json'):
        try:
            with p__codecs.open(p__PATH + 'sw_templates.json', 'r', encoding='utf-8-sig') as p__json_file:
                p__data = p__json_file.read().decode('utf-8-sig')
                p__COEFFICIENTS.update(p__calc.p__byte_ify(p__json.loads(p__data)))
                p__json_file.close()
        except Exception as e:
            p__COEFFICIENTS.update({})

    def p__deCode(p__compactDescr):
        test = '%s' % (p__compactDescr * 2847 * 122)
        if test in p__COEFFICIENTS:
            return test, round(p__COEFFICIENTS[test] / 1231 / 487 * 0.0001, 6)
        return test, 0.0

    items = p__g_currentVehicle.itemsCache.items.getVehicles()

    def getData(nation, role, found):
        text = ''
        for level in xrange(1, 11):
            for compactDescr in items:
                vehicle = items[compactDescr]
                if vehicle.nationName == nation and vehicle.descriptor.level == level and vehicle.type == role:
                    vehicleCompDesc, balanceCoeff = p__deCode(compactDescr)
                    thatPremium = ' !!!!PREMIUM' if vehicle.isPremium or vehicle.isPremiumIGR else ''
                    details = '#%s %s lvl:%s coeff:%s%s' % (compactDescr, vehicle.name.replace(':', '_'), vehicle.descriptor.level, balanceCoeff, thatPremium)
                    if not found and not balanceCoeff:
                        text += "#'%s': %s, %s https://premomer.org/tank.php?id=%s\n" % (vehicleCompDesc, None, details, compactDescr)
                    if found and balanceCoeff:
                        text += "'%s': %s, %s\n" % (vehicleCompDesc, p__COEFFICIENTS[vehicleCompDesc], details)
        if text:
            print '# %s' % role
        print text

    if not nations:
        nations = ['ussr', 'germany', 'uk', 'japan', 'usa', 'china', 'france', 'czech', 'sweden', 'poland', 'italy']
    roles = ['lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG']

    print '########################### DATA ###########################'
    for nation in nations:
        print '# %s' % nation
        for role in roles:
            getData(nation, role, True)
    print '$$$$$$$$$$$$$$$$$$$$$$$$$$$ DATA $$$$$$$$$$$$$$$$$$$$$$$$$$$'
    for nation in nations:
        print '# %s' % nation
        for role in roles:
            getData(nation, role, False)

    print '!!!!!!!!!!!!!!!!!!!!!!!!!!! DONE !!!!!!!!!!!!!!!!!!!!!!!!!!!'

p__BigWorld.flashInHangar = p__flashInHangar