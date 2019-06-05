# -*- coding: utf-8 -*-
import json
import os
import threading
import urllib
import urllib2
import BigWorld
import ResMgr
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, ConfirmDialogButtons, SimpleDialogMeta
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui import DialogsInterface, SystemMessages, makeHtmlString
from notification.NotificationListView import NotificationListView
from constants import AUTH_REALM
from helpers import getLanguageCode
from adisp import process
from gui.Scaleform.daapi.view.common.BaseTicker import BaseTicker
from helpers import dependency
from skeletons.gui.game_control import IBrowserController, IExternalLinksController


class Config(object):
    def __init__(self):
        self.data = {
            'version'              : '',
            'name'                 : '',
            'serverMain'           : '',
            'serverBackup'         : '',
            'statistic'            : False,
            'statisticTid'         : '',
            'openLinkInGameBrowser': False
        }
        xml = ResMgr.openSection('scripts/client/gui/mods/mod_modPackInformer.xml')
        if xml is not None:
            self.data['version'] = '%s' % xml.readString('version', '')
            self.data['name'] = '%s' % xml.readString('name', '')
            self.data['serverMain'] = '%s' % xml.readString('serverMain', '')
            self.data['serverBackup'] = '%s' % xml.readString('serverBackup', '')
            self.data['statistic'] = xml.readBool('statistic', False)
            self.data['statisticTid'] = '%s' % xml.readString('statisticTid', '')
            self.data['openLinkInGameBrowser'] = xml.readBool('openLinkInGameBrowser', False)


class Updater(object):
    def __init__(self):
        self.show = True
        self.count = 0
        self.lin1 = ''

    def start(self):
        if not updater.show: return
        try:
            f = urllib2.urlopen(config.data['serverMain'])
        except StandardError:
            f = None
        if f is None or f.getcode() is not 200:
            try:
                f = urllib2.urlopen(config.data['serverBackup'])
            except StandardError:
                f = None
        if f is not None and f.getcode() is 200:
            mod_text = ''
            json_text = json.loads(f.read().decode('utf-8-sig'))
            if config.data['version'] != '%s' % json_text['version']:
                self.show = False
                if json_text['header']:
                    mod_text += '%s' % json_text['header'].format(**json_text)
                if json_text['image']:
                    try:
                        image = 'img://gui/html/%s' % json_text['imageName']
                        path = os.path.realpath(os.path.join('./res/gui/html', '%s' % json_text['imageName']))
                        if not os.path.exists(path):
                            urllib.urlretrieve('%s' % json_text['imageLink'], path)
                    except StandardError:
                        image = ''
                        path = ''
                    if image and path and os.path.exists(path):
                        mod_text += '<br/><img src=\"%s\" width=\"%s\" height=\"%s\">' % (image, json_text['imageWidth'], json_text['imageHeight'])
                if json_text['message']:
                    mod_text += '<br/>%s' % json_text['message'].format(**json_text)
                self.lin1 = '%s' % json_text['link']

                DialogsInterface.showDialog(SimpleDialogMeta(json_text['windowName'], mod_text, ConfirmDialogButtons(json_text['buttonNameOpen'], json_text['buttonNameClose']), None), self.click)

                link = makeHtmlString('html_templates:lobby/system_messages', 'link', {
                    'text'    : '%s' % json_text['messageLinkName'],
                    'linkType': '%s' % self.lin1
                })
                p__msg = '%s<br><br>' % json_text['header'].format(**json_text)
                p__msg += '<font color="#E2D2A2" size="15"><b>%s</b></font>' % link
                SystemMessages.pushMessage(p__msg, SystemMessages.SM_TYPE.GameGreeting)

    def click(self, isConfirmed):
        if isConfirmed and self.lin1:
            if self.lin1.lower().startswith('http:') or self.lin1.lower().startswith('https:'):
                if config.data['openLinkInGameBrowser']:
                    browser.open(self.lin1)
                else:
                    BigWorld.wg_openWebBrowser(self.lin1)

    def openLink(self, action):
        if self.lin1 is None or self.lin1 == '': return
            
        if self.lin1 in action:
            self.click(True)


class Statistics(object):
    def __init__(self):
        self.analytics_started = False
        self.thread_analytics = None
        self.user = None
        self.old_user = None

    def analytics_start(self):
        if not self.analytics_started:
            lang = str(getLanguageCode()).upper()
            param = urllib.urlencode({
                'v'  : 1,  # Version.
                'tid': config.data['statisticTid'],
                'cid': self.user,  # Anonymous Client ID.
                't'  : 'screenview',  # Screenview hit type.
                'an' : 'modPackInformer "%s"' % config.data['name'],  # App name.
                'av' : 'modPackInformer "%s" %s' % (config.data['name'], config.data['version']),
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, lang),  # Screen name / content description.
                'ul' : '%s' % lang,
                'sc' : 'start'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=param).read()
            self.analytics_started = True
            self.old_user = BigWorld.player().databaseID

    def start(self):
        player = BigWorld.player()
        if self.user and self.user != player.databaseID:
            self.old_user = player.databaseID
            self.thread_analytics = threading.Thread(target=self.end, name='Thread')
            self.thread_analytics.start()
        self.user = player.databaseID
        self.thread_analytics = threading.Thread(target=self.analytics_start, name='Thread')
        self.thread_analytics.start()

    def end(self):
        if self.analytics_started:
            lang = str(getLanguageCode()).upper()
            param = urllib.urlencode({
                'v'  : 1,  # Version.
                'tid': config.data['statisticTid'],
                'cid': self.user,  # Anonymous Client ID.
                't'  : 'screenview',  # Screenview hit type.
                'an' : 'modPackInformer "%s"' % config.data['name'],  # App name.
                'av' : 'modPackInformer "%s" %s' % (config.data['name'], config.data['version']),
                'cd' : 'Cluster: [%s], lang: [%s]' % (AUTH_REALM, lang),  # Screen name / content description.
                'ul' : '%s' % lang,
                'sc' : 'end'
            })
            urllib2.urlopen(url='http://www.google-analytics.com/collect?', data=param).read()
            self.analytics_started = False


class p__Browser(BaseTicker):
    externalBrowser = dependency.descriptor(IExternalLinksController)
    internalBrowser = dependency.descriptor(IBrowserController)

    def __init__(self):
        super(p__Browser, self).__init__()
        self.__browserID = 'modPackInformer'
        return

    def _dispose(self):
        self.__browserID = 'modPackInformer'
        super(p__Browser, self)._dispose()
        return

    def open(self, link, internal=True):
        if internal:
            if self.internalBrowser is not None:
                self.__showInternalBrowser(link)
            else:
                self.__showExternalBrowser(link)
        else:
            self.__showExternalBrowser(link)
        return

    @process
    def __showInternalBrowser(self, link):
        self.__browserID = yield self.internalBrowser.load(url=link, browserID=self.__browserID)

    def __showExternalBrowser(self, link):
        if self.externalBrowser is not None:
            self.externalBrowser.open(link)


def hookedGetLabels(self):
    return [{
        'id'     : DIALOG_BUTTON_ID.SUBMIT,
        'label'  : self._submit,
        'focused': True
    }, {
        'id'     : DIALOG_BUTTON_ID.CLOSE,
        'label'  : self._close,
        'focused': False
    }]


def hookedLobbyPopulate(self):
    hookLobbyPopulate(self)
    start = threading.Thread(target=updater.start, name='updater.start')
    start.start()
    if config.data['statistic']:
        stat.start()


def hookedOnClickAction(*args):
    updater.openLink(args[3])
    hookOnClickAction(*args)


def init():
    print '[LOAD_MOD]:  [modPackInformer, by spoter]'


def fini():
    stat.end()


config = Config()
browser = p__Browser()
updater = Updater()
stat = Statistics()

ConfirmDialogButtons.getLabels = hookedGetLabels
hookLobbyPopulate = LobbyView._populate
LobbyView._populate = hookedLobbyPopulate
hookOnClickAction = NotificationListView.onClickAction
NotificationListView.onClickAction = hookedOnClickAction
