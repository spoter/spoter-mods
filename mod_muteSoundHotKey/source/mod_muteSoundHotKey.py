# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

import BigWorld
import Keys
from Avatar import PlayerAvatar
from account_helpers.settings_core import settings_constants
from gui import InputHandler
from helpers import getLanguageCode


class _Config(object):
    def __init__(self):
        self.ids = 'muteSoundHotKey'
        self.version = 'v1.01 (2022-02-16)'
        self.version_id = 101
        self.author = 'by spoter'
        self.dataDefault = {
            'version'                   : self.version_id,
            'enabled'                   : True,
            'showMessage'               : True,
            'restoreSoundAfterBattleEnd': True,
            'hotkey'                    : [Keys.KEY_F9]
        }
        self.i18n = {
            'version'                                   : self.version_id,
            'UI_description'                            : 'Mute Sound HotKey',
            'UI_setting_hotkey_text'                    : 'Hotkey',
            'UI_setting_showMessage_text'               : 'Show status message in battle',
            'UI_setting_restoreSoundAfterBattleEnd_text': 'Restore Sound after battle end',
            'UI_setting_soundMuted'                     : 'Game Sound ON',
            'UI_setting_soundRestored'                  : 'Game Sound OFF',
        }
        if 'ru' in '%s'.lower() % getLanguageCode():
            self.i18n.update({
                'UI_description'                            : 'Горячая клавиша отключения звуков в игре',
                'UI_setting_hotkey_text'                    : 'Горячая клавиша',
                'UI_setting_showMessage_text'               : 'Показывать сообщение в бою',
                'UI_setting_restoreSoundAfterBattleEnd_text': 'Восстанавливать звук после окончания текущего боя',
                'UI_setting_soundMuted'                     : 'Игровые Звуки ВКЛ',
                'UI_setting_soundRestored'                  : 'Игровые Звуки ВЫКЛ',
            })
        self.data, self.i18n = g_gui.register_data(self.ids, self.dataDefault, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print('[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author))

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [
                g_gui.optionCheckBox(*self.p__getI18nParam('showMessage')),
                g_gui.optionCheckBox(*self.p__getI18nParam('restoreSoundAfterBattleEnd')),
            ],
            'column2'        : [
                g_gui.optionButton(*self.p__getI18nParamButton('hotkey', 'F9')),
            ]
        }

    def p__getI18nParam(self, name):
        # return varName, value, defaultValue, text, tooltip, defaultValueText
        tooltip = 'UI_setting_%s_tooltip' % name
        tooltip = self.i18n[tooltip] if tooltip in self.i18n else ''
        defaultValueText = 'UI_setting_%s_default' % name
        defaultValueText = self.i18n[defaultValueText] if defaultValueText in self.i18n else '%s' % self.dataDefault[name]
        return name, self.data[name], self.dataDefault[name], self.i18n['UI_setting_%s_text' % name], tooltip, defaultValueText

    def p__getI18nParamButton(self, name, defaultValueText):
        params = self.p__getI18nParam(name)
        return params[:5] + (defaultValueText,)

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class Support(object):
    def __init__(self):
        self.masterVolume = 100.0
        self.mutedSound = False

    def startBattle(self):
        InputHandler.g_instance.onKeyDown += self.injectButton

    def endBattle(self):
        InputHandler.g_instance.onKeyDown -= self.injectButton
        if config.data['enabled'] and config.data['restoreSoundAfterBattleEnd'] and self.mutedSound:
            BigWorld.player().gunRotator.settingsCore.applySetting(settings_constants.SOUND.MASTER, self.masterVolume)

    def showStatusMessage(self):
        if config.data['enabled'] and config.data['showMessage']:
            message = config.i18n['UI_setting_soundMuted'] if self.mutedSound else config.i18n['UI_setting_soundRestored']
            color = '#84DE40' if self.mutedSound else '#FFA500'
            inject.message(message, color)

    @inject.log
    def injectButton(self, event):
        if g_gui.get_key(config.data['hotkey']) and event.isKeyDown():
            player = BigWorld.player()
            if not player or not config.data['enabled']:
                return
            if not self.mutedSound:
                self.masterVolume = player.gunRotator.settingsCore.getSetting(settings_constants.SOUND.MASTER)
                player.gunRotator.settingsCore.applySetting(settings_constants.SOUND.MASTER, 0.0)
            else:
                player.gunRotator.settingsCore.applySetting(settings_constants.SOUND.MASTER, self.masterVolume)
            self.showStatusMessage()
            self.mutedSound = not self.mutedSound


# start mod
config = _Config()
support = Support()


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    support.startBattle()


@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
@inject.log
def hookDestroyGUI(func, *args):
    support.endBattle()
    func(*args)
