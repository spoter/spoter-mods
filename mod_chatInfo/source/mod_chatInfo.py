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
COLOR = ['#0000FF', '#A52A2B', '#D3691E', '#6595EE', '#FCF5C8', '#00FFFF', '#28F09C', '#FFD700', '#008000', '#ADFF2E', '#FF69B5', '#00FF00', '#FFA500', '#FFC0CB', '#800080', '#FF0000', '#8378FC', '#DB0400', '#80D639', '#FFE041', '#FFFF00', '#FA8072', '#FE0E00', '#FE7903', '#F8F400', '#60FF00', '#02C9B3', '#D042F3']
MENU = ['UI_color_blue', 'UI_color_brown', 'UI_color_chocolate', 'UI_color_cornflower_blue', 'UI_color_cream', 'UI_color_cyan', 'UI_color_emerald', 'UI_color_gold', 'UI_color_green', 'UI_color_green_yellow', 'UI_color_hot_pink', 'UI_color_lime',
        'UI_color_orange', 'UI_color_pink', 'UI_color_purple', 'UI_color_red', 'UI_color_wg_blur', 'UI_color_wg_enemy', 'UI_color_wg_friend', 'UI_color_wg_squad', 'UI_color_yellow', 'UI_color_nice_red', 'UI_color_very_bad', 'UI_color_bad', 'UI_color_normal', 'UI_color_good', 'UI_color_very_good', 'UI_color_unique']


class Config(object):
    def __init__(self):
        self.ids = 'chatInfo'
        self.version = 'v1.05 (2019-04-25)'
        self.version_id = 105
        self.author = 'by spoter'
        self.data = {
            'version'           : self.version_id,
            'enabled'           : True,
            'newbieDays'        : 30,
            'newbieWinRate'     : 46.0,
            'twinkBattles'      : 5.0,
            'showNewbie'        : True,
            'showTwink'         : True,
            'showWinRate'       : True,
            'showBattles'       : True,
            'colorNewbie'       : 11,
            'colorNewbieSpammer': 23,
            'colorTwink'        : 6,
            'colorTwinkSpammer' : 23
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
            'UI_setting_newbieDays_value'          : ' day\'s',
            'UI_setting_newbieWinRate_text'        : 'Newbie winRate status',
            'UI_setting_newbieWinRate_value'       : '%',
            'UI_setting_twinkBattles_text'         : 'Twink battles status',
            'UI_setting_twinkBattles_value'        : 'k',
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
            'UI_color_blue'                        : 'Blue',
            'UI_color_brown'                       : 'Brown',
            'UI_color_chocolate'                   : 'Chocolate',
            'UI_color_cornflower_blue'             : 'Cornflower Blue',
            'UI_color_cream'                       : 'Cream',
            'UI_color_cyan'                        : 'Cyan',
            'UI_color_emerald'                     : 'Emerald',
            'UI_color_gold'                        : 'Gold',
            'UI_color_green'                       : 'Green',
            'UI_color_green_yellow'                : 'Green Yellow',
            'UI_color_hot_pink'                    : 'Hot Pink',
            'UI_color_lime'                        : 'Lime',
            'UI_color_orange'                      : 'Orange',
            'UI_color_pink'                        : 'Pink',
            'UI_color_purple'                      : 'Purple',
            'UI_color_red'                         : 'Red',
            'UI_color_wg_blur'                     : 'WG Blur',
            'UI_color_wg_enemy'                    : 'WG Enemy',
            'UI_color_wg_friend'                   : 'WG Friend',
            'UI_color_wg_squad'                    : 'WG Squad',
            'UI_color_yellow'                      : 'Yellow',
            'UI_color_nice_red'                    : 'Nice Red',
            'UI_color_very_bad'                    : 'Very bad rating',
            'UI_color_bad'                         : 'Bad rating',
            'UI_color_normal'                      : 'Normal rating',
            'UI_color_good'                        : 'Good rating',
            'UI_color_very_good'                   : 'Very good rating',
            'UI_color_unique'                      : 'Unique rating'
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
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
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_setting_colorNewbie_text'],
                    'tooltip'     : self.i18n['UI_setting_colorNewbie_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : self.generator_menu(),
                    'width'       : 200,
                    'value'       : self.data['colorNewbie'],
                    'varName'     : 'colorNewbie'
                }, {
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_setting_colorNewbieSpammer_text'],
                    'tooltip'     : self.i18n['UI_setting_colorNewbieSpammer_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : self.generator_menu(),
                    'width'       : 200,
                    'value'       : self.data['colorNewbieSpammer'],
                    'varName'     : 'colorNewbieSpammer'
                }, {
                    'type'        : 'Slider',
                    'text'        : self.i18n['UI_setting_newbieWinRate_text'],
                    'minimum'     : 10.0,
                    'maximum'     : 60.0,
                    'snapInterval': 1.0,
                    'value'       : self.data['newbieWinRate'],
                    'format'      : '{{value}}%s' % self.i18n['UI_setting_newbieWinRate_value'],
                    'varName'     : 'newbieWinRate'
                }, {
                    'type'        : 'Slider',
                    'text'        : self.i18n['UI_setting_newbieDays_text'],
                    'minimum'     : 1,
                    'maximum'     : 90,
                    'snapInterval': 1,
                    'value'       : self.data['newbieDays'],
                    'format'      : '{{value}}%s' % self.i18n['UI_setting_newbieDays_value'],
                    'varName'     : 'newbieDays'
                }
            ],
            'column2'        : [
                {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showTwink_text'],
                    'value'  : self.data['showTwink'],
                    'tooltip': self.i18n['UI_setting_showTwink_tooltip'],
                    'varName': 'showTwink'
                }, {
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_setting_colorTwink_text'],
                    'tooltip'     : self.i18n['UI_setting_colorTwink_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : self.generator_menu(),
                    'width'       : 200,
                    'value'       : self.data['colorTwink'],
                    'varName'     : 'colorTwink'
                }, {
                    'type'        : 'Dropdown',
                    'text'        : self.i18n['UI_setting_colorTwinkSpammer_text'],
                    'tooltip'     : self.i18n['UI_setting_colorTwinkSpammer_tooltip'],
                    'itemRenderer': 'DropDownListItemRendererSound',
                    'options'     : self.generator_menu(),
                    'width'       : 200,
                    'value'       : self.data['colorTwinkSpammer'],
                    'varName'     : 'colorTwinkSpammer'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showBattles_text'],
                    'value'  : self.data['showBattles'],
                    'tooltip': self.i18n['UI_setting_showBattles_tooltip'],
                    'varName': 'showBattles'
                }, {
                    'type'   : 'CheckBox',
                    'text'   : self.i18n['UI_setting_showWinRate_text'],
                    'value'  : self.data['showWinRate'],
                    'tooltip': self.i18n['UI_setting_showWinRate_tooltip'],
                    'varName': 'showWinRate'
                }, {
                    'type'        : 'Slider',
                    'text'        : self.i18n['UI_setting_twinkBattles_text'],
                    'minimum'     : 0.1,
                    'maximum'     : 12.0,
                    'snapInterval': 0.1,
                    'value'       : self.data['twinkBattles'],
                    'format'      : '{{value}}%s' % self.i18n['UI_setting_twinkBattles_value'],
                    'varName'     : 'twinkBattles'
                }

            ]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)

    def generator_menu(self):
        res = []
        for i in xrange(0, len(COLOR)):
            res.append({
                'label': '<font color="%s">%s</font>' % (COLOR[i], self.i18n[MENU[i]])
            })
        return res


class ChatInfo(object):
    def __init__(self):
        self.dossiers = {}
        self.threadArray = []

    @staticmethod
    def getColor(rating, value):
        color = 'FFFFFF'
        for i, v in enumerate(COLORS):
            if value >= rating[i]:
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
                'battles': float('%.1f' % (dossier['statistics']['all']['battles'] / 1000.0)) if dossier['statistics']['all']['battles'] else 0.0,
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
            if databaseID in self.dossiers:
                if not message.group:
                    if config.data['showNewbie']:
                        if self.dossiers[databaseID]['newbie'] or chatInfo.dossiers[databaseID]['winRate'] <= config.data['newbieWinRate']:
                            if not chatInfo.dossiers[databaseID]['winRate']:
                                result = result.replace('#979589', COLOR[config.data['colorNewbieSpammer']])
                            else:
                                result = result.replace('#979589', '%s' % COLOR[config.data['colorNewbie']])
                    if config.data['showTwink']:
                        if not self.dossiers[databaseID]['newbie'] and chatInfo.dossiers[databaseID]['battles'] <= config.data['twinkBattles']:
                            if not chatInfo.dossiers[databaseID]['winRate']:
                                result = result.replace('#979589', COLOR[config.data['colorTwinkSpammer']])
                            else:
                                result = result.replace('#979589', COLOR[config.data['colorTwink']])
                winRate = ''
                battles = ''
                if config.data['showWinRate']:
                    winRate = '<font color="%s">%s%%</font>' % (self.getColor(WIN, chatInfo.dossiers[databaseID]['winRate']), self.dossiers[databaseID]['winRate'])
                if config.data['showBattles']:
                    battles = '<font color="%s">%sk</font>' % (self.getColor(BATTLES, chatInfo.dossiers[databaseID]['battles']), self.dossiers[databaseID]['battles'])
                if winRate or battles:
                    result = result.replace('&nbsp;', '%s%s' % (config.i18n['UI_chat_battles'].format(battles=battles), config.i18n['UI_chat_winRate'].format(winRate=winRate)))

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
