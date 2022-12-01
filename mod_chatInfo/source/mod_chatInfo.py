# -*- coding: utf-8 -*-
import datetime
import json
import threading
import urllib2

# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

# noinspection PyProtectedMember
from messenger.gui.Scaleform.channels.bw.lobby_controllers import _ChannelController

COLORS = ['#FE0E00', '#FE7903', '#F8F400', '#60FF00', '#02C9B3', '#D042F3']
WIN = [0.0, 46.5, 48.5, 52.5, 57.5, 64.5]
BATTLES = [0.0, 2.0, 6.0, 16.0, 30.0, 43.0]


class Config(object):
    def __init__(self):
        self.ids = 'chatInfo'
        self.version = 'v2.01 (2022-12-01)'
        self.version_id = 201
        self.author = 'by spoter'
        self.dataDefault = {
            'version'           : self.version_id,
            'enabled'           : True,
            'newbieDays'        : 30,
            'newbieWinRate'     : 46.0,
            'twinkBattles'      : 5.0,
            'showNewbie'        : True,
            'showTwink'         : True,
            'showWinRate'       : True,
            'showBattles'       : True,
            'colorNewbie'       : '#00FF00',
            'colorNewbieSpammer': '#FE7903',
            'colorTwink'        : '#28F09C',
            'colorTwinkSpammer' : '#FE7903'
        }
        self.i18n = {
            'version'                              : self.version_id,
            'UI_description'                       : 'Chat Info',
            'UI_setting_showNewbie_text'           : 'Show Newbie status in chat',
            'UI_setting_showNewbie_tooltip'        : '{HEADER}<font color="#FFD700">Info:</font>{/HEADER}{BODY}Newbie status:\n<font color="#FFD700">low played days\nlow winRate</font>{/BODY}',
            'UI_setting_showWinRate_text'          : 'Show winRate to user in chat',
            'UI_setting_showWinRate_tooltip'       : '',
            'UI_setting_showTwink_text'            : 'Show Twink status in chat',
            'UI_setting_showTwink_tooltip'         : '{HEADER}<font color="#FFD700">Info:</font>{/HEADER}{BODY}Twink status:\n<font color="#FFD700">low played battles</font>{/BODY}',
            'UI_setting_showBattles_text'          : 'Show Battles to user in chat',
            'UI_setting_showBattles_tooltip'       : '',
            'UI_setting_newbieDays_text'           : 'How long is a newbie',
            'UI_setting_newbieDays_formats'        : ' day\'s',
            'UI_setting_newbieWinRate_text'        : 'Newbie winRate status',
            'UI_setting_newbieWinRate_formats'     : '%',
            'UI_setting_twinkBattles_text'         : 'Twink battles status',
            'UI_setting_twinkBattles_formats'      : 'k',
            'UI_setting_colorNewbie_text'          : 'Newbie Color in chat',
            'UI_setting_colorNewbie_tooltip'       : '',
            'UI_setting_colorNewbieSpammer_text'   : 'Newbie Spammer Color in chat',
            'UI_setting_colorNewbieSpammer_tooltip': '{HEADER}<font color="#FFD700">Info:</font>{/HEADER}{BODY}Spammer status:\n<font color="#FFD700">0% WinRate</font>{/BODY}',
            'UI_setting_colorTwink_text'           : 'Twink Color in chat',
            'UI_setting_colorTwink_tooltip'        : '',
            'UI_setting_colorTwinkSpammer_text'    : 'Twink Spammer Color in chat',
            'UI_setting_colorTwinkSpammer_tooltip' : '{HEADER}<font color="#FFD700">Info:</font>{/HEADER}{BODY}Spammer status:\n<font color="#FFD700">0% WinRate</font>{/BODY}',
            'UI_chat_winRate'                      : '[{winRate}]',
            'UI_chat_battles'                      : '[{battles}]',
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.dataDefault, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [
                g_gui.optionCheckBox(*self.getI18nParam('showNewbie')),
                g_gui.optionColorHEX(*self.getI18nParam('colorNewbie')),
                g_gui.optionColorHEX(*self.getI18nParam('colorNewbieSpammer')),
                g_gui.optionSlider(*self.getI18nParamSlider('newbieWinRate', 10, 60, 1)),
                g_gui.optionSlider(*self.getI18nParamSlider('newbieDays', 1, 90, 1)),
            ],
            'column2'        : [
                g_gui.optionCheckBox(*self.getI18nParam('showTwink')),
                g_gui.optionColorHEX(*self.getI18nParam('colorTwink')),
                g_gui.optionColorHEX(*self.getI18nParam('colorTwinkSpammer')),
                g_gui.optionCheckBox(*self.getI18nParam('showBattles')),
                g_gui.optionCheckBox(*self.getI18nParam('showWinRate')),
                g_gui.optionSlider(*self.getI18nParamSlider('twinkBattles', 0.1, 12.0, 0.1)),

            ]
        }

    def getI18nParam(self, name):
        # return varName, value, defaultValue, text, tooltip, defaultValueText
        tooltip = 'UI_setting_%s_tooltip' % name
        tooltip = self.i18n[tooltip] if tooltip in self.i18n else ''
        defaultValueText = 'UI_setting_%s_default' % name
        defaultValueText = self.i18n[defaultValueText] if defaultValueText in self.i18n else '%s' % self.dataDefault[name]
        return name, self.data[name], self.dataDefault[name], self.i18n['UI_setting_%s_text' % name], tooltip, defaultValueText

    def getI18nParamSlider(self, name, minValue, maxValue, step):
        # return varName, value, defaultValue, minValue, maxValue, step, text, formats, tooltip, defaultValueText
        params = self.getI18nParam(name)
        formats = 'UI_setting_%s_formats' % name
        formats = self.i18n[formats] if formats in self.i18n else ''
        return params[0], params[1], params[2], minValue, maxValue, step, params[3], formats, params[4], params[5]

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class ChatInfo(object):
    def __init__(self):
        self.dossiers = {}
        self.threadArray = []

    @staticmethod
    def getColor(rating, value):
        color = '#FFFFFF'
        for i, v in enumerate(COLORS):
            if value >= rating[i]:
                color = v
        return color

    def loadStats(self, databaseID):
        if databaseID in self.dossiers:
            if (datetime.datetime.utcnow() - self.dossiers[databaseID]['time']).total_seconds() < 3600:
                return self.dossiers[databaseID]
        try:
            url = 'https://api.worldoftanks.{region}/wot/account/info/?application_id=7c185c71df3e4d3190f0733df31b9f5f&fields=created_at%2Cglobal_rating%2Cstatistics.all.wins%2C+statistics.all.battles&account_id={id}'.format(region=self.region(databaseID), id=databaseID)
            request = json.loads(urllib2.urlopen(url, timeout=1).read()).get('data', None)
        except IOError as e:
            print 'LOG ERROR[chatInfo] IOError: %s' % str(e)
            request = None
        if request:
            dossier = request['%s' % databaseID]
            self.dossiers[databaseID] = {
                'newbie' : (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(dossier['created_at'])).total_seconds() < config.data['newbieDays'] * 86400,
                'winRate': float('%.2f' % (dossier['statistics']['all']['wins'] * 100.0 / dossier['statistics']['all']['battles'])) if dossier['statistics']['all']['battles'] else 0.0,
                'battles': float('%.1f' % (dossier['statistics']['all']['battles'] / 1000.0)) if dossier['statistics']['all']['battles'] else 0.0,
                'time'   : datetime.datetime.utcnow()
            }

    def thread(self, databaseID):
        try:
            self.threadArray.append(threading.Thread(target=self.loadStats, args=(databaseID,)))
            self.threadArray[-1].start()
        except StandardError as e:
            print 'LOG ERROR[chatInfo] StandardError: %s' % str(e)

    def generateText(self, message, result):
        try:
            databaseID = message.originator
            if databaseID in self.dossiers:
                if not message.group:
                    if config.data['showNewbie']:
                        if self.dossiers[databaseID]['newbie'] or chatInfo.dossiers[databaseID]['winRate'] <= config.data['newbieWinRate']:
                            if not chatInfo.dossiers[databaseID]['winRate']:
                                result = result.replace('#979589', config.data['colorNewbieSpammer'])
                            else:
                                result = result.replace('#979589', '%s' % config.data['colorNewbie'])
                    if config.data['showTwink']:
                        if not self.dossiers[databaseID]['newbie'] and chatInfo.dossiers[databaseID]['battles'] <= config.data['twinkBattles']:
                            if not chatInfo.dossiers[databaseID]['winRate']:
                                result = result.replace('#979589', config.data['colorTwinkSpammer'])
                            else:
                                result = result.replace('#979589', config.data['colorTwink'])
                winRate = ''
                battles = ''
                if config.data['showWinRate']:
                    winRate = '<font color="%s">%s%%</font>' % (self.getColor(WIN, chatInfo.dossiers[databaseID]['winRate']), self.dossiers[databaseID]['winRate'])
                if config.data['showBattles']:
                    battles = '<font color="%s">%sk</font>' % (self.getColor(BATTLES, chatInfo.dossiers[databaseID]['battles']), self.dossiers[databaseID]['battles'])
                if winRate or battles:
                    result = result.replace('&nbsp;', '%s%s' % (config.i18n['UI_chat_battles'].format(battles=battles), config.i18n['UI_chat_winRate'].format(winRate=winRate)))

        except StandardError as e:
            print 'LOG ERROR[chatInfo] StandardError: %s' % str(e)
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
