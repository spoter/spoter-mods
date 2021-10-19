# -*- coding: utf-8 -*-

import BigWorld
from Avatar import PlayerAvatar
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from gui.battle_control.controllers import feedback_events
# noinspection PyProtectedMember
from gui.battle_control.controllers.personal_efficiency_ctrl import _AGGREGATED_DAMAGE_EFFICIENCY_TYPES, _createEfficiencyInfoFromFeedbackEvent
# noinspection PyProtectedMember,PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

SOUND_LIST = ['soundSpotted', 'soundAssist']
TEXT_LIST = ['macros_Spotted', 'macros_AssistRadio', 'macros_AssistTrack', 'macros_AssistStun']

GENERATOR = {
    BATTLE_EVENT_TYPE.SPOTTED     : ['UI_message_Spotted_text', 'messageColorSpotted', 'macros_Spotted'],
    BATTLE_EVENT_TYPE.RADIO_ASSIST: ['UI_message_AssistRadio_text', 'messageColorAssistRadio', 'macros_AssistRadio'],
    BATTLE_EVENT_TYPE.TRACK_ASSIST: ['UI_message_AssistTrack_text', 'messageColorAssistTrack', 'macros_AssistTrack'],
    BATTLE_EVENT_TYPE.STUN_ASSIST : ['UI_message_AssistStun_text', 'messageColorAssistStun', 'macros_AssistStun']
}


class Config(object):
    def __init__(self):
        self.ids = 'spotted_extended_light'
        self.version = 'v4.11 (2021-10-19)'
        self.version_id = 411
        self.author = 'by spoter'
        self.data = {
            'version'                : self.version_id,
            'enabled'                : True,
            'sound'                  : True,
            'iconSizeX'              : 47,
            'iconSizeY'              : 16,
            'soundSpotted'           : 'enemy_sighted_for_team',
            'soundAssist'            : 'gun_intuition',
            'messageColorSpotted'    : '#FF69B5',
            'messageColorAssistRadio': '#28F09C',
            'messageColorAssistTrack': '#00FF00',
            'messageColorAssistStun' : '#00FFFF',
            'macros_Spotted': '{vehicles}',
            'macros_AssistRadio': '{vehicles}{damage}',
            'macros_AssistTrack': '{vehicles}{damage}',
            'macros_AssistStun': '{vehicles}{damage}',
        }
        self.i18n = {
            'version'                                   : self.version_id,
            'UI_description'                            : 'Spotted extended Light',
            'UI_setting_sound_text'                     : 'Use sound in battle',
            'UI_setting_sound_tooltip'                  : '',
            'UI_setting_sound_default'                  : 'Default: %s' % ('On' if self.data['sound'] else 'Off'),
            'UI_setting_soundSpotted_text'              : 'ID sound to Spotted',
            'UI_setting_soundSpotted_tooltip'           : '',
            'UI_setting_soundSpotted_default'           : 'Default: %s' % self.data['soundSpotted'],
            'UI_setting_soundAssist_text'               : 'ID sound to Assist',
            'UI_setting_soundAssist_tooltip'            : '',
            'UI_setting_soundAssist_default'            : 'Default: %s' % self.data['soundAssist'],
            'UI_setting_iconSizeX_text'                 : 'Icon size X-coordinate',
            'UI_setting_iconSizeX_value'                : ' px.',
            'UI_setting_iconSizeX_tooltip'              : '',
            'UI_setting_iconSizeX_default'              : 'Default: %s' % self.data['iconSizeX'],
            'UI_setting_iconSizeY_text'                 : 'Icon size Y-coordinate',
            'UI_setting_iconSizeY_value'                : ' px.',
            'UI_setting_iconSizeY_tooltip'              : '',
            'UI_setting_iconSizeY_default'              : 'Default: %s' % self.data['iconSizeY'],
            'UI_setting_messageColorSpotted_text'       : 'Color to message "Spotted',
            'UI_setting_messageColorSpotted_tooltip'    : '',
            'UI_setting_messageColorSpotted_default'    : 'Default: %s' % self.data['messageColorSpotted'],
            'UI_setting_messageColorAssistRadio_text'   : 'Color to message "Radio Hit Assist"',
            'UI_setting_messageColorAssistRadio_tooltip': '',
            'UI_setting_messageColorAssistRadio_default': 'Default: %s' % self.data['messageColorAssistRadio'],
            'UI_setting_messageColorAssistTrack_text'   : 'Color to message "Track Hit Assist"',
            'UI_setting_messageColorAssistTrack_tooltip': '',
            'UI_setting_messageColorAssistTrack_default': 'Default: %s' % self.data['messageColorAssistTrack'],
            'UI_setting_messageColorAssistStun_text'    : 'Color to message "Stun Hit Assist"',
            'UI_setting_messageColorAssistStun_tooltip' : '',
            'UI_setting_messageColorAssistStun_default' : 'Default: %s' % self.data['messageColorAssistStun'],
            'UI_message_Spotted_text'                   : 'Spotted:',
            'UI_message_Spotted_default'                : 'Default: %s' % self.data['macros_Spotted'],
            'UI_message_Spotted_description'            : 'Macros: Spotted',
            'UI_message_AssistRadio_text'               : 'Assist Radio:',
            'UI_message_AssistRadio_default'            : 'Default: %s' % self.data['macros_AssistRadio'],
            'UI_message_AssistRadio_description'        : 'Macros: Assist Radio',
            'UI_message_AssistTrack_text'               : 'Assist Track:',
            'UI_message_AssistTrack_default'            : 'Default: %s' % self.data['macros_AssistTrack'],
            'UI_message_AssistTrack_description'        : 'Macros: Assist Track',
            'UI_message_AssistStun_text'                : 'Assist Stun:',
            'UI_message_AssistStun_default'             : 'Default: %s' % self.data['macros_AssistStun'],
            'UI_message_AssistStun_description'         : 'Macros: Assist Stun',
            'UI_message_macrosList'                     : 'Available macros in messages {icons}, {names}, {vehicles}, {icons_names}, {icons_vehicles}, {full}, {damage}'
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {'modDisplayName': self.i18n['UI_description'], 'settingsVersion': self.version_id, 'enabled': self.data['enabled'], 'column1': self._getLeftOptions(), 'column2': self._getRightOptions()}

    def _getLeftOptions(self):
        return [
            g_gui.optionCheckBox('sound', self.data['sound'], self.i18n['UI_setting_sound_text'], self.i18n['UI_setting_sound_tooltip'], self.i18n['UI_setting_sound_default']),
            g_gui.optionSlider('iconSizeX', self.data['iconSizeX'], 5, 150, 1, self.i18n['UI_setting_iconSizeX_text'], self.i18n['UI_setting_iconSizeX_value'], self.i18n['UI_setting_iconSizeX_tooltip'], self.i18n['UI_setting_iconSizeX_default']),
            g_gui.optionSlider('iconSizeY', self.data['iconSizeY'], 5, 150, 1, self.i18n['UI_setting_iconSizeY_text'], self.i18n['UI_setting_iconSizeY_value'], self.i18n['UI_setting_iconSizeY_tooltip'], self.i18n['UI_setting_iconSizeY_default']),
            g_gui.optionColorHEX('messageColorSpotted', self.data['messageColorSpotted'], self.i18n['UI_setting_messageColorSpotted_text'], self.i18n['UI_setting_messageColorSpotted_tooltip'], self.i18n['UI_setting_messageColorSpotted_default']),
            g_gui.optionColorHEX('messageColorAssistRadio', self.data['messageColorAssistRadio'], self.i18n['UI_setting_messageColorAssistRadio_text'], self.i18n['UI_setting_messageColorAssistRadio_tooltip'], self.i18n['UI_setting_messageColorAssistRadio_default']),
            g_gui.optionColorHEX('messageColorAssistTrack', self.data['messageColorAssistTrack'], self.i18n['UI_setting_messageColorAssistTrack_text'], self.i18n['UI_setting_messageColorAssistTrack_tooltip'], self.i18n['UI_setting_messageColorAssistTrack_default']),
            g_gui.optionColorHEX('messageColorAssistStun', self.data['messageColorAssistStun'], self.i18n['UI_setting_messageColorAssistStun_text'], self.i18n['UI_setting_messageColorAssistStun_tooltip'], self.i18n['UI_setting_messageColorAssistStun_default']),
            g_gui.optionTextInput('soundSpotted', self.data['soundSpotted'], self.i18n['UI_setting_soundSpotted_text'], self.i18n['UI_setting_soundSpotted_tooltip'], self.i18n['UI_setting_soundSpotted_default']),
            g_gui.optionTextInput('soundAssist', self.data['soundAssist'], self.i18n['UI_setting_soundAssist_text'], self.i18n['UI_setting_soundAssist_tooltip'], self.i18n['UI_setting_soundAssist_default']),
            g_gui.optionTextInput('macros_Spotted', self.data['macros_Spotted'], self.i18n['UI_message_Spotted_description'], self.i18n['UI_message_macrosList'], self.i18n['UI_message_Spotted_default']),
            g_gui.optionTextInput('macros_AssistRadio', self.data['macros_AssistRadio'], self.i18n['UI_message_AssistRadio_description'], self.i18n['UI_message_macrosList'], self.i18n['UI_message_AssistRadio_default']),
            g_gui.optionTextInput('macros_AssistTrack', self.data['macros_AssistTrack'], self.i18n['UI_message_AssistTrack_description'], self.i18n['UI_message_macrosList'], self.i18n['UI_message_AssistTrack_default']),
            g_gui.optionTextInput('macros_AssistStun', self.data['macros_AssistStun'], self.i18n['UI_message_AssistStun_description'], self.i18n['UI_message_macrosList'], self.i18n['UI_message_AssistStun_default']),

        ]

    # noinspection PyMethodMayBeStatic
    def _getRightOptions(self):
        return []

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
            if macros in config.data[i]:
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
        text, color, macros = GENERATOR[event]
        return '%s%s' %(config.i18n[text], config.data[macros].format(**self.format_str)), config.data[color]

    def post_message(self, events):
        if not config.data['enabled']:
            return
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
                if self.check_macros('{names}'): self.format_str['names'] += '[<b>%s</b>]' % target_info.playerName if target_info.playerName else icon
                if self.check_macros('{vehicles}'): self.format_str['vehicles'] += '[<b>%s</b>]' % target_info.vehicleName if target_info.vehicleName else icon
                if self.check_macros('{icons_names}'): self.format_str['icons_names'] += '%s[<b>%s</b>]' % (icon, target_info.playerName) if target_info.playerName else icon
                if self.check_macros('{icons_vehicles}'): self.format_str['icons_vehicles'] += '%s[<b>%s</b>]' % (icon, target_info.vehicleName) if target_info.vehicleName else icon
                if self.check_macros('{damage}'):
                    extra = _createEfficiencyInfoFromFeedbackEvent(feedbackEvent)
                    if extra and extra.getType() in _AGGREGATED_DAMAGE_EFFICIENCY_TYPES: self.format_str['damage'] += '<b> +%s</b>' % extra.getDamage()
                if self.check_macros('{full}'):
                    self.format_str['full'] += '%s[<b>%s</b>]' % (icon, target_info) if target_info else icon
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
