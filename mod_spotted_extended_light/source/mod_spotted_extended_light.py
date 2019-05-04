# -*- coding: utf-8 -*-

import BigWorld
from Avatar import PlayerAvatar
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from gui.battle_control.controllers import feedback_events
from gui.battle_control.controllers.personal_efficiency_ctrl import _AGGREGATED_DAMAGE_EFFICIENCY_TYPES
# noinspection PyProtectedMember
from gui.mods.mod_mods_gui import g_gui, inject

SOUND_LIST = ['soundSpotted', 'soundAssist']
TEXT_LIST = ['UI_message_Spotted_text', 'UI_message_AssistRadio_text', 'UI_message_AssistTrack_text', 'UI_message_AssistStun_text']
COLOR = ['#0000FF', '#A52A2B', '#D3691E', '#6595EE', '#FCF5C8', '#00FFFF', '#28F09C', '#FFD700', '#008000', '#ADFF2E', '#FF69B5', '#00FF00', '#FFA500', '#FFC0CB', '#800080', '#FF0000', '#8378FC', '#DB0400', '#80D639', '#FFE041', '#FFFF00', '#FA8072']
MENU = ['UI_menu_blue', 'UI_menu_brown', 'UI_menu_chocolate', 'UI_menu_cornflower_blue', 'UI_menu_cream', 'UI_menu_cyan', 'UI_menu_emerald', 'UI_menu_gold', 'UI_menu_green', 'UI_menu_green_yellow', 'UI_menu_hot_pink', 'UI_menu_lime',
        'UI_menu_orange', 'UI_menu_pink', 'UI_menu_purple', 'UI_menu_red', 'UI_menu_wg_blur', 'UI_menu_wg_enemy', 'UI_menu_wg_friend', 'UI_menu_wg_squad', 'UI_menu_yellow', 'UI_menu_nice_red']
GENERATOR = {
    BATTLE_EVENT_TYPE.SPOTTED     : ['UI_message_Spotted_text', 'messageColorSpotted'],
    BATTLE_EVENT_TYPE.RADIO_ASSIST: ['UI_message_AssistRadio_text', 'messageColorAssistRadio'],
    BATTLE_EVENT_TYPE.TRACK_ASSIST: ['UI_message_AssistTrack_text', 'messageColorAssistTrack'],
    BATTLE_EVENT_TYPE.STUN_ASSIST : ['UI_message_AssistStun_text', 'messageColorAssistStun']
}


class Config(object):
    def __init__(self):
        self.ids = 'spotted_extended_light'
        self.version = 'v4.06 (2019-05-04)'
        self.version_id = 406
        self.author = 'by spoter'
        self.data = {
            'version'                : self.version_id,
            'enabled'                : True,
            'sound'                  : True,
            'iconSizeX'              : 47,
            'iconSizeY'              : 16,
            'soundSpotted'           : 'enemy_sighted_for_team',
            'soundAssist'            : 'gun_intuition',
            'messageColorSpotted'    : 10,
            'messageColorAssistRadio': 6,
            'messageColorAssistTrack': 11,
            'messageColorAssistStun' : 5
        }
        self.i18n = {
            'version'                                   : self.version_id,
            'UI_description'                            : 'Spotted extended Light',
            'UI_setting_sound_text'                     : 'Use sound in battle',
            'UI_setting_sound_tooltip'                  : '{HEADER}<font color="#FFD700">Info:</font>{/HEADER}{BODY}Configure sounds in config file: <font color="#FFD700">/mods/configs/spotted_extended_light/spotted_extended_light.json</font>'
                                                          '{/BODY}',
            'UI_setting_iconSizeX_text'                 : 'Icon size X-coordinate',
            'UI_setting_iconSizeX_value'                : ' px.',
            'UI_setting_iconSizeY_text'                 : 'Icon size Y-coordinate',
            'UI_setting_iconSizeY_value'                : ' px.',
            'UI_setting_messageColorSpotted_text'       : 'Color to message "Spotted',
            'UI_setting_messageColorSpotted_tooltip'    : '',
            'UI_setting_messageColorAssistRadio_text'   : 'Color to message "Radio Hit Assist"',
            'UI_setting_messageColorAssistRadio_tooltip': '',
            'UI_setting_messageColorAssistTrack_text'   : 'Color to message "Track Hit Assist"',
            'UI_setting_messageColorAssistTrack_tooltip': '',
            'UI_setting_messageColorAssistStun_text'    : 'Color to message "Stun Hit Assist"',
            'UI_setting_messageColorAssistStun_tooltip' : '',
            'UI_menu_blue'                              : 'Blue',
            'UI_menu_brown'                             : 'Brown',
            'UI_menu_chocolate'                         : 'Chocolate',
            'UI_menu_cornflower_blue'                   : 'Cornflower Blue',
            'UI_menu_cream'                             : 'Cream',
            'UI_menu_cyan'                              : 'Cyan',
            'UI_menu_emerald'                           : 'Emerald',
            'UI_menu_gold'                              : 'Gold',
            'UI_menu_green'                             : 'Green',
            'UI_menu_green_yellow'                      : 'Green Yellow',
            'UI_menu_hot_pink'                          : 'Hot Pink',
            'UI_menu_lime'                              : 'Lime',
            'UI_menu_orange'                            : 'Orange',
            'UI_menu_pink'                              : 'Pink',
            'UI_menu_purple'                            : 'Purple',
            'UI_menu_red'                               : 'Red',
            'UI_menu_wg_blur'                           : 'WG Blur',
            'UI_menu_wg_enemy'                          : 'WG Enemy',
            'UI_menu_wg_friend'                         : 'WG Friend',
            'UI_menu_wg_squad'                          : 'WG Squad',
            'UI_menu_yellow'                            : 'Yellow',
            'UI_menu_nice_red'                          : 'Nice Red',
            'UI_message_Spotted_text'                   : 'Spotted {vehicles}',
            'UI_message_AssistRadio_text'               : 'Assist Radio:{vehicles}{damage}',
            'UI_message_AssistTrack_text'               : 'Assist Track:{vehicles}{damage}',
            'UI_message_AssistStun_text'                : 'Assist Stun:{vehicles}{damage}',
            'UI_message_macrosList'                     : 'Available macros in messages {icons}, {names}, {vehicles}, {icons_names}, {icons_vehicles}, {full}, {damage}'
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
                'text'   : self.i18n['UI_setting_sound_text'],
                'value'  : self.data['sound'],
                'tooltip': self.i18n['UI_setting_sound_tooltip'],
                'varName': 'sound'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_setting_iconSizeX_text'],
                'minimum'     : 5,
                'maximum'     : 150,
                'snapInterval': 1,
                'value'       : self.data['iconSizeX'],
                'format'      : '{{value}}%s [47]' % self.i18n['UI_setting_iconSizeX_value'],
                'varName'     : 'iconSizeX'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_setting_iconSizeY_text'],
                'minimum'     : 5,
                'maximum'     : 150,
                'snapInterval': 1,
                'value'       : self.data['iconSizeY'],
                'format'      : '{{value}}%s [16]' % self.i18n['UI_setting_iconSizeY_value'],
                'varName'     : 'iconSizeY'
            }],
            'column2'        : [{
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_messageColorSpotted_text'],
                'tooltip'     : self.i18n['UI_setting_messageColorSpotted_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['messageColorSpotted'],
                'varName'     : 'messageColorSpotted'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_messageColorAssistRadio_text'],
                'tooltip'     : self.i18n['UI_setting_messageColorAssistRadio_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['messageColorAssistRadio'],
                'varName'     : 'messageColorAssistRadio'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_messageColorAssistTrack_text'],
                'tooltip'     : self.i18n['UI_setting_messageColorAssistTrack_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['messageColorAssistTrack'],
                'varName'     : 'messageColorAssistTrack'
            }, {
                'type'        : 'Dropdown',
                'text'        : self.i18n['UI_setting_messageColorAssistStun_text'],
                'tooltip'     : self.i18n['UI_setting_messageColorAssistStun_tooltip'],
                'itemRenderer': 'DropDownListItemRendererSound',
                'options'     : self.generator_menu(),
                'width'       : 200,
                'value'       : self.data['messageColorAssistStun'],
                'varName'     : 'messageColorAssistStun'
            }]
        }

    def generator_menu(self):
        res = []
        for i in xrange(0, len(COLOR)):
            res.append({
                'label': '<font color="%s">%s</font>' % (COLOR[i], self.i18n[MENU[i]])
            })
        return res

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class Assist(object):
    def __init__(self):
        self.format_str = {}
        self.format_recreate()

    @staticmethod
    def check_macros(macros):
        for i in TEXT_LIST:
            if macros in config.i18n[i]:
                return True

    def format_recreate(self):
        self.format_str = {
            'icons'         : '',
            'names'         : '',
            'vehicles'      : '',
            'icons_names'   : '',
            'icons_vehicles': '',
            'full'          : '',
            'damage'        : ''
        }

    @staticmethod
    def sound(assist_type):
        BigWorld.player().soundNotifications.play(config.data[SOUND_LIST[assist_type]])

    def textGenerator(self, event):
        text, color = GENERATOR[event]
        return config.i18n[text].format(**self.format_str), COLOR[config.data[color]]

    def post_message(self, events):
        g_sessionProvider = BigWorld.player().guiSessionProvider
        self.format_recreate()
        for data in events:
            feedbackEvent = feedback_events.PlayerFeedbackEvent.fromDict(data)
            eventID = feedbackEvent.getBattleEventType()
            if eventID in [BATTLE_EVENT_TYPE.SPOTTED, BATTLE_EVENT_TYPE.RADIO_ASSIST, BATTLE_EVENT_TYPE.TRACK_ASSIST, BATTLE_EVENT_TYPE.STUN_ASSIST]:
                vehicleID = feedbackEvent.getTargetID()
                icon = '<img src="img://%s" width="%s" height="%s" />' % (g_sessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.iconPath.replace('..', 'gui'), config.data['iconSizeX'], config.data['iconSizeY'])
                target_info = g_sessionProvider.getCtx().getPlayerFullNameParts(vID=vehicleID)
                if self.check_macros('{icons}'): self.format_str['icons'] += icon
                if self.check_macros('{names}'): self.format_str['names'] += '[%s]' % target_info[1] if target_info[1] else icon
                if self.check_macros('{vehicles}'): self.format_str['vehicles'] += '[%s]' % target_info[4] if target_info[4] else icon
                if self.check_macros('{icons_names}'): self.format_str['icons_names'] += '%s[%s]' % (icon, target_info[1]) if target_info[1] else icon
                if self.check_macros('{icons_vehicles}'): self.format_str['icons_vehicles'] += '%s[%s]' % (icon, target_info[4]) if target_info[4] else icon
                if self.check_macros('{damage}'):
                    extra = feedbackEvent.getExtra()
                    if extra and feedbackEvent.getType() in _AGGREGATED_DAMAGE_EFFICIENCY_TYPES: self.format_str['damage'] += ' +%s' % extra.getDamage()
                if self.check_macros('{full}'):
                    self.format_str['full'] += '%s[%s]' % (icon, target_info) if target_info else icon
                if eventID == BATTLE_EVENT_TYPE.SPOTTED:
                    if config.data['sound']: assist.sound(0)
                else:
                    if config.data['sound']: assist.sound(1)
                text, color = self.textGenerator(eventID)
                inject.message(text, color)


config = Config()
assist = Assist()


@inject.hook(PlayerAvatar, 'onBattleEvents')
@inject.log
def onBattleEvents(func, *args):
    func(*args)
    assist.post_message(args[1])
