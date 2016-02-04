# -*- coding: utf-8 -*-
#Embedded file name: E:/tmpshit/py27/scripts\account_manager.py
import codecs
import json
import os
import random

import BigWorld
import Keys

import game
from ConnectionManager import CONNECTION_METHOD
from ConnectionManager import connectionManager
from gui import InputHandler
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.framework import ViewTypes, ScopeTemplates
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.app_loader import g_appLoader
from gui.shared import g_itemsCache
from predefined_hosts import g_preDefinedHosts


class UserAccounts:
    def __init__(self):
        if not os.path.isfile('./res_mods/accounts.manager'):
            self.accounts = []
            self.write_accounts()
        self.renew_accounts()

    def renew_accounts(self):
        with codecs.open('./res_mods/accounts.manager', 'r', encoding='utf-8-sig') as f:
            filedata = f.read()
        try:
            self.accounts = json.loads(filedata)
        except Exception as e:
            self.accounts = []
            print e

    def write_accounts(self):
        data = json.dumps(self.accounts)
        f = codecs.open('./res_mods/accounts.manager', 'w', encoding='utf-8-sig')
        f.write(data)
        f.close()


class AccountsManager(AbstractWindowView):
    def __init__(self):
        AbstractWindowView.__init__(self)

        def fuckincheck():
            if hasattr(BigWorld, 'renewAccsManager'):
                if BigWorld.renewAccsManager:
                    BigWorld.renewAccsManager = False
                    self.destroy()
                    loadWindow('AccountsManager')
            BigWorld.callback(0.2, lambda: fuckincheck())

        fuckincheck()

    def _populate(self):
        zdata = {}
        for z in BigWorld.wh_data.accounts:
            account = z
            cur = {
                'time'    : str(random.randint(10, 22)) + ':' + str(random.randint(10, 60)),
                'id'      : account['id'],
                'mode'    : 'edit',
                'silver'  : str(account['silver']),
                'gold'    : str(account['gold']),
                'user'    : account['title'],
                'cluster' : 'RU' + str(account['cluster'] + 1),
                'email'   : account['email'],
                'password': BigWorld.wg_ucpdata(account['password'])
            }
            zdata[len(zdata)] = cur

        AbstractWindowView._populate(self)
        self.callToFlash(zdata)

    def callFromFlash(self, data):
        class Mobj:
            def __init__(self):
                pass

        BigWorld.wh_current = Mobj()
        BigWorld.wh_current.mode = 'add'
        BigWorld.wh_current.submitLabel = 'Добавить'
        BigWorld.wh_current.cancelLabel = 'Отменить'
        if data.action == 'addAcc':
            loadWindow('AccountsManagerSubwindow')
            return
        if data.action == 'edit' and BigWorld.isKeyDown(Keys.KEY_LCONTROL):
            for q in BigWorld.wh_data.accounts:
                account = q
                if account['id'] == data.id:
                    BigWorld.wh_current.accId = account['id']
                    BigWorld.wh_current.mode = 'edit'
                    BigWorld.wh_current.submitLabel = 'Сохранить'
                    BigWorld.wh_current.cancelLabel = 'Удалить'
                    BigWorld.wh_current.title = account['title']
                    BigWorld.wh_current.email = account['email']
                    BigWorld.wh_current.password = BigWorld.wg_ucpdata(account['password'])
                    BigWorld.wh_current.cluster = account['cluster']
                    loadWindow('AccountsManagerSubwindow')
                    return
        if data.action == 'edit' and BigWorld.isKeyDown(Keys.KEY_LALT):
            for q in xrange(len(BigWorld.wh_data.accounts)):
                if BigWorld.wh_data.accounts[q]['id'] == data.id:
                    BigWorld.wh_data.accounts.pop(q)
                    BigWorld.wh_data.write_accounts()
                    BigWorld.wh_data.renew_accounts()
                    self.destroy()
                    loadWindow('AccountsManager')
                    return

        if data.action == 'login' or data.action == 'edit':
            for q in BigWorld.wh_data.accounts:
                account = q
                if account['id'] == data.id:
                    params = {
                        'login'      : account['email'],
                        'auth_method': CONNECTION_METHOD.BASIC,
                        'session'    : '0'
                    }
                    password = BigWorld.wg_ucpdata(account['password'])
                    serverName = g_preDefinedHosts.shortList()[int(account['cluster']) + 1][0]
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
    def __init__(self):
        AbstractWindowView.__init__(self)

    def _populate(self):
        zdata = None
        adata = BigWorld.wh_current
        if BigWorld.wh_current.mode == 'edit':
            zdata = {
                'id'            : adata.accId,
                'mode'          : 'edit',
                'submitBtnLabel': adata.submitLabel,
                'cancelBtnLabel': adata.cancelLabel,
                'title'         : adata.title,
                'email'         : adata.email,
                'password'      : adata.password,
                'cluster'       : adata.cluster
            }
        elif BigWorld.wh_current.mode == 'add':
            zdata = {
                'mode': 'add'
            }
        AbstractWindowView._populate(self)
        self.callToFlash(zdata)

    def callFromFlash(self, data):
        curAccs = BigWorld.wh_data.accounts
        if data.mode == 'add':
            accData = {
                'title'   : data.title,
                'cluster' : data.cluster,
                'email'   : data.email,
                'password': BigWorld.wg_cpdata(data.password),
                'id'      : random.randint(999999, 9999999999999L),
                'gold'    : 0,
                'silver'  : 0
            }
            curAccs.append(accData)
        elif data.mode == 'edit':
            for c in curAccs:
                if c['id'] == int(data.accId):
                    c['password'] = BigWorld.wg_cpdata(data.password)
                    c['title'] = data.title
                    c['email'] = data.email
                    c['cluster'] = data.cluster
                    break

        BigWorld.wh_data.accounts = curAccs
        BigWorld.wh_data.write_accounts()
        BigWorld.wh_data.renew_accounts()
        BigWorld.renewAccsManager = True
        self.destroy()

    def callToFlash(self, data):
        if self._isDAAPIInited() and data:
            self.flashObject.as_callToFlash(data)

    @staticmethod
    def as_isModalS():
        return True

    def onWindowClose(self):
        self.destroy()


def loadWindow(alias):
    g_appLoader.getApp().loadView(alias, alias)


def sGatherData():
    if hasattr(BigWorld, 'player'):
        if hasattr(BigWorld.player(), 'name'):
            if len(BigWorld.player().name) > 0 and not hasattr(BigWorld.player(), 'arena'):
                credit, gold = g_itemsCache.items.stats.money
                for q in BigWorld.wh_data.accounts:
                    if q['email'].lower() == str(connectionManager.loginName.lower()):
                        if gold != q['gold']:
                            q['gold'] = gold
                        if credit != q['silver']:
                            q['silver'] = credit
                        player = BigWorld.player()
                        if hasattr(player, 'databaseID'):
                            playerID = player.databaseID
                        else:
                            playerID = player.arena.vehicles[player.playerVehicleID]['accountDBID']
                        if playerID != q['id']:
                            q['id'] = playerID
                        break
                BigWorld.wh_data.write_accounts()
                BigWorld.wh_data.renew_accounts()


BigWorld.wh_data = UserAccounts()

_aManagerAlias = 'AccountsManager'
_aManagerSettings = ViewSettings(_aManagerAlias, AccountsManager, 'AccountsManager.swf', ViewTypes.WINDOW, 'showAccountsManager', ScopeTemplates.DEFAULT_SCOPE)
g_entitiesFactories.addSettings(_aManagerSettings)

_aManagerSubAlias = 'AccountsManagerSubwindow'
_aManagerSubSettings = ViewSettings(_aManagerSubAlias, AccountsManagerSubwindow, 'AccountsManagerWindow.swf', ViewTypes.WINDOW, 'showAccountsManagerSubwindow', ScopeTemplates.DEFAULT_SCOPE)
g_entitiesFactories.addSettings(_aManagerSubSettings)


def inject_handle_key_event(event):
    is_down, key, mods, is_repeat = game.convertKeyEvent(event)
    if mods == Keys.MODIFIER_CTRL and key == Keys.KEY_B and is_down:
        loadWindow(_aManagerAlias)


# noinspection PyProtectedMember
hooked_update_all = Hangar._Hangar__updateAll

def hook_update_all(*args):
    hooked_update_all(*args)
    try:
        sGatherData()
    except Exception as e:
        print('account manager hook_update_all', e)


InputHandler.g_instance.onKeyDown += inject_handle_key_event
InputHandler.g_instance.onKeyUp += inject_handle_key_event

Hangar._Hangar__updateAll = hook_update_all

print '[LOAD_MOD]:  [account_manager_extended v1.01, by S0me0ne, reworked by spoter]'