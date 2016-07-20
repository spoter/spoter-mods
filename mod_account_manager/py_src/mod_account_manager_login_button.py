# -*- coding: utf-8 -*-
from gui.Scaleform.framework import ViewTypes, ScopeTemplates, g_entitiesFactories, ViewSettings
from gui.Scaleform.framework.entities.View import View
from gui.app_loader import g_appLoader
from gui.shared import events, g_eventBus

import BigWorld

from gui.Scaleform.daapi.view.login.LoginView import LoginView
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView

class AccountsManagerButtonController(object):
    def __init__(self):
        self.isLobby = False
        self.flash = None

        loginPopulate = LoginView._populate
        lobbyPopulate = LobbyView._populate
        LoginView._populate = lambda baseClass: self.__hooked_loginPopulate(baseClass, loginPopulate)
        LobbyView._populate = lambda baseClass: self.__hooked_lobbyPopulate(baseClass, lobbyPopulate)

        g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, self.__onAppInitialized)

    def __onAppInitialized(self, *args):
        app = g_appLoader.getDefLobbyApp()
        if app is not None:
            BigWorld.callback(0.0, lambda: app.loadView('AccountsManagerLoginButton'))

    def __hooked_loginPopulate(self, baseClass, baseFunc):
        baseFunc(baseClass)
        self.isLobby = False
        if self.flash is not None:
            self.flash.processPopulate()

    def __hooked_lobbyPopulate(self, baseClass, baseFunc):
        baseFunc(baseClass)
        self.isLobby = True
        if self.flash is not None:
            self.flash.processPopulate()

class AccountsManagerLoginButton(View):
    def _populate(self):
        g_AccMngr.flash = self
        super(AccountsManagerLoginButton, self)._populate()
        self.processPopulate()

    def _dispose(self):
        super(AccountsManagerLoginButton, self)._dispose()

    def processPopulate(self):
        if self._isDAAPIInited():
            if g_AccMngr.isLobby:
                self.flashObject.as_populateLobby()
            else:
                self.flashObject.as_populateLogin()

    def py_log(self, text):
        print('[AccountsManagerLoginButton]: %s' % text)

    def py_openAccMngr(self):
        g_appLoader.getDefLobbyApp().loadView('AccountsManager')

    def py_getTranslate(self):
        return {
            'tooltip_l10n': 'Account manager'
        }

g_AccMngr = AccountsManagerButtonController()

g_entitiesFactories.addSettings(ViewSettings('AccountsManagerLoginButton', AccountsManagerLoginButton, 'AccountsManager/AccountsManagerLoginButton.swf', ViewTypes.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE))
