# -*- coding: utf-8 -*-
import copy
import BigWorld
import GUI
from Avatar import PlayerAvatar
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from Vehicle import Vehicle
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.framework import ViewTypes
from gui.battle_control.controllers import feedback_events
from gui.mods.mod_mods_gui import COMPONENT_ALIGN, COMPONENT_EVENT, COMPONENT_TYPE, g_gui, g_guiFlash, inject
from helpers import dependency, i18n
from skeletons.account_helpers.settings_core import ISettingsCore

ACHIEVEMENT_CONDITIONS = {
    # медаль                  # условие, текущее значение, граница проверки
    'warrior'                 : {'minFrags': [6, 0, 4]},
    'invader'                 : {'minCapturePts': [80, 0, 60]},
    'sniper'                  : {'minAccuracy': [0.85, 0.0, 0.85],
                                 'minShots'   : [10, 0, 7],
                                 'minDamage'  : [1000, 0, 700]},
    'sniper2'                 : {'minAccuracy'             : [0.85, 0.0, 0.85],
                                 'minDamage'               : [1000, 0, 700],
                                 'minHitsWithDamagePercent': [0.8, 0.0, 0.8],
                                 'sniperDistance'          : [300.0, 0, 300.0],
                                 'minShots'                : [8, 0, 6]},
    'mainGun'                 : {'minDamage'                  : [1000, 0, 1000],
                                 'minDamageToTotalHealthRatio': [0.2, 0, 0.2]},
    'defender'                : {'minPoints': [70, 0, 50]},
    'steelwall'               : {'minDamage': [1000, 0, 700],
                                 'minHits'  : [11, 0, 7]},
    'supporter'               : {'minAssists': [6, 0, 4]},
    'scout'                   : {'minDetections': [9, 0, 5]},
    'evileye'                 : {'minAssists': [6, 0, 3]},
    'medalRadleyWalters'      : {'minLevel': [5, 0, 5],
                                 'minKills': [8, 0, 6],
                                 'maxKills': [9, 0, 6]},
    'medalLafayettePool'      : {'minLevel': [5, 0, 5],
                                 'minKills': [10, 0, 9],
                                 'maxKills': [13, 0, 9]},
    'heroesOfRassenay'        : {'minKills': [14, 0, 13],
                                 'maxKills': [255, 0, 13]},
    'medalOrlik'              : {'minVictimLevelDelta': [1, 0, 1],
                                 'minKills'           : [2, 0, 1]},
    'medalLehvaslaiho'        : {'minVictimLevelDelta': [1, 0, 1],
                                 'minKills'           : [2, 0, 1],
                                 'maxKills'           : [2, 0, 1]},
    'medalOskin'              : {'minVictimLevelDelta': [1, 0, 1],
                                 'minKills'           : [3, 0, 2],
                                 'maxKills'           : [3, 0, 2]},
    'medalNikolas'            : {'minVictimLevelDelta': [1, 0, 1],
                                 'minKills'           : [4, 0, 3],
                                 'maxKills'           : [255, 0, 3]},
    'medalHalonen'            : {'minVictimLevelDelta': [2, 0, 2],
                                 'minKills'           : [2, 0, 1]},
    'medalPascucci'           : {'minKills': [2, 0, 1],
                                 'maxKills': [2, 0, 1]},
    'medalDumitru'            : {'minKills': [3, 0, 2],
                                 'maxKills': [255, 0, 2]},
    'medalBurda'              : {'minVictimLevelDelta': [1, 0, 1],
                                 'minKills'           : [3, 0, 2],
                                 'maxKills'           : [255, 0, 2]},
    'medalBillotte'           : {'hpPercentage': [20, 0, 20],
                                 'minCrits'    : [5, 0, 3],
                                 'minKills'    : [2, 0, 1],
                                 'maxKills'    : [2, 0, 1]},
    'medalBrunoPietro'        : {'hpPercentage': [20, 0, 20],
                                 'minCrits'    : [5, 0, 3],
                                 'minKills'    : [3, 0, 2],
                                 'maxKills'    : [4, 0, 2]},
    'medalTarczay'            : {'hpPercentage': [20, 0, 20],
                                 'minCrits'    : [5, 0, 3],
                                 'minKills'    : [5, 0, 4],
                                 'maxKills'    : [255, 0, 4]},
    'medalKolobanov'          : {'teamDiff': [5, 0, 5]},
    'medalBrothersInArms'     : {'minKills': [3, 0, 3]},
    'medalCrucialContribution': {'minKills': [12, 0, 9]},
    'medalDeLanglade'         : {'minKills': [4, 0, 2]},
    'medalTamadaYoshio'       : {'minKills'           : [2, 0, 1],
                                 'maxKills'           : [255, 0, 1],
                                 'minVictimLevelDelta': [1, 0, 1]},
    'kamikaze'                : {'levelDelta': [1, 0, 1]},
    'huntsman'                : {'minKills': [3, 0, 2]},
    'bombardier'              : {'minKills': [2, 0, 1]},
    'luckyDevil'              : {'radius': [10.99, 0, 10.99]},
    'ironMan'                 : {'minHits': [10, 0, 7]},
    'sturdy'                  : {'minHealth': [10.0, 0, 10.0]},
    'alaric'                  : {'minKills'    : [2, 0, 1],
                                 'minMonuments': [1, 0, 1]},
    'lumberjack'              : {'minKills': [3, 0, 2],
                                 'minTrees': [30, 0, 20]},
    'wolfAmongSheep'          : {'minDamage': [1, 0, 1]},
    'geniusForWar'            : {'minXP': [1, 0, 1]},
    'willToWinSpirit'         : {'enemyCount': [3, 0, 3]},
    'fightingReconnaissance'  : {'maxPosInTopDamager': [3, 0, 3],
                                 'minSpottedCount'   : [2, 0, 1]},
    'monolith'                : {'maxSpeed_ms': [11 / 3.6, 0, 11 / 3.6]},
    'medalAntiSpgFire'        : {'minKills': [2, 0, 2]},
    'medalStark'              : {'minKills': [2, 0, 2],
                                 'hits'    : [2, 0, 2]},
    'medalGore'               : {'minDamageRate': [8, 0, 8],
                                 'minDamage'    : [2000, 0, 1600]},
    'medalCoolBlood'          : {'maxDistance': [100, 0, 100],
                                 'minKills'   : [2, 0, 1]},
    'promisingFighter'        : {'maxPosInTopXPGainer': [3, 0, 3]},
    'heavyFire'               : {'maxPosInTopDamager': [3, 0, 3]},
    'fighter'                 : {'minKills': [4, 0, 3],
                                 'maxKills': [5, 0, 3]},
    'duelist'                 : {'minKills': [2, 0, 1]},
    'bonecrusher'             : {'minCrits': [5, 0, 5]},
    'charmed'                 : {'minVehs': [4, 0, 4]},
    'tacticalAdvantage'       : {'maxLevel': [7, 0, 7]},
    'secretOperations'        : {'minGroupLen': [2, 0, 2]},
    'shoulderToShoulder'      : {'minKills'      : [12, 0, 12],
                                 'minDamageDealt': [30000, 0, 28000]},
    'aloneInTheField'         : {'minDamageDealt': [10000, 0, 9000]},
    'fallenFlags'             : {'minFlags': [4, 0, 4]},
    'effectiveSupport'        : {'minDamageDealt': [2000, 0, 1800]},
    'falloutDieHard'          : {'minKills'      : [5, 0, 5],
                                 'minDamageDealt': [10000, 0, 10000]},
    'predator'                : {'minKills': [5, 0, 5]},
    'champion'                : {'minKills'       : [5, 0, 5],
                                 'minDamageDealt' : [10000, 0, 10000],
                                 'minFlagsCapture': [3, 0, 3]},
    'bannerman'               : {'minFlagsCapture': [4, 0, 4]},
    'ironShield'              : {'minDamage'         : [1800, 0, 1800],
                                 'DestructibleEntity': [150, 0, 150],
                                 'SectorBase'        : [50, 0, 50]},
    'occupyingForce'          : {'minBasePoints': [100, 0, 100]},
    'supremeGun'              : {'minDamageDealt': [10000, 0, 10000]},
    'smallArmy'               : {'minVehiclesDestroyed': [20, 0, 20]}}
ACHIEVEMENT_CONDITIONS_EXT = {'warrior'           : {'minFrags': [8, 0, 6]},
                              'heroesOfRassenay'  : {'minKills': [21, 0, 18],
                                                     'maxKills': [255, 0, 18]},
                              'medalLafayettePool': {'minLevel': [5, 0, 5],
                                                     'minKills': [13, 0, 10],
                                                     'maxKills': [20, 0, 10]},
                              'medalRadleyWalters': {'minLevel': [5, 0, 5],
                                                     'minKills': [10, 0, 8],
                                                     'maxKills': [12, 0, 8]}}


class Config(object):
    def __init__(self):
        self.ids = 'insigniaMonitor'
        self.version = 'v1.01 (2019-05-04)'
        self.version_id = 101
        self.author = 'by spoter'
        self.data = {
            'version'        : self.version_id,
            'enabled'        : True,
            'panelSuccess'   : {'x': 1260, 'y': -900, 'width': 163, 'height': 50, 'drag': True, 'border': True, 'alignX': COMPONENT_ALIGN.LEFT, 'alignY': COMPONENT_ALIGN.BOTTOM},
            'panelConditions': {'x': 650, 'y': -300, 'width': 163, 'height': 50, 'drag': True, 'border': True, 'alignX': COMPONENT_ALIGN.LEFT, 'alignY': COMPONENT_ALIGN.BOTTOM},
            'shadowText'     : {'distance': 0, 'angle': 0, 'color': 0x000000, "alpha": 1, 'blurX': 1, 'blurY': 1, 'strength': 1, 'quality': 1},
            'font'           : '$IMELanguageBar',
            'fontSize'       : 10,
            'fontColor'      : '#FFFFFF',
        }
        self.i18n = {
            'version'       : self.version_id,
            'UI_description': 'insignia monitor',
            'minDetections' : '<img src=\"img://gui/maps/mod_insigniaMonitor/conditions/condition_assist.png\" vspace=\"-6\" width=\"10\" height=\"10\" />',
            'minFrags' : '<img src=\"img://gui/maps/mod_insigniaMonitor/conditions/condition_kill_vehicles.png\" vspace=\"-6\" width=\"10\" height=\"10\" />',

            'scout'         : '<img src=\"img://gui/maps/mod_insigniaMonitor/insignia/scout.png\" width=\"32\" height=\"32\"/>',
            'scout_success' : '<img src=\"img://gui/maps/mod_insigniaMonitor/insignia/scout.png\"/>',
            'warrior' : '<img src=\"img://gui/maps/mod_insigniaMonitor/insignia/warrior.png\" width=\"32\" height=\"32\"/>',
            'warrior_success': '<img src=\"img://gui/maps/mod_insigniaMonitor/insignia/warrior.png\"/>',

        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        res = {
            'modDisplayName' : self.i18nGet('UI_aim_name'),
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [],
            'column2'        : [],
        }
        # self.p__addLabel(res['column1'], 'LABEL')
        # self.p__addCheckbox(res['column1'], 'ARTY_SHOW')

        # self.p__addSlider(res['column1'], 'STABILIZATION_FIX', 0, 20, 1, '%s [12]' % self.i18nGet('UI_FORMAT_%'))
        # self.p__addMenu(res['column1'], 'AMMO_RANDOM', 2, 300)

        # self.p__addTextInput(res['column1'], 'GENERATE_FREEZES_TO_CLANS', True)

        # self.p__addHotkey(res['column2'], 'TRACKS_FORCE_KEY')

        return res

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)

    def i18nGet(self, key):
        return self.i18n.get(key, key)

    def p__addSlider(self, row, varName, minValue, maxValue, step, prefix=''):
        row.append({
            'type'        : 'Slider',
            'text'        : self.i18nGet('UI_' + varName),
            'tooltip'     : self.i18nGet('UI_' + varName + '_tooltip'),
            'minimum'     : minValue,
            'maximum'     : maxValue,
            'snapInterval': step,
            'value'       : self.data[varName],
            'format'      : '{{value}} %s' % prefix,
            'varName'     : varName
        })

    def p__addCheckbox(self, row, varName):
        row.append({
            'type'   : 'CheckBox',
            'text'   : self.i18nGet('UI_' + varName),
            'tooltip': self.i18nGet('UI_' + varName + '_tooltip'),
            'value'  : self.data[varName],
            'varName': varName
        })

    def p__addHotkey(self, row, varName):
        row.append({
            'type'        : 'HotKey',
            'text'        : self.i18nGet('UI_' + varName),
            'tooltip'     : self.i18nGet('UI_' + varName + '_tooltip'),
            'value'       : self.data[varName],
            'defaultValue': self.data[varName],
            'varName'     : varName
        })

    @staticmethod
    def p__addLabelBlank(row, count):
        for i in xrange(count):
            row.append({
                'type'   : 'Label',
                'text'   : '',
                'tooltip': '',
            })

    def p__addLabel(self, row, varName, showTooltip=False):
        row.append({
            'type'   : 'Label',
            'text'   : self.i18nGet('UI_' + varName),
            'tooltip': self.i18nGet('UI_' + varName + '_tooltip') if showTooltip else '',
        })

    def p__addTextInput(self, row, varName, showTooltip=False):
        row.append({
            'type'   : 'TextInput',
            'text'   : self.i18nGet('UI_' + varName),
            'tooltip': self.i18nGet('UI_' + varName + '_tooltip') if showTooltip else '',
            'value'  : self.data[varName],
            'varName': varName,
        })

    @staticmethod
    def p__addEmpty(row):
        row.append({
            'type': 'Empty'
        })

    def p__addRadioButtons(self, row, varName, defaultValue, listData):
        a = []
        for i in listData:
            a.append({
                'label': i
            })
        # print a
        row.append({
            'type'   : 'RadioButtonGroup',
            'text'   : self.i18nGet('UI_' + varName),
            'tooltip': self.i18nGet('UI_' + varName + '_tooltip'),
            'options': a,
            'value'  : defaultValue,
            'varName': varName
        })
        # print row

    def p__addMenu(self, row, varName, menuCount, width=200):
        a = []
        for i in xrange(menuCount):
            a.append({
                'label': self.i18nGet('UI_' + varName + '_menu' + '%s' % i)
            })
        row.append({
            'type'        : 'Dropdown',
            'text'        : self.i18nGet('UI_' + varName),
            'tooltip'     : self.i18nGet('UI_' + varName + '_tooltip'),
            'itemRenderer': 'DropDownListItemRendererSound',
            'options'     : a,
            'width'       : width,
            'value'       : self.data[varName],
            'varName'     : varName
        })


class Flash(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.data = {}
        self.panelSuccessSlots = []
        self.panelConditionsSlots = []

    def startBattle(self):
        if not config.data['enabled']: return
        self.data = {
            'panelSuccess'   : config.data.get('panelSuccess'),
            'panelConditions': config.data.get('panelConditions'),
            'shadow'         : {'shadow': config.data.get('shadowText')},
        }
        self.panelSuccessSlots = []
        self.panelConditionsSlots = []
        COMPONENT_EVENT.UPDATED += self.update
        self.createObject('panelSuccess', COMPONENT_TYPE.PANEL)
        self.createObject('panelConditions', COMPONENT_TYPE.PANEL)
        # g_guiResetters.add(self.screenResize)
        # self.screenResize()

    def stopBattle(self):
        if not config.data['enabled']: return
        # g_guiResetters.remove(self.screenResize)
        COMPONENT_EVENT.UPDATED -= self.update
        self.deleteObject('panelSuccess')
        for id in self.panelSuccessSlots:
            self.deleteObject('panelSuccess.slot%s' % id)
        self.deleteObject('panelConditions')
        for id in self.panelConditionsSlots:
            self.deleteObject('panelConditions.slot%s' % id)
        self.panelSuccessSlots = []
        self.panelConditionsSlots = []
        self.data.clear()

    def deleteObject(self, name):
        g_guiFlash.deleteComponent(name)

    def createObject(self, name, type):
        g_guiFlash.createComponent(name, type, self.data[name] if '.slot' not in name else self.data['slot'])

    def createSlot(self, name, slot):
        x = slot * 40
        self.data[name] = {'text': '', 'x': x, 'y': 0, 'tooltip': '', 'index': 1, 'multiline': True}
        g_guiFlash.createComponent(name, COMPONENT_TYPE.LABEL, self.data[name])

    def updateObject(self, name, data):
        g_guiFlash.updateComponent(name, data)

    def sendToPanelSuccess(self, name, insignia):
        if insignia['panelSuccess'] > 0:
            ids = insignia['panelSuccess']
        else:
            ids = self.panelSuccessSlots[-1] + 1 if self.panelSuccessSlots else 1
            insigniaMonitor.insignia[name]['panelSuccess'] = ids
            self.panelSuccessSlots.append(ids)
            self.createSlot('panelSuccess.slot%s' % ids, ids)
            self.updateObject('panelSuccess.slot%s' % ids, self.data['shadow'])

        tooltip = i18n.makeString('#achievements:%s_descr' % name)
        text = config.i18n['%s_success' % name]
        self.setText(text, tooltip, slot=ids)

    def sendToPanelConditions(self, name, insignia):
        if insignia['panelConditions'] > 0:
            ids = insignia['panelConditions']
        else:
            ids = self.panelConditionsSlots[-1] + 1 if self.panelConditionsSlots else 1
            insigniaMonitor.insignia[name]['panelConditions'] = ids
            self.panelConditionsSlots.append(ids)
            self.createSlot('panelConditions.slot%s' % ids, ids)
            self.updateObject('panelConditions.slot%s' % ids, self.data['shadow'])

        tooltip = i18n.makeString('#achievements:%s_descr' % name)

        text = '%s\n' % config.i18n[name]
        for cond in insignia['conditions']:
            text += '%s%s[%s]\n' % (config.i18n[cond], insignia['conditions'][cond][1], insignia['conditions'][cond][0])

        self.setText(text, tooltip, panel='panelConditions', slot=ids)

    def removeOnPanelConditions(self, insignia):
        if insignia['panelConditions'] > 0:
            ids = insignia['panelConditions']
            if ids in self.panelConditionsSlots:
                del self.panelConditionsSlots[self.panelConditionsSlots.index(ids)]
                self.deleteObject('panelConditions.slot%s' % ids)

    @inject.log
    def update(self, alias, props):
        # Component "testSprite" updated : {'y': 32.0, 'x': 256.0}
        print 'Component "%s" updated : %s' % (alias, props)
        '''
        if str(alias) == str(config.ids):
            x = int(props.get('x', config.data['panel']['x']))
            if x and x != int(config.data['panel']['x']):
                config.data['panel']['x'] = x
                self.data[COMPONENT_TYPE.PANEL]['x'] = x
            y = int(props.get('y', config.data['panel']['y']))
            if y and y != int(config.data['panel']['y']):
                config.data['panel']['y'] = y
                self.data[COMPONENT_TYPE.PANEL]['y'] = y
            self.screenResize()
            print '%s Flash coordinates updated : y = %i, x = %i, props: %s' % (alias, config.data['panel']['y'], config.data['panel']['x'], props)
        '''

    def setupSize(self, h=None, w=None):
        height = int(config.data['panelSize'].get('heightNormal', 50)) if not worker.altMode else int(config.data['panelSize'].get('heightAlt', 80))
        width = int(config.data['panelSize'].get('widthNormal', 163)) if not worker.altMode else int(config.data['panelSize'].get('widthAlt', 163))
        if config.data['UI'] == 1:
            height = 30 if not worker.altMode else 45
            width = 152 if not worker.altMode else 152
        if config.data['UI'] == 2:
            height = 30 if not worker.altMode else 50
            width = 130 if not worker.altMode else 130
        if config.data['UI'] == 3:
            height = 70 if not worker.altMode else 100
            width = 130 if not worker.altMode else 130
        if config.data['UI'] == 4:
            height = 50 if not worker.altMode else 80
            width = 163 if not worker.altMode else 163

        if config.data['UI'] in (5, 6, 7, 8):
            height = 82 if not worker.altMode else 82
            width = 343 if not worker.altMode else 343

        if h is not None and w is not None:
            height = h
            width = w

        height = height * config.data['battleMessageSizeInPercent'] / 100
        width = width * config.data['battleMessageSizeInPercent'] / 100

        for name in self.data:
            self.data[name]['height'] = height
            self.data[name]['width'] = width
        data = {'height': height, 'width': width}
        self.updateObject(COMPONENT_TYPE.PANEL, data)
        self.updateObject(COMPONENT_TYPE.LABEL, data)
        if config.data['background']:
            self.updateObject(COMPONENT_TYPE.IMAGE, data)

    def setText(self, text, tooltip, panel='panelSuccess', slot=1):
        name = '%s.slot%s' % (panel, slot)
        txt = '<font face="%s" size="%s" color="%s" vspace="-3" align="baseline" >%s</font>' % (config.data['font'], config.data['fontSize'], config.data['fontColor'], text)
        tooltips = '<font face="%s" size="%s" color="%s" vspace="-3" align="baseline" >%s</font>' % (config.data['font'], config.data['fontSize'], config.data['fontColor'], tooltip)
        self.updateObject(name, {'text': txt, 'tooltip': tooltips})

    def setVisible(self, status, panel=0):
        data = {'visible': status}
        if panel == 1 or not panel:
            self.updateObject('panelSuccess', data)
        if panel == 2 or not panel:
            self.updateObject('panelConditions', data)

    @staticmethod
    def screenFix(screen, value, mod, align=1):
        if align == 1:  # положительное
            if value + mod > screen:
                return max(0, int(screen - mod))
            if value < 0:
                return 0
        if align == -1:  # отрицательное
            if value - mod < -screen:
                return min(0, int(-screen + mod))
            if value > 0:
                return 0
        if align == 0:  # центр
            scr = screen / 2
            if value < scr:
                return int(scr - mod)
            if value > -scr:
                return int(-scr)
        return None

    @inject.log
    def screenResize(self):
        curScr = GUI.screenResolution()
        scale = self.settingsCore.interfaceScale.get()
        xMo, yMo = curScr[0] / scale, curScr[1] / scale
        x = None
        if config.data['panel']['alignX'] == COMPONENT_ALIGN.LEFT:
            x = self.screenFix(xMo, config.data['panel']['x'], config.data['panel']['width'], 1)
        if config.data['panel']['alignX'] == COMPONENT_ALIGN.RIGHT:
            x = self.screenFix(xMo, config.data['panel']['x'], config.data['panel']['width'], -1)
        if config.data['panel']['alignX'] == COMPONENT_ALIGN.CENTER:
            x = self.screenFix(xMo, config.data['panel']['x'], config.data['panel']['width'], 0)
        if x is not None:
            if x != int(config.data['panel']['x']):
                config.data['panel']['x'] = x
                self.data[COMPONENT_TYPE.PANEL]['x'] = x
        y = None
        if config.data['panel']['alignY'] == COMPONENT_ALIGN.TOP:
            y = self.screenFix(yMo, config.data['panel']['y'], config.data['panel']['height'], 1)
        if config.data['panel']['alignY'] == COMPONENT_ALIGN.BOTTOM:
            y = self.screenFix(yMo, config.data['panel']['y'], config.data['panel']['height'], -1)
        if config.data['panel']['alignY'] == COMPONENT_ALIGN.CENTER:
            y = self.screenFix(yMo, config.data['panel']['y'], config.data['panel']['height'], 0)
        if y is not None:
            if y != int(config.data['panel']['y']):
                config.data['panel']['y'] = y
                self.data[COMPONENT_TYPE.PANEL]['y'] = y
        config.apply(config.data)
        self.updateObject(COMPONENT_TYPE.PANEL, self.data[COMPONENT_TYPE.PANEL])


class InsigniaMonitor(object):
    def __init__(self):
        self.insignia = {
            'scout': {
                'status'         : False,
                'available'      : True,
                'panelSuccess'   : 0,
                'panelConditions': 0,
                'conditions'     : {'minDetections': [9, 0, 5]},
            },
        }
        self.insigniaTest = ['scout', 'warrior']

    def checkArenaType(self):
        return BigWorld.player().arena.bonusType not in ARENA_BONUS_TYPE.RANDOM_RANGE

    def startBattle(self):
        self.insignia.clear()
        arena = BigWorld.player().arena
        if self.checkArenaType(): return
        ACHIEVEMENT = ACHIEVEMENT_CONDITIONS if arena.bonusType == ARENA_BONUS_TYPE.REGULAR else ACHIEVEMENT_CONDITIONS_EXT
        for name in ACHIEVEMENT:
            if name not in self.insigniaTest:
                continue
            conditions = self.getAchievementCondition(arena.bonusType, name)
            if conditions:
                self.insignia[name] = {
                    'status'         : False,
                    'available'      : True,
                    'panelSuccess'   : 0,
                    'panelConditions': 0,
                    'conditions'     : conditions
                }

    def stopBattle(self):
        self.insignia.clear()

    def getAchievementCondition(self, arenaBonusType, medal):
        if arenaBonusType == ARENA_BONUS_TYPE.EPIC_RANDOM:
            return copy.deepcopy(ACHIEVEMENT_CONDITIONS_EXT[medal]) if medal in ACHIEVEMENT_CONDITIONS_EXT else {}
        if arenaBonusType == ARENA_BONUS_TYPE.REGULAR:
            return copy.deepcopy(ACHIEVEMENT_CONDITIONS[medal]) if medal in ACHIEVEMENT_CONDITIONS else {}
        return {}

    def getConditions(self, insignia):
        if insignia in self.insignia:
            if self.insignia[insignia]['available']:
                return self.insignia[insignia]['conditions']
        return {}

    def getCondition(self, insignia, name):
        conditions = self.getConditions(insignia)
        if name in conditions:
            return conditions[name][1]
        return

    def setCondition(self, insignia, name, value):
        conditions = self.getConditions(insignia)
        if name in conditions:
            conditions[name][1] = value
            if self.insignia[insignia]['available']:
                self.insigniaStatus(insignia, conditions)

    def insigniaStatus(self, insignia, conditions):
        count = len(conditions)
        done = 0
        process = 0
        for cond in conditions:
            value, status, border = conditions[cond]
            if status >= value:
                done += 1
            if status >= border:
                process += 1
        if done >= count:
            self.insignia[insignia]['status'] = True
            flash.removeOnPanelConditions(self.insignia[insignia])
            return flash.sendToPanelSuccess(insignia, self.insignia[insignia])
        if process >= count:
            return flash.sendToPanelConditions(insignia, self.insignia[insignia])
        return flash.removeOnPanelConditions(self.insignia[insignia])

    def setNotAvailable(self, insignia):
        if insignia in self.insignia:
            if not self.insignia[insignia]['status']:
                self.insignia[insignia]['available'] = False
                return flash.removeOnPanelConditions(self.insignia[insignia])


class InsigniaEngine(object):
    def __init__(self):
        self.result = {}

    def startBattle(self):
        insigniaMonitor.startBattle()
        self.result.clear()
        player = BigWorld.player()
        vehicles = player.arena.vehicles
        myTeam = player.team
        enemy = []
        for vehicle in vehicles:
            if vehicles[vehicle]['team'] != myTeam:
                enemy.append(vehicle)
        self.result['Detections'] = enemy

    def stopBattle(self):
        insigniaMonitor.stopBattle()
        self.result.clear()

    def onBattleEvents(self, events):
        if insigniaMonitor.checkArenaType(): return
        for data in events:
            feedbackEvent = feedback_events.PlayerFeedbackEvent.fromDict(data)
            eventID = feedbackEvent.getBattleEventType()
            if eventID == BATTLE_EVENT_TYPE.SPOTTED:
                insigniaEngine.insigniaScout()
            if eventID == BATTLE_EVENT_TYPE.KILL:
                insigniaEngine.insigniaWarrior()

    def insigniaScout(self, test = False):
        if 'scout' in insigniaMonitor.insignia:
            battle = inject.g_appLoader().getDefBattleApp()
            if battle is not None:
                comp = battle.containerManager.getContainer(ViewTypes.VIEW).getView()
                if comp is not None:
                    # noinspection PyProtectedMember
                    entries = comp.components['minimap'].getPlugin('vehicles')._entries
                    for vehicleID in entries:
                        if entries[vehicleID].isEnemy() and entries[vehicleID].isActive():
                            if vehicleID in self.result['Detections']:
                                self.result['Detections'].remove(vehicleID)
                    value = insigniaMonitor.getCondition('scout', 'minDetections')
                    if value is None: return
                    if 9 - len(self.result['Detections']) - value < 1:
                        if not test:
                            value += 1
                    else:
                        if value < 9:
                            insigniaMonitor.setNotAvailable('scout')
                            return
                    insigniaMonitor.setCondition('scout', 'minDetections', value)

    def insigniaWarrior(self):
        if 'warrior' in insigniaMonitor.insignia:
            value = insigniaMonitor.getCondition('warrior', 'minFrags')
            if value is None: return
            value += 1
            insigniaMonitor.setCondition('warrior', 'minFrags', value)


config = Config()
flash = Flash()
insigniaMonitor = InsigniaMonitor()
insigniaEngine = InsigniaEngine()


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    flash.startBattle()
    insigniaEngine.startBattle()


@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
@inject.log
def hookDestroyGUI(func, *args):
    flash.stopBattle()
    insigniaEngine.stopBattle()
    func(*args)


@inject.hook(Vehicle, 'startVisual')
@inject.log
def hookVehicleStartVisual(func, *args):
    func(*args)
    insigniaEngine.insigniaScout(True)


@inject.hook(PlayerAvatar, 'onBattleEvents')
@inject.log
def onBattleEvents(func, *args):
    func(*args)
    insigniaEngine.onBattleEvents(args[1])


BigWorld.flashData = flash.data
BigWorld.flashSetVisible = flash.setVisible
BigWorld.flashSetText = flash.setText
