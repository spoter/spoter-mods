# -*- coding: utf-8 -*-
import json
import os
import time
from hashlib import md5
import codecs
import traceback

import BigWorld

from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.app_loader import g_appLoader
from predefined_hosts import g_preDefinedHosts
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta, DIALOG_BUTTON_ID
from gui import DialogsInterface
from gui.login import g_loginManager
from helpers import getLanguageCode

SHOW_DEBUG = True

I18N = {
    'UI_settingDelete'             : 'Delete',
    'UI_settingCancel'             : 'Cancel',
    'UI_settingEnter'              : "<font color='#FFFF33' size='18'>Enter</font>",
    'UI_settingEdit'               : "<font color='#9ACD32' size='18'>Edit</font>",
    'UI_settingDeleteAccount'      : "<font color='#FF4500' size='18'>Delete</font>",
    'UI_settingAccountManager'     : 'Account manager',
    'UI_settingAdd'                : 'Add',
    'UI_settingAutoEnter'          : 'Auto Enter',
    'UI_settingAcceptDeleteAccount': 'Accept delete account',
    'UI_settingAccountDelete'      : 'Delete Account',
    'UI_settingSave'               : 'Save',
    'UI_settingServer'             : 'Server:',
    'UI_settingShowPassword'       : 'Show password',
    'UI_settingNick'               : 'Nick:',
    'UI_settingManageYourAccount'  : 'Manage Your account'
}

def log(*args):
    if SHOW_DEBUG:
        msg = 'DEBUG[account_manager]: '
        length = len(args)
        for text in args:
            length -= 1
            if length:
                msg += '%s, ' % text
            else:
                msg += '%s' % text
        print msg

def bite_ify(inputs):
    if inputs:
        if isinstance(inputs, dict):
            return {bite_ify(key): bite_ify(value) for key, value in inputs.iteritems()}
        elif isinstance(inputs, list):
            return [bite_ify(element) for element in inputs]
        elif isinstance(inputs, unicode):
            return inputs.encode('utf-8')
        else:
            return inputs
    return inputs

def _load_json(name, configOld, path, save=False):
    configNew = configOld
    if not os.path.exists(path):
        os.makedirs(path)
    newPath = '%s%s.json' % (path, name)
    if save:
        with codecs.open(newPath, 'w', encoding='utf-8-sig') as jsonFile:
            jsonFile.write('%s' % bite_ify(json.dumps(configOld, sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig', separators=(',', ': '))))
            jsonFile.close()
            configNew = configOld
    else:
        if os.path.isfile(newPath):
            try:
                with codecs.open(newPath, 'r', encoding='utf-8-sig') as jsonFile:
                    configNew = bite_ify(json.loads(jsonFile.read().decode('utf-8-sig')))
                    jsonFile.close()
            except Exception as e:
                log('[ERROR]:     %s' % e)
                traceback.print_exc()
        else:
            with codecs.open(newPath, 'w', encoding='utf-8-sig') as jsonFile:
                jsonFile.write('%s' % bite_ify(json.dumps(configOld, sort_keys=True, indent=4, ensure_ascii=False, encoding='utf-8-sig', separators=(',', ': '))))
                jsonFile.close()
                configNew = configOld
                log('[ERROR]:     [Not found config, create default: %s' % newPath)
    return configNew

I18N = _load_json('%s'.lower() % getLanguageCode(), I18N, './res_mods/configs/account_manager/i18n/')

class AM_MODES:
    ADD = 'add'
    EDIT = 'edit'
    DELETE = 'delete'

class Mobj: pass

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
        except StandardError:
            self.accounts = []

    def write_accounts(self):
        data = BigWorld.wg_cpdata(json.dumps(self.accounts).encode('zlib').encode('base64'))
        with open(self.__accounts_manager, 'w') as f:
            f.write(data)

class RemoveConfirmDialogButtons:
    def getLabels(self):
        return [{
            'id'     : DIALOG_BUTTON_ID.SUBMIT,
            'label'  : I18N['UI_settingDelete'],
            'focused': True
        }, {
            'id'     : DIALOG_BUTTON_ID.CLOSE,
            'label'  : I18N['UI_settingCancel'],
            'focused': False
        }]

class AccountsManager(AbstractWindowView):
    def __init__(self):
        AbstractWindowView.__init__(self)

    def py_log(self, text):
        print('[AccountsManager]: %s' % text)

    def py_setLoginDataById(self, id, form):
        for account in BigWorld.wh_data.accounts:
            if str(account['id']) != id:
                continue
            form.login.text = BigWorld.wg_ucpdata(account['email'])
            getattr(form, 'pass').text = BigWorld.wg_ucpdata(account['password'])
            form.server.selectedIndex = int(account['cluster'])
            form.submit.enabled = True
            g_loginManager.clearToken2Preference()
            self.destroy()

    def py_getTranslate(self):
        return {
            'submit_l10n'      : I18N['UI_settingEnter'],
            'edit_l10n'        : I18N['UI_settingEdit'],
            'delete_l10n'      : I18N['UI_settingDeleteAccount'],
            'window_title_l10n': I18N['UI_settingAccountManager'],
            'add_l10n'         : I18N['UI_settingAdd'],
            'auto_enter_l10n'  : I18N['UI_settingAutoEnter']
        }

    def _populate(self):
        AbstractWindowView._populate(self)
        zdata = []
        clusters = g_preDefinedHosts.shortList()
        for account in BigWorld.wh_data.accounts:
            account['cluster'] = int(account['cluster'])
            if len(clusters) - 1 < account['cluster']:
                account['cluster'] = 0
            cluster_name = clusters[account['cluster']][1].split().pop()
            zdata.append({
                'id'     : account['id'],
                'user'   : account['title'],
                'cluster': cluster_name
            })
        self.callToFlash(zdata)

    def py_openAddAccountWindow(self):
        BigWorld.wh_current = Mobj()
        BigWorld.wh_current.mode = 'add'
        loadWindow('AccountsManagerSubwindow')
        self.destroy()

    def callFromFlash(self, data):
        BigWorld.wh_current = Mobj()
        if data.action == AM_MODES.EDIT:
            for account in BigWorld.wh_data.accounts:
                if str(account['id']) != str(data.id):
                    continue
                BigWorld.wh_current.accId = account['id']
                BigWorld.wh_current.mode = data.action
                BigWorld.wh_current.title = account['title']
                BigWorld.wh_current.email = BigWorld.wg_ucpdata(account['email'])
                BigWorld.wh_current.password = BigWorld.wg_ucpdata(account['password'])
                BigWorld.wh_current.cluster = account['cluster']
                loadWindow('AccountsManagerSubwindow')
                self.destroy()
                return
        elif data.action == AM_MODES.DELETE:
            _buttons = RemoveConfirmDialogButtons()
            meta = SimpleDialogMeta(message=I18N['UI_settingAcceptDeleteAccount'], title=I18N['UI_settingAccountDelete'], buttons=_buttons)

            def onClickAction(result):
                if not result:
                    return
                for it in BigWorld.wh_data.accounts:
                    if str(it['id']) != str(data.id):
                        continue
                    BigWorld.wh_data.accounts.remove(it)
                    BigWorld.wh_data.write_accounts()
                    BigWorld.wh_data.renew_accounts()
                    self.destroy()
                    loadWindow('AccountsManager')
                    return

            DialogsInterface.showDialog(meta, onClickAction)

    def callToFlash(self, data):
        if self._isDAAPIInited():
            self.flashObject.as_callToFlash(data)

    def as_isModalS(self):
        return True

    def onWindowClose(self):
        self.destroy()

    def onModuleDispose(self):
        pass

class AccountsManagerSubwindow(AbstractWindowView):
    __clusters = []

    def __init__(self):
        if not self.__clusters:
            for cluster in g_preDefinedHosts.shortList():
                self.__clusters.append({
                    'label': cluster[1],
                    'data' : cluster[1]
                })
        AbstractWindowView.__init__(self)

    def py_log(self, text):
        print('[AccountsManagerSubwindow]: %s' % text)

    def py_get_clusters(self):
        return self.__clusters

    def py_getTranslate(self):
        return {
            'save_l10n'         : I18N['UI_settingSave'],
            'cancel_l10n'       : '#settings:cancel_button',
            'server_l10n'       : I18N['UI_settingServer'],
            'show_password_l10n': I18N['UI_settingShowPassword'],
            'password_l10n'     : '#menu:login/password',
            'nick_l10n'         : I18N['UI_settingNick'],
            'window_title_l10n' : I18N['UI_settingManageYourAccount']
        }

    def _populate(self):
        AbstractWindowView._populate(self)
        if not self._isDAAPIInited():
            return
        acc = BigWorld.wh_current
        if BigWorld.wh_current.mode == AM_MODES.EDIT:
            self.flashObject.as_setEditAccountData(acc.accId, acc.title, acc.email, acc.password, min(int(acc.cluster), len(self.__clusters) - 1))
        elif BigWorld.wh_current.mode == AM_MODES.ADD:
            self.flashObject.as_setAddAccount()

    def py_setAddAccount(self, title, email, password, cluster):
        BigWorld.wh_data.accounts.append({
            'title'   : title,
            'cluster' : cluster,
            'email'   : BigWorld.wg_cpdata(email),
            'password': BigWorld.wg_cpdata(password),
            'id'      : md5.new('id = %s' % time.time()).hexdigest(),
        })
        BigWorld.wh_data.write_accounts()
        BigWorld.wh_data.renew_accounts()
        self.destroy()
        loadWindow('AccountsManager')

    def py_setEditAccount(self, id, title, email, password, cluster):
        for it in BigWorld.wh_data.accounts:
            if str(it['id']) != str(id):
                continue
            it['title'] = title
            it['cluster'] = cluster
            it['email'] = BigWorld.wg_cpdata(email)
            it['password'] = BigWorld.wg_cpdata(password)
            break
        BigWorld.wh_data.write_accounts()
        BigWorld.wh_data.renew_accounts()
        self.destroy()
        loadWindow('AccountsManager')

    def as_isModalS(self):
        return True

    def onWindowClose(self):
        self.destroy()
        loadWindow('AccountsManager')

def loadWindow(alias):
    g_appLoader.getDefLobbyApp().loadView(alias)

def init():
    from gui.Scaleform.framework import ViewTypes, ScopeTemplates, g_entitiesFactories, ViewSettings
    BigWorld.wh_data = UserAccounts()
    g_entitiesFactories.addSettings(ViewSettings('AccountsManager', AccountsManager, 'AccountsManager/AccountsManager.swf', ViewTypes.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE))
    g_entitiesFactories.addSettings(ViewSettings('AccountsManagerSubwindow', AccountsManagerSubwindow, 'AccountsManager/AccountsManagerWindow.swf', ViewTypes.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE))

print '[LOAD_MOD]:  [account_manager v1.05, by S0me0ne, reworked by ShadowHunterRUS & spoter]'
