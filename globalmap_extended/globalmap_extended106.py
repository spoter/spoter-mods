# -*- coding: utf-8 -*-
import BigWorld, ResMgr
from urllib import urlopen
import json
import time
import datetime
from Account import Account
from gui.Scaleform.daapi.view.lobby.hangar import Hangar
from notification.NotificationListView import NotificationListView
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, ConfirmDialogButtons,SimpleDialogMeta
import os
from adisp import async, process
from gui.Scaleform.framework import ViewTypes, AppRef
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from functools import partial
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared import events
from gui import game_control
from constants import AUTH_REALM
import random
import glob

BigWorld.module_globalmap_extended = True
BigWorld.globalmap_extended ={
    'EM': False,
    'browserID': None,
    'callback': None,
    'windowssize_x': 1020, 
    'windowssize_y': 580,
    'btn_count1': 0,
    'btn_count2': 0,
    'GK_on': True,
    'Btn_GM': 'G.Map',
    'GK_site': 'http://worldoftanks.ru/clanwars/maps/globalmap/',
    'Btn_Yandex': 'Yandex',
    'Yandex_on': False,
    'Btn_Google': 'Google',
    'Google_on': False,
    'Btn_Other1': 'RU WG Forum',
    'Site_Other1': 'http://forum.worldoftanks.ru/index.php?/forum/174-',
    'Other1': False,
    'Btn_Other2': 'RU Koreanrandom',
    'Site_Other2': 'http://www.koreanrandom.com/forum/forum/44-',
    'Other2': False,
    'Btn_Other3': 'RU Expromt-Max Team',
    'Site_Other3': 'http://expromt-max.ru/forum/spoter/',
    'Other3': False,
    'Btn_Other4': 'NA Roughnecks Mods',
    'Site_Other4': 'http://roughnecksxvmmods.ipbhost.com/index.php?/forum/113-',
    'Other4': False,
    'Btn_Other5': 'NA WG Forum',
    'Site_Other5': 'http://forum.worldoftanks.com/index.php?/forum/189-',
    'Other5': False,    
    'Btn_Other6': 'EU WG Forum',
    'Site_Other6': 'http://forum.worldoftanks.eu/index.php?/topic/432069-',
    'Other6': False,
    'Btn_Other7': 'RU LJ world-of-tanks',
    'Site_Other7': 'http://world-of-tanks.livejournal.com/',
    'Other7': False,
    'Btn_Other8': 'RU LJ world-of-ru',
    'Site_Other8': 'http://world-of-ru.livejournal.com/',
    'Other8': False,    
    'config': ResMgr.openSection('scripts/client/mods/globalmap_extended.xml', True)
    }
BigWorld.globalmap_extended['RU'] = True if AUTH_REALM == 'RU' else False


def get_server():
    server = 'null'
    if AUTH_REALM == 'RU':
        server = 'ru'
    elif AUTH_REALM == 'EU':
        server = 'eu'
    elif AUTH_REALM == 'NA':
        server = 'com'
    elif AUTH_REALM == 'ASIA':
        server = 'asia'
    elif AUTH_REALM == 'KR':
        server = 'kr'
    return {'server': server}

if get_server()['server'] == 'ru':
    BigWorld.globalmap_extended['GK_site'] = 'http://worldoftanks.ru/clanwars/maps/globalmap/'

if get_server()['server'] == 'eu':
    BigWorld.globalmap_extended['GK_site'] = 'http://worldoftanks.eu/clanwars/maps/globalmap/'

if get_server()['server'] == 'com':
    BigWorld.globalmap_extended['GK_site'] = 'http://worldoftanks.com/clanwars/maps/globalmap/'

if get_server()['server'] == 'asia':
    BigWorld.globalmap_extended['GK_site'] = 'http://worldoftanks.asia/en/content/clanwars_guide/'

if get_server()['server'] == 'kr':
    BigWorld.globalmap_extended['GK_site'] = 'http://worldoftanks.asia/en/content/clanwars_guide/'

NotificationPopulate_announcer_old = NotificationListView._populate
NotificationOnClickAction_announcer_old = NotificationListView.onClickAction
oldUpdateAll = Hangar._Hangar__updateAll
#
description = 'globalmap_extended.pyc'
author = 'by spoter'
version = 'v1.06(31.05.2015)'
debug_opt = False
if BigWorld.globalmap_extended['RU']:
    description = 'Мод: "Закладочка"'
    author = 'автор: spoter'

def codepa(text):
    try:
        return text.encode('windows-1251')
    except:
        return text
sys_mes = {}
sys_mes['DEBUG'] = '[DEBUG]' #if BigWorld.globalmap_extended['RU'] else 'ОТЛАДКА'
sys_mes['LOAD_MOD'] = codepa('[ЗАГРУЗКА]:  ') if BigWorld.globalmap_extended['RU'] else '[LOAD_MOD]:  '
sys_mes['INFO'] = codepa('[ИНФО]:      ') if BigWorld.globalmap_extended['RU'] else '[INFO]:     '
sys_mes['ERROR'] = codepa('[ОШИБКА]:    ') if BigWorld.globalmap_extended['RU'] else '[ERROR]:     '
sys_mes['MSG_RECREATE_XML'] = codepa('XML конфиг не найден, создаем заново') if BigWorld.globalmap_extended['RU'] else 'XML not found, recreating'
sys_mes['MSG_RECREATE_XML_DONE'] = codepa('XML конфиг создан УСПЕШНО') if BigWorld.globalmap_extended['RU'] else 'XML recreating DONE'
sys_mes['MSG_INIT'] = codepa('применение настроек...') if BigWorld.globalmap_extended['RU'] else 'initialized ...'
sys_mes['MSG_DEACTIVATED'] = codepa('Обнаружены конфликты с компонентами из модпака protanki, %s деактивируется...') %codepa(description) if BigWorld.globalmap_extended['RU'] else 'Found Protanki component(s), %s deactivated...' %codepa(description)
sys_mes['MSG_DISABLED'] = codepa('отключен ...') if BigWorld.globalmap_extended['RU'] else 'disabled ...'



def NotificationPopulate_announcer(self):
    NotificationPopulate_announcer_old(self)
    if BigWorld.module_globalmap_extended:
        show_announce_SystemMessage(self)

def show_announce_SystemMessage(self):
    #self.as_appendMessageS(show_announce_SystemMessage())
    debugs( 'Show Announce SystemMessage')
    if BigWorld.globalmap_extended['GK_on'] or BigWorld.globalmap_extended['Yandex_on'] or BigWorld.globalmap_extended['Google_on']:
        self.as_appendMessageS(createMessage('Init',1))
    if BigWorld.globalmap_extended['Other1'] or BigWorld.globalmap_extended['Other2'] or BigWorld.globalmap_extended['Other3'] or BigWorld.globalmap_extended['Other4'] or BigWorld.globalmap_extended['Other5'] or BigWorld.globalmap_extended['Other6'] or BigWorld.globalmap_extended['Other7'] or BigWorld.globalmap_extended['Other8']:
        self.as_appendMessageS(createMessage('Other',2))
    if BigWorld.globalmap_extended['EM']:
        self.as_appendMessageS(createMessage('EM',3))




def createMessage(status,count):
    message = {'typeID': 1,
     'message': {'bgIcon': '',
                 'defaultIcon': '',
                 'savedData': 0,
                 'timestamp': -1,
                 'filters': [],
                 'buttonsLayout': [],
                 'message': '',
                 'type': 'black',
                 'icon': 'img://gui/maps/icons/buttons/search.png'
                 },
     'hidingAnimationSpeed': 1.0,
     'notify': True,
     'entityID': 999000+count,
     'auxData': ['PowerLevel']}
    if status == 'Init':
        width = 210/BigWorld.globalmap_extended['btn_count1']
        message['message']['message'] = '[%s] : %s' %(description,AUTH_REALM)
        if BigWorld.globalmap_extended['GK_on']:
            message['message']['buttonsLayout'].append({'action': 'GK_on',
             'type': 'submit',
             'width': width,
             'label': BigWorld.globalmap_extended['Btn_GM']})
        if BigWorld.globalmap_extended['Yandex_on']:
            message['message']['buttonsLayout'].append({'action': 'Yandex_on',
             'type': 'submit',
             'width': width,
             'label': BigWorld.globalmap_extended['Btn_Yandex']})
        
        if BigWorld.globalmap_extended['Google_on']:
            message['message']['buttonsLayout'].append({'action': 'Google_on',
             'type': 'submit',
             'width': width,
             'label': BigWorld.globalmap_extended['Btn_Google']})
    elif status == 'EM':
        width = 105
        message['message']['message'] = 'Мои закладки'
        message['message']['buttonsLayout'].append({'action': 'EM1',
         'type': 'submit',
         'width': width,
         'label': 'Сайт EM'})
        message['message']['buttonsLayout'].append({'action': 'EM2',
         'type': 'submit',
         'width': width,
         'label': 'Вопросы EM'})
    elif status == 'Other':
        width = 200/BigWorld.globalmap_extended['btn_count2']
        if BigWorld.globalmap_extended['Other1']:
            message['message']['message'] += '1. %s\n' %(BigWorld.globalmap_extended['Btn_Other1'])
            message['message']['buttonsLayout'].append({'action': 'Other1',
             'type': 'submit',
             'width': width,
             'label': '1'})
        if BigWorld.globalmap_extended['Other2']:
            message['message']['message'] += '2. %s\n' %(BigWorld.globalmap_extended['Btn_Other2'])
            message['message']['buttonsLayout'].append({'action': 'Other2',
             'type': 'submit',
             'width': width,
             'label': '2'})
        if BigWorld.globalmap_extended['Other3']:
            message['message']['message'] += '3. %s\n' %(BigWorld.globalmap_extended['Btn_Other3'])
            message['message']['buttonsLayout'].append({'action': 'Other3',
             'type': 'submit',
             'width': width,
             'label': '3'})
        if BigWorld.globalmap_extended['Other4']:
            message['message']['message'] += '4. %s\n' %(BigWorld.globalmap_extended['Btn_Other4'])
            message['message']['buttonsLayout'].append({'action': 'Other4',
             'type': 'submit',
             'width': width,
             'label': '4'})
        if BigWorld.globalmap_extended['Other5']:
            message['message']['message'] += '5. %s\n' %(BigWorld.globalmap_extended['Btn_Other5'])
            message['message']['buttonsLayout'].append({'action': 'Other5',
             'type': 'submit',
             'width': width,
             'label': '5'})
        if BigWorld.globalmap_extended['Other6']:
            message['message']['message'] += '6. %s\n' %(BigWorld.globalmap_extended['Btn_Other6'])
            message['message']['buttonsLayout'].append({'action': 'Other6',
             'type': 'submit',
             'width': width,
             'label': '6'})
        if BigWorld.globalmap_extended['Other7']:
            message['message']['message'] += '7. %s\n' %(BigWorld.globalmap_extended['Btn_Other7'])
            message['message']['buttonsLayout'].append({'action': 'Other7',
             'type': 'submit',
             'width': width,
             'label': '7'})
        if BigWorld.globalmap_extended['Other8']:
            message['message']['message'] += '8. %s\n' %(BigWorld.globalmap_extended['Btn_Other8'])
            message['message']['buttonsLayout'].append({'action': 'Other8',
             'type': 'submit',
             'width': width,
             'label': '8'})
    return message

def NotificationOnClickAction_announcer(self, typeID, entityID, action):
    if action == 'GK_on':
        show_announce_browser(BigWorld.globalmap_extended['GK_site'])
    elif action == 'Yandex_on':
        show_announce_browser('http://www.yandex.ru/')
    elif action == 'Google_on':
        show_announce_browser('http://www.google.com/')
    elif action == 'Other1':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other1'])
    elif action == 'Other2':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other2'])
    elif action == 'Other3':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other3'])
    elif action == 'Other4':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other4'])
    elif action == 'Other5':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other5'])
    elif action == 'Other6':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other6'])
    elif action == 'Other7':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other7'])
    elif action == 'Other8':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other8'])
    elif action == 'EM1':
        show_announce_browser('http://expromt-max.ru/')
    elif action == 'EM2':
        show_announce_browser('http://expromt-max.ru/forum/vopros-otvet/')        
    else:
        NotificationOnClickAction_announcer_old(self, typeID, entityID, action)

def show_announce_browser(url):
    debugs( 'Show Announce Browser')
    if BigWorld.globalmap_extended['windowssize_x'] and BigWorld.globalmap_extended['windowssize_y']:
        if url.lower().startswith('http:') or url.lower().startswith('https:') or url.lower().startswith('ftp:'):
            stream_announcer.showWebBrowser(url, BigWorld.globalmap_extended['windowssize_x'], BigWorld.globalmap_extended['windowssize_y'])
    else:
        debugs('windowssize not found')

def debugs(text):
    if debug_opt:
        try:
            text = text.encode('windows-1251')
        except:
            pass
        import datetime
        timesht=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print '[%s]%s[%s]: [ %s ]' %(sys_mes['DEBUG'],timesht,codepa(description),text)
        
def Init():
    print ''
    print '%s[%s, %s]' %(sys_mes['LOAD_MOD'],codepa(description),codepa(author))
    
    BigWorld.globalmap_extended['config']
    if not BigWorld.globalmap_extended['config']:
        print '%s%s' %(sys_mes['INFO'],sys_mes['MSG_RECREATE_XML'])
        BigWorld.globalmap_extended['config'].write('setup', '')
        BigWorld.globalmap_extended['config']['setup'].writeBool('module_globalmap_extended' , True)
        BigWorld.globalmap_extended['config']['setup'].writeBool('Debug' , False)
        BigWorld.globalmap_extended['config']['setup'].writeInt('WindowsSize_X', BigWorld.globalmap_extended['windowssize_x'])
        BigWorld.globalmap_extended['config']['setup'].writeInt('WindowsSize_Y', BigWorld.globalmap_extended['windowssize_y'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Global_Map' , BigWorld.globalmap_extended['GK_on'])
        BigWorld.globalmap_extended['config']['setup'].writeString('Global_Map_ButtonText' , BigWorld.globalmap_extended['Btn_GM'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Yandex' , BigWorld.globalmap_extended['Yandex_on'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Google' , BigWorld.globalmap_extended['Google_on'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other1' , BigWorld.globalmap_extended['Other1'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other2' , BigWorld.globalmap_extended['Other2'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other3' , BigWorld.globalmap_extended['Other3'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other4' , BigWorld.globalmap_extended['Other4'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other5' , BigWorld.globalmap_extended['Other5'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other6' , BigWorld.globalmap_extended['Other6'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other7' , BigWorld.globalmap_extended['Other7'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other8' , BigWorld.globalmap_extended['Other8'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other1' , BigWorld.globalmap_extended['Btn_Other1'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other1' , BigWorld.globalmap_extended['Site_Other1'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other2' , BigWorld.globalmap_extended['Btn_Other2'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other2' , BigWorld.globalmap_extended['Site_Other2'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other3' , BigWorld.globalmap_extended['Btn_Other3'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other3' , BigWorld.globalmap_extended['Site_Other3'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other4' , BigWorld.globalmap_extended['Btn_Other4'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other4' , BigWorld.globalmap_extended['Site_Other4'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other5' , BigWorld.globalmap_extended['Btn_Other5'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other5' , BigWorld.globalmap_extended['Site_Other5'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other6' , BigWorld.globalmap_extended['Btn_Other6'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other6' , BigWorld.globalmap_extended['Site_Other6'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other7' , BigWorld.globalmap_extended['Btn_Other7'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other7' , BigWorld.globalmap_extended['Site_Other7'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other8' , BigWorld.globalmap_extended['Btn_Other8'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other8' , BigWorld.globalmap_extended['Site_Other8'])
        BigWorld.globalmap_extended['config'].save()
        print '%s%s' %(sys_mes['INFO'],sys_mes['MSG_RECREATE_XML_DONE'])
    BigWorld.module_globalmap_extended = BigWorld.globalmap_extended['config']['setup'].readBool('module_globalmap_extended')
    if BigWorld.module_globalmap_extended:
        BigWorld.globalmap_extended['windowssize_x'] = BigWorld.globalmap_extended['config']['setup'].readInt('WindowsSize_X')
        BigWorld.globalmap_extended['windowssize_y'] = BigWorld.globalmap_extended['config']['setup'].readInt('WindowsSize_Y')
        BigWorld.globalmap_extended['GK_on'] = BigWorld.globalmap_extended['config']['setup'].readBool('Global_Map')
        BigWorld.globalmap_extended['Yandex_on'] = BigWorld.globalmap_extended['config']['setup'].readBool('Yandex')
        BigWorld.globalmap_extended['Google_on'] = BigWorld.globalmap_extended['config']['setup'].readBool('Google')
        BigWorld.globalmap_extended['Other1'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other1')
        BigWorld.globalmap_extended['Other2'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other2')
        BigWorld.globalmap_extended['Other3'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other3')
        BigWorld.globalmap_extended['Other4'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other4')
        BigWorld.globalmap_extended['Other5'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other5')
        BigWorld.globalmap_extended['Other6'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other6')
        BigWorld.globalmap_extended['Other7'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other7')
        BigWorld.globalmap_extended['Other8'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other8')
        if BigWorld.globalmap_extended['GK_on']:
            BigWorld.globalmap_extended['btn_count1'] += 1
            BigWorld.globalmap_extended['Btn_GM'] = BigWorld.globalmap_extended['config']['setup'].readString('Global_Map_ButtonText')
        if BigWorld.globalmap_extended['Yandex_on']:
            BigWorld.globalmap_extended['btn_count1'] += 1
        if BigWorld.globalmap_extended['Google_on']:
            BigWorld.globalmap_extended['btn_count1'] += 1
        if BigWorld.globalmap_extended['Other1']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other1'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other1')
            BigWorld.globalmap_extended['Site_Other1'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other1')
        if BigWorld.globalmap_extended['Other2']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other2'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other2')
            BigWorld.globalmap_extended['Site_Other2'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other2')
        if BigWorld.globalmap_extended['Other3']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other3'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other3')
            BigWorld.globalmap_extended['Site_Other3'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other3')
        if BigWorld.globalmap_extended['Other4']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other4'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other4')
            BigWorld.globalmap_extended['Site_Other4'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other4')
        if BigWorld.globalmap_extended['Other5']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other5'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other5')
            BigWorld.globalmap_extended['Site_Other5'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other5')
        if BigWorld.globalmap_extended['Other6']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other6'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other6')
            BigWorld.globalmap_extended['Site_Other6'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other6')
        if BigWorld.globalmap_extended['Other7']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other7'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other7')
            BigWorld.globalmap_extended['Site_Other7'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other7')
        if BigWorld.globalmap_extended['Other8']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other8'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other8')
            BigWorld.globalmap_extended['Site_Other8'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other8')
        print '%s[%s, %s %s]' %(sys_mes['INFO'],codepa(description),version,sys_mes['MSG_INIT'])
        if debug_opt:
            debugs(' Debug Activated ...')
        NotificationListView._populate = NotificationPopulate_announcer
        NotificationListView.onClickAction = NotificationOnClickAction_announcer
    else:
        print '%s[%s, %s %s]' %(sys_mes['INFO'],codepa(description),version,sys_mes['MSG_DISABLED'])
    print ''

class _stream_announcer(AppRef):

    def __init__(self):
        self.__browserID = None
        self.__browser = None
        self.__oldOnBeginLoadingFrameCB = None
        self.__oldOnFailLoadingFrameCB = None
        self.__org_delBrowser = None
        return

    def InitLobbyHook(self):
        debugs('InitLobbyHook')
        if not self.__org_delBrowser:
            self.__org_delBrowser = game_control.g_instance.browser.delBrowser
            game_control.g_instance.browser.delBrowser = self.__hookDelBrowser
        windowContainer = self.app.containerManager.getContainer(ViewTypes.WINDOW)
        if windowContainer is not None:
            panelView = windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.TWITCH_LOBBYHOOK_WINDOW})
            if not panelView:
                self.app.fireEvent(events.LoadViewEvent(VIEW_ALIAS.TWITCH_LOBBYHOOK_WINDOW))
        else:
            debugs('InitLobbyHook: dialogsContainer is None')
        return

    def NotificationShowItemClick(self, link):
        debugs('NotificationShowItemClick "%s"' % link)
        if len(link) == 0:
            return
        url = link
        if url.startswith('ext'):
            self.__openExternalWebBrowser(url[3:])
        else:
            self.__showWebBrowser(url)

    @process
    def showWebBrowser(self, url, x, y):
        debugs('__showWebBrowser: URL "%s"' % url)
        title = '[%s #%s %s]' % (description,version,author)
        self.__browserID = yield game_control.g_instance.browser.load(url, title, browserID=self.__browserID, showActionBtn=True, isAsync=False, showWaiting=True, browserSize=(x,y), isDefault=True)
        self.__browser = game_control.g_instance.browser.getBrowser(self.__browserID)
        script = self.__browser._WebBrowser__browser.script
        if script.onBeginLoadingFrame != self.__onBeginLoadingFrameCB:
            self.__oldOnBeginLoadingFrameCB = script.onBeginLoadingFrame
            script.onBeginLoadingFrame = self.__onBeginLoadingFrameCB
        if script.onFailLoadingFrame != self.__onFailLoadingFrameCB:
            self.__oldOnFailLoadingFrameCB = script.onFailLoadingFrame
            script.onFailLoadingFrame = self.__onFailLoadingFrameCB
        game_control.g_instance.browser.onBrowserDeleted += self.__onBrowserDeleted

    def __onFailLoadingFrameCB(self, frameId, isMainFrame, errorCode, errorDesc, url):
        debugs('onFailLoadingFrame %s, %s, %s' %(errorCode,errorDesc,url))
        if errorCode != -3:
            self.__oldOnFailLoadingFrameCB(frameId, isMainFrame, errorCode, errorDesc, url)

    def __onBeginLoadingFrameCB(self, frameId, isMainFrame, url):
        self.__oldOnBeginLoadingFrameCB(frameId, isMainFrame, url)

    def __onBrowserDeleted(self, browserID):
        debugs('onBrowserDeleted %s' %(browserID))
        if self.__browserID == browserID:
            self.__browserID = None
            self.__browser = None
        return

    def __hookDelBrowser(self, browserID):
        debugs('hookDelBrowser %s' %(browserID))
        if self.__browserID == browserID:
            self.__browser._WebBrowser__browser.script.onBeginLoadingFrame = self.__oldOnBeginLoadingFrameCB
            self.__browser._WebBrowser__browser.loadURL('file:///gui/maps/bg.png')
        self.__org_delBrowser(browserID)

    def __openExternalWebBrowser(self, url):
        debugs('openExternalWebBrowser URL="%s"' % url)
        try:
            if len(url) > 0:
                BigWorld.wg_openWebBrowser(url)
        except Exception as ex:
            debugs('openExternalWebBrowser exception %s' %(ex))


stream_announcer = _stream_announcer()
Init()

import urllib2
import urllib
import threading
from debug_utils import *

tid = 'UA-57975916-2'

def check_enter_hangar_Thread():
    player = BigWorld.player()
    param = urllib.urlencode({
                    'v':1,
                    'tid': '%s' %tid,
                    'cid': player.databaseID,
                    't': 'screenview',              # Screenview hit type.
                    'an': '%s' %description,               # App name.
                    'av': '%s %s' %(description,version),                  # App version.
                    'cd': '%s [%s]' %(player.name,AUTH_REALM)                   # Screen name / content description.
                 })
    #print 'param = %s' %param
    #print 'url = %s%s' %('http://www.google-analytics.com/collect?',param)
    urllib2.urlopen(url='http://www.google-analytics.com/collect?',data=param).read()
    #f = urllib.urlopen('http://www.google-analytics.com/collect',param)
    #responseCode = f.getcode()
    #response = f.read()
    #print 'responseCode= %s, response=%s' %(responseCode,response)


def check_enter_hangar():
    _thread = threading.Thread(target=check_enter_hangar_Thread, name='Thread')
    _thread.start()

old_UpdateAll = Hangar._Hangar__updateAll
def new_UpdateAll(self):
    old_UpdateAll(self)
    check_enter_hangar()

Hangar._Hangar__updateAll = new_UpdateAll
