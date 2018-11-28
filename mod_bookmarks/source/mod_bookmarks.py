# -*- coding: utf-8 -*-

import BigWorld
import re
from gui.mods.mod_mods_gui import browser, g_gui, inject
from notification.NotificationListView import NotificationListView
from notification.settings import NOTIFICATION_GROUP


class Config(object):
    def __init__(self):
        self.ids = 'bookmarks'
        self.version = 'v1.01 (2018-11-28)'
        self.version_id = 101
        self.author = 'by spoter'
        self.data = {
            'version'  : self.version_id,
            'enabled'  : True,
            'showLiked': True,
            'showMods' : True,
            'showStats': True,
            'showNews' : True,
            'showBlog' : True,
            'liked'    : [
                ['Канал Вспышки', 'https://www.youtube.com/user/VspishkaArm/videos'],
                ['Канал ТоТ СаМый CEZAR', 'https://www.youtube.com/user/UC1HLYmxSmpQ_plKZw6QNwfg/videos'],
                ['Канал KorbenDallas', 'https://www.youtube.com/user/UCHJUP0eG8AiejFG_xkJGbRA/videos'],
                ['Всё актуальное и самое важное о мире Танков.', 'http://vk.com/wotclue'],
            ],
            'mods'     : [
                ['wotspeak.ru', 'http://wotspeak.ru'],
                ['wotsite.net', 'http://wotsite.net'],
                ['wgmods.net', 'https://wgmods.net'],
                ['aces.gg', 'http://aces.gg/mods/'],
                ['res-mods.ru', 'http://res-mods.ru']
            ],
            'stats'    : [
                ['kttc.ru', 'https://kttc.ru/wot/ru/user/{}'],
                ['wot-news.com', 'http://wot-news.com/stat/nstat/ru/ru/{}'],
                ['noobmeter.com', 'http://www.noobmeter.com/player/ru/{}'],
                ['wotomatic.net ', 'http://wotomatic.net/?search={}']
            ],
            'news'     : [
                ['Новости World of Tanks каждый день', 'http://wot-news.com'],
                ['Новости WoT на официальном сайте', 'http://worldoftanks.ru/ru/news/'],
                ['Всё актуальное и самое важное о мире Танков.', 'http://vk.com/wotclue'],
                ['Последняя информация о будущих обновлениях', 'http://vk.com/wotleaks'],
            ],
            'blog'     : [
                ['Канал Вспышки', 'https://www.youtube.com/user/VspishkaArm/videos'],
                ['Канал Near_You', 'https://www.youtube.com/user/alexeykuchkin/videos'],
                ['Канал ТоТ СаМый CEZAR', 'https://www.youtube.com/channel/UC1HLYmxSmpQ_plKZw6QNwfg/videos'],
                ['Канал KorbenDallas', 'https://www.youtube.com/channel/UCHJUP0eG8AiejFG_xkJGbRA/videos'],
                ['Канал G1deon', 'https://www.youtube.com/user/gdwintmn/videos'],
                ['Канал GrimOptimist', 'https://www.youtube.com/user/dmitryamba/videos'],
                ['Канал jmr WoT', 'https://www.youtube.com/user/JMRWoT/videos'],
                ['Канал Fermani WoT', 'https://www.youtube.com/user/fermani1/videos'],
                ['Канал Rados23 K.R.S', 'https://www.youtube.com/channel/UCohZi_kki3pz_p9wSAXeGzg/videos'],
                ['Канал Amway921', 'https://www.youtube.com/user/Amway921WOT/videos'],
                ['Канал DeSeRtod', 'https://www.youtube.com/user/DeSeRtodTV/videos'],
                ['Канал Arti25', 'https://www.youtube.com/user/TheArti25/videos'],
                ['Канал EviL_GrannY', 'https://www.youtube.com/channel/UCIIOIYlkNb6vFftQV-nUhDQ/videos'],
            ]
        }
        self.i18n = {
            'version'                     : self.version_id,
            'UI_description'              : 'Bookmarks',
            'UI_setting_showLiked_text'   : 'Show Liked site bookmarks',
            'UI_setting_showLiked_tooltip': '',
            'UI_setting_showMods_text'    : 'Show Mods site bookmarks',
            'UI_setting_showMods_tooltip' : '',
            'UI_setting_showStats_text'   : 'Show Statistics site bookmarks',
            'UI_setting_showStats_tooltip': '',
            'UI_setting_showNews_text'    : 'Show News site bookmarks',
            'UI_setting_showNews_tooltip' : '',
            'UI_setting_showBlog_text'    : 'Show Blog Bookmarks',
            'UI_setting_showBlog_tooltip' : '',
            'UI_setting_config_text'      : 'Links list in config: /mods/configs/bookmarks/bookmarks.json',
            'UI_setting_config_tooltip'   : '',
            'UI_setting_message_liked'    : 'Liked site bookmarks',
            'UI_setting_message_mods'     : 'Mods site bookmarks',
            'UI_setting_message_stats'    : 'Statistics site bookmarks',
            'UI_setting_message_news'     : 'News site bookmarks',
            'UI_setting_message_blog'     : 'Blog Bookmarks',
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_showLiked_text'],
                'value'  : self.data['showLiked'],
                'tooltip': self.i18n['UI_setting_showLiked_tooltip'],
                'varName': 'showLiked'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_showMods_text'],
                'value'  : self.data['showMods'],
                'tooltip': self.i18n['UI_setting_showMods_tooltip'],
                'varName': 'showMods'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_showStats_text'],
                'value'  : self.data['showStats'],
                'tooltip': self.i18n['UI_setting_showStats_tooltip'],
                'varName': 'showStats'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_showNews_text'],
                'value'  : self.data['showNews'],
                'tooltip': self.i18n['UI_setting_showNews_tooltip'],
                'varName': 'showNews'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_showBlog_text'],
                'value'  : self.data['showBlog'],
                'tooltip': self.i18n['UI_setting_showBlog_tooltip'],
                'varName': 'showBlog'
            }, {
                'type'   : 'Label',
                'text'   : self.i18n['UI_setting_config_text'],
                'tooltip': self.i18n['UI_setting_config_tooltip'],
            }],
            'column2'        : []
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class Messages(object):
    def __init__(self):
        pass

    @staticmethod
    def createMessage(status, priority):
        message = {
            'typeID'              : 1,
            'entityID'            : 999000 + priority,
            'message'             : {'bgIcon'       : '',
                                     'defaultIcon'  : '',
                                     'savedData'    : 0,
                                     'timestamp'    : -1,
                                     'filters'      : [],
                                     'buttonsLayout': [],
                                     'message'      : '',
                                     'type'         : 'black',
                                     'icon'         : 'img://gui/maps/icons/buttons/search.png'
                                     },
            'hidingAnimationSpeed': 1.0,
            'notify'              : False,
            'auxData'             : ['PowerLevel']}
        links = ''
        if status == 'showLiked':
            message['message']['message'] = '%s\n' % config.i18n['UI_setting_message_liked']
            links = 'liked'

        if status == 'showMods':
            message['message']['message'] = '%s\n' % config.i18n['UI_setting_message_mods']
            links = 'mods'

        if status == 'showStats':
            message['message']['message'] = '%s\n' % config.i18n['UI_setting_message_stats']
            links = 'stats'

        if status == 'showNews':
            message['message']['message'] = '%s\n' % config.i18n['UI_setting_message_news']
            links = 'news'

        if status == 'showBlog':
            message['message']['message'] = '%s\n' % config.i18n['UI_setting_message_blog']
            links = 'blog'
        if links:
            for obj in config.data[links]:
                message['message']['message'] += '<a href="event:%s">%s</a>\n' % (obj[1], obj[0])
        return message

    def popUpGenerator(self):
        message = []
        if config.data['showMods']:
            message.append(self.createMessage('showMods', 1))
        if config.data['showStats']:
            message.append(self.createMessage('showStats', 2))
        if config.data['showNews']:
            message.append(self.createMessage('showNews', 3))
        if config.data['showBlog']:
            message.append(self.createMessage('showBlog', 4))
        if config.data['showLiked']:
            message.append(self.createMessage('showLiked', 5))
        return message

    @staticmethod
    def openLink(entityID, action):
        if entityID in xrange(999001, 999006):
            if re.match('https?://', action, re.I):
                if entityID == 999002:
                    action = action.format(BigWorld.player().name)
                browser.open(action)
                return True
        return


config = Config()
messages = Messages()


@inject.hook(NotificationListView, '_NotificationListView__getMessagesList')
@inject.log
def hookNotificationListViewGetMessagesList(func, *args):
    result = func(*args)
    # noinspection PyProtectedMember
    if args[0]._NotificationListView__currentGroup == NOTIFICATION_GROUP.OFFER:
        result.extend(messages.popUpGenerator())
    return result


@inject.hook(NotificationListView, 'onClickAction')
@inject.log
def hookNotificationListViewOnClickAction(func, *args):
    if messages.openLink(args[2], args[3]):
        return
    func(*args)
