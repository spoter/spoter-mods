# -*- coding: utf-8 -*-
import datetime
import json
import threading
import urllib2

# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

# noinspection PyProtectedMember
from messenger.gui.Scaleform.channels.bw.lobby_controllers import _ChannelController

COLORS = ['FE0E00', 'FE7903', 'F8F400', '60FF00', '02C9B3', 'D042F3']
WIN = [0.0, 46.5, 48.5, 52.5, 57.5, 64.5]


class Config(object):
    def __init__(self):
        self.ids = 'chatInfo'
        self.version = 'v1.02 (2017-10-20)'
        self.version_id = 102
        self.author = 'by spoter'
        self.data = {
            'version'    : self.version_id,
            'enabled'    : True,
            'newbieDays' : 30,
            'newbieWinRate': 46.0,
            'showNewbie' : True,
            'showWinRate': True,
        }
        self.i18n = {
            'version'                       : self.version_id,
            'UI_description'                : 'Chat Info',
            'UI_setting_showNewbie_text'    : 'Show Newbie status in chat',
            'UI_setting_showNewbie_tooltip' : '',
            'UI_setting_showWinRate_text'   : 'Show winRate to user in chat',
            'UI_setting_showWinRate_tooltip': '',
            'UI_setting_newbieDays_text'    : 'How long is a newbie',
            'UI_setting_newbieDays_value'   : ' day\'s',
            'UI_setting_newbieWinRate_text' : 'Newbie winRate status',
            'UI_setting_newbieWinRate_value': '%',
            'UI_chat_newbieMarkColor'                : '#60FF00',
            'UI_chat_winRate'               : '[{winRate}]'
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n)
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [
                {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showNewbie_text'],
                    'value'  : self.data['showNewbie'],
                    'tooltip': self.i18n['UI_setting_showNewbie_tooltip'],
                    'varName': 'showNewbie'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showWinRate_text'],
                    'value'  : self.data['showWinRate'],
                    'tooltip': self.i18n['UI_setting_showWinRate_tooltip'],
                    'varName': 'showWinRate'
                }
            ],
            'column2'        : [
                {
                    'type'        : 'Slider',
                    'text'        : self.i18n['UI_setting_newbieDays_text'],
                    'minimum'     : 1,
                    'maximum'     : 90,
                    'snapInterval': 1,
                    'value'       : self.data['newbieDays'],
                    'format'      : '{{value}}%s' % self.i18n['UI_setting_newbieDays_value'],
                    'varName'     : 'newbieDays'
                }, {
                    'type'        : 'Slider',
                    'text'        : self.i18n['UI_setting_newbieWinRate_text'],
                    'minimum'     : 10.0,
                    'maximum'     : 60.0,
                    'snapInterval': 1.0,
                    'value'       : self.data['newbieWinRate'],
                    'format'      : '{{value}}%s' % self.i18n['UI_setting_newbieWinRate_value'],
                    'varName'     : 'newbieWinRate'
                }
            ]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings)
        g_gui.update(self.ids, self.template)


class ChatInfo(object):
    def __init__(self):
        self.dossiers = {}
        self.threadArray = []

    @staticmethod
    def getColor(value):
        color = 'FFFFFF'
        for i, v in enumerate(COLORS):
            if value >= WIN[i]:
                color = v
        return color

    def loadStats(self, databaseID):
        if databaseID in self.dossiers:
            if (datetime.datetime.utcnow() - self.dossiers[databaseID]['time']).total_seconds() < 3600:
                return self.dossiers[databaseID]
        try:
            url = 'https://api.worldoftanks.{region}/wot/account/info/?application_id=demo&fields=created_at%2Cglobal_rating%2Cstatistics.all.wins%2C+statistics.all.battles&account_id={id}'.format(region=self.region(databaseID), id=databaseID)
            request = json.loads(urllib2.urlopen(url, timeout=1).read()).get('data', None)
        except IOError:
            request = None
        if request:
            dossier = request['%s' % databaseID]
            self.dossiers[databaseID] = {
                'newbie' : (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(dossier['created_at'])).total_seconds() < config.data['newbieDays'] * 86400,
                'winRate': float('%.2f' % (dossier['statistics']['all']['wins'] * 100.0 / dossier['statistics']['all']['battles'])) if dossier['statistics']['all']['battles'] else 0.0,
                'time'   : datetime.datetime.utcnow()
            }

    def thread(self, databaseID):
        try:
            self.threadArray.append(threading.Thread(target=self.loadStats, args=(databaseID,)))
            self.threadArray[-1].start()
        except StandardError:
            pass

    def generateText(self, message, result):
        try:
            databaseID = message.originator
            if message.originatorNickName == 'spoter':
                result = result.replace('spoter', '<font color="#D042F3">spoter[мододел]</font>')
            if databaseID in self.dossiers:
                if config.data['showNewbie'] and not message.group:
                    if self.dossiers[databaseID]['newbie'] or chatInfo.dossiers[databaseID]['winRate'] <= config.data['newbieWinRate']:
                        if not chatInfo.dossiers[databaseID]['winRate']:
                            result = result.replace('#979589', '#FE7903')
                        else:
                            result = result.replace('#979589', '%s' %config.i18n['UI_chat_newbieMarkColor'])
                if config.data['showWinRate']:
                    winRate = '<font color="#%s">%s%%</font>' % (self.getColor(chatInfo.dossiers[databaseID]['winRate']), self.dossiers[databaseID]['winRate'])
                    result = result.replace('&nbsp;', '%s' % config.i18n['UI_chat_winRate'].format(winRate=winRate))
        except StandardError:
            pass
        return result

    @staticmethod
    def region(databaseID):
        if databaseID < 500000000:
            return 'ru'
        if databaseID < 1000000000:
            return 'eu'
        if databaseID < 2000000000:
            return 'na'
        return 'asia'

config = Config()
chatInfo = ChatInfo()


@inject.hook(_ChannelController, '_format')
@inject.log
def _format(func, self, message, doFormatting=True):
    chatInfo.thread(message.originator)
    return chatInfo.generateText(message, func(self, message, doFormatting))
