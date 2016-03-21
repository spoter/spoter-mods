# -*- coding: utf-8 -*-
import BigWorld, ResMgr
from urllib import urlopen
import json
import time
import datetime
from Account import Account
from notification.NotificationListView import NotificationListView
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, ConfirmDialogButtons,SimpleDialogMeta
import os
from adisp import async, process
from gui.Scaleform.framework import ViewTypes#, AppRef
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
    'Btn_Other9': 'RU WG Forum',
    'Site_Other9': 'http://forum.worldoftanks.ru/index.php?/forum/174-',
    'Other9': False,
    'Btn_Other10': 'RU Koreanrandom',
    'Site_Other10': 'http://www.koreanrandom.com/forum/forum/44-',
    'Other10': False,
    'Btn_Other11': 'RU Expromt-Max Team',
    'Site_Other11': 'http://expromt-max.ru/forum/spoter/',
    'Other11': False,
    'Btn_Other12': 'NA Roughnecks Mods',
    'Site_Other12': 'http://roughnecksxvmmods.ipbhost.com/index.php?/forum/113-',
    'Other12': False,
    'Btn_Other13': 'NA WG Forum',
    'Site_Other13': 'http://forum.worldoftanks.com/index.php?/forum/189-',
    'Other13': False,    
    'Btn_Other14': 'EU WG Forum',
    'Site_Other14': 'http://forum.worldoftanks.eu/index.php?/topic/432069-',
    'Other14': False,
    'Btn_Other15': 'RU LJ world-of-tanks',
    'Site_Other15': 'http://world-of-tanks.livejournal.com/',
    'Other15': False,
    'Btn_Other16': 'RU LJ world-of-ru',
    'Site_Other16': 'http://world-of-ru.livejournal.com/',
    'Other16': False,        
    'Btn_Other17': 'RU Koreanrandom',
    'Site_Other17': 'http://www.koreanrandom.com/forum/forum/44-',
    'Other17': False,
    'Btn_Other18': 'RU Koreanrandom',
    'Site_Other18': 'http://www.koreanrandom.com/forum/forum/44-',
    'Other18': False,
    'Btn_Other19': 'RU Koreanrandom',
    'Site_Other19': 'http://www.koreanrandom.com/forum/forum/44-',
    'Other19': False,
    'Btn_Other20': 'RU Koreanrandom',
    'Site_Other20': 'http://www.koreanrandom.com/forum/forum/44-',
    'Other20': False,
    'config': ResMgr.openSection('scripts/client/gui/mods/mod_globalmap_extended.xml', True)
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

#
description = 'globalmap_extended.pyc'
author = 'by spoter'
version = 'v1.07(21.03.2016)'
debug_opt = False
if BigWorld.globalmap_extended['RU']:
    description = 'Мод: "Закладочка"'
    author = 'автор: spoter, expoint'

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
        if BigWorld.globalmap_extended['Other9']:
            message['message']['message'] += '9. %s\n' %(BigWorld.globalmap_extended['Btn_Other9'])
            message['message']['buttonsLayout'].append({'action': 'Other9',
             'type': 'submit',
             'width': width,
             'label': '9'})
        if BigWorld.globalmap_extended['Other10']:
            message['message']['message'] += '10. %s\n' %(BigWorld.globalmap_extended['Btn_Other10'])
            message['message']['buttonsLayout'].append({'action': 'Other10',
             'type': 'submit',
             'width': width,
             'label': '10'})
        if BigWorld.globalmap_extended['Other11']:
            message['message']['message'] += '11. %s\n' %(BigWorld.globalmap_extended['Btn_Other11'])
            message['message']['buttonsLayout'].append({'action': 'Other11',
             'type': 'submit',
             'width': width,
             'label': '11'})
        if BigWorld.globalmap_extended['Other12']:
            message['message']['message'] += '12. %s\n' %(BigWorld.globalmap_extended['Btn_Other12'])
            message['message']['buttonsLayout'].append({'action': 'Other12',
             'type': 'submit',
             'width': width,
             'label': '12'})
        if BigWorld.globalmap_extended['Other13']:
            message['message']['message'] += '13. %s\n' %(BigWorld.globalmap_extended['Btn_Other13'])
            message['message']['buttonsLayout'].append({'action': 'Other13',
             'type': 'submit',
             'width': width,
             'label': '13'})
        if BigWorld.globalmap_extended['Other14']:
            message['message']['message'] += '14. %s\n' %(BigWorld.globalmap_extended['Btn_Other14'])
            message['message']['buttonsLayout'].append({'action': 'Other14',
             'type': 'submit',
             'width': width,
             'label': '14'})
        if BigWorld.globalmap_extended['Other15']:
            message['message']['message'] += '15. %s\n' %(BigWorld.globalmap_extended['Btn_Other15'])
            message['message']['buttonsLayout'].append({'action': 'Other15',
             'type': 'submit',
             'width': width,
             'label': '15'})
        if BigWorld.globalmap_extended['Other16']:
            message['message']['message'] += '16. %s\n' %(BigWorld.globalmap_extended['Btn_Other16'])
            message['message']['buttonsLayout'].append({'action': 'Other16',
             'type': 'submit',
             'width': width,
             'label': '16'})
        if BigWorld.globalmap_extended['Other17']:
            message['message']['message'] += '17. %s\n' %(BigWorld.globalmap_extended['Btn_Other17'])
            message['message']['buttonsLayout'].append({'action': 'Other17',
             'type': 'submit',
             'width': width,
             'label': '17'})
        if BigWorld.globalmap_extended['Other18']:
            message['message']['message'] += '18. %s\n' %(BigWorld.globalmap_extended['Btn_Other18'])
            message['message']['buttonsLayout'].append({'action': 'Other18',
             'type': 'submit',
             'width': width,
             'label': '18'})
        if BigWorld.globalmap_extended['Other19']:
            message['message']['message'] += '19. %s\n' %(BigWorld.globalmap_extended['Btn_Other19'])
            message['message']['buttonsLayout'].append({'action': 'Other19',
             'type': 'submit',
             'width': width,
             'label': '19'})
        if BigWorld.globalmap_extended['Other20']:
            message['message']['message'] += '20. %s\n' %(BigWorld.globalmap_extended['Btn_Other20'])
            message['message']['buttonsLayout'].append({'action': 'Other20',
             'type': 'submit',
             'width': width,
             'label': '20'})
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
    elif action == 'Other9':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other9'])
    elif action == 'Other10':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other10'])
    elif action == 'Other11':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other11'])
    elif action == 'Other12':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other12'])
    elif action == 'Other13':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other13'])
    elif action == 'Other14':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other14'])
    elif action == 'Other15':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other15'])
    elif action == 'Other16':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other16'])        
    elif action == 'Other17':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other17'])
    elif action == 'Other18':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other18'])
    elif action == 'Other19':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other19'])
    elif action == 'Other20':
        show_announce_browser(BigWorld.globalmap_extended['Site_Other20'])       
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
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other9' , BigWorld.globalmap_extended['Other9'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other10' , BigWorld.globalmap_extended['Other10'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other11' , BigWorld.globalmap_extended['Other11'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other12' , BigWorld.globalmap_extended['Other12'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other13' , BigWorld.globalmap_extended['Other13'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other14' , BigWorld.globalmap_extended['Other14'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other15' , BigWorld.globalmap_extended['Other15'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other16' , BigWorld.globalmap_extended['Other16'])        
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other17' , BigWorld.globalmap_extended['Other17'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other18' , BigWorld.globalmap_extended['Other18'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other19' , BigWorld.globalmap_extended['Other19'])
        BigWorld.globalmap_extended['config']['setup'].writeBool('Other20' , BigWorld.globalmap_extended['Other20'])
                
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
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other9' , BigWorld.globalmap_extended['Btn_Other9'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other9' , BigWorld.globalmap_extended['Site_Other9'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other10' , BigWorld.globalmap_extended['Btn_Other10'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other10' , BigWorld.globalmap_extended['Site_Other10'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other11' , BigWorld.globalmap_extended['Btn_Other11'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other11' , BigWorld.globalmap_extended['Site_Other11'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other12' , BigWorld.globalmap_extended['Btn_Other12'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other12' , BigWorld.globalmap_extended['Site_Other12'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other13' , BigWorld.globalmap_extended['Btn_Other13'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other13' , BigWorld.globalmap_extended['Site_Other13'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other14' , BigWorld.globalmap_extended['Btn_Other14'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other14' , BigWorld.globalmap_extended['Site_Other14'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other15' , BigWorld.globalmap_extended['Btn_Other15'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other15' , BigWorld.globalmap_extended['Site_Other15'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other16' , BigWorld.globalmap_extended['Btn_Other16'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other16' , BigWorld.globalmap_extended['Site_Other16'])        
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other17' , BigWorld.globalmap_extended['Btn_Other17'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other17' , BigWorld.globalmap_extended['Site_Other17'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other18' , BigWorld.globalmap_extended['Btn_Other18'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other18' , BigWorld.globalmap_extended['Site_Other18'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other19' , BigWorld.globalmap_extended['Btn_Other19'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other19' , BigWorld.globalmap_extended['Site_Other19'])
        BigWorld.globalmap_extended['config']['setup'].writeString('ButtonText_Other20' , BigWorld.globalmap_extended['Btn_Other20'])
        BigWorld.globalmap_extended['config']['setup'].writeString('SiteUrl_Other20' , BigWorld.globalmap_extended['Site_Other20'])
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
        BigWorld.globalmap_extended['Other9'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other9')
        BigWorld.globalmap_extended['Other10'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other10')
        BigWorld.globalmap_extended['Other11'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other11')
        BigWorld.globalmap_extended['Other12'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other12')
        BigWorld.globalmap_extended['Other13'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other13')
        BigWorld.globalmap_extended['Other14'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other14')
        BigWorld.globalmap_extended['Other15'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other15')
        BigWorld.globalmap_extended['Other16'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other16')        
        BigWorld.globalmap_extended['Other17'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other17')
        BigWorld.globalmap_extended['Other18'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other18')
        BigWorld.globalmap_extended['Other19'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other19')
        BigWorld.globalmap_extended['Other20'] = BigWorld.globalmap_extended['config']['setup'].readBool('Other20')

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
        if BigWorld.globalmap_extended['Other9']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other9'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other9')
            BigWorld.globalmap_extended['Site_Other9'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other9')
        if BigWorld.globalmap_extended['Other10']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other10'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other10')
            BigWorld.globalmap_extended['Site_Other10'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other10')
        if BigWorld.globalmap_extended['Other11']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other11'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other11')
            BigWorld.globalmap_extended['Site_Other11'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other11')
        if BigWorld.globalmap_extended['Other12']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other12'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other12')
            BigWorld.globalmap_extended['Site_Other12'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other12')
        if BigWorld.globalmap_extended['Other13']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other13'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other13')
            BigWorld.globalmap_extended['Site_Other13'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other13')
        if BigWorld.globalmap_extended['Other14']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other14'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other14')
            BigWorld.globalmap_extended['Site_Other14'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other14')
        if BigWorld.globalmap_extended['Other15']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other15'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other15')
            BigWorld.globalmap_extended['Site_Other15'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other15')
        if BigWorld.globalmap_extended['Other16']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other16'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other16')
            BigWorld.globalmap_extended['Site_Other16'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other16')            
        if BigWorld.globalmap_extended['Other17']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other17'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other17')
            BigWorld.globalmap_extended['Site_Other17'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other17')
        if BigWorld.globalmap_extended['Other18']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other18'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other18')
            BigWorld.globalmap_extended['Site_Other18'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other18')
        if BigWorld.globalmap_extended['Other19']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other19'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other19')
            BigWorld.globalmap_extended['Site_Other19'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other19')
        if BigWorld.globalmap_extended['Other20']:
            BigWorld.globalmap_extended['btn_count2'] += 1
            BigWorld.globalmap_extended['Btn_Other20'] = BigWorld.globalmap_extended['config']['setup'].readString('ButtonText_Other20')
            BigWorld.globalmap_extended['Site_Other20'] = BigWorld.globalmap_extended['config']['setup'].readString('SiteUrl_Other20')
            
        print '%s[%s, %s %s]' %(sys_mes['INFO'],codepa(description),version,sys_mes['MSG_INIT'])
        if debug_opt:
            debugs(' Debug Activated ...')
        NotificationListView._populate = NotificationPopulate_announcer
        NotificationListView.onClickAction = NotificationOnClickAction_announcer
    else:
        print '%s[%s, %s %s]' %(sys_mes['INFO'],codepa(description),version,sys_mes['MSG_DISABLED'])
    print ''

class AppRef(object):
    __reference = None

    @property
    def app(self):
        return AppRef.__reference

    @property
    def gfx(self):
        return AppRef.__reference.movie

    @classmethod
    def setReference(cls, app):
        cls.__reference = app

    @classmethod
    def clearReference(cls):
        cls.__reference = None
        return
        
        
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
