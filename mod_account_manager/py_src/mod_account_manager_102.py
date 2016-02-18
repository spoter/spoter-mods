# -*- coding: utf-8 -*-

import json, os, random

import BigWorld
import Keys

from ConnectionManager import CONNECTION_METHOD, connectionManager
from gui import InputHandler, DialogsInterface
from gui.app_loader import g_appLoader
from gui.Scaleform.framework import ViewTypes, ScopeTemplates, g_entitiesFactories, ViewSettings
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta, DIALOG_BUTTON_ID
from predefined_hosts import g_preDefinedHosts
import game



class UserAccounts:
    __accounts_manager = None
    def __init__(self):
        prefsFilePath = unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore')
        self.__accounts_manager = os.path.join(os.path.dirname(prefsFilePath), 'accounts.manager')
        if not os.path.isfile(self.__accounts_manager):
            self.accounts = []
            self.write_accounts()
        self.renew_accounts()

    def renew_accounts(self):
        try:
            with open(self.__accounts_manager, 'r') as f:
                filedata = f.read()
            filedata = BigWorld.wg_ucpdata(filedata)
            self.accounts = json.loads(filedata.decode('base64').decode('zlib'))
        except:
            self.accounts = []

    def write_accounts(self):
        data = BigWorld.wg_cpdata(json.dumps(self.accounts).encode('zlib').encode('base64'))
        with open(self.__accounts_manager, 'w') as f:
            f.write(data)


class RemoveConfirmDialogButtons():
    def getLabels(self):
        return [{'id':DIALOG_BUTTON_ID.SUBMIT,'label':'Удалить','focused':True},{'id':DIALOG_BUTTON_ID.CLOSE,'label':'Отмена','focused':False}]


class AccountsManager(AbstractWindowView):
    def __init__(self):
        AbstractWindowView.__init__(self)

    def py_log(self, text):
        print('[AccountsManager]: %s' % text)

    def py_getTranslate(self):
        return {
            'submit_l10n' : "<font color='#FFFF33'>Войти</font>",
            'edit_l10n' : "<font color='#9ACD32'>Изменить</font>",
            'delete_l10n' : "<font color='#FF4500'>Удалить</font>",
            'window_title_l10n' : 'Менеджер аккаунтов',
            'add_l10n' : 'Добавить'
        }

    def _populate(self):
        AbstractWindowView._populate(self)
        zdata = []
        clusters = g_preDefinedHosts.shortList()
        for account in BigWorld.wh_data.accounts:
            account['cluster'] = int(account['cluster'])
            if len(clusters)-1<account['cluster']:
                account['cluster'] = 0
            cluster_name = clusters[account['cluster']][1].split().pop()
            zdata.append({
                'id'      : account['id'],
                'user'    : account['title'],
                'cluster' : cluster_name
            })
        self.callToFlash(zdata)

    def callFromFlash(self, data):
        class Mobj:
            def __init__(self):
                pass

        BigWorld.wh_current = Mobj()
        BigWorld.wh_current.mode = 'add'
        if data.action == 'addAcc':
            loadWindow('AccountsManagerSubwindow')
            self.destroy()
            return

        elif data.action == 'edit':
            for account in BigWorld.wh_data.accounts:
                if str(account['id']) == str(data.id):
                    BigWorld.wh_current.accId = account['id']
                    BigWorld.wh_current.mode = 'edit'
                    BigWorld.wh_current.title = account['title']
                    BigWorld.wh_current.email = BigWorld.wg_ucpdata(account['email'])
                    BigWorld.wh_current.password = BigWorld.wg_ucpdata(account['password'])
                    BigWorld.wh_current.cluster = account['cluster']
                    loadWindow('AccountsManagerSubwindow')
                    self.destroy()
                    return

        elif data.action == 'delete':
            _buttons = RemoveConfirmDialogButtons()
            meta = SimpleDialogMeta(message='Подтвердите удаление аккаунта.', title='Удаление аккаунта.', buttons=_buttons)
            DialogsInterface.showDialog(meta, lambda result: onClickAction(result))
            def onClickAction(result):
                if result:
                    for q in xrange(len(BigWorld.wh_data.accounts)):
                        if str(BigWorld.wh_data.accounts[q]['id']) == str(data.id):
                            BigWorld.wh_data.accounts.pop(q)
                            BigWorld.wh_data.write_accounts()
                            BigWorld.wh_data.renew_accounts()
                            self.destroy()
                            loadWindow('AccountsManager')
                            return

        elif data.action == 'submit':
            for account in BigWorld.wh_data.accounts:
                if str(account['id']) == str(data.id):
                    params = {
                        'login'      : BigWorld.wg_ucpdata(account['email']),
                        'auth_method': CONNECTION_METHOD.BASIC,
                        'session'    : '0'
                    }
                    password = BigWorld.wg_ucpdata(account['password'])
                    clusters = g_preDefinedHosts.shortList()
                    account['cluster'] = int(account['cluster'])
                    if len(clusters)-1<account['cluster']:
                        account['cluster'] = 0
                    serverName = clusters[account['cluster']][0]
                    connectionManager.initiateConnection(params, password, serverName)
                    return

    def callToFlash(self, data):
        if self._isDAAPIInited():
            self.flashObject.as_callToFlash(data)

    @staticmethod
    def as_isModalS():
        return True

    def onWindowClose(self):
        self.destroy()

    def onModuleDispose(self):
        pass


class AccountsManagerSubwindow(AbstractWindowView):
    __clusters = []

    def __init__(self):
        for cluster in g_preDefinedHosts.shortList():
            self.__clusters.append({'label':cluster[1],'data':cluster[1]})
        AbstractWindowView.__init__(self)

    def py_log(self, text):
        print('[AccountsManagerSubwindow]: %s' % text)

    def py_get_clusters(self):
        return self.__clusters

    def py_getTranslate(self):
        return {
            'save_l10n' : 'Сохранить',
            'cancel_l10n' : '#settings:cancel_button',
            'server_l10n' : '#menu:login/server',
            'show_password_l10n' : 'Показать пароль',
            'password_l10n' : '#menu:login/password',
            'nick_l10n' : 'Ник:',
            'window_title_l10n' : 'Управление аккаунтом'
        }

    def _populate(self):
        AbstractWindowView._populate(self)
        zdata = {}
        adata = BigWorld.wh_current
        if BigWorld.wh_current.mode == 'edit':
            zdata['id'] = adata.accId
            zdata['mode'] = 'edit'
            zdata['title'] = adata.title
            zdata['email'] = adata.email
            zdata['password'] = adata.password
            zdata['cluster'] = int(adata.cluster)
            if len(self.__clusters)-1<zdata['cluster']:
                zdata['cluster'] = 0
        elif BigWorld.wh_current.mode == 'add':
            zdata['mode'] = 'add'
        self.callToFlash(zdata)

    def callFromFlash(self, data):
        curAccs = BigWorld.wh_data.accounts
        if data.mode == 'add':
            curAccs.append({
                'title'   : data.title,
                'cluster' : data.cluster,
                'email'   : BigWorld.wg_cpdata(data.email),
                'password': BigWorld.wg_cpdata(data.password),
                'id'      : random.randint(999999, 9999999999999L),
            })
        elif data.mode == 'edit':
            for c in curAccs:
                if str(c['id']) == str(data.accId):
                    c['title'] = data.title
                    c['cluster'] = data.cluster
                    c['email'] = BigWorld.wg_cpdata(data.email)
                    c['password'] = BigWorld.wg_cpdata(data.password)
                    break

        BigWorld.wh_data.accounts = curAccs
        BigWorld.wh_data.write_accounts()
        BigWorld.wh_data.renew_accounts()
        self.destroy()
        loadWindow('AccountsManager')

    def callToFlash(self, data):
        if self._isDAAPIInited() and data:
            self.flashObject.as_callToFlash(data)

    @staticmethod
    def as_isModalS():
        return True

    def onWindowClose(self):
        self.destroy()
        loadWindow('AccountsManager')


def loadWindow(alias):
    g_appLoader.getApp().loadView(alias, alias)


BigWorld.wh_data = UserAccounts()

_aManagerAlias = 'AccountsManager'
_aManagerSettings = ViewSettings(_aManagerAlias, AccountsManager, 'AccountsManager/AccountsManager.swf', ViewTypes.WINDOW, 'showAccountsManager', ScopeTemplates.DEFAULT_SCOPE)
g_entitiesFactories.addSettings(_aManagerSettings)

_aManagerSubAlias = 'AccountsManagerSubwindow'
_aManagerSubSettings = ViewSettings(_aManagerSubAlias, AccountsManagerSubwindow, 'AccountsManager/AccountsManagerWindow.swf', ViewTypes.WINDOW, 'showAccountsManagerSubwindow', ScopeTemplates.DEFAULT_SCOPE)
g_entitiesFactories.addSettings(_aManagerSubSettings)

def inject_handle_key_event(event):
    is_down, key, mods, is_repeat = game.convertKeyEvent(event)
    if mods == Keys.MODIFIER_CTRL and key == Keys.KEY_B and is_down:
        loadWindow(_aManagerAlias)

InputHandler.g_instance.onKeyDown += inject_handle_key_event
InputHandler.g_instance.onKeyUp += inject_handle_key_event




print '[LOAD_MOD]:  [account_manager_extended v1.02, by S0me0ne, reworked by spoter]'
