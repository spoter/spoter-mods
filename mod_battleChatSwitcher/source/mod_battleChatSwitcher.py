# -*- coding: utf-8 -*-
import Keys
# noinspection PyUnresolvedReferences
from gui import InputHandler
from gui.app_loader import g_appLoader
from gui.mods.mod_mods_gui import g_gui, inject
from account_helpers.settings_core import settings_constants
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency


class Config(object):
    def __init__(self):
        self.ids = 'battleChatSwitcher'
        self.version = 'v1.03 (2018-05-29)'
        self.version_id = 103
        self.author = 'by spoter'
        self.buttons = {
            'button': [Keys.KEY_Z, [Keys.KEY_LCONTROL, Keys.KEY_RCONTROL]]
        }
        self.data = {
            'version': self.version_id,
            'enabled': True,
            'button' : self.buttons['button'],
        }
        self.i18n = {
            'version'                  : self.version_id,
            'UI_description'           : 'Battle chat switcher',
            'UI_setting_button_text'   : 'Hot key: battle chat',
            'UI_setting_button_tooltip': '{HEADER}<font color="#FFD700">Info:</font>{/HEADER}{BODY}Fast disable or enable battle chat{/BODY}',
            'UI_message_chatOn'        : 'Chat: enable',
            'UI_message_chatOff'       : 'Chat: disable'
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_setting_button_text'],
                'tooltip'     : self.i18n['UI_setting_button_tooltip'],
                'value'       : self.data['button'],
                'defaultValue': self.buttons['button'],
                'varName'     : 'button'
            }
            ],
            'column2'        : []
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class BattleChatSwitcher(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        InputHandler.g_instance.onKeyDown += self.injectButton

    @inject.log
    def injectButton(self, event):
        if not config.data['enabled']: return
        if g_appLoader.getDefBattleApp():
            if g_gui.get_key(config.data['button']) and event.isKeyDown():
                status = not self.settingsCore.options.getSetting(settings_constants.GAME.DISABLE_BATTLE_CHAT).get()
                self.settingsCore.applySetting(settings_constants.GAME.DISABLE_BATTLE_CHAT, status)
                self.settingsCore.confirmChanges(self.settingsCore.applyStorages(restartApproved=False))
                inject.message(config.i18n['UI_message_chatOn'] if status else config.i18n['UI_message_chatOff'], '#FFA500' if status else '#84DE40')


config = Config()
battleChatSwitcher = BattleChatSwitcher()
