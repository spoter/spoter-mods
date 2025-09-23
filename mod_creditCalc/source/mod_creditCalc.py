# -*- coding: utf-8 -*-
import codecs
import collections
import json
import os
import threading
from Queue import Queue
from functools import partial

# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import COMPONENT_ALIGN, COMPONENT_EVENT, COMPONENT_TYPE, g_gui, g_guiFlash as g_flash

import BattleReplay
import BigWorld
import Event
import Keys
import ResMgr
from Avatar import PlayerAvatar
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import ARENA_BONUS_TYPE
from frameworks.wulf import WindowLayer as ViewTypes
from gui import InputHandler
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.impl.lobby.crew.widget.crew_widget import CrewWidget
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, g_entitiesFactories
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.battle_constants import VEHICLE_DEVICE_IN_COMPLEX_ITEM, VEHICLE_VIEW_STATE
from gui.battle_control.controllers import feedback_events
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.formatters import icons
from gui.shared.gui_items import Vehicle
from gui.shared.personality import ServicesLocator
from helpers import getLanguageCode
from messenger.formatters.service_channel import BattleResultsFormatter

try:
    # noinspection PyUnresolvedReferences
    from gui import oldskool

    # noinspection PyUnresolvedReferences
    oldskoolCore = BigWorld.oldskoolCore
except Exception:
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
            if not config.data['hangarShow']:
                return
            self.setPosition(config.data['hangar_x'], config.data['hangar_y'])  # x and y
            self.setBackground(config.data['hangarBackground'], '0x000000', 0.4)  # change to false if dont want
            # self.setText('Test Test Test')  # text


class FlashMeta(View):

    def _populate(self):
        super(FlashMeta, self)._populate()
        flashInHangar.setText += self._setText
        flashInHangar.setPosition += self._setPosition
        flashInHangar.setBackground += self._setBackground

    def _dispose(self):
        super(FlashMeta, self)._dispose()

    def py_newPos(self, posX, posY):
        config.data['hangar_x'] = posX
        config.data['hangar_y'] = posY
        config.apply(config.data)

    def _setText(self, text):
        if self._isDAAPIInited():
            self.flashObject.as_setText(text)

    def _setPosition(self, x, y):
        if self._isDAAPIInited():
            self.flashObject.as_setPosition(x, y)

    def _setBackground(self, enabled, bgcolor, alpha):
        if self._isDAAPIInited():
            self.flashObject.as_setBackground(enabled, bgcolor, alpha)


CHASSIS_ALL_ITEMS = frozenset(VEHICLE_DEVICE_IN_COMPLEX_ITEM.keys() + VEHICLE_DEVICE_IN_COMPLEX_ITEM.values())
DAMAGE_EVENTS = frozenset([BATTLE_EVENT_TYPE.RADIO_ASSIST, BATTLE_EVENT_TYPE.TRACK_ASSIST, BATTLE_EVENT_TYPE.STUN_ASSIST, BATTLE_EVENT_TYPE.DAMAGE, BATTLE_EVENT_TYPE.TANKING, BATTLE_EVENT_TYPE.RECEIVED_DAMAGE])

DEBUG = True
DEBUG_COEFF = True


class Config(object):
    def __init__(self):
        self.ids = 'creditCalc'
        self.author = 'www.b4it.org'
        self.version = 'v2.11 (2025-09-23)'
        self.version_id = 211
        self.versionI18n = 3401
        lang = getLanguageCode().lower()
        self.dataDefault = {
            'version'          : self.version_id,
            'enabled'          : True,
            'battle_x'         : 60,
            'battle_y'         : -252,
            'hangar_x'         : 325.0,
            'hangar_y'         : 505.0,
            'battleBackground': True,
            'battleShow'      : True,
            'hangarBackground': True,
            'hangarShow'      : True,
        }
        self.i18n = {
            'version'                         : self.versionI18n,
            'UI_description'                  : 'creditCalc',
            'UI_setting_label_text'           : 'Calculate credits in battle; a ±1000 silver difference is normal dispersion. If larger, play one battle without dealing damage.',
            'UI_setting_label1_text'          : 'Wait until the battle finishes without exiting to the hangar. Income: green = victory, red = defeat. Expenses: ammo and consumables.',
            'UI_setting_label2_text'          : 'Additional info in battle: press ALT and Ctrl keys',
            'UI_setting_battleBackground_text': 'Background in battle',
            'UI_setting_hangarBackground_text': 'Background in Garage',
            'UI_setting_hangarShow_text'      : 'Show in Garage',
            'UI_setting_battleShow_text'      : 'Show in battle',
            'UI_setting_battle_x_text'        : 'Battle text position: X',
            'UI_setting_battle_y_text'        : 'Battle text position: Y',
            'UI_setting_hangar_x_text'        : 'Garage text position: X',
            'UI_setting_hangar_y_text'        : 'Garage text position: Y',

        }
        if 'ru' in lang:
            self.i18n.update({
                'UI_setting_label_text'           : 'Калькуляция серебра в бою; разница ±1000 — нормальный разброс. Если больше — сыграйте один бой без нанесения урона.',
                'UI_setting_label1_text'          : 'Дождитесь завершения боя, не выходя в ангар. Доход: зелёный — победа, красный — поражение. Расходы: цена снарядов и расходников.',
                'UI_setting_label2_text'          : 'Дополнительная информация в бою: нажмите клавиши ALT и CTRL',
                'UI_setting_battleBackground_text': 'Задний фон в бою',
                'UI_setting_hangarBackground_text': 'Задний фон в ангаре',
                'UI_setting_hangarShow_text'      : 'Показывать в ангаре',
                'UI_setting_battleShow_text'      : 'Показывать в бою',
                'UI_setting_battle_x_text'        : 'Позиция текста в бою: X',
                'UI_setting_battle_y_text'        : 'Позиция текста в бою: Y',
                'UI_setting_hangar_x_text'        : 'Позиция текста в ангаре: X',
                'UI_setting_hangar_y_text'        : 'Позиция текста в ангаре: Y',
            })
        if 'cn' in lang or 'zh' in lang:
            self.i18n.update({
                "UI_description"                  : "银币收益计算",
                "UI_setting_battleBackground_text": "战斗界面背景",
                "UI_setting_hangarShow_text"      : "在车库中显示",
                "UI_setting_hangarBackground_text": "车库背景",
                "UI_setting_battleShow_text"      : "显示在战斗中",
                "UI_setting_label1_text"          : "等待战斗结束，不要返回机库。收益：绿色=胜利，红色=失败。开销：弹药与消耗品。",
                "UI_setting_label2_text"          : "战斗中更多信息：按下 ALT 和 Ctrl 键",
                "UI_setting_label_text"           : "在战斗中计算银币；±1000 银币差额属于正常波动。若更大：进行一场不造成伤害的战斗。",
                "UI_setting_battle_x_text"        : "战斗文本位置: X",
                "UI_setting_battle_y_text"        : "战斗文本位置: Y",
                "UI_setting_hangar_x_text"        : "车库文本位置: X",
                "UI_setting_hangar_y_text"        : "车库文本位置: Y",
            })
        if g_gui:
            self.data, self.i18n = g_gui.register_data(self.ids, self.dataDefault, self.i18n, 'www.b4it.org')
            g_gui.register(self.ids, self.template, self.data, self.apply)
            print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [
                g_gui.optionCheckBox(*self.getI18nParam('hangarShow')),
                g_gui.optionCheckBox(*self.getI18nParam('battleShow')),
                g_gui.optionCheckBox(*self.getI18nParam('hangarBackground')),
                g_gui.optionCheckBox(*self.getI18nParam('battleBackground')),
                g_gui.optionLabel(self.i18n['UI_setting_label_text']),
                g_gui.optionLabel(self.i18n['UI_setting_label1_text']),
                g_gui.optionLabel(self.i18n['UI_setting_label2_text']),
            ],
            'column2'        : [
                g_gui.optionSlider(*self.getI18nParamSlider('battle_x', -2000, 2000, 1)),
                g_gui.optionSlider(*self.getI18nParamSlider('battle_y', -2000, 2000, 1)),
                g_gui.optionSlider(*self.getI18nParamSlider('hangar_x', -2000, 2000, 1)),
                g_gui.optionSlider(*self.getI18nParamSlider('hangar_y', -2000, 2000, 1)),
            ]
        }

    def getI18nParam(self, name):
        # return varName, value, defaultValue, text, tooltip, defaultValueText
        tooltip = 'UI_setting_%s_tooltip' % name
        tooltip = self.i18n[tooltip] if tooltip in self.i18n else ''
        defaultValueText = 'UI_setting_%s_default' % name
        defaultValueText = self.i18n[defaultValueText] if defaultValueText in self.i18n else '%s' % self.dataDefault[name]
        return name, self.data[name], self.dataDefault[name], self.i18n['UI_setting_%s_text' % name], tooltip, defaultValueText

    def getI18nParamSlider(self, name, minValue, maxValue, step):
        # return varName, value, defaultValue, minValue, maxValue, step, text, formats, tooltip, defaultValueText
        params = self.getI18nParam(name)
        formats = 'UI_setting_%s_formats' % name
        formats = self.i18n[formats] if formats in self.i18n else ''
        return params[0], params[1], params[2], minValue, maxValue, step, params[3], formats, params[4], params[5]

    def apply(self, settings):
        if g_gui:
            self.data = g_gui.update_data(self.ids, settings, 'www.b4it.org')
            g_gui.update(self.ids, self.template)


class MyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(MyJSONEncoder, self).__init__(*args, **kwargs)
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
                    output.append(json.dumps(item, ensure_ascii=False, encoding='utf-8-sig'))
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
                output.append(self.current_indent_str + json.dumps(key, ensure_ascii=False, encoding='utf-8-sig') + ": " + self.encode(value))
            self.current_indent -= self.indent
            self.current_indent_str = "".join([" " for x in range(self.current_indent)])
            return "{\n" + ",\n".join(output) + "\n" + self.current_indent_str + "}"
        else:
            return json.dumps(o, ensure_ascii=False, encoding='utf-8-sig')


class CreditsCalculator(object):
    def __init__(self):
        self.coeffTable()
        self.COEFFICIENTS['USE_DATA'] = False
        self.AVERAGES = [(1.37, 1.37), (1.13, 1.28), (1.04, 1.35), (1.029, 1.42), (1.04, 1.5), (0.92, 1.3), (0.82, 1.4), (0.75, 1.5), (0.72, 0.72), (0.71, 0.72)]
        self.coeffDefaults = [0.53, 0.583, 0.6, 0.605, 0.62, 0.625, 0.63, 0.632, 0.633, 0.64, 0.65, 0.659, 0.66, 0.67, 0.6745, 0.68, 0.69, 0.7, 0.702, 0.708, 0.71, 0.711, 0.715, 0.72, 0.721, 0.724, 0.725, 0.73, 0.732, 0.734, 0.735, 0.745, 0.75, 0.751, 0.752, 0.753, 0.756, 0.759, 0.76, 0.764, 0.77, 0.774, 0.776, 0.777, 0.779, 0.78, 0.782, 0.783, 0.787, 0.788, 0.79, 0.791, 0.793, 0.795, 0.797, 0.798, 0.8, 0.802, 0.804, 0.805, 0.817, 0.82, 0.824, 0.825, 0.828, 0.83, 0.835, 0.836, 0.84, 0.847, 0.85, 0.854, 0.858, 0.861, 0.865, 0.868, 0.873, 0.874, 0.88, 0.883, 0.892, 0.894, 0.899, 0.9, 0.901, 0.906, 0.907, 0.909, 0.912, 0.9125, 0.915, 0.918, 0.922, 0.925, 0.928, 0.93, 0.931, 0.932, 0.935, 0.943, 0.945, 0.95, 0.964, 0.968, 0.969, 0.975, 0.976, 0.98, 0.987, 0.99, 0.997, 1.0, 1.0044, 1.0074, 1.012, 1.018, 1.02, 1.025, 1.026, 1.03, 1.0336, 1.044, 1.045, 1.046, 1.05, 1.053, 1.057, 1.07, 1.077, 1.08, 1.085, 1.086, 1.088, 1.089, 1.09, 1.0902, 1.093, 1.094, 1.1, 1.102, 1.104, 1.108, 1.109,
                              1.11, 1.113, 1.115, 1.12, 1.122, 1.127, 1.128, 1.129, 1.14, 1.1425, 1.15, 1.154, 1.1585, 1.168, 1.17, 1.1782, 1.18, 1.199, 1.2, 1.21, 1.219, 1.22, 1.25, 1.253, 1.2558, 1.26, 1.27, 1.276, 1.3, 1.311, 1.3145, 1.33, 1.35, 1.36, 1.365, 1.38, 1.4, 1.419, 1.43, 1.437, 1.44, 1.445, 1.45, 1.46, 1.4734, 1.48, 1.485, 1.49, 1.5, 1.52, 1.53, 1.55, 1.56, 1.57, 1.575, 1.59, 1.6, 1.62, 1.63, 1.637, 1.64, 1.65, 1.67, 1.75, 1.81]
        resMgr = ResMgr.openSection('../version.xml')
        if resMgr is None:
            resMgr = ResMgr.openSection('version.xml')
            if resMgr is None:
                resMgr = ResMgr.openSection('./version.xml')
        ver = 'temp' if resMgr is None else resMgr.readString('version')
        i1 = ver.find('.')
        i2 = ver.find('#')
        self.PATH = ''.join(['./res_mods/', ver[i1 + 1:i2 - 1], '/system/'])
        self.readJson()
        self.PREMIUM_ACC = self.COEFFICIENTS['USE_DATA']
        self.iconCredits = '<img src=\"img://gui/maps/icons/quests/bonuses/big/credits.png\" vspace=\"-7\" width=\"20\" height=\"20\" />'
        self.textWin = ''
        self.textDEFEAT = ''
        self.tempResults = {}
        self.item = None
        self.altMode = False
        self.ctrlMode = False
        self.hangarOutcome = 0
        self.hangarItems = {}
        self.hangarAmmo = {}
        self.killed = False
        self.repairCost = 0
        self.costRepairs = {}
        self.usedItems = {}
        self.hangarHeader = ''

    def byte_ify(self, inputs):
        if inputs:
            if isinstance(inputs, dict):
                return {self.byte_ify(key): self.byte_ify(value) for key, value in inputs.iteritems()}
            elif isinstance(inputs, list):
                return [self.byte_ify(element) for element in inputs]
            elif isinstance(inputs, unicode):
                return inputs.encode('utf-8')
            else:
                return inputs
        return inputs

    def writeJson(self):
        if not os.path.exists(self.PATH):
            os.makedirs(self.PATH)
        with codecs.open(self.PATH + 'sw_templates.json', 'w', encoding='utf-8-sig') as json_file:
            data = json.dumps(collections.OrderedDict(sorted(self.COEFFICIENTS.items(), key=lambda t: t[0])), sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig', separators=(',', ': '), cls=MyJSONEncoder)
            json_file.write('%s' % self.byte_ify(data))
            json_file.close()

    def readJson(self):
        if os.path.isfile(self.PATH + 'sw_templates.json'):
            try:
                with codecs.open(self.PATH + 'sw_templates.json', 'r', encoding='utf-8-sig') as json_file:
                    data = json_file.read().decode('utf-8-sig')
                    self.COEFFICIENTS.update(self.byte_ify(json.loads(data)))
                    json_file.close()
            except Exception as e:
                self.writeJson()
        else:
            self.writeJson()

    def getHangarData(self, isPremium):
        if self.COEFFICIENTS['USE_DATA'] != isPremium:
            self.COEFFICIENTS['USE_DATA'] = isPremium
            self.writeJson()
        self.PREMIUM_ACC = isPremium

        # outcomeFull = 0
        outcome = 0
        for installedItem in g_currentVehicle.item.battleBoosters.installed.getItems():
            price = installedItem.buyPrices.getSum().price.credits
            # outcomeFull += price if not installedItem.inventoryCount else installedItem.getSellPrice().price.credits
            outcome += price if not installedItem.inventoryCount else 0
        self.hangarOutcome = outcome

        self.hangarItems = {}
        for installedItem in g_currentVehicle.item.consumables.installed.getItems():
            price = installedItem.buyPrices.getSum().price.credits
            self.hangarItems[installedItem.intCD] = [price if not installedItem.inventoryCount else 0, price if not installedItem.inventoryCount else installedItem.getSellPrice().price.credits]
        self.hangarAmmo = {}
        for ammo in g_currentVehicle.item.gun.defaultAmmo:
            self.hangarAmmo[ammo.intCD] = [ammo.buyPrices.getSum().price.credits if not ammo.inventoryCount else ammo.getSellPrice().price.credits, 0, 0]

        if DEBUG or DEBUG_COEFF:
            if g_currentVehicle.item:
                if self.item == g_currentVehicle.item.descriptor.type.compactDescr:
                    return
                vehicleCompDesc, balanceCoeff = self.deCode(g_currentVehicle.item.descriptor.type.compactDescr)
                notSavedCoeff = not balanceCoeff
                if notSavedCoeff:
                    ids = 1 if 'premium' in g_currentVehicle.item.tags else 0
                    balanceCoeff = self.AVERAGES[g_currentVehicle.item.level - 1][ids]
                text = '<b>  {0} calcCredits {1} {0}\n '.format(icons.nutStat() * 3, 'to <font color=\"#6595EE\">oldskool.vip</font>' if oldskoolCore else 'by <font color=\"#6595EE\">www.b4it.org</font>')
                text += icons.makeImageTag(Vehicle.getTypeSmallIconPath(g_currentVehicle.item.type, g_currentVehicle.item.isPremium), width=30, height=30, vSpace=-7 if g_currentVehicle.item.isPremium else -5) + g_currentVehicle.item.shortUserName
                text += ' : %s %s%s%% %s</b>' % (icons.creditsBig(), 'coeff: ~' if notSavedCoeff else 'coeff: ', round(balanceCoeff * 100, 2), '!!!' if notSavedCoeff else '')
                self.hangarHeader = text
                self.hangarMessage()
                self.item = g_currentVehicle.item.descriptor.type.compactDescr

    def timer(self):
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        if vehicle:
            self.startBattle()
            return
        BigWorld.callback(0.1, self.timer)

    def code(self, compactDescr, balanceCoeff):
        test = '%s' % compactDescr
        self.COEFFICIENTS[test] = balanceCoeff
        self.writeJson()
        return test, self.COEFFICIENTS[test]

    def deCode(self, compactDescr):
        test = '%s' % compactDescr
        if test in self.COEFFICIENTS:
            return test, round(self.COEFFICIENTS[test], 6)
        return test, 0.0

    def startBattle(self):
        self.altMode = False
        self.ctrlMode = False
        player = BigWorld.player()
        InputHandler.g_instance.onKeyDown += self.keyPressed
        InputHandler.g_instance.onKeyUp += self.keyPressed
        player.arena.onVehicleKilled += self.onVehicleKilled
        # if player.guiSessionProvider.shared.vehicleState is not None:
        #    player.guiSessionProvider.shared.vehicleState.onVehicleStateUpdated += self.deviceTouched
        ammoCtrl = player.guiSessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded += self.onShellsAdded
            ammoCtrl.onShellsUpdated += self.onShellsUpdated
        flash.startBattle()
        flash.visible(False)
        vehicle = player.getVehicleAttached()
        self.costRepairs.update({
            'gun'            : vehicle.typeDescriptor.gun.maxRepairCost,
            'engine'         : vehicle.typeDescriptor.engine.maxRepairCost,
            'turretRotator'  : vehicle.typeDescriptor.turret.turretRotatorHealth.maxRepairCost,
            'surveyingDevice': vehicle.typeDescriptor.turret.surveyingDeviceHealth.maxRepairCost,
            'ammoBay'        : vehicle.typeDescriptor.hull.ammoBayHealth.maxRepairCost,
            'radio'          : vehicle.typeDescriptor.radio.maxRepairCost,
            'fuelTank'       : vehicle.typeDescriptor.fuelTank.maxRepairCost,
            'chassis'        : vehicle.typeDescriptor.chassis.maxRepairCost
        })
        self.costRepairs.update({name: vehicle.typeDescriptor.chassis.maxRepairCost for name in CHASSIS_ALL_ITEMS})
        if not self.hangarItems:
            self.hangarItems = {763: (3000, 3000), 1019: (20000, 20000), 1275: (3000, 3000), 1531: (20000, 20000), 1787: (5000, 5000), 4859: (20000, 20000), 4091: (20000, 20000), 2299: (20000, 20000), 2555: (20000, 20000), 3067: (20000, 20000), 251: (3000, 3000), 3323: (3000, 3000), 4347: (5000, 5000), 3579: (20000, 20000), 15867: (20000, 20000), 25851: (20000, 20000), 16123: (20000, 20000), 2043: (5000, 5000), 16379: (20000, 20000), 16635: (20000, 20000), 4603: (20000, 20000), 507: (20000, 20000)}
        self.usedItems = {}
        # vehicleName = player.guiSessionProvider.getCtx().getPlayerFullNameParts(vID=vehicle.id).vehicleName
        self.item = None
        self.name = vehicle.typeDescriptor.name
        self.vehicleName = player.guiSessionProvider.getCtx().getPlayerFullNameParts(vID=vehicle.id).vehicleName
        self.level = vehicle.typeDescriptor.level
        self.textWin = ''
        self.textDEFEAT = ''
        player = BigWorld.player()
        arenaDP = player.guiSessionProvider.getArenaDP()
        self.listAlly = vos_collections.AllyItemsCollection().ids(arenaDP)
        self.listAlly.remove(player.playerVehicleID)
        self.PREMIUM_ACC = self.COEFFICIENTS['USE_DATA']
        self.readJson()
        self.SPOT = 0
        self.ASSIST = 0
        self.DAMAGE_SELF_SPOT = 0  # 100% sure we're spotting
        self.DAMAGE_OTHER_SPOT = 0  # 100% sure someone else is spotting
        self.DAMAGE_UNKNOWN_SPOT = 0  # uncertanty who is spotting
        self.DAMAGE_STUN = 0
        self.DAMAGE_ASSIST = 0
        self.WinResult = 0
        self.WinResultMin = 0
        self.DefeatResult = 0
        self.DefeatResultMin = 0
        self.premium = 1.5 if self.PREMIUM_ACC else 1.0  # точно!
        self.compactDescr, self.balanceCoeff = self.deCode(vehicle.typeDescriptor.type.compactDescr)
        if not self.balanceCoeff:
            ids = 1 if 'premium' in vehicle.typeDescriptor.type.tags else 0
            self.balanceCoeff = self.AVERAGES[self.level - 1][ids]
        self.killed = False
        self.repairCost = 0
        self.calc()

    def canSpotTarget(self, targetVehicle):
        distSq = (targetVehicle.position - BigWorld.player().getOwnVehiclePosition()).lengthSquared
        # assume we can spot target 100% sure at 100m or at 75% of our vision radius
        if distSq < 10000:
            return True

        circularVisionRadius = BigWorld.player().guiSessionProvider.shared.feedback.getVehicleAttrs()['circularVisionRadius']
        if distSq < circularVisionRadius * circularVisionRadius * 0.75 * 0.75:
            return True

        return False

    def canNeverSpotTarget(self, targetVehicle):
        # we can's spot target outside of our vision radius
        distSq = (targetVehicle.position - BigWorld.player().getOwnVehiclePosition()).lengthSquared
        circularVisionRadius = BigWorld.player().guiSessionProvider.shared.feedback.getVehicleAttrs()['circularVisionRadius']
        if distSq > circularVisionRadius * circularVisionRadius:
            return True
        return False

    def onBattleEvents(self, events):
        player = BigWorld.player()
        guiSessionProvider = player.guiSessionProvider
        radio = 0
        track = 0
        stun = 0
        if guiSessionProvider.shared.vehicleState.getControllingVehicleID() == player.playerVehicleID:
            for data in events:
                feedbackEvent = feedback_events.PlayerFeedbackEvent.fromDict(data)
                eventType = feedbackEvent.getBattleEventType()
                targetID = feedbackEvent.getTargetID()
                if eventType == BATTLE_EVENT_TYPE.SPOTTED:
                    vehicle = BigWorld.entity(targetID)
                    self.SPOT += 1
                    if vehicle and 'SPG' in vehicle.typeDescriptor.type.tags:
                        self.SPOT += 1
                if eventType in DAMAGE_EVENTS:
                    extra = feedbackEvent.getExtra()
                    if extra:
                        if eventType == BATTLE_EVENT_TYPE.RADIO_ASSIST:
                            radio += extra.getDamage()
                        if eventType == BATTLE_EVENT_TYPE.TRACK_ASSIST:
                            track += extra.getDamage()
                        if eventType == BATTLE_EVENT_TYPE.STUN_ASSIST:
                            stun += extra.getDamage()
                        if eventType == BATTLE_EVENT_TYPE.DAMAGE:
                            arenaDP = guiSessionProvider.getArenaDP()
                            if arenaDP.isEnemyTeam(arenaDP.getVehicleInfo(targetID).team):
                                vehicle = BigWorld.entity(targetID)
                                if vehicle:
                                    if vehicle.stunInfo > 0.0:
                                        self.DAMAGE_STUN += extra.getDamage()
                                    elif self.canSpotTarget(vehicle):
                                        self.DAMAGE_SELF_SPOT += extra.getDamage()
                                    elif self.canNeverSpotTarget(vehicle):
                                        self.DAMAGE_OTHER_SPOT += extra.getDamage()
                                    else:
                                        self.DAMAGE_UNKNOWN_SPOT += extra.getDamage()
        data = [radio, track, stun]
        self.ASSIST += max(data)
        self.calc()

    def deviceTouched(self, state, value):
        if self.killed:
            return
        player = BigWorld.player()
        ctrl = player.guiSessionProvider.shared
        vehicle = player.getVehicleAttached()
        # self.repairCost = int(vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth + vehicle.health)
        # getMaxRepairCost = vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth
        self.repairCost = 0  # int(round(getMaxRepairCost - getMaxRepairCost * vehicle.health / round(vehicle.typeDescriptor.maxHealth)))
        if state == VEHICLE_VIEW_STATE.DEVICES:
            # print 'max:%s, maxHP:%s, hp:%s' % (vehicle.typeDescriptor.getMaxRepairCost(), vehicle.typeDescriptor.maxHealth, vehicle.health)
            # print 'repairCost1:%s' % self.repairCost
            self.repairCost = 0
            repairs = 0
            for equipment in ctrl.equipments.iterEquipmentsByTag('repairkit'):
                for itemName, deviceState in equipment[1].getEntitiesIterator():
                    if deviceState == 'destroyed':
                        if itemName in self.costRepairs:
                            # print 'module:%s, %s' % (itemName, deviceState)
                            repairs += self.costRepairs[itemName]
                    if deviceState == 'critical':
                        if itemName in self.costRepairs:
                            # print 'module:%s, %s' % (itemName, deviceState)
                            repairs += self.costRepairs[itemName] / 2
            self.repairCost += int(round(repairs))
            # print 'modules:%s' %(repairs)
            # print 'repairCost2:%s' % self.repairCost
            # print 'repairCost3:%s' % int(round(self.repairCost * self.balanceCoeff))
        self.calc()

    def onVehicleKilled(self, target_id, *args):
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        if vehicle == None:
            vehicleID = player.playerVehicleID
        else:
            vehicleID =  vehicle.id
        if target_id == vehicleID:
            self.killed = True
            self.calc()
            return
            # self.repairCost = int(vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth + vehicle.health)
            getMaxRepairCost = vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth
            self.repairCost = int(round(getMaxRepairCost - getMaxRepairCost * vehicle.health / round(vehicle.typeDescriptor.maxHealth)))
            ctrl = player.guiSessionProvider.shared
            repairs = 0
            for equipment in ctrl.equipments.iterEquipmentsByTag('repairkit'):
                for itemName, deviceState in equipment[1].getEntitiesIterator():
                    if deviceState == 'destroyed':
                        if itemName in self.costRepairs:
                            repairs += self.costRepairs[itemName]
                    if deviceState == 'critical':
                        if itemName in self.costRepairs:
                            repairs += self.costRepairs[itemName] / 2
            self.repairCost += int(repairs)
            self.calc()

    def battleOutcome(self):
        player = BigWorld.player()
        ctrl = player.guiSessionProvider.shared
        # priceFull = self.hangarOutcome[1]
        price = self.hangarOutcome  # + int(round(self.repairCost * self.balanceCoeff))
        if not self.killed:
            try:
                for item in ctrl.equipments.getOrderedEquipmentsLayout():
                    if item and item[0] in self.hangarItems:
                        prevQuantity = item[1].getPrevQuantity()
                        quantity = item[1].getQuantity()
                        if item[0] not in self.usedItems:
                            self.usedItems[item[0]] = [not prevQuantity and quantity < 65535, self.hangarItems[item[0]][1], self.hangarItems[item[0]][1]]
                        if prevQuantity > 0 and 1 < quantity < 65535:
                            self.usedItems[item[0]][0] = True
            except Exception as e:
                pass
        # print self.usedItems
        for equipment in self.usedItems:
            if self.usedItems[equipment][0]:
                price += self.usedItems[equipment][1]
        for ammo in self.hangarAmmo:
            if self.hangarAmmo[ammo][1]:
                price += self.hangarAmmo[ammo][0] * self.hangarAmmo[ammo][1]
        return int(round(price))

    def onShellsAdded(self, intCD, descriptor, quantity, *args):
        if intCD in self.hangarAmmo:
            self.hangarAmmo[intCD][2] = quantity
            self.calc()

    def onShellsUpdated(self, intCD, quantity, *args):
        if intCD in self.hangarAmmo:
            self.hangarAmmo[intCD][1] = self.hangarAmmo[intCD][2] - quantity
            self.calc()

    def calc(self, hangar=False):
        if not config.data['enabled']:
            return
        if not (DEBUG or DEBUG_COEFF):
            return
        assistCoeff = 5
        spotCoeff = 100
        damageStunCoeff = 7.7
        damageSpottedCoeff = 7.5
        damageSelfCoeff = 10
        defeatCredits = self.level * 700
        winCredits = self.level * 1300

        assistCredits = self.ASSIST * assistCoeff
        spotCredits = self.SPOT * spotCoeff
        stunCredits = self.DAMAGE_STUN * damageStunCoeff

        damageMinCredits = self.DAMAGE_SELF_SPOT * damageSelfCoeff + (self.DAMAGE_UNKNOWN_SPOT + self.DAMAGE_OTHER_SPOT) * damageSpottedCoeff
        damageMaxCredits = (self.DAMAGE_SELF_SPOT + self.DAMAGE_UNKNOWN_SPOT) * damageSelfCoeff + self.DAMAGE_OTHER_SPOT * damageSpottedCoeff

        outcomeCredits = self.battleOutcome()

        self.DefeatResult = int(int(self.balanceCoeff * int(defeatCredits + assistCredits + spotCredits + damageMaxCredits + stunCredits) - 0.5) * self.premium + 0.5)
        self.DefeatResultMin = int(int(self.balanceCoeff * int(defeatCredits + assistCredits + spotCredits + damageMinCredits + stunCredits) - 0.5) * self.premium + 0.5)

        self.WinResult = int(int(self.balanceCoeff * int(winCredits + assistCredits + spotCredits + damageMaxCredits + stunCredits) - 0.5) * self.premium + 0.5)
        self.WinResultMin = int(int(self.balanceCoeff * int(winCredits + assistCredits + spotCredits + damageMinCredits + stunCredits) - 0.5) * self.premium + 0.5)

        if not hangar and flash:
            textWinner = self.correctedText(self.WinResultMin, self.WinResult, outcomeCredits)
            textDefeat = self.correctedText(self.DefeatResult, self.DefeatResult, outcomeCredits)
            colorWin = '#80D639'
            colorDefeat = '#FF6347'
            self.textWin = '<font size=\"20\" color=\"%s\">~%s%s</font>' % (colorWin, self.iconCredits, textWinner)
            self.textDEFEAT = '<font size=\"20\" color=\"%s\">~%s%s</font>' % (colorDefeat, self.iconCredits, textDefeat)
            if self.compactDescr not in self.tempResults:
                vehicle = BigWorld.player().getVehicleAttached()
                self.tempResults[self.compactDescr] = {
                    'descr'      : vehicle.typeDescriptor.type.compactDescr,
                    'premium'    : self.premium,
                    'damage'     : self.DAMAGE_SELF_SPOT + self.DAMAGE_UNKNOWN_SPOT + self.DAMAGE_OTHER_SPOT + self.DAMAGE_STUN,
                    'assist'     : self.ASSIST,
                    'spot'       : self.SPOT,
                    'level'      : self.level,
                    'name'       : self.name.replace(':', '_'),
                    'repairCost' : int(round(vehicle.typeDescriptor.getMaxRepairCost() - vehicle.typeDescriptor.maxHealth)),
                    'clearRepair': False,
                }
            self.tempResults[self.compactDescr]['damage'] = self.DAMAGE_SELF_SPOT + self.DAMAGE_UNKNOWN_SPOT + self.DAMAGE_OTHER_SPOT + self.DAMAGE_STUN
            self.tempResults[self.compactDescr]['assist'] = self.ASSIST
            self.tempResults[self.compactDescr]['spot'] = self.SPOT
            if self.tempResults[self.compactDescr]['repairCost'] == self.repairCost:
                self.tempResults[self.compactDescr]['clearRepair'] = True
            else:
                self.tempResults[self.compactDescr]['clearRepair'] = False
            flash.visible(True)
            flash.setCreditsText(self.textWin if not self.altMode else self.textDEFEAT)

    def keyPressed(self, event):
        player = BigWorld.player()
        if not player.arena: return
        if player.arena.bonusType != ARENA_BONUS_TYPE.REGULAR: return
        isKeyDownTrigger = event.isKeyDown()
        if event.key in [Keys.KEY_LALT, Keys.KEY_RALT]:
            if isKeyDownTrigger:
                self.altMode = True
            if event.isKeyUp():
                self.altMode = False
            self.calc()
        if event.key in [Keys.KEY_LCONTROL, Keys.KEY_RCONTROL]:
            if isKeyDownTrigger:
                self.ctrlMode = True
            if event.isKeyUp():
                self.ctrlMode = False
            self.calc()

    def correctedText(self, min, max, outcome):
        out = '<font color=\"#FF0000\"> -%s</font>' % outcome if outcome else ''
        if min != max:
            if self.ctrlMode:
                return '%s[%s]%s' % (min, int(max * 1.05), out)  # add 5% to max credits range
            return '%s%s' % (min, out)
        return '%s%s' % (max, out)

    def getDebugText(self):
        debugText = 'Coeff: %s: %s\n' % ('MISS' if self.compactDescr not in self.COEFFICIENTS else 'FOUND', self.balanceCoeff)
        if self.compactDescr not in self.COEFFICIENTS:
            debugText += '\nCredit Calc needs to learn\non this vehicle\n'
            if not self.tempResults[self.compactDescr]['damage']:
                debugText += 'JUST SUICIDE FAST plz!\n'
                debugText += 'And wait until battle down\n'
            else:
                debugText += 'wrong battle! play again\n'
        return debugText

    def stopBattle(self):
        player = BigWorld.player()
        self.ctrlMode = False
        self.altMode = False
        player.arena.onVehicleKilled -= self.onVehicleKilled
        # if player.guiSessionProvider.shared.vehicleState is not None:
        #    player.guiSessionProvider.shared.vehicleState.onVehicleStateUpdated -= self.deviceTouched
        ammoCtrl = player.guiSessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded -= self.onShellsAdded
            ammoCtrl.onShellsUpdated -= self.onShellsUpdated
        InputHandler.g_instance.onKeyDown -= self.keyPressed
        InputHandler.g_instance.onKeyUp -= self.keyPressed
        flash.stopBattle()
        if DEBUG:
            if self.compactDescr not in self.tempResults:
                return
            self.compactDescr, self.balanceCoeff = self.deCode(self.tempResults[self.compactDescr]['descr'])
            print 'tempResults', self.tempResults[self.compactDescr]
            outcomeCredits = self.battleOutcome()
            textWinner = '~%s' % self.correctedText(self.WinResultMin, self.WinResult, outcomeCredits)
            textDefeat = '~%s' % self.correctedText(self.DefeatResultMin, self.DefeatResult, outcomeCredits)
            textWinnerPremium = ''
            textDefeatPremium = ''
            if BattleReplay.g_replayCtrl.isPlaying:
                textWinnerPremium = ', With Premium account: ~%s Credits' % self.correctedText(int(1.5 * self.WinResultMin), int(1.5 * self.WinResult), outcomeCredits)
                textDefeatPremium = ', With Premium account: ~%s Credits' % self.correctedText(int(1.5 * self.DefeatResultMin), int(1.5 * self.DefeatResult), outcomeCredits)
            price = self.hangarOutcome
            for equipment in self.usedItems:
                if self.usedItems[equipment][0]:
                    price += self.usedItems[equipment][1]
            for ammo in self.hangarAmmo:
                if self.hangarAmmo[ammo][1]:
                    price += self.hangarAmmo[ammo][0] * self.hangarAmmo[ammo][1]
            consumables = int(round(price))

            print '#' * 40
            print 'Credits calculation mode'
            print 'VEHICLE: %s level:%s (id:%s)' % (self.tempResults[self.compactDescr]['name'], self.tempResults[self.compactDescr]['level'], self.compactDescr)
            print 'damage:%s, assist:%s, spot:%s, %s' % (self.tempResults[self.compactDescr]['damage'], self.tempResults[self.compactDescr]['assist'], self.tempResults[self.compactDescr]['spot'], 'clear repaired' if self.tempResults[self.compactDescr]['clearRepair'] else 'not cleared repair')
            print 'damage detail: selfSpot:%s, unkwnSpot:%s, othrSpot:%s, forStunned:%s, ' % (self.DAMAGE_SELF_SPOT, self.DAMAGE_UNKNOWN_SPOT, self.DAMAGE_OTHER_SPOT, self.DAMAGE_STUN)
            print 'coeff:%s, premCoeff:%s' % (self.balanceCoeff, self.tempResults[self.compactDescr]['premium'])
            print 'repairCost:%s[%s], consumables:%s' % (-int(round(self.repairCost * self.balanceCoeff)), -self.repairCost, -consumables)
            amm0 = ''
            for ammo in self.hangarAmmo:
                amm0 += '%s Credits (%s * %s) ' % (self.hangarAmmo[ammo][0] * self.hangarAmmo[ammo][1], self.hangarAmmo[ammo][0], self.hangarAmmo[ammo][1])
            if amm0:
                print 'Ammo: %s' % amm0
            print 'WINNER:%s Credits' % textWinner + textWinnerPremium
            print 'DEFEAT:%s Credits' % textDefeat + textDefeatPremium
            print '#' * 40
            print self.getDebugText()
        self.hangarOutcome = 0
        self.hangarItems = {}
        self.hangarAmmo = {}
        self.killed = False
        self.repairCost = 0
        self.costRepairs = {}
        self.usedItems = {}

    def hangarMessage(self):
        if not config.data['enabled']:
            return
        # if not (DEBUG or DEBUG_COEFF):
        #    return
        if ServicesLocator.hangarSpace is not None and ServicesLocator.hangarSpace.inited:
            self.recalculatedMessage = '<font size=\"20\" color=\"#FFE041\">%s</font>\n' % self.hangarHeader
            if self.textWin or self.textDEFEAT:
                textWinner = self.correctedText(self.WinResultMin, self.WinResult, 0)
                textDefeat = self.correctedText(self.DefeatResult, self.DefeatResult, 0)
                colorWin = '#80D639'
                colorDefeat = '#FF6347'
                self.textWin = '<font size=\"20\" color=\"%s\">~%s%s</font>' % (colorWin, self.iconCredits, textWinner)
                self.textDEFEAT = '<font size=\"20\" color=\"%s\">~%s%s</font>' % (colorDefeat, self.iconCredits, textDefeat)
                self.recalculatedMessage += '  ' + self.textWin + '<font size=\"20\" color=\"#FFE041\"> %s </font>' % self.vehicleName + self.textDEFEAT
            self.timerMessage()
            # SystemMessages.pushMessage(msg, SystemMessages.SM_TYPE.GameGreeting)

    def timerMessage(self):
        if not config.data['hangarShow']:
            return
        if g_currentVehicle.item:
            return
            flashInHangar.setPosition(config.data['hangar_x'], config.data['hangar_y'])  # x and y
            flashInHangar.setBackground(config.data['hangarBackground'], '0x000000', 0.4)  # change to false if dont want
            flashInHangar.setText(self.recalculatedMessage)
            # SystemMessages.pushMessage(self.recalculatedMessage, SystemMessages.SM_TYPE.GameGreeting)
            return
        BigWorld.callback(1.0, self.timerMessage)

    def tester(self, credits, premiumCoeff, winCoeff, level, assist, spot):
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
                if DEBUG:
                    print 'search pool: %s' % ranged, pool[ranged], boosterCoeff
                return result
        return result

    def sortValues(self, value, debug=False):
        try:
            index = self.coeffDefaults.index(filter(lambda x: value <= x + 0.0005, self.coeffDefaults)[0])
            if DEBUG or debug:
                print 'sortValues value: %s=>[%s]<%s' % (self.coeffDefaults[index], value, self.coeffDefaults[index + 1] if len(self.coeffDefaults) > index + 1 else self.coeffDefaults[index])
            return self.coeffDefaults[index]
        except Exception as e:
            if DEBUG or debug:
                print 'sortValues error not in range:%s' % value
            return value

    def sortResult(self, data1, data2, testCoeff):
        if data1 and data2:
            check1 = self.sortValues(round(sum(data1) / len(data1), 5), DEBUG_COEFF)
            check2 = self.sortValues(round(sum(data2) / len(data2), 5), DEBUG_COEFF)
            if check1 == testCoeff or check2 == testCoeff:
                return testCoeff
            if check1 == check2:
                return check1
            if check1 in data2:
                return check1
            if check2 in data1:
                return check2
        return 0.0

    def resultReCalc(self, typeCompDescr, isWin, credits, originalCredits, spot, assist, damage, repair):
        if DEBUG or DEBUG_COEFF:
            print '$$$$$ resultReCalc started'
        self.readJson()
        vehicleCompDesc, testCoeff = self.deCode(typeCompDescr)
        if vehicleCompDesc in self.tempResults:
            # if self.tempResults[vehicleCompDesc]['clearRepair'] and False:
            #    if DEBUG or DEBUG_COEFF:
            #        print '$$$$$$$$$$$$$$ CLEAR REPAIR MODE $$$$$$$$$$$$$$'
            #    calcRepair = int(round(self.tempResults[vehicleCompDesc]['repairCost'] * testCoeff))
            #    if DEBUG or DEBUG_COEFF:
            #        level = self.tempResults[vehicleCompDesc]['level']
            #        winCoeff = 1300 if isWin else 700
            #        print 'VEHICLE: %s level:%s (id:%s)' % (self.tempResults[vehicleCompDesc]['name'], self.tempResults[vehicleCompDesc]['level'], vehicleCompDesc)
            #        print 'level:%s, assist:%s, spot:%s, winCoeff:%s, balanceCoeff:%s' % (level, assist, spot, winCoeff, testCoeff)
            #        print 'repair:%s calcRepair:%s' % (repair, calcRepair)
            #    if repair != calcRepair:
            #        check = round(repair / round(self.tempResults[vehicleCompDesc]['repairCost']), 4)
            #        if DEBUG or DEBUG_COEFF:
            #            print 'repair / calcRepair = %s' % (repair / round(self.tempResults[vehicleCompDesc]['repairCost']))
            #            print 'possible coeffs:', check
            #            print '####2 resultReCalc SAVED coeff[%s]' % check
            #        self.compactDescr, self.balanceCoeff = self.code(typeCompDescr, check)
            #        self.readJson()
            #        if DEBUG or DEBUG_COEFF:
            #            print "####1 '%s': %s," % (self.compactDescr,self.balanceCoeff)
            #        if DEBUG or DEBUG_COEFF:
            #            self.recalculatedMessage = '<font size=\"20\" color=\"#FFE041\">Credits Calc to %s (id:%s)\nNew coeff:%s assigned, %s to %s</font>\n' % (self.tempResults[vehicleCompDesc]['name'], self.compactDescr, check, testCoeff, check)
            #            BigWorld.callback(1.0, self.timerMessage)
            #    return
            if not damage:
                if DEBUG or DEBUG_COEFF:
                    print '$$$$$$$$$$$$$$ NO DAMAGE MODE $$$$$$$$$$$$$$'
                checkCorrectedBattleData = credits / float(originalCredits)
                if DEBUG:
                    if checkCorrectedBattleData != 1.5:
                        print '$$$$ BATTLE DATA INCORRECT! PLAY AGAIN $$$$'
                # premiumCoeff = self.premium
                # if BattleReplay.g_replayCtrl.isPlaying:
                premiumCoeff = 1.0 if checkCorrectedBattleData < 1.01 else 1.5
                winCoeff = 1300 if isWin else 700
                level = self.tempResults[vehicleCompDesc]['level']
                result1 = self.tester(originalCredits, 1.0, isWin, level, assist, spot)
                result2 = self.tester(credits, 1.5, isWin, level, assist, spot)

                checkData = int(int(1.0 * int(level * winCoeff + assist * 5 + spot * 100) - 0.5) * premiumCoeff + 0.5)
                if premiumCoeff > 1.1:
                    coeff1 = round(checkData / originalCredits, 4)
                else:
                    coeff1 = round(originalCredits / checkData, 4)
                check = self.sortResult(result1, result2, coeff1)
                if DEBUG:
                    print 'VEHICLE: %s level:%s (id:%s)' % (self.tempResults[vehicleCompDesc]['name'], self.tempResults[vehicleCompDesc]['level'], vehicleCompDesc)
                    print 'level:%s, assist:%s, spot:%s, winCoeff:%s, balanceCoeff:%s' % (level, assist, spot, winCoeff, testCoeff)
                    print 'credits:%s originalCredits:%s, checkData:%s' % (credits, originalCredits, checkData)
                    print 'credits / originalCredits = %s' % checkCorrectedBattleData
                    print 'possible coeffs:', check
                checkOne = check
                # if check and testCoeff == check:
                #    return
                # if coeff1 == testCoeff:
                #    return
                if DEBUG:
                    print '#### resultReCalc coeff1[%s] and testCoeff[%s]' % (coeff1, testCoeff)
                    print 'result1 = ', result1
                    if result1:
                        print 'result1 coeff = %s' % round(sum(result1) / len(result1), 4)
                    print 'result2 = ', result2
                    if result2:
                        print 'result2 coeff = %s' % round(sum(result2) / len(result2), 4)
                if DEBUG_COEFF:
                    print '$$$$ 1 round coeff:%s' % round(sum(result1) / len(result1), 4), result1
                    print '$$$$ 2 round coeff:%s' % round(sum(result2) / len(result2), 4), result2
                    print '$$$$ VEHICLE: %s level:%s (id:%s)' % (self.tempResults[vehicleCompDesc]['name'], self.tempResults[vehicleCompDesc]['level'], vehicleCompDesc)
                    print '$$$$ originalCoeff: %s, possibleCoeff1: %s, possibleCoeff2: %s' % (testCoeff, checkOne, check)
                self.readJson()
                checkData *= premiumCoeff
                coeff2 = round(credits / checkData, 4)
                checkAgain = self.sortResult(result1, result2, coeff2)
                if checkAgain and check != checkAgain:
                    check = checkAgain
                if DEBUG:
                    print '#### resultReCalc coeff2[%s] and coeff1[%s] and check[%s]' % (coeff2, coeff1, check)
                if coeff1 == coeff2 and coeff1 != 1.0:
                    if DEBUG or DEBUG_COEFF:
                        print '####1 resultReCalc SAVED coeff[%s] ' % (coeff2)

                    self.compactDescr, self.balanceCoeff = self.code(typeCompDescr, coeff2)
                    self.readJson()
                    if DEBUG or DEBUG_COEFF:
                        print "####1 '%s': %s," % (self.compactDescr, self.balanceCoeff)
                else:
                    if check:
                        if DEBUG or DEBUG_COEFF:
                            print '####2 resultReCalc SAVED coeff[%s]' % check
                        self.compactDescr, self.balanceCoeff = self.code(typeCompDescr, check)
                        self.readJson()
                        if DEBUG or DEBUG_COEFF:
                            print "####2 '%s': %s," % (self.compactDescr, self.balanceCoeff)
                if DEBUG or DEBUG_COEFF:
                    self.recalculatedMessage = '<font size=\"20\" color=\"#FFE041\">Credit calculation for %s (id:%s)\nNew coeff %s assigned, %s -> %s</font>\n' % (self.tempResults[vehicleCompDesc]['name'], self.compactDescr, check, testCoeff, check)
                    BigWorld.callback(1.0, self.timerMessage)
            # del self.tempResults[vehicleCompDesc]

    def receiveBattleResult(self, isSuccess, battleResults):
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
        self.resultReCalc(playerVehicles['typeCompDescr'], battleResults['common']['winnerTeam'] == playerVehicles['team'], playerVehicles['factualCredits'], playerVehicles['originalCredits'], spot, assist, damage, repair)

    def coeffTable(self):
        self.COEFFICIENTS = {}
        self.COEFFICIENTS.update({
            # italy
            # lightTank
            '161'  : 1.4,  # lvl:1 italy_It04_Fiat_3000
            '417'  : 1.1,  # lvl:2 italy_It05_Carro_L6_40
            # mediumTank
            '673'  : 1.15,  # lvl:2 italy_It06_M14_41
            '929'  : 1.1,  # lvl:3 italy_It03_M15_42
            '1185' : 1.0,  # lvl:4 italy_It07_P26_40
            '1441' : 1.0,  # lvl:5 italy_It11_P43
            '1697' : 0.9,  # lvl:6 italy_It10_P43_bis
            '1953' : 0.8,  # lvl:7 italy_It09_P43_ter
            '2209' : 0.7,  # lvl:8 italy_It14_P44_Pantera
            '51361': 1.5,  # lvl:8 italy_It13_Progetto_M35_mod_46  !!!!PREMIUM
            '2465' : 0.72,  # lvl:9 italy_It12_Prototipo_Standard_B
            # '51617': None, #lvl:10 italy_It08_Progetto_M40_mod_65_bob  https://premomer.org/tank.php?id=51617
            # '50849': None, #lvl:10 italy_It20_Carro_Combattimento_45t  !!!!PREMIUM https://premomer.org/tank.php?id=50849
            '2721' : 0.73,  # lvl:10 italy_It08_Progetto_M40_mod_65
            # heavyTank
            # '3233': None, #lvl:7 italy_It16_Carro_d_assalto_P88  https://premomer.org/tank.php?id=3233
            '3745' : 0.708,  # lvl:8 italy_It17_Progetto_CC55_mod_54
            # '51105': None, #lvl:8 italy_It18_Progetto_C45_mod_71  !!!!PREMIUM https://premomer.org/tank.php?id=51105
            # '3489': None, #lvl:9 italy_It19_Progetto_C50_mod_66  https://premomer.org/tank.php?id=3489
            '2977' : 1.05,  # lvl:10 italy_It15_Rinoceronte
        })
        self.COEFFICIENTS.update({
            # sweden
            # lightTank
            '129'  : 1.4,  # lvl:1 sweden_S05_Strv_M21_29
            '51841': 1.2,  # lvl:2 sweden_S15_L_60  !!!!PREMIUM
            '385'  : 1.102,  # lvl:2 sweden_S03_Strv_M38
            '641'  : 1.05,  # lvl:3 sweden_S12_Strv_M40
            # mediumTank
            '897'  : 1.05,  # lvl:4 sweden_S04_Lago_I
            '1153' : 1.1,  # lvl:5 sweden_S02_Strv_M42
            '51585': 1.2,  # lvl:6 sweden_S01_Strv_74_A2  !!!!PREMIUM
            '1409' : 0.9,  # lvl:6 sweden_S07_Strv_74
            '1665' : 0.8,  # lvl:7 sweden_S13_Leo
            '4993' : 0.7,  # lvl:8 sweden_S29_UDES_14_5
            '52609': 1.6,  # lvl:8 sweden_S23_Strv_81_sabaton  !!!!PREMIUM
            '52353': 1.6,  # lvl:8 sweden_S23_Strv_81  !!!!PREMIUM
            '53121': 1.5,  # lvl:8 sweden_S26_Lansen_C  !!!!PREMIUM
            # '53377': None, #lvl:9 sweden_S30_UDES_03_Alt_3  !!!!PREMIUM https://premomer.org/tank.php?id=53377
            '5249' : 0.72,  # lvl:9 sweden_S27_UDES_16
            '5505' : 0.73,  # lvl:10 sweden_S28_UDES_15_16
            # heavyTank
            # '54657': None, #lvl:8 sweden_S32_Bofors_Tornvagn  !!!!PREMIUM https://premomer.org/tank.php?id=54657
            '1921' : 0.8,  # lvl:8 sweden_S18_EMIL_1951_E1
            '52865': 1.5,  # lvl:8 sweden_S25_EMIL_51  !!!!PREMIUM
            '2177' : 0.73,  # lvl:9 sweden_S17_EMIL_1952_E2
            # '54145': None, #lvl:9 sweden_S31_Strv_K  !!!!PREMIUM https://premomer.org/tank.php?id=54145
            '53889': 0.73,  # lvl:10 sweden_S16_Kranvagn_bob
            '2433' : 0.71,  # lvl:10 sweden_S16_Kranvagn
            # AT-SPG
            '2689' : 1.05,  # lvl:2 sweden_S09_L_120_TD
            '2945' : 0.95,  # lvl:3 sweden_S20_Ikv_72
            '3201' : 0.93,  # lvl:4 sweden_S19_Sav_M43
            '3457' : 0.98,  # lvl:5 sweden_S14_Ikv_103
            '3713' : 0.901,  # lvl:6 sweden_S08_Ikv_65_Alt_2
            '3969' : 0.8,  # lvl:7 sweden_S06_Ikv_90_Typ_B_Bofors
            # '53633': None, #lvl:8 sweden_S22_Strv_S1_FL  !!!!PREMIUM https://premomer.org/tank.php?id=53633
            '52097': 1.6,  # lvl:8 sweden_S22_Strv_S1  !!!!PREMIUM
            '4225' : 0.72,  # lvl:8 sweden_S21_UDES_03
            '4481' : 0.7,  # lvl:9 sweden_S10_Strv_103_0_Series
            # '54401': None, #lvl:9 sweden_S10_Strv_103_0_Series_FL  !!!!PREMIUM https://premomer.org/tank.php?id=54401
            '4737' : 0.63,  # lvl:10 sweden_S11_Strv_103B
        })
        self.COEFFICIENTS.update({
            # poland
            # lightTank
            '1169' : 1.419,  # lvl:1 poland_Pl14_4TP
            '1425' : 1.1,  # lvl:2 poland_Pl09_7TP
            '401'  : 1.3,  # lvl:2 poland_Pl01_TKS_20mm  !!!!PREMIUM
            '1681' : 1.1,  # lvl:3 poland_Pl06_10TP
            '1937' : 1.018,  # lvl:4 poland_Pl07_14TP
            # mediumTank
            '2193' : 1.0044,  # lvl:5 poland_Pl12_25TP_KSUST_II
            # '3729': None, #lvl:5 poland_Pl17_DS_PZlnz  https://premomer.org/tank.php?id=3729
            '2449' : 0.9,  # lvl:6 poland_Pl10_40TP_Habicha
            '145'  : 1.25,  # lvl:6 poland_Pl03_PzV_Poland  !!!!PREMIUM
            # '3985': None, #lvl:6 poland_Pl18_BUGI  https://premomer.org/tank.php?id=3985
            '51345': 1.25,  # lvl:6 poland_Pl16_T34_85_Rudy  !!!!PREMIUM
            # '4241': None, #lvl:7 poland_Pl20_CS_44  https://premomer.org/tank.php?id=4241
            # '51089': None, #lvl:8 poland_Pl19_CS_52_LIS  !!!!PREMIUM https://premomer.org/tank.php?id=51089
            # '4497': None, #lvl:8 poland_Pl23_CS_53  https://premomer.org/tank.php?id=4497
            # '8081': None, #lvl:9 poland_Pl22_CS_59  https://premomer.org/tank.php?id=8081
            # '5265': None, #lvl:10 poland_Pl21_CS_63  https://premomer.org/tank.php?id=5265
            # heavyTank
            '2705' : 0.858,  # lvl:7 poland_Pl11_45TP_Habicha
            '913'  : 1.5,  # lvl:8 poland_Pl08_50TP_prototyp  !!!!PREMIUM
            '2961' : 0.791,  # lvl:8 poland_Pl13_53TP_Markowskiego
            '3217' : 0.73,  # lvl:9 poland_Pl05_50TP_Tyszkiewicza
            '3473' : 0.71,  # lvl:10 poland_Pl15_60TP_Lewandowskiego
        })
        self.COEFFICIENTS.update({
            # japan
            # lightTank
            # '41057': None, #lvl:1 japan_J01_NC27_bot  https://premomer.org/tank.php?id=41057
            '609'  : 1.3,  # lvl:1 japan_J01_NC27
            '3169' : 1.2996,  # lvl:2 japan_J02_Te_Ke  !!!!PREMIUM
            '865'  : 1.1,  # lvl:2 japan_J03_Ha_Go
            # '41313': None, #lvl:2 japan_J04_Ke_Ni_bootcamp  https://premomer.org/tank.php?id=41313
            '2401' : 1.1,  # lvl:3 japan_J04_Ke_Ni
            '2145' : 1.1,  # lvl:3 japan_J07_Chi_Ha
            # '51809': None, #lvl:3 japan_J05_Ke_Ni_B  !!!!PREMIUM https://premomer.org/tank.php?id=51809
            '2913' : 1.2,  # lvl:4 japan_J06_Ke_Ho
            # mediumTank
            '353'  : 1.2,  # lvl:2 japan_J15_Chi_Ni
            '5985' : 1.1,  # lvl:2 japan_J26_Type_89
            '1633' : 1.1,  # lvl:4 japan_J09_Chi_He
            '1377' : 1.0,  # lvl:5 japan_J08_Chi_Nu
            '51553': 1.5,  # lvl:5 japan_J12_Chi_Nu_Kai  !!!!PREMIUM
            '1889' : 0.85,  # lvl:6 japan_J10_Chi_To
            # '39009': None, #lvl:7 japan_J11_Chi_Ri_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39009
            '1121' : 0.77,  # lvl:7 japan_J11_Chi_Ri
            # '38753': None, #lvl:8 japan_J13_STA_1_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38753
            '52065': 1.5,  # lvl:8 japan_J18_STA_2_3  !!!!PREMIUM
            '52833': 1.5,  # lvl:8 japan_J30_Edelweiss  !!!!PREMIUM
            '2657' : 0.69,  # lvl:8 japan_J13_STA_1
            '3425' : 0.75,  # lvl:9 japan_J14_Type_61
            # '39265': None, #lvl:10 japan_J16_ST_B1_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39265
            '3681' : 0.73,  # lvl:10 japan_J16_ST_B1
            # heavyTank
            # '41569': None, #lvl:2 japan_J22_Type_95_bootcamp  https://premomer.org/tank.php?id=41569
            '4705' : 1.05,  # lvl:3 japan_J21_Type_91
            '4449' : 1.05,  # lvl:4 japan_J22_Type_95
            '5729' : 1.05,  # lvl:5 japan_J23_Mi_To
            '52321': 1.2,  # lvl:6 japan_J19_Tiger_I_Jpn  !!!!PREMIUM
            '5473' : 0.9,  # lvl:6 japan_J24_Mi_To_130_tons
            '5217' : 0.83,  # lvl:7 japan_J28_O_I_100
            '4961' : 0.8,  # lvl:8 japan_J27_O_I_120
            '52577': 1.5,  # lvl:8 japan_J29_Nameless  !!!!PREMIUM
            '4193' : 0.71,  # lvl:9 japan_J25_Type_4
            '3937' : 0.73,  # lvl:10 japan_J20_Type_2605
        })
        self.COEFFICIENTS.update({
            # china
            # lightTank
            '1329' : 1.419,  # lvl:1 china_Ch06_Renault_NC31
            # '41009': None, #lvl:1 china_Ch06_Renault_NC31_bot  https://premomer.org/tank.php?id=41009
            '2353' : 1.128,  # lvl:2 china_Ch07_Vickers_MkE_Type_BT26
            # '41265': None, #lvl:2 china_Ch08_Type97_Chi_Ha_bootcamp  https://premomer.org/tank.php?id=41265
            '4401' : 1.0074,  # lvl:3 china_Ch08_Type97_Chi_Ha
            '3121' : 1.0336,  # lvl:4 china_Ch09_M5
            '4913' : 0.925,  # lvl:6 china_Ch15_59_16
            '64817': 1.35,  # lvl:6 china_Ch24_Type64  !!!!PREMIUM
            '3377' : 0.78,  # lvl:7 china_Ch16_WZ_131
            '305'  : 1.4,  # lvl:7 china_Ch02_Type62  !!!!PREMIUM
            '3889' : 0.6745,  # lvl:8 china_Ch17_WZ131_1_WZ132
            # '38705': None, #lvl:8 china_Ch17_WZ131_1_WZ132_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38705
            '62001': 1.5,  # lvl:8 china_Ch42_WalkerBulldog_M41D  !!!!PREMIUM
            '5681' : 0.67,  # lvl:9 china_Ch28_WZ_132A
            '5937' : 0.66,  # lvl:10 china_Ch29_Type_62C_prot
            # mediumTank
            # '64305': None, #lvl:1 china_Ch04_T34_1_training  https://premomer.org/tank.php?id=64305
            # '2609': None, #lvl:2 china_Ch20_Type58_bootcamp  https://premomer.org/tank.php?id=2609
            '4657' : 1.11,  # lvl:5 china_Ch21_T34
            '5169' : 0.909,  # lvl:6 china_Ch20_Type58
            '1073' : 0.78,  # lvl:7 china_Ch04_T34_1
            '64049': 1.575,  # lvl:8 china_Ch14_T34_3  !!!!PREMIUM
            '49'   : 1.575,  # lvl:8 china_Ch01_Type59  !!!!PREMIUM
            '561'  : 1.575,  # lvl:8 china_Ch01_Type59_Gold  !!!!PREMIUM
            '63793': 1.5,  # lvl:8 china_Ch26_59_Patton  !!!!PREMIUM
            '1585' : 0.708,  # lvl:8 china_Ch05_T34_2
            # '65329': None, #lvl:8 china_Ch43_WZ_122_2  !!!!PREMIUM https://premomer.org/tank.php?id=65329
            '1841' : 0.71,  # lvl:9 china_Ch18_WZ-120
            # '39217': None, #lvl:10 china_Ch19_121_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39217
            '63537': 0.73,  # lvl:10 china_Ch25_121_mod_1971B  !!!!PREMIUM
            '4145' : 0.73,  # lvl:10 china_Ch19_121
            # heavyTank
            '3633' : 0.874,  # lvl:7 china_Ch10_IS2
            # '60721': None, #lvl:8 china_Ch46_113_140  !!!!PREMIUM https://premomer.org/tank.php?id=60721
            # '61745': None, #lvl:8 china_Ch23_112_FL  !!!!PREMIUM https://premomer.org/tank.php?id=61745
            '65073': 1.575,  # lvl:8 china_Ch03_WZ_111_A  !!!!PREMIUM
            '2865' : 0.782,  # lvl:8 china_Ch11_110
            '817'  : 1.575,  # lvl:8 china_Ch03_WZ-111  !!!!PREMIUM
            # '38961': None, #lvl:8 china_Ch11_110_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38961
            '64561': 1.55,  # lvl:8 china_Ch23_112  !!!!PREMIUM
            '2097' : 0.7,  # lvl:9 china_Ch12_111_1_2_3
            # '60465': None, #lvl:9 china_Ch45_WZ_114  !!!!PREMIUM https://premomer.org/tank.php?id=60465
            # '56369': None, #lvl:9 china_Ch12_111_1_2_3_FL  !!!!PREMIUM https://premomer.org/tank.php?id=56369
            # '62769': None, #lvl:10 china_Ch22_113P  !!!!PREMIUM https://premomer.org/tank.php?id=62769
            '5425' : 0.774,  # lvl:10 china_Ch22_113
            # '62513': None, #lvl:10 china_Ch22_113_Beijing_Opera  !!!!PREMIUM https://premomer.org/tank.php?id=62513
            # '61233': None, #lvl:10 china_Ch41_WZ_111_5A_bob  https://premomer.org/tank.php?id=61233
            '6193' : 0.77,  # lvl:10 china_Ch41_WZ_111_5A
            # '62257': None, #lvl:10 china_Ch41_WZ_111_QL  !!!!PREMIUM https://premomer.org/tank.php?id=62257
            # AT-SPG
            '6449' : 1.05,  # lvl:2 china_Ch30_T-26G_FT
            '6705' : 0.95,  # lvl:3 china_Ch31_M3G_FT
            '6961' : 0.9,  # lvl:4 china_Ch32_SU-76G_FT
            '7217' : 0.95,  # lvl:5 china_Ch33_60G_FT
            '7473' : 0.9,  # lvl:6 china_Ch34_WZ131G_FT
            '7729' : 0.8,  # lvl:7 china_Ch35_T-34-2G_FT
            '7985' : 0.72,  # lvl:8 china_Ch36_WZ111_1G_FT
            # '61489': None, #lvl:8 china_Ch39_WZ120_1G_FT_FL  !!!!PREMIUM https://premomer.org/tank.php?id=61489
            '63281': 1.5,  # lvl:8 china_Ch39_WZ120_1G_FT  !!!!PREMIUM
            # '63025': None, #lvl:9 china_Ch40_WZ120G_FT  !!!!PREMIUM https://premomer.org/tank.php?id=63025
            '8241' : 0.7,  # lvl:9 china_Ch37_WZ111G_FT
            '8497' : 0.62,  # lvl:10 china_Ch38_WZ113G_FT
            # '60977': None, #lvl:10 china_Ch44_114_SP2  !!!!PREMIUM https://premomer.org/tank.php?id=60977
        })
        self.COEFFICIENTS.update({
            # czech
            # lightTank
            '113'  : 1.4,  # lvl:1 czech_Cz06_Kolohousenka
            '369'  : 1.1,  # lvl:2 czech_Cz03_LT_vz35
            '625'  : 1.05,  # lvl:3 czech_Cz10_LT_vz38
            # mediumTank
            '881'  : 1.0,  # lvl:4 czech_Cz11_V_8_H
            '1137' : 1.0,  # lvl:5 czech_Cz09_T_24
            '51569': 1.3,  # lvl:6 czech_Cz01_Skoda_T40  !!!!PREMIUM
            '1393' : 0.9,  # lvl:6 czech_Cz08_T_25
            '1649' : 0.77,  # lvl:7 czech_Cz05_T34_100
            '1905' : 0.72,  # lvl:8 czech_Cz07_TVP_46
            '51825': 1.5,  # lvl:8 czech_Cz13_T_27  !!!!PREMIUM
            '2161' : 0.71,  # lvl:9 czech_Cz02_TVP_T50
            '2417' : 0.73,  # lvl:10 czech_Cz04_T50_51
            # heavyTank
            # '3697': None, #lvl:7 czech_Cz19_Vz_44_1  https://premomer.org/tank.php?id=3697
            # '51313': None, #lvl:7 czech_Cz15_Skoda_T-45_Prem  !!!!PREMIUM https://premomer.org/tank.php?id=51313
            # '3441': None, #lvl:8 czech_Cz18_TNH_105_1000  https://premomer.org/tank.php?id=3441
            # '51057': None, #lvl:8 czech_Cz14_Skoda_T-56  !!!!PREMIUM https://premomer.org/tank.php?id=51057
            # '3185': None, #lvl:9 czech_Cz16_TNH_T_vz51  https://premomer.org/tank.php?id=3185
            # '2929': None, #lvl:10 czech_Cz17_Vz_55  https://premomer.org/tank.php?id=2929
        })
        self.COEFFICIENTS.update({
            # uk
            # lightTank
            '5201' : 1.199,  # lvl:1 uk_GB03_Cruiser_Mk_I
            '593'  : 1.1,  # lvl:2 uk_GB14_M2
            '54865': 1.2996,  # lvl:2 uk_GB76_Mk_VIC  !!!!PREMIUM
            '6993' : 1.089,  # lvl:2 uk_GB69_Cruiser_Mk_II
            '4945' : 1.026,  # lvl:3 uk_GB04_Valentine
            '1361' : 1.0,  # lvl:3 uk_GB15_Stuart_I
            '7761' : 1.09,  # lvl:3 uk_GB58_Cruiser_Mk_III
            '7505' : 1.089,  # lvl:4 uk_GB59_Cruiser_Mk_IV
            '6481' : 1.077,  # lvl:5 uk_GB60_Covenanter
            '2129' : 1.057,  # lvl:6 uk_GB20_Crusader
            # '55377': None, #lvl:6 uk_GB108_A46  !!!!PREMIUM https://premomer.org/tank.php?id=55377
            '59729': 0.7799,  # lvl:7 uk_GB104_GSR_3301_Setter
            '59473': 0.68,  # lvl:8 uk_GB102_LHMTV
            '58449': 1.5,  # lvl:8 uk_GB101_FV1066_Senlac  !!!!PREMIUM
            '58705': 0.6701,  # lvl:9 uk_GB103_GSOR3301_AVR_FS
            '58961': 0.66,  # lvl:10 uk_GB100_Manticore
            # mediumTank
            '81'   : 1.637,  # lvl:1 uk_GB01_Medium_Mark_I
            # '41553': None, #lvl:1 uk_GB107_Cavalier_SH  https://premomer.org/tank.php?id=41553
            # '41041': None, #lvl:1 uk_GB01_Medium_Mark_I_bot  https://premomer.org/tank.php?id=41041
            '337'  : 1.253,  # lvl:2 uk_GB05_Vickers_Medium_Mk_II
            # '41297': None, #lvl:2 uk_GB05_Vickers_Medium_Mk_II_bot  https://premomer.org/tank.php?id=41297
            '2385' : 1.089,  # lvl:3 uk_GB06_Vickers_Medium_Mk_III
            '849'  : 1.026,  # lvl:4 uk_GB07_Matilda
            '52817': 1.26,  # lvl:4 uk_GB33_Sentinel_AC_I  !!!!PREMIUM
            '1617' : 1.0,  # lvl:4 uk_GB17_Grant_I
            # '51281': None, #lvl:4 uk_GB113_Matilda_LVT  !!!!PREMIUM https://premomer.org/tank.php?id=51281
            # '60241': None, #lvl:5 uk_GB37_Valliant  !!!!PREMIUM https://premomer.org/tank.php?id=60241
            '12881': 1.0,  # lvl:5 uk_GB50_Sherman_III
            # '16209': None, #lvl:5 uk_GB107_Cavalier  https://premomer.org/tank.php?id=16209
            '53585': 1.53,  # lvl:5 uk_GB68_Matilda_Black_Prince  !!!!PREMIUM
            '57169': 1.3,  # lvl:6 uk_GB95_Ekins_Firefly_M4A4  !!!!PREMIUM
            '56145': 1.22,  # lvl:6 uk_GB35_Sentinel_AC_IV  !!!!PREMIUM
            # '39249': None, #lvl:6 uk_GB21_Cromwell_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39249
            '1105' : 0.932,  # lvl:6 uk_GB21_Cromwell
            # '28241': None, #lvl:6 uk_GB19_Sherman_Firefly_MapsTraining_Dummy_MT_2  https://premomer.org/tank.php?id=28241
            '55889': 1.25,  # lvl:6 uk_GB85_Cromwell_Berlin  !!!!PREMIUM
            '3665' : 0.85,  # lvl:6 uk_GB19_Sherman_Firefly
            '5457' : 0.77,  # lvl:7 uk_GB22_Comet
            # '38737': None, #lvl:8 uk_GB23_Centurion_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38737
            '56913': 1.5,  # lvl:8 uk_GB94_Centurion_Mk5-1_RAAC  !!!!PREMIUM
            # '58193': None, #lvl:8 uk_GB70_N_FV4202_105_FL  !!!!PREMIUM https://premomer.org/tank.php?id=58193
            # '57425': None, #lvl:8 uk_GB97_Chimera  !!!!PREMIUM https://premomer.org/tank.php?id=57425
            '15441': 1.55,  # lvl:8 uk_GB87_Chieftain_T95_turret  !!!!PREMIUM
            '5969' : 0.825,  # lvl:8 uk_GB23_Centurion
            '55633': 1.6,  # lvl:8 uk_GB70_N_FV4202_105  !!!!PREMIUM
            # '60497': None, #lvl:9 uk_GB106_Cobra  !!!!PREMIUM https://premomer.org/tank.php?id=60497
            '5713' : 0.73,  # lvl:9 uk_GB24_Centurion_Mk3
            '7249' : 0.73,  # lvl:10 uk_GB86_Centurion_Action_X
            '14929': 0.73,  # lvl:10 uk_GB70_FV4202_105
            # heavyTank
            '54353': 1.4,  # lvl:5 uk_GB51_Excelsior  !!!!PREMIUM
            '2897' : 1.115,  # lvl:5 uk_GB08_Churchill_I
            # '40017': None, #lvl:5 uk_GB08_Churchill_I_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40017
            # '59217': None, #lvl:6 uk_GB105_Black_Prince_2019  !!!!PREMIUM https://premomer.org/tank.php?id=59217
            '53841': 1.38,  # lvl:6 uk_GB63_TOG_II  !!!!PREMIUM
            '4689' : 0.98,  # lvl:6 uk_GB09_Churchill_VII
            '3153' : 0.836,  # lvl:7 uk_GB10_Black_Prince
            '55121': 1.3,  # lvl:7 uk_GB52_A45  !!!!PREMIUM
            '56657': 1.5,  # lvl:8 uk_GB93_Caernarvon_AX  !!!!PREMIUM
            # '52049': None, #lvl:8 uk_GB111_Charlemagne  !!!!PREMIUM https://premomer.org/tank.php?id=52049
            # '51537': None, #lvl:8 uk_GB112_Caliban  !!!!PREMIUM https://premomer.org/tank.php?id=51537
            # '38993': None, #lvl:8 uk_GB11_Caernarvon_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38993
            '3921' : 0.825,  # lvl:8 uk_GB11_Caernarvon
            # '53329': None, #lvl:9 uk_GB12_Conqueror_FL  !!!!PREMIUM https://premomer.org/tank.php?id=53329
            '4433' : 0.752,  # lvl:9 uk_GB12_Conqueror
            '15697': 0.745,  # lvl:10 uk_GB91_Super_Conqueror
            # '56401': None, #lvl:10 uk_GB88_T95_Chieftain_turret  !!!!PREMIUM https://premomer.org/tank.php?id=56401
            '6225' : 0.745,  # lvl:10 uk_GB13_FV215b  !!!!PREMIUM
            '57937': 0.73,  # lvl:10 uk_GB98_T95_FV4201_Chieftain  !!!!PREMIUM
            # '40273': None, #lvl:10 uk_GB13_FV215b_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40273
            '15185': 0.73,  # lvl:10 uk_GB84_Chieftain_Mk6  !!!!PREMIUM
            # AT-SPG
            '8273' : 1.1,  # lvl:2 uk_GB39_Universal_CarrierQF2
            '8017' : 0.9,  # lvl:4 uk_GB42_Valentine_AT
            '9041' : 0.945,  # lvl:4 uk_GB57_Alecto
            '13393': 0.95,  # lvl:5 uk_GB44_Archer
            '8785' : 0.997,  # lvl:5 uk_GB73_AT2
            '9553' : 0.9,  # lvl:6 uk_GB74_AT8
            '57681': 1.43,  # lvl:6 uk_GB96_Excalibur  !!!!PREMIUM
            '14417': 0.9,  # lvl:6 uk_GB45_Achilles_IIC
            '9809' : 1.012,  # lvl:6 uk_GB40_Gun_Carrier_Churchill
            '54097': 1.38,  # lvl:7 uk_GB71_AT_15A  !!!!PREMIUM
            '10065': 0.795,  # lvl:7 uk_GB75_AT7
            '14161': 0.75,  # lvl:7 uk_GB41_Challenger
            # '39761': None, #lvl:8 uk_GB72_AT15_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39761
            '59985': 1.5,  # lvl:8 uk_GB99_Turtle_Mk1  !!!!PREMIUM
            '8529' : 0.724,  # lvl:8 uk_GB72_AT15
            '14673': 0.71,  # lvl:8 uk_GB80_Charioteer
            # '52305': None, #lvl:8 uk_GB109_GSOR_1008  !!!!PREMIUM https://premomer.org/tank.php?id=52305
            '13137': 0.65,  # lvl:9 uk_GB81_FV4004
            '52561': 0.715,  # lvl:9 uk_GB32_Tortoise
            '9297' : 0.583,  # lvl:10 uk_GB48_FV215b_183  !!!!PREMIUM
            '13905': 0.6,  # lvl:10 uk_GB83_FV4005
            '15953': 0.583,  # lvl:10 uk_GB92_FV217
            # SPG
            '10577': 1.15,  # lvl:2 uk_GB25_Loyd_Gun_Carriage
            '54609': 1.81,  # lvl:3 uk_GB78_Sexton_I  !!!!PREMIUM
            '3409' : 1.09,  # lvl:3 uk_GB27_Sexton
            '10833': 1.05,  # lvl:4 uk_GB26_Birch_Gun
            '11089': 1.1,  # lvl:5 uk_GB28_Bishop
            # '39505': None, #lvl:6 uk_GB77_FV304_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39505
            '11857': 1.0,  # lvl:6 uk_GB77_FV304
            '11345': 0.8,  # lvl:7 uk_GB29_Crusader_5inch
            '12113': 0.75,  # lvl:8 uk_GB79_FV206
            '11601': 0.75,  # lvl:9 uk_GB30_FV3805
            '12369': 0.77,  # lvl:10 uk_GB31_Conqueror_Gun
        })
        self.COEFFICIENTS.update({
            # france
            # lightTank
            # '41025': None, #lvl:1 france_F01_RenaultFT_bot  https://premomer.org/tank.php?id=41025
            '577'  : 1.63,  # lvl:1 france_F01_RenaultFT
            '43329': 1.2,  # lvl:2 france_F111_AM39_Gendron_Somua  !!!!PREMIUM
            '15169': 1.1,  # lvl:2 france_F50_FCM36_20t
            '1601' : 1.276,  # lvl:2 france_F02_D1
            '15937': 1.1,  # lvl:2 france_F49_RenaultR35
            '1345' : 1.219,  # lvl:2 france_F12_Hotchkiss_H35
            '43841': 1.09,  # lvl:2 france_F42_AMR_35  !!!!PREMIUM
            '5953' : 1.113,  # lvl:3 france_F13_AMX38
            '2881' : 1.046,  # lvl:4 france_F14_AMX40
            '14145': 1.0,  # lvl:5 france_F62_ELC_AMX
            # '40001': None, #lvl:5 france_F62_ELC_AMX_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40001
            '17985': 0.87,  # lvl:6 france_F109_AMD_Panhard_178B
            '6465' : 0.873,  # lvl:6 france_F15_AMX_12t
            '5185' : 0.824,  # lvl:7 france_F16_AMX_13_75
            '63297': 1.3998,  # lvl:7 france_F69_AMX13_57_100_GrandFinal  !!!!PREMIUM
            '18241': 0.7799,  # lvl:7 france_F107_Hotchkiss_EBR
            '63809': 1.4,  # lvl:7 france_F69_AMX13_57_100  !!!!PREMIUM
            '43585': 1.5,  # lvl:8 france_F106_Panhard_EBR_75_Mle1954  !!!!PREMIUM
            '17473': 0.68,  # lvl:8 france_F87_Batignolles-Chatillon_12t
            '18497': 0.68,  # lvl:8 france_F110_Lynx_6x6
            # '59969': None, #lvl:8 france_F97_ELC_EVEN_90_FL  !!!!PREMIUM https://premomer.org/tank.php?id=59969
            '61505': 1.5,  # lvl:8 france_F97_ELC_EVEN_90  !!!!PREMIUM
            '4929' : 0.67,  # lvl:9 france_F17_AMX_13_90
            # '38977': None, #lvl:9 france_F17_AMX_13_90_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38977
            '18753': 0.6701,  # lvl:9 france_F100_Panhard_EBR_90
            '17217': 0.66,  # lvl:10 france_F88_AMX_13_105
            '19009': 0.66,  # lvl:10 france_F108_Panhard_EBR_105
            # mediumTank
            # '13377': None, #lvl:1 france_F43_AMC_35_SH  https://premomer.org/tank.php?id=13377
            '13121': 1.0,  # lvl:3 france_F44_Somua_S35
            '321'  : 1.025,  # lvl:3 france_F03_D2
            '14913': 1.0,  # lvl:4 france_F70_SARL42
            '4417' : 1.05,  # lvl:5 france_F11_Renault_G1R
            # '60993': None, #lvl:6 france_F85_M4A1_FL10  !!!!PREMIUM https://premomer.org/tank.php?id=60993
            '60737': 1.25,  # lvl:6 france_F113_Bretagne_Panther  !!!!PREMIUM
            # '60225': None, #lvl:8 france_F116_Bat_Chatillon_Bourrasque  !!!!PREMIUM https://premomer.org/tank.php?id=60225
            '63553': 1.5,  # lvl:8 france_F68_AMX_Chasseur_de_char_46  !!!!PREMIUM
            # '32065': None, #lvl:8 france_F117_Alt_Proto_AMX_30  !!!!PREMIUM https://premomer.org/tank.php?id=32065
            '63041': 1.5,  # lvl:8 france_F73_M4A1_Revalorise  !!!!PREMIUM
            '62529': 1.6,  # lvl:8 france_F19_Lorraine40t  !!!!PREMIUM
            # '64577': None, #lvl:8 france_F73_M4A1_Revalorise_FL  !!!!PREMIUM https://premomer.org/tank.php?id=64577
            '5697' : 0.817,  # lvl:9 france_F75_Char_de_25t
            # '60481': None, #lvl:9 france_F114_Projet_4_1  !!!!PREMIUM https://premomer.org/tank.php?id=60481
            '15681': 0.75,  # lvl:9 france_F71_AMX_30_prototype
            '15425': 0.73,  # lvl:10 france_F72_AMX_30
            # '40257': None, #lvl:10 france_F18_Bat_Chatillon25t_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40257
            '3649' : 0.75,  # lvl:10 france_F18_Bat_Chatillon25t
            # heavyTank
            # '41281': None, #lvl:2 france_F04_B1_bootcamp  https://premomer.org/tank.php?id=41281
            '1089' : 1.08,  # lvl:4 france_F04_B1
            '6721' : 1.08,  # lvl:5 france_F05_BDR_G1B
            '2625' : 0.906,  # lvl:6 france_F06_ARL_44
            '6977' : 0.795,  # lvl:7 france_F07_AMX_M4_1945
            '62273': 1.5,  # lvl:8 france_F84_Somua_SM  !!!!PREMIUM
            # '65345': None, #lvl:8 france_F74_AMX_M4_1949_FL  !!!!PREMIUM https://premomer.org/tank.php?id=65345
            '16449': 0.8,  # lvl:8 france_F81_Char_de_65t
            # '39233': None, #lvl:8 france_F08_AMX_50_100_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39233
            '62017': 1.6,  # lvl:8 france_F74_AMX_M4_1949_Liberte  !!!!PREMIUM
            '64065': 1.445,  # lvl:8 france_F65_FCM_50t  !!!!PREMIUM
            '3137' : 0.793,  # lvl:8 france_F08_AMX_50_100
            '62785': 1.6,  # lvl:8 france_F74_AMX_M4_1949  !!!!PREMIUM
            # '64321': None, #lvl:9 france_F83_AMX_M4_Mle1949_Bis_FL  !!!!PREMIUM https://premomer.org/tank.php?id=64321
            # '43073': None, #lvl:9 france_F115_Lorraine_50t  !!!!PREMIUM https://premomer.org/tank.php?id=43073
            '3905' : 0.702,  # lvl:9 france_F09_AMX_50_120
            '16705': 0.72,  # lvl:9 france_F83_AMX_M4_Mle1949_Bis
            '6209' : 0.75,  # lvl:10 france_F10_AMX_50B
            '16961': 0.71,  # lvl:10 france_F82_AMX_M4_Mle1949_Ter
            # '64833': None, #lvl:10 france_F10_AMX_50B_fallout  https://premomer.org/tank.php?id=64833
            # AT-SPG
            '7745' : 0.99,  # lvl:2 france_F30_RenaultFT_AC
            '8257' : 0.918,  # lvl:3 france_F52_RenaultUE57
            '2369' : 1.3,  # lvl:3 france_F27_FCM_36Pak40  !!!!PREMIUM
            '9793' : 0.969,  # lvl:4 france_F32_Somua_Sau_40
            '61249': 1.45,  # lvl:5 france_F112_M10_RBFM  !!!!PREMIUM
            '10049': 0.907,  # lvl:5 france_F33_S_35CA
            # '39745': None, #lvl:5 france_F33_S_35CA_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39745
            '11585': 0.912,  # lvl:6 france_F34_ARL_V39
            '10817': 0.787,  # lvl:7 france_F35_AMX_AC_Mle1946
            '12097': 0.71,  # lvl:8 france_F36_AMX_AC_Mle1948
            '61761': 1.5,  # lvl:8 france_F89_Canon_dassaut_de_105  !!!!PREMIUM
            # '38721': None, #lvl:8 france_F36_AMX_AC_Mle1948_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38721
            '11073': 0.7,  # lvl:9 france_F37_AMX50_Foch
            '13889': 0.53,  # lvl:10 france_F64_AMX_50Fosh_155  !!!!PREMIUM
            '17729': 0.5299,  # lvl:10 france_F64_AMX_50Fosh_B
            # SPG
            '833'  : 1.15,  # lvl:2 france_F20_RenaultBS
            '3393' : 1.08,  # lvl:3 france_F21_Lorraine39_L_AM
            '14657': 1.086,  # lvl:4 france_F66_AMX_Ob_Am105
            '4161' : 1.104,  # lvl:5 france_F22_AMX_105AM
            # '39489': None, #lvl:5 france_F28_105_leFH18B2_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39489
            '2113' : 1.35,  # lvl:5 france_F28_105_leFH18B2  !!!!PREMIUM
            '4673' : 1.122,  # lvl:6 france_F23_AMX_13F3AM
            '28225': 1.5,  # lvl:6 france_F23_AMX_13F3AM_MapsTraining_Dummy_SPG_2
            '7233' : 0.9,  # lvl:7 france_F24_Lorraine155_50
            '7489' : 0.71,  # lvl:8 france_F25_Lorraine155_51
            '14401': 0.64,  # lvl:9 france_F67_Bat_Chatillon155_55
            '11841': 0.78,  # lvl:10 france_F38_Bat_Chatillon155_58
        })
        self.COEFFICIENTS.update({
            # usa
            # lightTank
            '40993': 1.5,  # lvl:1 usa_A01_T1_Cunningham_bot
            '545'  : 1.365,  # lvl:1 usa_A01_T1_Cunningham
            '51489': 1.27,  # lvl:2 usa_A19_T2_lt  !!!!PREMIUM
            '53537': 1.45,  # lvl:2 usa_A74_T1_E6  !!!!PREMIUM
            '41761': 1.4,  # lvl:2 usa_A22_M5_Stuart_bootcamp
            '55073': 1.3,  # lvl:2 usa_A93_T7_Combat_Car  !!!!PREMIUM
            '41505': 1.5,  # lvl:2 usa_A03_M3_Stuart_bootcamp
            '1825' : 1.102,  # lvl:2 usa_A02_M2_lt
            '289'  : 1.07,  # lvl:3 usa_A03_M3_Stuart
            '52001': 1.26,  # lvl:3 usa_A33_MTLS-1G14  !!!!PREMIUM
            '52769': 1.57,  # lvl:3 usa_A43_M22_Locust  !!!!PREMIUM
            '5153' : 1.08,  # lvl:4 usa_A22_M5_Stuart
            '9761' : 1.0,  # lvl:5 usa_A34_M24_Chaffee
            '5409' : 1.1,  # lvl:5 usa_A23_M7_med
            '16673': 0.85,  # lvl:6 usa_A94_T37
            # '50977': None, #lvl:6 usa_A134_M24E2_SuperChaffee  !!!!PREMIUM https://premomer.org/tank.php?id=50977
            # '28705': None, #lvl:6 usa_A71_T21_MapsTraining_Dummy_LT_2  https://premomer.org/tank.php?id=28705
            '15137': 0.88,  # lvl:6 usa_A71_T21
            # '57633': None, #lvl:7 usa_A112_T71E2  !!!!PREMIUM https://premomer.org/tank.php?id=57633
            # '38689': None, #lvl:7 usa_A103_T71E1_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38689
            '15649': 0.78,  # lvl:7 usa_A103_T71E1
            '19745': 0.78,  # lvl:7 usa_A112_T71E2R
            '17953': 0.68,  # lvl:8 usa_A97_M41_Bulldog
            '57889': 1.5,  # lvl:8 usa_A99_T92_LT  !!!!PREMIUM
            '18209': 0.67,  # lvl:9 usa_A100_T49
            '19489': 0.66,  # lvl:10 usa_A116_XM551
            # mediumTank
            # '54305': None, #lvl:1 usa_A06_M4A3E8_Sherman_training  https://premomer.org/tank.php?id=54305
            # '42785': None, #lvl:1 usa_A72_T25_2_SH  https://premomer.org/tank.php?id=42785
            '5665' : 1.127,  # lvl:2 usa_A24_T2_med
            # '42017': None, #lvl:2 usa_A25_M2_med_bootcamp  https://premomer.org/tank.php?id=42017
            '41249': 1.4,  # lvl:2 usa_A24_T2_med_bot
            # '42273': None, #lvl:2 usa_A36_Sherman_Jumbo_bootcamp  https://premomer.org/tank.php?id=42273
            '34593': 1.26,  # lvl:3 usa_A148_Convertible_Medium_Tank_T3  !!!!PREMIUM
            '4897' : 1.044,  # lvl:3 usa_A25_M2_med
            # '20257': None, #lvl:4 usa_A129_T6_medium  https://premomer.org/tank.php?id=20257
            # '28193': None, #lvl:4 usa_A129_T6_medium_MapsTraining_Dummy_MT_1  https://premomer.org/tank.php?id=28193
            '3105' : 1.109,  # lvl:4 usa_A04_M3_Grant
            '52257': 1.59,  # lvl:5 usa_A44_M4A2E4  !!!!PREMIUM
            '12577': 1.4,  # lvl:5 usa_A78_M4_Improved  !!!!PREMIUM
            '1057' : 0.968,  # lvl:5 usa_A05_M4_Sherman
            # '40481': None, #lvl:5 usa_A05_M4_Sherman_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40481
            '51745': 1.55,  # lvl:5 usa_A62_Ram-II  !!!!PREMIUM
            '59681': 1.22,  # lvl:6 usa_A118_M4_Thunderbolt  !!!!PREMIUM
            '1313' : 0.868,  # lvl:6 usa_A06_M4A3E8_Sherman
            # '39457': None, #lvl:6 usa_A36_Sherman_Jumbo_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39457
            '56097': 1.22,  # lvl:6 usa_A104_M4A3E8A  !!!!PREMIUM
            '10017': 0.854,  # lvl:6 usa_A36_Sherman_Jumbo
            '11809': 1.3,  # lvl:7 usa_A86_T23E3  !!!!PREMIUM
            '1569' : 0.776,  # lvl:7 usa_A07_T20
            '59937': 1.3,  # lvl:7 usa_A121_M26_Cologne  !!!!PREMIUM
            # '38945': None, #lvl:8 usa_A90_T69_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38945
            '2337' : 1.6,  # lvl:8 usa_A08_T23
            '57377': 1.5,  # lvl:8 usa_A111_T25_Pilot  !!!!PREMIUM
            '14625': 0.67,  # lvl:8 usa_A90_T69
            # '39969': None, #lvl:8 usa_A35_Pershing_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39969
            '57121': 1.575,  # lvl:8 usa_A63_M46_Patton_KR  !!!!PREMIUM
            '34081': 1.45,  # lvl:8 usa_A149_AMBT  !!!!PREMIUM
            '62241': 1.5,  # lvl:8 usa_A127_TL_1_LPC  !!!!PREMIUM
            '13345': 1.575,  # lvl:8 usa_A80_T26_E4_SuperPershing  !!!!PREMIUM
            # '50721': None, #lvl:8 usa_A136_T42  !!!!PREMIUM https://premomer.org/tank.php?id=50721
            # '35105': None, #lvl:8 usa_A140_ASTRON_REX_105mm  !!!!PREMIUM https://premomer.org/tank.php?id=35105
            '53793': 1.5,  # lvl:8 usa_A81_T95_E2  !!!!PREMIUM
            '5921' : 0.708,  # lvl:8 usa_A35_Pershing
            # '60961': None, #lvl:8 usa_A80_T26_E4_SuperPershing_FL  !!!!PREMIUM https://premomer.org/tank.php?id=60961
            # '58401': None, #lvl:9 usa_A63_M46_Patton_FL  !!!!PREMIUM https://premomer.org/tank.php?id=58401
            '8993' : 0.751,  # lvl:9 usa_A63_M46_Patton
            '15905': 0.73,  # lvl:10 usa_A92_M60  !!!!PREMIUM
            # '40737': None, #lvl:10 usa_A120_M48A5_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40737
            # '55841': None, #lvl:10 usa_A95_T95_E6  !!!!PREMIUM https://premomer.org/tank.php?id=55841
            # '56865': None, #lvl:10 usa_A106_M48A2_120  !!!!PREMIUM https://premomer.org/tank.php?id=56865
            '14113': 0.734,  # lvl:10 usa_A120_M48A5
            # heavyTank
            # '28449': None, #lvl:5 usa_A21_T14_MapsTraining_Player_HT_1  https://premomer.org/tank.php?id=28449
            '3361' : 1.094,  # lvl:5 usa_A09_T1_hvy
            '33'   : 1.62,  # lvl:5 usa_A21_T14  !!!!PREMIUM
            '801'  : 0.932,  # lvl:6 usa_A10_M6
            # '61473': None, #lvl:7 usa_A126_PzVI_Tiger_II_capt  !!!!PREMIUM https://premomer.org/tank.php?id=61473
            '3873' : 0.836,  # lvl:7 usa_A11_T29
            # '40225': None, #lvl:7 usa_A11_T29_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40225
            '52513': 1.67,  # lvl:8 usa_A45_M6A2E1  !!!!PREMIUM
            '58657': 1.5,  # lvl:8 usa_A115_Chrysler_K_GF  !!!!PREMIUM
            # '60705': None, #lvl:8 usa_A13_T34_hvy_FL  !!!!PREMIUM https://premomer.org/tank.php?id=60705
            # '43553': None, #lvl:8 usa_A141_M_IV_Y  !!!!PREMIUM https://premomer.org/tank.php?id=43553
            # '51233': None, #lvl:8 usa_A132_T77  !!!!PREMIUM https://premomer.org/tank.php?id=51233
            '4385' : 0.828,  # lvl:8 usa_A12_T32
            # '63265': None, #lvl:8 usa_A12_T32_FL  !!!!PREMIUM https://premomer.org/tank.php?id=63265
            # '59425': None, #lvl:8 usa_A13_T34_hvy_BF  !!!!PREMIUM https://premomer.org/tank.php?id=59425
            # '63009': None, #lvl:8 usa_A117_T26E5_FL  !!!!PREMIUM https://premomer.org/tank.php?id=63009
            '59169': 1.575,  # lvl:8 usa_A117_T26E5_Patriot  !!!!PREMIUM
            # '60193': None, #lvl:8 usa_A115_Chrysler_K  !!!!PREMIUM https://premomer.org/tank.php?id=60193
            '2849' : 1.575,  # lvl:8 usa_A13_T34_hvy  !!!!PREMIUM
            # '39201': None, #lvl:8 usa_A13_T34_hvy_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39201
            '58913': 1.575,  # lvl:8 usa_A117_T26E5  !!!!PREMIUM
            '61985': 1.5,  # lvl:8 usa_A124_T54E2  !!!!PREMIUM
            '61729': 0.7799,  # lvl:9 usa_A125_AEP_1  !!!!PREMIUM
            # '62753': None, #lvl:9 usa_A128_concept_1b  !!!!PREMIUM https://premomer.org/tank.php?id=62753
            '9505' : 0.735,  # lvl:9 usa_A66_M103
            '15393': 0.7,  # lvl:9 usa_A89_T54E1
            '10785': 0.735,  # lvl:10 usa_A69_T110E5
            '14881': 0.73,  # lvl:10 usa_A67_T57_58
            '64801': 1.59,  # lvl:10 usa_A69_T110E5_bob
            '35361': 0.968,  # lvl:10 usa_A69_T110E5_cl  !!!!PREMIUM
            # AT-SPG
            # '18977': None, #lvl:2 usa_A26_T18  https://premomer.org/tank.php?id=18977
            '6177' : 1.05,  # lvl:2 usa_A46_T3
            '6433' : 0.95,  # lvl:3 usa_A109_T56_GMC
            '7713' : 0.835,  # lvl:4 usa_A29_T40
            '10273': 0.899,  # lvl:4 usa_A57_M8A1
            # '39713': None, #lvl:5 usa_A58_T67_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39713
            '10529': 0.964,  # lvl:5 usa_A58_T67
            '6945' : 0.976,  # lvl:5 usa_A30_M10_Wolverine
            '11553': 0.798,  # lvl:6 usa_A41_M18_Hellcat
            '7201' : 0.861,  # lvl:6 usa_A31_M36_Slagger
            '61217': 1.2998,  # lvl:6 usa_A123_T78  !!!!PREMIUM
            '62497': 0.7979,  # lvl:7 usa_A130_Super_Hellcat  !!!!PREMIUM
            '56609': 1.4,  # lvl:7 usa_A102_T28_concept  !!!!PREMIUM
            '56353': 1.35,  # lvl:7 usa_A101_M56  !!!!PREMIUM
            '9249' : 0.817,  # lvl:7 usa_A64_T25_AT
            '11041': 0.732,  # lvl:7 usa_A72_T25_2
            '8225' : 0.724,  # lvl:8 usa_A39_T28
            '60449': 1.5,  # lvl:8 usa_A122_TS-5  !!!!PREMIUM
            '11297': 0.711,  # lvl:8 usa_A68_T28_Prototype
            '2593' : 0.721,  # lvl:9 usa_A14_T30
            '8737' : 0.69,  # lvl:9 usa_A40_T95
            # '58145': None, #lvl:9 usa_A14_T30_FL  !!!!PREMIUM https://premomer.org/tank.php?id=58145
            '13857': 0.632,  # lvl:10 usa_A85_T110E3
            '13089': 0.625,  # lvl:10 usa_A83_T110E4
            # SPG
            # '19233': None, #lvl:2 usa_A15_T57  https://premomer.org/tank.php?id=19233
            '2081' : 1.2,  # lvl:2 usa_A107_T1_HMC
            '3617' : 1.1,  # lvl:3 usa_A16_M7_Priest
            '18465': 1.1,  # lvl:3 usa_A108_T18_HMC
            '4641' : 1.08,  # lvl:4 usa_A17_M37
            '18721': 1.1,  # lvl:4 usa_A27_T82
            '4129' : 1.17,  # lvl:5 usa_A18_M41
            '16417': 1.02,  # lvl:6 usa_A87_M44
            '7969' : 0.83,  # lvl:7 usa_A32_M12
            '7457' : 0.7,  # lvl:8 usa_A37_M40M43
            '16161': 0.69,  # lvl:9 usa_A88_M53_55
            '8481' : 0.8,  # lvl:10 usa_A38_T92
        })
        self.COEFFICIENTS.update({
            # germany
            # lightTank
            # '40977': None, #lvl:1 germany_G12_Ltraktor_bot  https://premomer.org/tank.php?id=40977
            # '44305': None, #lvl:1 germany_G00_Bomber_SH  https://premomer.org/tank.php?id=44305
            '3089' : 1.311,  # lvl:1 germany_G12_Ltraktor
            # '41233': None, #lvl:2 germany_G06_PzII_bot  https://premomer.org/tank.php?id=41233
            '2065' : 1.0902,  # lvl:2 germany_G06_PzII
            # '43281': None, #lvl:2 germany_G160_Pz_Kpfw_35_R_mit_T_26_Turm  !!!!PREMIUM https://premomer.org/tank.php?id=43281
            '785'  : 1.093,  # lvl:2 germany_G07_Pz35t
            # '42513': None, #lvl:2 germany_G102_Pz_III_bootcamp  https://premomer.org/tank.php?id=42513
            '47633': 1.2,  # lvl:2 germany_G139_MKA  !!!!PREMIUM
            # '42001': None, #lvl:2 germany_G08_Pz38t_bootcamp  https://premomer.org/tank.php?id=42001
            '12817': 1.25,  # lvl:2 germany_G53_PzI
            # '42769': None, #lvl:2 germany_G117_Toldi_III_bootcamp  https://premomer.org/tank.php?id=42769
            '52497': 1.0,  # lvl:2 germany_G33_H39_captured  !!!!PREMIUM
            '60433': 1.2,  # lvl:2 germany_G108_PzKpfwII_AusfD  !!!!PREMIUM
            '4881' : 1.085,  # lvl:3 germany_G102_Pz_III
            # '43537': None, #lvl:3 germany_G161_Pz_Kpfw_M15_38_t  !!!!PREMIUM https://premomer.org/tank.php?id=43537
            '63505': 1.2997,  # lvl:3 germany_G117_Toldi_III  !!!!PREMIUM
            '12561': 1.0,  # lvl:3 germany_G63_PzI_ausf_C
            '3345' : 0.987,  # lvl:3 germany_G08_Pz38t
            '13073': 1.0,  # lvl:3 germany_G82_Pz_II_AusfG
            '51729': 1.2,  # lvl:3 germany_G36_PzII_J  !!!!PREMIUM
            '54801': 1.5,  # lvl:3 germany_G50_T-15  !!!!PREMIUM
            '8209' : 1.053,  # lvl:4 germany_G52_Pz38_NA
            '6161' : 1.05,  # lvl:4 germany_G25_PzII_Luchs
            '5393' : 1.02,  # lvl:5 germany_G26_VK1602
            '25617': 0.817, #lvl:6 germany_G158_VK2801_105_SPXXI  !!!!PREMIUM
            '10001': 0.825,  # lvl:6 germany_G66_VK2801
            '18961': 0.78,  # lvl:7 germany_G113_SP_I_C
            '14353': 1.4,  # lvl:7 germany_G85_Auf_Panther  !!!!PREMIUM
            '20241': 0.68,  # lvl:8 germany_G126_HWK_12
            # '47889': None, #lvl:8 germany_G85_Aufklarungspanzer_V  !!!!PREMIUM https://premomer.org/tank.php?id=47889
            '50961': 1.4,  # lvl:8 germany_G120_M41_90_GrandFinal  !!!!PREMIUM
            '47377': 1.5,  # lvl:8 germany_G140_HWK_30  !!!!PREMIUM
            '64017': 1.4,  # lvl:8 germany_G120_M41_90  !!!!PREMIUM
            '18449': 0.67,  # lvl:9 germany_G103_RU_251
            '19985': 0.66,  # lvl:10 germany_G125_Spz_57_Rh
            # mediumTank
            # '57873': None, #lvl:1 germany_G10_PzIII_AusfJ_training  https://premomer.org/tank.php?id=57873
            # '58385': None, #lvl:1 germany_G03_PzV_Panther_training  https://premomer.org/tank.php?id=58385
            # '43793': None, #lvl:1 germany_G24_VK3002DB_SH  https://premomer.org/tank.php?id=43793
            # '42257': None, #lvl:2 germany_G80_Pz_IV_AusfD_bootcamp  https://premomer.org/tank.php?id=42257
            # '41745': None, #lvl:2 germany_G03_PzV_Panther_bootcamp  https://premomer.org/tank.php?id=41745
            '51985': 1.26,  # lvl:3 germany_G34_S35_captured  !!!!PREMIUM
            '59665': 1.22,  # lvl:3 germany_G100_Gtraktor_Krupp  !!!!PREMIUM
            '17169': 1.0,  # lvl:3 germany_G83_Pz_IV_AusfA
            '13585': 1.1,  # lvl:4 germany_G86_VK2001DB
            '4369' : 1.129,  # lvl:4 germany_G10_PzIII_AusfJ
            '17425': 1.05,  # lvl:4 germany_G80_Pz_IV_AusfD
            # '17': None, #lvl:5 germany_G79_Pz_IV_AusfGH  https://premomer.org/tank.php?id=17
            '54545': 1.52,  # lvl:5 germany_G46_T-25  !!!!PREMIUM
            # '45585': None, #lvl:5 germany_G81_Pz_IV_AusfH_GuP  !!!!PREMIUM https://premomer.org/tank.php?id=45585
            '63249': 1.3999,  # lvl:5 germany_G116_Turan_III_prot  !!!!PREMIUM
            '6417' : 1.168,  # lvl:5 germany_G28_PzIII_IV
            '2577' : 1.1,  # lvl:5 germany_G13_VK3001H
            # '54033': None, #lvl:5 germany_G32_PzV_PzIV_ausf_Alfa  !!!!PREMIUM https://premomer.org/tank.php?id=54033
            '55057': 1.4,  # lvl:5 germany_G70_PzIV_Hydro  !!!!PREMIUM
            '18193': 1.1,  # lvl:5 germany_G81_Pz_IV_AusfH
            '51473': 1.48,  # lvl:5 germany_G32_PzV_PzIV  !!!!PREMIUM
            '61457': 1.4,  # lvl:5 germany_G107_PzKpfwIII_AusfK  !!!!PREMIUM
            # '50449': None, #lvl:6 germany_G32_PzV_PzIV_CN  !!!!PREMIUM https://premomer.org/tank.php?id=50449
            # '50705': None, #lvl:6 germany_G32_PzV_PzIV_ausf_Alfa_CN  !!!!PREMIUM https://premomer.org/tank.php?id=50705
            '57361': 1.26,  # lvl:6 germany_G77_PzIV_Schmalturm  !!!!PREMIUM
            '14097': 0.9,  # lvl:6 germany_G87_VK3002DB_V1
            '15889': 0.85,  # lvl:6 germany_G96_VK3002M
            '57617': 1.56,  # lvl:7 germany_G78_Panther_M10  !!!!PREMIUM
            '4113' : 0.759,  # lvl:7 germany_G24_VK3002DB
            # '40209': None, #lvl:7 germany_G03_PzV_Panther_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40209
            '1297' : 0.805,  # lvl:7 germany_G03_PzV_Panther
            # '45841': None, #lvl:8 germany_G154_Kpz_07_RH  !!!!PREMIUM https://premomer.org/tank.php?id=45841
            '8465' : 0.791,  # lvl:8 germany_G64_Panther_II
            '60177': 1.5,  # lvl:8 germany_G106_PzKpfwPanther_AusfF  !!!!PREMIUM
            # '38929': None, #lvl:8 germany_G64_Panther_II_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38929
            # '46609': None, #lvl:8 germany_G142_M48RPz  !!!!PREMIUM https://premomer.org/tank.php?id=46609
            '64273': 1.5,  # lvl:8 germany_G119_Pz58_Mutz  !!!!PREMIUM
            # '56849': None, #lvl:8 germany_G119_Panzer58_FL  !!!!PREMIUM https://premomer.org/tank.php?id=56849
            # '49937': None, #lvl:8 germany_G119_Panzer58_BF  !!!!PREMIUM https://premomer.org/tank.php?id=49937
            '13841': 0.67,  # lvl:8 germany_G88_Indien_Panzer
            '63761': 1.0,  # lvl:8 germany_G119_Panzer58  !!!!PREMIUM
            '10257': 0.779,  # lvl:9 germany_G54_E-50
            # '46353': None, #lvl:9 germany_G147_Kunze_Panzer  !!!!PREMIUM https://premomer.org/tank.php?id=46353
            # '56593': None, #lvl:9 germany_G54_E-50_FL  !!!!PREMIUM https://premomer.org/tank.php?id=56593
            '60945': 0.8,  # lvl:9 germany_G105_T-55_NVA_DDR  !!!!PREMIUM
            # '47121': None, #lvl:9 germany_G144_Kpz_50t  !!!!PREMIUM https://premomer.org/tank.php?id=47121
            '14865': 0.75,  # lvl:9 germany_G91_Pro_Ag_A
            '14609': 0.75,  # lvl:10 germany_G89_Leopard1
            '12305': 0.73,  # lvl:10 germany_G73_E50_Ausf_M
            # '43025': None, #lvl:10 germany_G89_Leopard1_bob  https://premomer.org/tank.php?id=43025
            # heavyTank
            # '58129': None, #lvl:1 germany_G16_PzVIB_Tiger_II_training  https://premomer.org/tank.php?id=58129
            '52241': 1.36,  # lvl:4 germany_G35_B-1bis_captured  !!!!PREMIUM
            '13329': 1.05,  # lvl:4 germany_G90_DW_II
            # '28177': None, #lvl:4 germany_G90_DW_II_MapsTraining_Dummy_HT_1  https://premomer.org/tank.php?id=28177
            '59409': 1.4,  # lvl:5 germany_G122_VK6501H  !!!!PREMIUM
            '49169': 1.2,  # lvl:6 germany_G136_Tiger_131  !!!!PREMIUM
            '2321' : 0.931,  # lvl:6 germany_G15_VK3601H
            '52753': 1.2,  # lvl:6 germany_G137_PzVI_Tiger_217  !!!!PREMIUM
            '7185' : 1.018,  # lvl:6 germany_G27_VK3001P
            # '61201': None, #lvl:7 germany_G04_PzVI_Tiger_IA  https://premomer.org/tank.php?id=61201
            '529'  : 0.901,  # lvl:7 germany_G04_PzVI_Tiger_I
            # '62225': None, #lvl:7 germany_G58_VK4502P7  !!!!PREMIUM https://premomer.org/tank.php?id=62225
            # '28689': None, #lvl:7 germany_G04_PzVI_Tiger_I_MapsTraining_Player_HT_2  https://premomer.org/tank.php?id=28689
            # '49681': None, #lvl:7 germany_G16_PzVIB_Tiger_II_F  !!!!PREMIUM https://premomer.org/tank.php?id=49681
            '62993': 1.5,  # lvl:7 germany_G118_VK4503  !!!!PREMIUM
            # '39441': None, #lvl:7 germany_G04_PzVI_Tiger_I_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39441
            '10769': 0.804,  # lvl:7 germany_G57_PzVI_Tiger_P
            # '39185': None, #lvl:8 germany_G16_PzVIB_Tiger_II_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39185
            # '65297': None, #lvl:8 germany_G51_Lowe_FL  !!!!PREMIUM https://premomer.org/tank.php?id=65297
            '46865': 1.5,  # lvl:8 germany_G143_E75_TS  !!!!PREMIUM
            '10513': 0.892,  # lvl:8 germany_G67_VK4502A
            '54289': 1.65,  # lvl:8 germany_G51_Lowe  !!!!PREMIUM
            '19729': 0.83,  # lvl:8 germany_G115_Typ_205B
            '5137' : 0.854,  # lvl:8 germany_G16_PzVIB_Tiger_II
            '48913': 1.5,  # lvl:8 germany_G138_VK168_02  !!!!PREMIUM
            '56081': 1.5,  # lvl:8 germany_G141_VK7501K  !!!!PREMIUM
            # '62737': None, #lvl:8 germany_G115_Typ_205_4_Jun  !!!!PREMIUM https://premomer.org/tank.php?id=62737
            '48145': 1.5,  # lvl:8 germany_G138_VK168_02_Mauerbrecher  !!!!PREMIUM
            '18705': 0.76,  # lvl:9 germany_G110_Typ_205
            '7441' : 0.788,  # lvl:9 germany_G58_VK4502P
            '9745' : 0.753,  # lvl:9 germany_G55_E-75
            '6929' : 0.84,  # lvl:10 germany_G42_Maus
            # '40721': None, #lvl:10 germany_G42_Maus_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40721
            '9489' : 0.764,  # lvl:10 germany_G56_E-100
            '19473': 0.73,  # lvl:10 germany_G134_PzKpfw_VII
            '58641': 0.73,  # lvl:10 germany_G92_VK7201  !!!!PREMIUM
            # AT-SPG
            '3601' : 0.987,  # lvl:2 germany_G21_PanzerJager_I
            # '41489': None, #lvl:2 germany_G21_PanzerJager_I_bootcamp  https://premomer.org/tank.php?id=41489
            '6673' : 0.915,  # lvl:3 germany_G20_Marder_II
            '17937': 0.85,  # lvl:4 germany_G101_StuG_III
            '1809' : 0.9125,  # lvl:4 germany_G09_Hetzer
            '11281': 0.85,  # lvl:4 germany_G39_Marder_III
            # '28433': None, #lvl:4 germany_G09_Hetzer_MapsTraining_Dummy_ATSPG_1  https://premomer.org/tank.php?id=28433
            # '46097': None, #lvl:4 germany_G151_Pz_Sfl_IC  !!!!PREMIUM https://premomer.org/tank.php?id=46097
            # '39697': None, #lvl:5 germany_G05_StuG_40_AusfG_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39697
            '1041' : 1.0044,  # lvl:5 germany_G05_StuG_40_AusfG
            '60689': 1.5,  # lvl:5 germany_G104_Stug_IV  !!!!PREMIUM
            '16145': 0.95,  # lvl:5 germany_G76_Pz_Sfl_IVc
            # '28945': None, #lvl:6 germany_G40_Nashorn_MapsTraining_Dummy_ATSPG_2  https://premomer.org/tank.php?id=28945
            '57105': 1.35,  # lvl:6 germany_G41_DickerMax  !!!!PREMIUM
            '1553' : 0.98,  # lvl:6 germany_G17_JagdPzIV
            '11793': 0.95,  # lvl:6 germany_G40_Nashorn
            # '39953': None, #lvl:7 germany_G48_E-25_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39953
            '55569': 1.3,  # lvl:7 germany_G48_E-25  !!!!PREMIUM
            '11025': 0.75,  # lvl:7 germany_G43_Sturer_Emil
            '61713': 1.3,  # lvl:7 germany_G109_Steyr_WT  !!!!PREMIUM
            '3857' : 0.825,  # lvl:7 germany_G18_JagdPanther
            '50193': 1.5,  # lvl:8 germany_G114_Rheinmetall_Skorpian  !!!!PREMIUM
            # '55825': None, #lvl:8 germany_G37_Ferdinand_FL  !!!!PREMIUM https://premomer.org/tank.php?id=55825
            '62481': 1.5,  # lvl:8 germany_G114_Skorpian  !!!!PREMIUM
            '48401': 1.5,  # lvl:8 germany_G112_KanonenJagdPanzer_105  !!!!PREMIUM
            '11537': 0.725,  # lvl:8 germany_G71_JagdPantherII
            '7697' : 0.725,  # lvl:8 germany_G37_Ferdinand
            # '40465': None, #lvl:8 germany_G37_Ferdinand_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40465
            '16657': 0.72,  # lvl:8 germany_G99_RhB_Waffentrager
            # '38673': None, #lvl:8 germany_G65_JagdTiger_SdKfz_185_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38673
            '55313': 1.55,  # lvl:8 germany_G65_JagdTiger_SdKfz_185  !!!!PREMIUM
            '61969': 1.5,  # lvl:8 germany_G112_KanonenJagdPanzer  !!!!PREMIUM
            # '49425': None, #lvl:8 germany_G44_JagdTigerH  !!!!PREMIUM https://premomer.org/tank.php?id=49425
            '16401': 0.7,  # lvl:9 germany_G97_Waffentrager_IV
            # '56337': None, #lvl:9 germany_G44_JagdTiger_FL  !!!!PREMIUM https://premomer.org/tank.php?id=56337
            '7953' : 0.68,  # lvl:9 germany_G44_JagdTiger
            '16913': 0.6,  # lvl:10 germany_G98_Waffentrager_E100
            # '48657': None, #lvl:10 germany_G98_Waffentrager_E100_P  !!!!PREMIUM https://premomer.org/tank.php?id=48657
            '12049': 0.659,  # lvl:10 germany_G72_JagdPz_E100
            '19217': 0.6,  # lvl:10 germany_G121_Grille_15_L63
            # SPG
            # '65041': None, #lvl:1 germany_Env_Artillery  https://premomer.org/tank.php?id=65041
            '15121': 1.33,  # lvl:2 germany_G93_GW_Mk_VIe
            '2833' : 1.18,  # lvl:3 germany_G11_Bison_I
            '5905' : 1.08,  # lvl:3 germany_G19_Wespe
            '4625' : 1.18,  # lvl:4 germany_G22_Sturmpanzer_II
            '15633': 1.03,  # lvl:4 germany_G95_Pz_Sfl_IVb
            '5649' : 1.12,  # lvl:5 germany_G23_Grille
            '273'  : 1.17,  # lvl:6 germany_G02_Hummel
            '8977' : 0.85,  # lvl:7 germany_G49_G_Panther
            '15377': 0.78,  # lvl:8 germany_G94_GW_Tiger_P
            '8721' : 0.7,  # lvl:9 germany_G45_G_Tiger
            '9233' : 0.82,  # lvl:10 germany_G61_G_E
        })
        self.COEFFICIENTS.update({
            # ussr
            # lightTank
            # '65281': None, #lvl:1 ussr_Observer  https://premomer.org/tank.php?id=65281
            # '40961': None, #lvl:1 ussr_R11_MS-1_bot  https://premomer.org/tank.php?id=40961
            '3329' : 0.918,  # lvl:1 ussr_R11_MS-1
            '1025' : 0.95,  # lvl:2 ussr_R08_BT-2
            # '50945': None, #lvl:2 ussr_R125_T_45  !!!!PREMIUM https://premomer.org/tank.php?id=50945
            '41473': 1.75,  # lvl:2 ussr_R86_LTP_bootcamp
            '15361': 0.82,  # lvl:2 ussr_R42_T-60
            # '41217': None, #lvl:2 ussr_R09_T-26_bot  https://premomer.org/tank.php?id=41217
            # '42241': None, #lvl:2 ussr_R03_BT-7_bootcamp  https://premomer.org/tank.php?id=42241
            # '43265': None, #lvl:2 ussr_R43_T-70_bootcamp  https://premomer.org/tank.php?id=43265
            '4609' : 0.892,  # lvl:2 ussr_R09_T-26
            '54529': 1.09,  # lvl:2 ussr_R84_Tetrarch_LL  !!!!PREMIUM
            # '41985': None, #lvl:2 ussr_R08_BT-2_bootcamp  https://premomer.org/tank.php?id=41985
            # '43009': None, #lvl:2 ussr_R22_T-46_bootcamp  https://premomer.org/tank.php?id=43009
            '52737': 1.6,  # lvl:3 ussr_R67_M3_LL  !!!!PREMIUM
            '60929': 1.3,  # lvl:3 ussr_R105_BT_7A  !!!!PREMIUM
            '15105': 0.85,  # lvl:3 ussr_R43_T-70
            '3073' : 0.836,  # lvl:3 ussr_R22_T-46
            '53505': 1.3145,  # lvl:3 ussr_R56_T-127  !!!!PREMIUM
            # '56577': None, #lvl:3 ussr_R86_LTP  !!!!PREMIUM https://premomer.org/tank.php?id=56577
            '52225': 1.3,  # lvl:3 ussr_R34_BT-SV  !!!!PREMIUM
            # '23041': None, #lvl:3 ussr_R174_BT-5  https://premomer.org/tank.php?id=23041
            # '44801': None, #lvl:3 ussr_R161_T_116  !!!!PREMIUM https://premomer.org/tank.php?id=44801
            # '40449': None, #lvl:4 ussr_R31_Valentine_LL_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40449
            '769'  : 0.975,  # lvl:4 ussr_R03_BT-7
            '52481': 1.575,  # lvl:4 ussr_R31_Valentine_LL  !!!!PREMIUM
            '15873': 1.02,  # lvl:4 ussr_R44_T80
            # '28161': None, #lvl:4 ussr_R44_T80_MapsTraining_Dummy_LT_1  https://premomer.org/tank.php?id=28161
            # '2049': None, #lvl:5 ussr_R12_A-20  https://premomer.org/tank.php?id=2049
            '9729' : 1.4,  # lvl:5 ussr_R70_T_50_2
            '9473' : 0.964,  # lvl:5 ussr_R41_T-50
            '16641': 0.83,  # lvl:6 ussr_R101_MT25
            # '45313': None, #lvl:6 ussr_R160_T_50_2  !!!!PREMIUM https://premomer.org/tank.php?id=45313
            '19457': 0.78,  # lvl:7 ussr_R131_Tank_Gavalov
            '45569': 1.5,  # lvl:8 ussr_R158_LT_432  !!!!PREMIUM
            '18433': 0.68,  # lvl:8 ussr_R107_LTB
            # '57345': None, #lvl:8 ussr_R98_T44_85M  !!!!PREMIUM https://premomer.org/tank.php?id=57345
            '18177': 0.67,  # lvl:9 ussr_R109_T54S
            '19201': 0.66,  # lvl:10 ussr_R132_VNII_100LT
            # mediumTank
            # '13057': None, #lvl:1 ussr_R46_KV-13_SH  https://premomer.org/tank.php?id=13057
            # '56321': None, #lvl:1 ussr_R07_T-34-85_training  https://premomer.org/tank.php?id=56321
            # '42497': None, #lvl:2 ussr_R06_T-28_bootcamp  https://premomer.org/tank.php?id=42497
            # '42753': None, #lvl:2 ussr_R07_T-34-85_bootcamp  https://premomer.org/tank.php?id=42753
            '47873': 1.3,  # lvl:3 ussr_R143_T_29  !!!!PREMIUM
            '33281': 1.5,  # lvl:4 ussr_R185_T_34_L_11_1941  !!!!PREMIUM
            '52993': 1.437,  # lvl:4 ussr_R68_A-32  !!!!PREMIUM
            '1537' : 0.997,  # lvl:4 ussr_R06_T-28
            '61441': 1.52,  # lvl:4 ussr_R118_T28_F30  !!!!PREMIUM
            '1'    : 1.094,  # lvl:5 ussr_R04_T-34
            '34305': 1.48,  # lvl:5 ussr_R193_M4A2_T_34  !!!!PREMIUM
            # '28673': None, #lvl:5 ussr_R04_T-34_MapsTraining_Player_MT_1  https://premomer.org/tank.php?id=28673
            '51457': 1.5,  # lvl:5 ussr_R32_Matilda_II_LL  !!!!PREMIUM
            '47105': 1.45,  # lvl:5 ussr_R154_T_34E_1943  !!!!PREMIUM
            '58113': 1.22,  # lvl:6 ussr_R108_T34_85M  !!!!PREMIUM
            '12289': 0.83,  # lvl:6 ussr_R57_A43
            '2561' : 0.906,  # lvl:6 ussr_R07_T-34-85
            # '48129': None, #lvl:6 ussr_R140_M4_Loza  !!!!PREMIUM https://premomer.org/tank.php?id=48129
            '59393': 1.25,  # lvl:6 ussr_R117_T34_85_Rudy  !!!!PREMIUM
            '57089': 1.25,  # lvl:7 ussr_R98_T44_85  !!!!PREMIUM
            # '28929': None, #lvl:7 ussr_R23_T-43_MapsTraining_Player_MT_2  https://premomer.org/tank.php?id=28929
            '35073': 1.5,  # lvl:7 ussr_R195_T34M_54  !!!!PREMIUM
            # '56833': None, #lvl:7 ussr_R99_T44_122  !!!!PREMIUM https://premomer.org/tank.php?id=56833
            '8961' : 0.928,  # lvl:7 ussr_R46_KV-13
            '6657' : 0.858,  # lvl:7 ussr_R23_T-43
            '12545': 0.77,  # lvl:7 ussr_R59_A44
            '32257': 1.5,  # lvl:8 ussr_R180_Object_274_A  !!!!PREMIUM
            '48897': 1.5,  # lvl:8 ussr_R122_T44_100B  !!!!PREMIUM
            '13313': 0.67,  # lvl:8 ussr_R60_Object416
            # '30977': None, #lvl:8 ussr_R173_K_91_2  !!!!PREMIUM https://premomer.org/tank.php?id=30977
            '47617': 1.5,  # lvl:8 ussr_R146_STG  !!!!PREMIUM
            '59905': 1.5,  # lvl:8 ussr_R112_T54_45  !!!!PREMIUM
            '61953': 1.5,  # lvl:8 ussr_R122_T44_100  !!!!PREMIUM
            '46337': 1.5,  # lvl:8 ussr_R127_T44_100_U  !!!!PREMIUM
            '62977': 1.5,  # lvl:8 ussr_R127_T44_100_P  !!!!PREMIUM
            '47361': 1.5,  # lvl:8 ussr_R146_STG_Tday  !!!!PREMIUM
            # '38913': None, #lvl:8 ussr_R20_T-44_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38913
            # '44033': None, #lvl:8 ussr_R20_T-44_FL  !!!!PREMIUM https://premomer.org/tank.php?id=44033
            '46081': 1.5,  # lvl:8 ussr_R127_T44_100_K  !!!!PREMIUM
            # '49153': None, #lvl:8 ussr_R127_T44_100_M  !!!!PREMIUM https://premomer.org/tank.php?id=49153
            '4353' : 0.802,  # lvl:8 ussr_R20_T-44
            # '43777': None, #lvl:8 ussr_R112_T54_45_FL  !!!!PREMIUM https://premomer.org/tank.php?id=43777
            '17665': 0.75,  # lvl:9 ussr_R104_Object_430_II
            # '21505': None, #lvl:9 ussr_R96_Object_430  https://premomer.org/tank.php?id=21505
            '7937' : 0.82,  # lvl:9 ussr_R40_T-54
            '33793': 1.52,  # lvl:9 ussr_R187_Object_590  !!!!PREMIUM
            # '57601': None, #lvl:9 ussr_R40_T-54_FL  !!!!PREMIUM https://premomer.org/tank.php?id=57601
            '15617': 0.73,  # lvl:10 ussr_R95_Object_907  !!!!PREMIUM
            '21761': 0.73,  # lvl:10 ussr_R144_K_91
            '34049': 1.5,  # lvl:10 ussr_R97_Object_140_cl  !!!!PREMIUM
            '17153': 0.73,  # lvl:10 ussr_R96_Object_430B
            # '60673': None, #lvl:10 ussr_R95_Object_907A  !!!!PREMIUM https://premomer.org/tank.php?id=60673
            # '61697': None, #lvl:10 ussr_R120_T22SR_A22  !!!!PREMIUM https://premomer.org/tank.php?id=61697
            '13825': 0.78,  # lvl:10 ussr_R87_T62A
            # '63745': None, #lvl:10 ussr_R87_T62A_fallout  https://premomer.org/tank.php?id=63745
            '16897': 0.82,  # lvl:10 ussr_R97_Object_140
            '19969': 0.73,  # lvl:10 ussr_R148_Object_430_U
            # heavyTank
            '54017': 1.4734,  # lvl:5 ussr_R38_KV-220  !!!!PREMIUM
            '33025': 1.3,  # lvl:5 ussr_R186_KV_1_Screened  !!!!PREMIUM
            '51713': 1.575,  # lvl:5 ussr_R33_Churchill_LL  !!!!PREMIUM
            # '1281': None, #lvl:5 ussr_R05_KV  https://premomer.org/tank.php?id=1281
            '11777': 1.0,  # lvl:5 ussr_R80_KV1
            # '51201': None, #lvl:5 ussr_R38_KV-220_beta  !!!!PREMIUM https://premomer.org/tank.php?id=51201
            '18689': 0.912,  # lvl:6 ussr_R13_KV-1s
            # '39425': None, #lvl:6 ussr_R106_KV85_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39425
            # '60161': None, #lvl:6 ussr_R114_Object_244  !!!!PREMIUM https://premomer.org/tank.php?id=60161
            '11265': 0.922,  # lvl:6 ussr_R72_T150
            '2817' : 0.583,  # lvl:6 ussr_R106_KV85
            # '64769': None, #lvl:6 ussr_R152_KV2_W  !!!!PREMIUM https://premomer.org/tank.php?id=64769
            # '39681': None, #lvl:6 ussr_R77_KV2_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39681
            '10497': 0.868,  # lvl:6 ussr_R77_KV2
            # '29185': None, #lvl:6 ussr_R72_T150_MapsTraining_Dummy_HT_2  https://premomer.org/tank.php?id=29185
            '49921': 1.5,  # lvl:7 ussr_R133_KV_122  !!!!PREMIUM
            '59137': 1.35,  # lvl:7 ussr_R71_IS_2B  !!!!PREMIUM
            '46593': 1.35,  # lvl:7 ussr_R156_IS_2M  !!!!PREMIUM
            '5889' : 0.894,  # lvl:7 ussr_R39_KV-3
            '513'  : 0.935,  # lvl:7 ussr_R01_IS
            # '31233': None, #lvl:7 ussr_R175_IS_2_screen  !!!!PREMIUM https://premomer.org/tank.php?id=31233
            # '22785': None, #lvl:8 ussr_R170_IS_2_II  https://premomer.org/tank.php?id=22785
            '9217' : 1.5,  # lvl:8 ussr_R61_Object252  !!!!PREMIUM
            # '43521': None, #lvl:8 ussr_R61_Object252_FL  !!!!PREMIUM https://premomer.org/tank.php?id=43521
            '63233': 1.5,  # lvl:8 ussr_R128_KV4_Kreslavskiy  !!!!PREMIUM
            '48641': 1.5,  # lvl:8 ussr_R134_Object_252K  !!!!PREMIUM
            '49665': 1.5,  # lvl:8 ussr_R134_Object_252U  !!!!PREMIUM
            '20481': 0.8,  # lvl:8 ussr_R139_IS_M
            # '39169': None, #lvl:8 ussr_R19_IS-3_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39169
            # '40193': None, #lvl:8 ussr_R54_KV-5_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40193
            '58881': 1.5,  # lvl:8 ussr_R113_Object_730  !!!!PREMIUM
            '11009': 0.922,  # lvl:8 ussr_R73_KV4
            '44289': 1.5,  # lvl:8 ussr_R165_Object_703_II  !!!!PREMIUM
            # '30721': None, #lvl:8 ussr_R165_Object_703_II_2  !!!!PREMIUM https://premomer.org/tank.php?id=30721
            # '49409': None, #lvl:8 ussr_R61_Object252_BF  !!!!PREMIUM https://premomer.org/tank.php?id=49409
            '62721': 1.5,  # lvl:8 ussr_R123_Kirovets_1  !!!!PREMIUM
            '53249': 1.5,  # lvl:8 ussr_R54_KV-5  !!!!PREMIUM
            '5377' : 0.797,  # lvl:8 ussr_R19_IS-3
            '60417': 1.5,  # lvl:8 ussr_R115_IS-3_auto  !!!!PREMIUM
            # '45825': None, #lvl:8 ussr_R115_IS-3_auto_test  https://premomer.org/tank.php?id=45825
            '19713': 0.77,  # lvl:9 ussr_R151_Object_257_2
            '20737': 0.77,  # lvl:9 ussr_R153_Object_705
            # '44545': None, #lvl:9 ussr_R119_Object_777  !!!!PREMIUM https://premomer.org/tank.php?id=44545
            # '22529': None, #lvl:9 ussr_R171_IS_3_II  https://premomer.org/tank.php?id=22529
            '10753': 0.756,  # lvl:9 ussr_R63_ST_I
            # '30465': None, #lvl:9 ussr_R172_Object_752  !!!!PREMIUM https://premomer.org/tank.php?id=30465
            '11521': 0.777,  # lvl:9 ussr_R81_IS8
            '6145' : 0.783,  # lvl:10 ussr_R90_IS_4M
            '7169' : 0.788,  # lvl:10 ussr_R45_IS-7
            # '61185': None, #lvl:10 ussr_R119_Object_777C  !!!!PREMIUM https://premomer.org/tank.php?id=61185
            # '64257': None, #lvl:10 ussr_R45_IS-7_fallout  https://premomer.org/tank.php?id=64257
            '32001': 1.5,  # lvl:10 ussr_R178_Object_780  !!!!PREMIUM
            # '50433': None, #lvl:10 ussr_R129_Object_257  !!!!PREMIUM https://premomer.org/tank.php?id=50433
            # '22273': None, #lvl:10 ussr_R169_ST_II  https://premomer.org/tank.php?id=22273
            # '31489': None, #lvl:10 ussr_R155_Object_277_bob  https://premomer.org/tank.php?id=31489
            '20993': 0.73,  # lvl:10 ussr_R145_Object_705_A
            '22017': 0.73,  # lvl:10 ussr_R155_Object_277
            # '40705': None, #lvl:10 ussr_R45_IS-7_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=40705
            '58369': 0.7,  # lvl:10 ussr_R110_Object_260  !!!!PREMIUM
            '46849': 0.7,  # lvl:10 ussr_R157_Object_279R  !!!!PREMIUM
            # AT-SPG
            '5121' : 0.964,  # lvl:2 ussr_R10_AT-1
            '41729': 1.75,  # lvl:2 ussr_R50_SU76I_bootcamp
            '54273': 1.2,  # lvl:3 ussr_R50_SU76I  !!!!PREMIUM
            '6913' : 0.724,  # lvl:4 ussr_R25_GAZ-74b
            '6401' : 0.795,  # lvl:4 ussr_R24_SU-76
            '53761': 1.3,  # lvl:5 ussr_R78_SU_85I  !!!!PREMIUM
            '257'  : 0.975,  # lvl:5 ussr_R02_SU-85
            '54785': 1.43,  # lvl:6 ussr_R49_SU100Y  !!!!PREMIUM
            '3585' : 0.854,  # lvl:6 ussr_R17_SU-100
            '2305' : 0.847,  # lvl:7 ussr_R18_SU-152
            '10241': 0.72,  # lvl:7 ussr_R74_SU100M1
            # '39937': None, #lvl:7 ussr_R18_SU-152_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=39937
            '59649': 1.35,  # lvl:7 ussr_R116_ISU122C_Berlin  !!!!PREMIUM
            '55297': 1.44,  # lvl:7 ussr_R89_SU122_44  !!!!PREMIUM
            # '62209': None, #lvl:8 ussr_R121_KV4_KTT  !!!!PREMIUM https://premomer.org/tank.php?id=62209
            '9985' : 0.798,  # lvl:8 ussr_R58_SU-101
            '31745': 1.6,  # lvl:8 ussr_R177_ISU_152K_BL10  !!!!PREMIUM
            '48385': 1.5,  # lvl:8 ussr_R135_T_103  !!!!PREMIUM
            '58625': 1.0,  # lvl:8 ussr_R111_ISU130  !!!!PREMIUM
            # '45057': None, #lvl:8 ussr_R159_SU_130PM  !!!!PREMIUM https://premomer.org/tank.php?id=45057
            # '38657': None, #lvl:8 ussr_R47_ISU-152_IGR  !!!!PREMIUM https://premomer.org/tank.php?id=38657
            '7425' : 0.711,  # lvl:8 ussr_R47_ISU-152
            '8193' : 0.62,  # lvl:9 ussr_R53_Object_704
            '12033': 0.702,  # lvl:9 ussr_R75_SU122_54
            '32769': 1.4734,  # lvl:9 ussr_R183_K_91_PT  !!!!PREMIUM
            # '21249': None, #lvl:9 ussr_R93_Object263  https://premomer.org/tank.php?id=21249
            '14337': 0.633,  # lvl:10 ussr_R93_Object263B
            # '50689': None, #lvl:10 ussr_R126_Object_730_5  !!!!PREMIUM https://premomer.org/tank.php?id=50689
            '20225': 0.63,  # lvl:10 ussr_R149_Object_268_4
            '13569': 0.605,  # lvl:10 ussr_R88_Object268
            # SPG
            '3841' : 0.98,  # lvl:2 ussr_R16_SU-18
            '7681' : 0.964,  # lvl:3 ussr_R66_SU-26
            '4865' : 1.044,  # lvl:4 ussr_R14_SU-5
            # '28417': None, #lvl:4 ussr_R14_SU-5_MapsTraining_Dummy_SPG_1  https://premomer.org/tank.php?id=28417
            '16385': 1.12,  # lvl:5 ussr_R100_SU122A
            '5633' : 1.0,  # lvl:6 ussr_R26_SU-8
            '16129': 0.945,  # lvl:7 ussr_R91_SU14_1
            '1793' : 0.935,  # lvl:7 ussr_R15_S-51
            '4097' : 0.78,  # lvl:8 ussr_R27_SU-14
            '8449' : 0.68,  # lvl:9 ussr_R51_Object_212
            '8705' : 0.76,  # lvl:10 ussr_R52_Object_261
        })


class Flash(object):
    def startBattle(self):
        if not config.data['battleShow']:
            return
        if not g_flash:
            return
        g_flash.createComponent('credits', COMPONENT_TYPE.PANEL, {
            'x'     : config.data['battle_x'],
            'y'     : config.data['battle_y'],
            'width' : 1,
            'height': 1,
            'drag'  : True, 'border': True, 'alignX': COMPONENT_ALIGN.LEFT, 'alignY': COMPONENT_ALIGN.BOTTOM})

        g_flash.createComponent('credits.text', COMPONENT_TYPE.LABEL, {
            'shadow': {"distance": 0, "angle": 0, "color": 0x000000, "alpha": 1, "blurX": 1, "blurY": 1, "strength": 1, "quality": 1},
            'text'  : '', 'width': 168, 'height': 25, 'index': 1, 'multiline': True, 'tooltip': '+1000 or -1000 it\'s normal calc\nIf calc incorrect, play battle without damage to fix it.\nFull time replays, no escape!!!'})
        if config.data['battleBackground']:
            g_flash.createComponent('credits.image', COMPONENT_TYPE.IMAGE, {
                'width': 168, 'height': 25, 'index': 0, 'image': '../maps/icons/quests/inBattleHint.png'})
        COMPONENT_EVENT.UPDATED += self.update

    def stopBattle(self):
        if not config.data['battleShow']:
            return
        if not g_flash:
            return
        COMPONENT_EVENT.UPDATED -= self.update
        g_flash.deleteComponent('credits.text')
        if config.data['battleBackground']:
            g_flash.deleteComponent('credits.image')
        g_flash.deleteComponent('credits')

    def update(self, alias, props):
        if not config.data['battleShow']:
            return
        if str(alias) == str('credits'):
            x = int(props.get('x', config.data['battle_x']))
            if x and x != int(config.data['battle_x']):
                config.data['battle_x'] = x
            y = int(props.get('y', config.data['battle_y']))
            if y and y != int(config.data['battle_y']):
                config.data['battle_y'] = y
            config.apply(config.data)
            # g_flash.updateComponent('credits.text', data)
            # print '%s Flash coordinates updated : y = %i, x = %i, props: %s' % (alias, config.data['battle_y'], config.data['battle_x'], props)

    def setCreditsText(self, text, width=0, height=0):
        if not config.data['battleShow']:
            return
        if not g_flash:
            return
        data = {'visible': True, 'text': text}
        if width:
            data['width'] = width
        if height:
            data['width'] = height
        g_flash.updateComponent('credits.text', data)

    def visible(self, status):
        if not config.data['battleShow']:
            return
        g_flash.updateComponent('credits', {'visible': status})


class BattleResultParser(object):
    def __init__(self):
        self.Threads = True
        self.ArenaIDQueue = Queue()
        self.ResultsCache = []
        self.ResultsAvailable = threading.Event()
        self.thread = threading.Thread(target=self.WaitResult)
        self.thread.setDaemon(True)
        self.thread.setName('WaitResult')
        self.thread.start()

    def CheckCallback(self, ArenaUniqueID, ErrorCode, battleResults):
        if ErrorCode in [-3, -5]:
            BigWorld.callback(1.0, lambda: self.ArenaIDQueue.put(ArenaUniqueID))
        elif ErrorCode >= 0:
            if ArenaUniqueID in self.ResultsCache: return
            calc.receiveBattleResult(True, battleResults)
            # print battleResults.get('arenaUniqueID')
            # print battleResults.get('personal')
            # print battleResults.get('common')

    def WaitResult(self):
        while self.Threads:
            ArenaUniqueID = self.ArenaIDQueue.get()
            self.ResultsAvailable.wait()
            try:
                BigWorld.player().battleResultsCache.get(ArenaUniqueID, partial(self.CheckCallback, ArenaUniqueID))
            except Exception as e:
                pass


config = Config()
#flashInHangar = flashInHangar()
flash = Flash()
calc = CreditsCalculator()
results = BattleResultParser()


def hook_start_battle(*args):
    if BigWorld.player().arena.bonusType == ARENA_BONUS_TYPE.REGULAR:
        calc.timer()
    hooked_start_battle(*args)


def hook_before_delete(*args):
    if BigWorld.player().arena.bonusType == ARENA_BONUS_TYPE.REGULAR:
        calc.stopBattle()
    hooked_before_delete(*args)

def hook_CrewWidget_updateWidgetModel(self):
    result = hooked_CrewWidget_updateWidgetModel(self)
    if g_currentVehicle.item:
        try:
            status = g_currentVehicle.itemsCache.items.stats.activePremiumExpiryTime > 0
        except Exception as e:
            status = False
        try:
            calc.getHangarData(status)
        except Exception as e:
            print 'ERROR: creditCalc crew:', e

    return result


def hook_onBattleEvents(self, events):
    hooked_onBattleEvents(self, events)
    if BigWorld.player().arena.bonusType == ARENA_BONUS_TYPE.REGULAR:
        calc.onBattleEvents(events)


def hook_LobbyPopulate(self):
    hooked_LobbyPopulate(self)
    BigWorld.callback(3.0, calc.hangarMessage)


def hook_BattleResultsFormatter_format(self, message, *args):
    arenaUniqueID = message.data.get('arenaUniqueID', 0)
    results.ArenaIDQueue.put(arenaUniqueID)
    return hooked_BattleResultsFormatter_format(self, message, *args)


def onAccountBecomePlayer():
    results.ResultsAvailable.set()


def IntoBattle():
    results.ResultsAvailable.clear()


hooked_start_battle = PlayerAvatar._PlayerAvatar__startGUI
hooked_before_delete = PlayerAvatar._PlayerAvatar__destroyGUI
hooked_onBattleEvents = PlayerAvatar.onBattleEvents
hooked_CrewWidget_updateWidgetModel = CrewWidget._CrewWidget__updateWidgetModel
hooked_LobbyPopulate = LobbyView._populate
hooked_BattleResultsFormatter_format = BattleResultsFormatter.format

PlayerAvatar._PlayerAvatar__startGUI = hook_start_battle
PlayerAvatar._PlayerAvatar__destroyGUI = hook_before_delete
PlayerAvatar.onBattleEvents = hook_onBattleEvents
CrewWidget._CrewWidget__updateWidgetModel = hook_CrewWidget_updateWidgetModel
LobbyView._populate = hook_LobbyPopulate
BattleResultsFormatter.format = hook_BattleResultsFormatter_format
g_playerEvents.onBattleResultsReceived += calc.receiveBattleResult
g_playerEvents.onAvatarReady += IntoBattle
g_playerEvents.onAccountBecomePlayer += onAccountBecomePlayer


def fini():
    results.Threads = False


def jsonGenerator(nations, onlyNew=False):
    from CurrentVehicle import g_currentVehicle as g_currentVehicle
    import ResMgr as ResMgr
    import os as os
    import codecs as codecs
    import json as json
    COEFFICIENTS = {}
    resMgr = ResMgr.openSection('../version.xml')
    if resMgr is None:
        resMgr = ResMgr.openSection('version.xml')
        if resMgr is None:
            resMgr = ResMgr.openSection('./version.xml')
    ver = 'temp' if resMgr is None else resMgr.readString('version')
    i1 = ver.find('.')
    i2 = ver.find('#')
    PATH = ''.join(['./res_mods/', ver[i1 + 1:i2 - 1], '/system/'])
    if os.path.isfile(PATH + 'sw_templates.json'):
        try:
            with codecs.open(PATH + 'sw_templates.json', 'r', encoding='utf-8-sig') as json_file:
                data = json_file.read().decode('utf-8-sig')
                COEFFICIENTS.update(calc.byte_ify(json.loads(data)))
                json_file.close()
        except Exception as e:
            COEFFICIENTS.update({})

    def deCode(compactDescr):
        test = '%s' % compactDescr
        if test in COEFFICIENTS:
            return test, round(COEFFICIENTS[test], 6)
        return test, 0.0

    items = g_currentVehicle.itemsCache.items.getVehicles()

    def getData(nation, role):
        text = ''
        for level in xrange(1, 11):
            for compactDescr in items:
                vehicle = items[compactDescr]
                if vehicle.nationName == nation and vehicle.descriptor.level == level and vehicle.type == role:
                    vehicleCompDesc, balanceCoeff = deCode(compactDescr)
                    thatPremium = ' !!!!PREMIUM' if vehicle.isPremium or vehicle.isPremiumIGR else ''
                    details = '#lvl:%s %s %s' % (vehicle.descriptor.level, vehicle.name.replace(':', '_'), thatPremium)
                    if not balanceCoeff:
                        text += "#'%s': %s, %s https://premomer.org/tank.php?id=%s\n" % (compactDescr, None, details, compactDescr)
                    if not onlyNew and balanceCoeff:
                        text += "'%s': %s, %s\n" % (compactDescr, balanceCoeff, details)
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
            getData(nation, role)
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!! DONE !!!!!!!!!!!!!!!!!!!!!!!!!!!'

#jsonGenerator(['ussr', 'germany', 'uk', 'japan', 'usa', 'china', 'france', 'czech', 'sweden', 'poland', 'italy'], True)

#BigWorld.flashInHangar = flashInHangar
