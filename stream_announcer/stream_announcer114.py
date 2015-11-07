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
import urllib2
import urllib
import threading
from debug_utils import *

BigWorld.stream_announcer ={
    'browserID': None,
    'status': 0,
    'callback': None,
    'announcement': '', 
    'type': 0, 
    'title': '', 
    'text': '', 
    'pinned': 0, 
    'time': '', 
    'YTID': '', 
    'id': 0, 
    'Btn1': 'Смотреть', 
    'Btn2': 'Закрыть',
    'Btn3': 'Свернуть',
    'Btn4': 'Подробнее',
    'bgIcon': '',
    'defaultIcon': '' ,
    'ip': '188.127.246.171',
    'file': ResMgr.openSection('scripts/client/mods/stream_announcer_status.xml', True),
    'icon': 'img://gui/maps/icons/library/ServerRebootIcon-1.png'}

#url = 'http://desertod.ru/client/API/isAnnouncement_test.php'


if not BigWorld.stream_announcer['file']:
    
    BigWorld.stream_announcer['file'].writeInt('status' , 0)
    BigWorld.stream_announcer['file'].writeInt('id' , 0)
    BigWorld.stream_announcer['file'].writeString('ip' , BigWorld.stream_announcer['ip'])
    BigWorld.stream_announcer['file'].save()

BigWorld.stream_announcer['ip'] = BigWorld.stream_announcer['file'].readString('ip')
url = 'http://%s/client/API/isAnnouncement.php' %BigWorld.stream_announcer['ip']

oldUpdateAll = Hangar._Hangar__updateAll
NotificationPopulate_announcer_old = NotificationListView._populate
NotificationOnClickAction_announcer_old = NotificationListView.onClickAction
#
description = 'stream_announcer'
author = 'by spoter'
version = 'v1.14(14.07.2015)'
debug_opt = False
BigWorld.module_stream_announcer = True


def status_file_load():
    if BigWorld.stream_announcer['file']:
        return BigWorld.stream_announcer['file'].readInt('status'), BigWorld.stream_announcer['file'].readInt('id')
    else:
        return 0, 0
        


def status_file_save():
    BigWorld.stream_announcer['file'].writeInt('status' , BigWorld.stream_announcer['status'])
    BigWorld.stream_announcer['file'].writeInt('id' , BigWorld.stream_announcer['id'])
    BigWorld.stream_announcer['file'].save()
    return True

#

#Конвертер символов
def byteify(input):
    if input:
        if isinstance(input, dict):
            return {byteify(key):byteify(value) for key,value in input.iteritems()}
        elif isinstance(input, list):
            return [byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input
    return input



def open_WebBrowser(url):
    openBrowser = BigWorld.wg_openWebBrowser
    openBrowser(url)


def announcer_timer_thread():
    _thread = threading.Thread(target=announcer_timer, name='Thread')
    _thread.start()


#таймер 60 сек на запрос урл
def announcer_timer():
    obj = False
    data = False
    if not isPlayerOnArena():
        try:
            url_get = urlopen(url)
            if url_get.getcode() != 200:
                raise Exception('ERROR: Bad request: %d' % url_get.getcode())
            server_request = url_get.read()
            data = json.loads(server_request.encode('utf-8'))
        except:
            data = False
        if data:
            obj= byteify(data)
        if obj:
            _status, _id = status_file_load()
            debugs( 'Actived Announce Found')
            if BigWorld.stream_announcer['status'] < 1:
                BigWorld.stream_announcer['status'] = 1
            BigWorld.stream_announcer['announcement'] = obj['announcement']
            BigWorld.stream_announcer['type'] = int(obj['type'])
            BigWorld.stream_announcer['title'] = obj['title']
            BigWorld.stream_announcer['text'] = obj['text']
            BigWorld.stream_announcer['pinned'] = int(obj['pinned'])
            BigWorld.stream_announcer['time'] = obj['time']
            BigWorld.stream_announcer['YTID'] = obj['YTID']
            BigWorld.stream_announcer['id'] = int(obj['id'])
            try:
                img = urlopen('http://i.ytimg.com/vi/'+str(BigWorld.stream_announcer['YTID'])+'/maxresdefault.jpg')
                if img.getcode() != 200:
                    raise Exception('ERROR: Bad request: %d' % img.getcode())
                with open(str(os.getcwd())+'/maxresdefault.jpg', 'wb') as f:
                    f.write(img.read())
            except:
                pass
            if int(_id) != int(BigWorld.stream_announcer['id']) and int(BigWorld.stream_announcer['id']) != 0:
                status_file_save()
            else:
                BigWorld.stream_announcer['status'] = _status
    
        else:
            debugs( 'No Actived Announce')
            BigWorld.stream_announcer['status'] = 0
            BigWorld.stream_announcer['announcement'] = ''
            BigWorld.stream_announcer['type'] = 0
            BigWorld.stream_announcer['title'] = ''
            BigWorld.stream_announcer['text'] = ''
            BigWorld.stream_announcer['pinned'] = 0
            BigWorld.stream_announcer['time'] = ''
            BigWorld.stream_announcer['YTID'] = ''
            BigWorld.stream_announcer['id'] = 0
        debugs('Info: step1 = Start, step2 = witing, step3 = cancel, step0 = not started announce')
        debugs('Now step'+str(BigWorld.stream_announcer['status']))
    BigWorld.callback(180.0, announcer_timer_thread)

def isPlayerOnArena(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        result = avatar.isOnArena
    except:
        result = False

    return result


#проверка при входе в ангар
def newUpdateAll(self):
    oldUpdateAll(self)
    if BigWorld.stream_announcer['status'] == 1:
        BigWorld.callback(1.0, show_announce_window)

#onBecomeNonPlayer_announcer_old = Account.onBecomeNonPlayer
#def onBecomeNonPlayer_announcer(self):
#    #BigWorld.cancelCallback(BigWorld.stream_announcer['callback'])
#    onBecomeNonPlayer_announcer_old(self)
#Account.onBecomeNonPlayer = onBecomeNonPlayer_announcer

#показ сообщения в системном лотке
def NotificationPopulate_announcer(self):
    NotificationPopulate_announcer_old(self)
    if BigWorld.stream_announcer['status'] != 0 and BigWorld.stream_announcer['status'] < 3:
        self.as_appendMessageS(show_announce_SystemMessage())

#реакция на нажатия кнопки
def NotificationOnClickAction_announcer(self, typeID, entityID, action):
    if action == 'openYoutube':
        show_announce_browser()
        #show_announce_window()
    elif action == 'openInformer':
        show_announce_browser_no_stream()
        #show_announce_window()
    elif action == 'closeInformer':
        BigWorld.stream_announcer['status'] = 3
        status_file_save()
    else:
        NotificationOnClickAction_announcer_old(self, typeID, entityID, action)


def create_mesageM():
    if BigWorld.stream_announcer['type'] == 1:
        debugs('Type of announce #NEWS')
        msg = '<b>'+str(BigWorld.stream_announcer['title'])+'</b><br/>'
        msg += str(BigWorld.stream_announcer['text'])
    elif BigWorld.stream_announcer['type'] == 2:
        debugs('Type of announce #VIDEO')
        msg = '<b>'+str(BigWorld.stream_announcer['title'])+'</b><br/>'
        msg += '<img src="img://maxresdefault.jpg"><br/>'
        msg += str(BigWorld.stream_announcer['text'])
    elif BigWorld.stream_announcer['type'] == 3:
        debugs('Type of announce #STREAM')
        date = datetime.datetime.strptime(BigWorld.stream_announcer['time'],'%d-%m-%Y %H:%M')
        date=datetime.datetime.strftime(date, '%H:%M')
        msg = '<b>'+str(BigWorld.stream_announcer['title'])+'</b> '+str(date)+'<br/>'
        msg += '<img src="img://maxresdefault.jpg"><br/>'
        msg += str(BigWorld.stream_announcer['text'])
    else:
        debugs('Type of announce #'+str(BigWorld.stream_announcer['type']))
        msg = '<b>'+str(BigWorld.stream_announcer['title'])+'</b><br/>'
        msg += str(BigWorld.stream_announcer['text'])
    return msg


def show_announce_window():
    debugs( 'Show Announce window')
    def click(isConfirmed):
        if isConfirmed:
            if BigWorld.stream_announcer['type'] > 1:
                if BigWorld.stream_announcer['YTID']:
                    youtubeurl = 'http://%s/client/frame.php' %BigWorld.stream_announcer['ip']
                    if youtubeurl.lower().startswith('http:') or youtubeurl.lower().startswith('https:') or youtubeurl.lower().startswith('ftp:'):
                        #open_WebBrowser(youtubeurl)#, True, 1020, 580)
                        stream_announcer.showWebBrowser(youtubeurl, 720, 550)
            else:
                youtubeurl = 'http://%s/client/frame.php' %BigWorld.stream_announcer['ip']
                if youtubeurl.lower().startswith('http:') or youtubeurl.lower().startswith('https:') or youtubeurl.lower().startswith('ftp:'):
                    #open_WebBrowser(youtubeurl)#, True)#, 720, 550)
                    stream_announcer.showWebBrowser(youtubeurl, 720, 550)
            BigWorld.stream_announcer['status'] = 2
            status_file_save()
        else:
            BigWorld.stream_announcer['status'] = 2
            status_file_save()
        debugs('Info: step1 = Start, step2 = witing, step3 = cancel, step0 = not started announce')
        debugs('Now step'+str(BigWorld.stream_announcer['status']))
    
    #if BigWorld.stream_announcer['status'] == 1:
    if BigWorld.stream_announcer['type'] > 1:
        DialogsInterface.showDialog(SimpleDialogMeta('', create_mesageM(), ConfirmDialogButtons(BigWorld.stream_announcer['Btn1'], BigWorld.stream_announcer['Btn3']), None), click)
    else:
        DialogsInterface.showDialog(SimpleDialogMeta('', create_mesageM(), ConfirmDialogButtons(BigWorld.stream_announcer['Btn4'], BigWorld.stream_announcer['Btn3']), None), click)

    

def show_announce_SystemMessage():
    debugs( 'Show Announce SystemMessage')
    msg = '<p><b>DeSeRtod Informer</b></p><br/>'
    if BigWorld.stream_announcer['status'] != 0 and BigWorld.stream_announcer['status'] < 3:
        msg += BigWorld.stream_announcer['title']
    return createMessage(msg)

def show_announce_browser():
    debugs( 'Show Announce Browser')
    if BigWorld.stream_announcer['YTID']:
        youtubeurl = 'http://%s/client/frame.php' %BigWorld.stream_announcer['ip']
        if youtubeurl.lower().startswith('http:') or youtubeurl.lower().startswith('https:') or youtubeurl.lower().startswith('ftp:'):
            BigWorld.stream_announcer['status'] = 2
            status_file_save()
            debugs('Info: step1 = Start, step2 = witing, step3 = cancel, step0 = not started announce')
            debugs('Now step'+str(BigWorld.stream_announcer['status']))
            #open_WebBrowser(youtubeurl)#, True)#, 1020, 580)
            stream_announcer.showWebBrowser(youtubeurl, 720, 550)
    else:
        debugs( 'Youtube url not found')

def show_announce_browser_no_stream():
    debugs( 'Show Announce Browser No Stream')
    youtubeurl = 'http://%s/client/frame.php' %BigWorld.stream_announcer['ip']
    if youtubeurl.lower().startswith('http:') or youtubeurl.lower().startswith('https:') or youtubeurl.lower().startswith('ftp:'):
        #open_WebBrowser(youtubeurl)#, True)#, 720, 550)
        stream_announcer.showWebBrowser(youtubeurl, 720, 550)
    else:
        debugs( 'url not found')


def createMessage(msg):
    message = {'typeID': 1,
     'message': {'bgIcon': BigWorld.stream_announcer['bgIcon'],
                 'defaultIcon': BigWorld.stream_announcer['defaultIcon'] ,
                 'savedData': 0,
                 'timestamp': time.time(),
                 'filters': [],
                 'buttonsLayout': [],
                 'message': msg,
                 'type': 'black',
                 'icon': BigWorld.stream_announcer['icon']},
     'hidingAnimationSpeed': 2000.0,
     'notify': True,
     'entityID': 99999,
     'auxData': ['GameGreeting']}
    if BigWorld.stream_announcer['type'] > 1:
        message['message']['buttonsLayout'].append({'action': 'openYoutube',
         'type': 'submit',
         'label': BigWorld.stream_announcer['Btn1']})
    else:
        message['message']['buttonsLayout'].append({'action': 'openInformer',
         'type': 'submit',
         'label': BigWorld.stream_announcer['Btn4']})
    message['message']['buttonsLayout'].append({'action': 'closeInformer',
     'type': 'submit',
     'label': BigWorld.stream_announcer['Btn2']})
    return message


old_getLabels = ConfirmDialogButtons.getLabels

def new_getLabels(self):
    return [{'id': DIALOG_BUTTON_ID.SUBMIT,
      'label': self._submit,
      'focused': True}, {'id': DIALOG_BUTTON_ID.CLOSE,
      'label': self._close,
      'focused': False}]

ConfirmDialogButtons.getLabels = new_getLabels






def debugs(text):
    if debug_opt:
        import datetime
        timesht=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print '['+str(timesht)+'][DEBUG]['+description+']: [ '+str(text)+' ]'
        
def Init():
    print ''
    print '[LOAD_MOD]:  ['+str(description)+' '+str(author)+']'
    #if not XML:
    #    print '[INFO]:     XML not found, recreating'
    #    XML.write('setup', '')
    #    XML['setup'].writeBool('module_autoaim_extended' , True)
    #    XML['setup'].writeBool('Debug' , False)
    #    XML.save()
    #    print '[INFO]:     XML recreating DONE'
    if BigWorld.module_stream_announcer:
        BigWorld.module_stream_announcer = True #str(XML['setup'].readBool('module_autoaim_extended'))
        print '[INFO]:      ['+str(description)+' '+str(version)+' initialized ...]'
        if debug_opt:
            debugs(str(description)+' Debug Activated ...')
        Hangar._Hangar__updateAll = newUpdateAll
        NotificationListView._populate = NotificationPopulate_announcer
        NotificationListView.onClickAction = NotificationOnClickAction_announcer
        announcer_timer_thread()
    else:
        print '[INFO]:      ['+str(description)+' '+str(version)+' disabled ...]'
    print ''

Init()



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
        title = BigWorld.stream_announcer['title']
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

    def __onFailLoadingFrameCB(self, frameId, isMainFrame, errorCode, url):
        debugs('onFailLoadingFrame '+str(errorCode)+', '+str(url))
        if errorCode != -3:
            self.__oldOnFailLoadingFrameCB(frameId, isMainFrame, errorCode, url)

    def __onBeginLoadingFrameCB(self, frameId, isMainFrame, url):
        self.__oldOnBeginLoadingFrameCB(frameId, isMainFrame, url)

    def __onBrowserDeleted(self, browserID):
        debugs('onBrowserDeleted '+str(browserID))
        if self.__browserID == browserID:
            self.__browserID = None
            self.__browser = None
        return

    def __hookDelBrowser(self, browserID):
        debugs('hookDelBrowser '+str(browserID))
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
            debugs('openExternalWebBrowser exception '+str(ex))


stream_announcer = _stream_announcer()


try:
    if BigWorld._analitics_started:
        BigWorld._analitics_started[description] = 0
except:
    BigWorld._analitics_started = {}
    BigWorld._analitics_started[description] = 0

tid = 'UA-57975916-5' # Код берется когда вы активиуете аналитику для мобильного приложения в https://www.google.com/analytics/
tid1 = 'UA-61288757-4' # Код берется когда вы активиуете аналитику для мобильного приложения в https://www.google.com/analytics/

def check_enter_hangar_Thread():
    if BigWorld._analitics_started[description] == 0:
        player = BigWorld.player()
        param = urllib.urlencode({
                        'v':1,                                      # Version.
                        'tid': '%s' %tid,                           # Tracking ID / Property ID.
                        'cid': player.databaseID,                   # Anonymous Client ID.
                        't': 'screenview',                          # Screenview hit type.
                        'an': '%s' %description,                    # App name.
                        'av': '%s %s' %(description,version),       # App version.
                        'cd': 'server [%s]' %(AUTH_REALM)   # Screen name / content description.
                     })
        param1 = urllib.urlencode({
                        'v':1,                                      # Version.
                        'tid': '%s' %tid1,                           # Tracking ID / Property ID.
                        'cid': player.databaseID,                   # Anonymous Client ID.
                        't': 'screenview',                          # Screenview hit type.
                        'an': '%s' %description,                    # App name.
                        'av': '%s %s' %(description,version),       # App version.
                        'cd': 'server [%s]' %(AUTH_REALM)   # Screen name / content description.
                     })
        #print 'http://www.google-analytics.com/collect?%s' %param
        urllib2.urlopen(url='http://www.google-analytics.com/collect?',data=param).read()
        urllib2.urlopen(url='http://www.google-analytics.com/collect?',data=param1).read()
        BigWorld._analitics_started[description] = 1


def check_enter_hangar():
    _thread = threading.Thread(target=check_enter_hangar_Thread, name='Thread')
    _thread.start()

old_UpdateAll = Hangar._Hangar__updateAll
def new_UpdateAll(self):
    old_UpdateAll(self)
    check_enter_hangar()

Hangar._Hangar__updateAll = new_UpdateAll

BigWorld._iddqd = True