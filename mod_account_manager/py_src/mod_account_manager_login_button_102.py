# -*- coding: utf-8 -*-

import GUI
from gui.Scaleform.framework import ViewTypes, ScopeTemplates, g_entitiesFactories, ViewSettings
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractViewMeta import AbstractViewMeta
from gui.app_loader import g_appLoader
from gui.shared import events, g_eventBus

class AccountsManagerLoginButton(View, AbstractViewMeta):
    def py_log(self, text):
        print('[AccountsManagerLoginButton]: %s' % text)

    def _populate(self):
        super(AccountsManagerLoginButton, self)._populate()

    def _dispose(self):
        super(AccountsManagerLoginButton, self)._dispose()

    def py_openAccMngr(self):
        g_appLoader.getApp().loadView('AccountsManager', 'AccountsManager')

    def py_getTranslate(self):
        return {
            'tooltip_l10n' : 'Менеджер аккаунтов'
        }


_btnAlias = 'AccountsManagerLoginButton'
_aManagerLoginButtonSettings = ViewSettings(_btnAlias, AccountsManagerLoginButton, 'AccountsManager/AccountsManagerLoginButton.swf', ViewTypes.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE)
g_entitiesFactories.addSettings(_aManagerLoginButtonSettings)

g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, lambda *args : g_appLoader.getDefLobbyApp().loadView(_btnAlias))
