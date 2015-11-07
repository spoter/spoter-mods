# -*- coding: utf-8 -*-
import os
import json
import codecs
import weakref

import BigWorld
import ResMgr
from gui.Scaleform.Minimap import Minimap
from gui.battle_control import g_sessionProvider
import GUI
from gui import g_guiResetters
from gui.Scaleform.Flash import Flash
from gui.Scaleform.Battle import Battle
from gui import InputHandler
import game
import Keys

setup = {'MODIFIER': {'MODIFIER_NONE': 0, 'MODIFIER_SHIFT': 1, 'MODIFIER_CTRL': 2, 'MODIFIER_ALT': 4}}

text_form = 'В свете: <b>{spotted}</b><br/>Не засвечены: <b>{not_spotted}</b><br/>Потеряны: <b>{lost}</b><br/>Мертвы: <b>{dead}</b><br/>'


class Config(object):
    def __init__(self):
        self.data = {'enable': True, 'debug': True, 'spotted_flash': {}}
        self.data['spotted_flash']['text'] = {}
        self.data['spotted_flash']['background'] = {}
        self.data['spotted_flash']['shadow'] = {}
        self.data['spotted_flash']['text']['format'] = text_form
        self.data['spotted_flash']['text']['x'] = 285
        self.data['spotted_flash']['text']['y'] = 445
        self.data['spotted_flash']['text']['alignX'] = 'left'
        self.data['spotted_flash']['text']['alignY'] = 'top'
        self.data['spotted_flash']['text']['default_font'] = '$IMELanguageBar'
        self.data['spotted_flash']['text']['default_font_size'] = 14
        self.data['spotted_flash']['text']['default_font_colour'] = '#adff00'
        self.data['spotted_flash']['background']['enable'] = False
        self.data['spotted_flash']['background']['image'] = 'img://gui/maps/bg.png'
        self.data['spotted_flash']['background']['x'] = 284
        self.data['spotted_flash']['background']['y'] = 443
        self.data['spotted_flash']['background']['width'] = 110
        self.data['spotted_flash']['background']['height'] = 90
        self.data['spotted_flash']['background']['alpha'] = 80
        self.data['spotted_flash']['shadow']['enable'] = True
        self.data['spotted_flash']['shadow']['distanceShadow'] = 0
        self.data['spotted_flash']['shadow']['angleShadow'] = 0
        self.data['spotted_flash']['shadow']['colorShadow'] = '#000000'
        self.data['spotted_flash']['shadow']['alphaShadow'] = 60
        self.data['spotted_flash']['shadow']['sizeShadow'] = 40
        self.data['spotted_flash']['shadow']['strengthShadow'] = 1000
        new_config = self.load_json('rod_mod', self.data)
        self.data = new_config
        self.do_config()

    def byteify(self, input):
        if input:
            if isinstance(input, dict):
                return {self.byteify(key): self.byteify(value) for key, value in input.iteritems()}
            elif isinstance(input, list):
                return [self.byteify(element) for element in input]
            elif isinstance(input, unicode):
                return input.encode('utf-8')
            else:
                return input
        return input

    def load_json(self, name, config, save=False):
        res = ResMgr.openSection('../paths.xml')
        sb = res['Paths']
        vals = sb.values()[0:2]
        config_new = config
        for vl in vals:
            path = '%s/scripts/client/gui/mods/' % vl.asString
            if os.path.isdir(path):
                new_path = '%s%s.json' % (path, name)
                if save:
                    with codecs.open(new_path, 'w', encoding='utf-8-sig') as json_file:
                        data = json.dumps(config, sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig') #encoding='utf-8-sig'
                        json_file.write('%s' % self.byteify(data))
                        json_file.close()
                        config_new = config
                else:
                    if os.path.isfile(new_path):
                        try:
                            with codecs.open(new_path, 'r', encoding='utf-8-sig') as json_file:
                                data = json_file.read().decode('utf-8-sig')
                                config_new = self.byteify(json.loads(data)) #.decode('utf-8-sig')
                                json_file.close()
                        except Exception as e:
                            print 'ERROR: %s' % e

                    else:
                        #with open(new_path, 'w') as json_file:
                        with codecs.open(new_path, 'w', encoding='utf-8-sig') as json_file:
                            data = json.dumps(config, sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig') #encoding='utf-8-sig'
                            json_file.write('%s' % self.byteify(data))
                            json_file.close()
                            config_new = config
        return config_new

    def do_config(self):
        spotted._enable = self.data['enable']
        spotted._debug = self.data['debug']
        if spotted.spotted_flash:
            spotted.spotted_flash.data.set_text_config(self.data['spotted_flash']['text']['x'], self.data['spotted_flash']['text']['y'], self.data['spotted_flash']['text']['alignX'],
                self.data['spotted_flash']['text']['alignY'], self.data['spotted_flash']['text']['default_font'], self.data['spotted_flash']['text']['default_font_size'],
                self.data['spotted_flash']['text']['default_font_colour'])
            spotted.spotted_flash.data.set_background_config(self.data['spotted_flash']['background']['enable'], self.data['spotted_flash']['background']['image'],
                self.data['spotted_flash']['background']['x'], self.data['spotted_flash']['background']['y'], self.data['spotted_flash']['background']['width'],
                self.data['spotted_flash']['background']['height'], self.data['spotted_flash']['background']['alpha'])
            spotted.spotted_flash.data.set_shadow_config(self.data['spotted_flash']['shadow']['enable'], self.data['spotted_flash']['shadow']['distanceShadow'],
                self.data['spotted_flash']['shadow']['angleShadow'], self.data['spotted_flash']['shadow']['colorShadow'], self.data['spotted_flash']['shadow']['alphaShadow'],
                self.data['spotted_flash']['shadow']['sizeShadow'], self.data['spotted_flash']['shadow']['strengthShadow'])


class Spotted(object):
    def __init__(self):
        self._spotted_cache = {}
        self._enable = False
        self._debug = False
        self._dead_callback = None
        self.spotted_flash = None

    def cleanupBattleData(self):
        self._spotted_cache = {}
        if self._dead_callback:
            BigWorld.cancelCallback(self._dead_callback)
        self._dead_callback = None
        self._text = None

    def getSpottedStatus(self):
        not_spotted = 0
        dead = 0
        lost = 0
        spotted = 0
        for vID in self._spotted_cache:
            if self._spotted_cache[vID] == 'not_spotted':
                not_spotted += 1
            elif self._spotted_cache[vID] == 'dead':
                dead += 1
            elif self._spotted_cache[vID] == 'lost':
                lost += 1
            elif self._spotted_cache[vID] == 'spotted':
                spotted += 1
        return [not_spotted, spotted, lost, dead]

    def updateSpottedStatus(self, vID, spotted):
        player = BigWorld.player()
        arena = player.arena if hasattr(player, 'arena') else None
        if arena is None:
            return
        else:
            arenaVehicle = arena.vehicles[vID] if vID in arena.vehicles else None
            if arenaVehicle is None:
                return
            if vID in self._spotted_cache:
                if not arenaVehicle['isAlive']:
                    self._spotted_cache[vID] = 'dead'
                    return
                if spotted:
                    self._spotted_cache[vID] = 'spotted'
                    return
                self._spotted_cache[vID] = 'lost'
        return

    def veh_list(self):
        enemyTeamVehIDs = g_sessionProvider.getArenaDP().getVehiclesIDs(True)
        for vID in enemyTeamVehIDs:
            self._spotted_cache[vID] = 'not_spotted'

    def _dead_status(self):
        if hasattr(BigWorld.player(), 'arena'):
            arena = BigWorld.player().arena
            for vID in self._spotted_cache:
                if self._spotted_cache[vID] != 'dead':
                    arenaVehicle = arena.vehicles[vID] if vID in arena.vehicles else None
                    if arenaVehicle:
                        if not arenaVehicle['isAlive']:
                            self._spotted_cache[vID] = 'dead'
                    else:
                        arenaDP = g_sessionProvider.getArenaDP()
                        if not arenaDP.getVehicleInfo(vID).isAlive():
                            self._spotted_cache[vID] = 'dead'
        self.post_text(self.getSpottedStatus())
        self._dead_callback = BigWorld.callback(0.3, self._dead_status)

    def post_text(self, data):
        if self._enable and self.spotted_flash:
            format_str = {
                'not_spotted': '%s' % data[0], 'spotted': '%s' % data[1], 'lost': '%s' % data[2], 'dead': '%s' % data[3], }
            MSG_TMP = config.data['spotted_flash']['text']['format'].format(**format_str)
            self.spotted_flash.data.setText(MSG_TMP)


def hook_Minimap__addEntry(self, vInfo, guiProps, location, doMark):
    spotted.updateSpottedStatus(vInfo.vehicleID, True)
    spotted.post_text(spotted.getSpottedStatus())
    return hooked_addEntry(self, vInfo, guiProps, location, doMark)


def hook_Minimap__delEntry(self, vehicleID):
    spotted.updateSpottedStatus(vehicleID, False)
    spotted.post_text(spotted.getSpottedStatus())
    return hooked_delEntry(self, vehicleID)


def inject_startBattle():
    spotted.cleanupBattleData()
    spotted.veh_list()
    spotted._dead_status()


def inject_stopBattle():
    spotted.cleanupBattleData()


class TextFlash(Flash):
    def __init__(self, parentUI, flash_name):
        Flash.__init__(self, flash_name)
        self.parentUI = parentUI
        self.movie.backgroundAlpha = 0.0
        self.component.wg_inputKeyMode = 2
        self.component.position.z = 0.5
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.flashSize = GUI.screenResolution()
        self.text = {}
        self.shadow = {}
        self.background = {}

    def _start(self):
        self.active(True)
        self._visibleV(True)
        self.set_def_config()
        self._updatePos()

    def set_def_config(self):
        self.text['x'] = config.data['spotted_flash']['text']['x']
        self.text['y'] = config.data['spotted_flash']['text']['y']
        self.text['alignX'] = config.data['spotted_flash']['text']['alignX']
        self.text['alignY'] = config.data['spotted_flash']['text']['alignY']
        self.text['default_font'] = config.data['spotted_flash']['text']['default_font']
        self.text['default_font_size'] = config.data['spotted_flash']['text']['default_font_size']
        self.text['default_font_colour'] = config.data['spotted_flash']['text']['default_font_colour']
        self.background['enable'] = config.data['spotted_flash']['background']['enable']
        self.background['image'] = config.data['spotted_flash']['background']['image']
        self.background['x'] = config.data['spotted_flash']['background']['x']
        self.background['y'] = config.data['spotted_flash']['background']['y']
        self.background['width'] = config.data['spotted_flash']['background']['width']
        self.background['height'] = config.data['spotted_flash']['background']['height']
        self.background['alpha'] = config.data['spotted_flash']['background']['alpha']
        self.shadow['enable'] = config.data['spotted_flash']['shadow']['enable']
        self.shadow['distanceShadow'] = config.data['spotted_flash']['shadow']['distanceShadow']
        self.shadow['angleShadow'] = config.data['spotted_flash']['shadow']['angleShadow']
        self.shadow['colorShadow'] = config.data['spotted_flash']['shadow']['colorShadow']
        self.shadow['alphaShadow'] = config.data['spotted_flash']['shadow']['alphaShadow']
        self.shadow['sizeShadow'] = config.data['spotted_flash']['shadow']['sizeShadow']
        self.shadow['strengthShadow'] = config.data['spotted_flash']['shadow']['strengthShadow']

    def set_text_config(self, x=None, y=None, alignX=None, alignY=None, default_font=None, default_font_size=None, default_font_colour=None):
        if x: self.text['x'] = int(x)
        if y: self.text['y'] = int(y)
        if alignX: self.text['alignX'] = '%s' % alignX
        if alignY: self.text['alignY'] = '%s' % alignY
        if default_font: self.text['default_font'] = '%s' % default_font
        if default_font_size: self.text['default_font_size'] = int(default_font_size)
        if default_font_colour: self.text['default_font_colour'] = '%s' % default_font_colour

    def set_background_config(self, enable=None, image=None, x=None, y=None, width=None, height=None, alpha=None):
        if enable: self.background['enable'] = enable
        if image: self.background['image'] = '%s' % image
        if x: self.background['x'] = int(x)
        if y: self.background['y'] = int(y)
        if width: self.background['width'] = int(width)
        if height: self.background['height'] = int(height)
        if alpha: self.background['alpha'] = int(alpha)

    def set_shadow_config(self, enable=None, distanceShadow=None, angleShadow=None, colorShadow=None, alphaShadow=None, sizeShadow=None, strengthShadow=None):
        if enable: self.shadow['enable'] = enable
        if distanceShadow: self.shadow['distanceShadow'] = int(distanceShadow)
        if angleShadow: self.shadow['angleShadow'] = int(angleShadow)
        if colorShadow: self.shadow['colorShadow'] = '%s' % colorShadow
        if alphaShadow: self.shadow['alphaShadow'] = int(alphaShadow)
        if sizeShadow: self.shadow['sizeShadow'] = int(sizeShadow)
        if strengthShadow: self.shadow['strengthShadow'] = int(strengthShadow)

    def _destroy(self):
        self.close()

    def _visibleV(self, bool):
        self.isVisible = bool
        self.component.visible = bool

    def _visibleTAB(self, event):
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if not isRepeat and key == 15:
            bool = not isDown if self.isVisible else False
            self.component.visible = bool

    def _updatePosDebug(self, modX, modY):
        self.text['x'] += modX
        self.text['y'] += modY
        self.background['x'] += modX
        self.background['y'] += modY

    def _updatePos(self):
        screenGUI = GUI.screenResolution()
        screenX = {'left': 0, 'center': screenGUI[0] / 2, 'right': screenGUI[0]}
        screenY = {'top': 0, 'center': screenGUI[1] / 2, 'bottom': screenGUI[1]}
        if self.text['x'] + 10 > screenGUI[0]: self.text['x'] = screenGUI[0] - 10
        if self.text['y'] + 10 > screenGUI[1]: self.text['y'] = screenGUI[1] - 10
        x = self.text['x']
        y = self.text['y']
        alignX = self.text['alignX']
        alignY = self.text['alignY']
        elemX = x + screenX.get(alignX, 0)
        elemY = y + screenY.get(alignY, 0)
        self.setPosition(elemX, elemY)
        if self.background['x'] + 10 > screenGUI[0]: self.background['x'] = screenGUI[0] - 10
        if self.background['y'] + 10 > screenGUI[1]: self.background['y'] = screenGUI[1] - 10
        if self.background['enable']:
            self.setBG(self.background['image'], self.background['x'], self.background['y'], self.background['width'], self.background['height'], self.background['alpha'])
        else:
            self.setBG(None, 0, 0, 0, 0, 0)
        config.data['spotted_flash']['text']['x'] = self.text['x']
        config.data['spotted_flash']['text']['y'] = self.text['y']
        config.data['spotted_flash']['background']['x'] = self.background['x']
        config.data['spotted_flash']['background']['y'] = self.background['y']

    def setPosition(self, posX, posY):
        self.flashCall('setPosition', [posX, posY])

    def setVisible(self, bool):
        self.flashCall('setVisible', [bool])

    def setAlpha(self, alpha):
        self.flashCall('setAlpha', [alpha])

    def setShadow(self, distanceShadow, angleShadow, colorShadow, alphaShadow, sizeShadow, strengthShadow):
        self.flashCall('setShadow', [distanceShadow, angleShadow, colorShadow, alphaShadow, sizeShadow, strengthShadow])

    def setBG(self, imageBG, XposBG, YposBG, widthBG, heightBG, alphaBG):
        self.flashCall('setBG', [imageBG, XposBG, YposBG, widthBG, heightBG, alphaBG])

    def setTextFlash(self, text):
        text = '<font size="%s" face="%s" color="%s" >%s</font>' % (self.text['default_font_size'], self.text['default_font'], self.text['default_font_colour'], text)
        self.flashCall('setText', [text])

    def setText(self, text):
        self.setTextFlash(text)
        if self.shadow['enable']:
            self.setShadow(self.shadow['distanceShadow'], self.shadow['angleShadow'], self.shadow['colorShadow'], self.shadow['alphaShadow'], self.shadow['sizeShadow'], self.shadow['strengthShadow'])
        else:
            self.setShadow(0, 0, '#000000', 0, 0, 0)

    def flashCall(self, funcName, args=None):
        self.call('TextFlash.' + funcName, args)


class Custom_Flash(object):
    def __init__(self, flash_name):
        self.data = TextFlash(weakref.proxy(self), flash_name)


def new_showAll(selfBattle, orig_showAll, isShow):
    orig_showAll(selfBattle, isShow)
    if spotted._enable:
        if spotted.spotted_flash is None: return
        spotted.spotted_flash.data._visibleV(isShow)


def new_afterCreate(self):
    orig_afterCreate(self)
    if spotted._enable:
        spotted.spotted_flash = Custom_Flash('spotted_count.swf')
        spotted.spotted_flash.data._start()
        g_guiResetters.add(spotted.spotted_flash.data._updatePos)
        config.do_config()
        inject_startBattle()


def new_beforeDelete(self):
    orig_beforeDelete(self)
    if spotted._enable:
        if spotted.spotted_flash is None: return
        spotted.spotted_flash.data._destroy()
        g_guiResetters.discard(spotted.spotted_flash.data._updatePos)
        spotted.spotted_flash.data = None
        spotted.spotted_flash = None
    inject_stopBattle()


def newhandleKeyEvent1(event):
    if spotted._enable:
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if spotted._debug and spotted.spotted_flash:
            if key == Keys.KEY_NUMPAD6 and isDown and mods == setup['MODIFIER']['MODIFIER_ALT']:
                spotted.spotted_flash.data._updatePosDebug(10, 0)
                spotted.spotted_flash.data._updatePos()
                __save_config_debug()
                print 'position change x +10'
            if key == Keys.KEY_NUMPAD4 and isDown and mods == setup['MODIFIER']['MODIFIER_ALT']:
                spotted.spotted_flash.data._updatePosDebug(-10, 0)
                spotted.spotted_flash.data._updatePos()
                __save_config_debug()
                print 'position change x -10'
            if key == Keys.KEY_NUMPAD8 and isDown and mods == setup['MODIFIER']['MODIFIER_ALT']:
                spotted.spotted_flash.data._updatePosDebug(0, -10)
                spotted.spotted_flash.data._updatePos()
                __save_config_debug()
                print 'position change y -10'
            if key == Keys.KEY_NUMPAD2 and isDown and mods == setup['MODIFIER']['MODIFIER_ALT']:
                spotted.spotted_flash.data._updatePosDebug(0, 10)
                spotted.spotted_flash.data._updatePos()
                __save_config_debug()
                print 'position change y +10'
            if key == Keys.KEY_NUMPADMINUS and isDown and mods == setup['MODIFIER']['MODIFIER_ALT']:
                __load_config_debug()
                spotted.spotted_flash.data._updatePos()
                print 'config reloaded'


def __save_config_debug():
    new_config = config.load_json('rod_mod', config.data, True)
    config.data = new_config
    config.do_config()


def __load_config_debug():
    new_config = config.load_json('rod_mod', config.data)
    config.data = new_config
    config.do_config()


#init
spotted = Spotted()
config = Config()

#hooked
hooked_addEntry = Minimap._Minimap__addEntry
hooked_delEntry = Minimap._Minimap__delEntry
orig_showAll = Battle.showAll
orig_afterCreate = Battle.afterCreate
orig_beforeDelete = Battle.beforeDelete

#hook
Minimap._Minimap__addEntry = hook_Minimap__addEntry
Minimap._Minimap__delEntry = hook_Minimap__delEntry
Battle.showAll = lambda selfBattle, isShow: new_showAll(selfBattle, orig_showAll, isShow)
Battle.afterCreate = new_afterCreate
Battle.beforeDelete = new_beforeDelete

#Inject
InputHandler.g_instance.onKeyDown += newhandleKeyEvent1
InputHandler.g_instance.onKeyUp += newhandleKeyEvent1

#settings
