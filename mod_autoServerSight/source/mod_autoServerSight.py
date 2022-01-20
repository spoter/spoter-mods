# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

import BigWorld
from Avatar import PlayerAvatar
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import getLanguageCode


class _Config(object):
    def __init__(self):
        self.ids = 'autoServerSight'
        self.version = 'v1.02 (2022-01-20)'
        self.version_id = 102
        self.author = 'by spoter'
        self.dataDefault = {
            'version'   : self.version_id,
            'enabled'   : True,
            'lightTank' : False,
            'mediumTank': False,
            'heavyTank' : False,
            'SPG'       : True,
            'AT-SPG'    : False,
        }
        self.i18n = {
            'version'                   : self.version_id,
            'UI_description'            : 'Auto server sight',
            'UI_setting_lightTank_text' : 'to LT',
            'UI_setting_mediumTank_text': 'to MT',
            'UI_setting_heavyTank_text' : 'to HT',
            'UI_setting_SPG_text'       : 'to Arty',
            'UI_setting_AT-SPG_text'    : 'to AT',
        }
        if 'ru' in '%s'.lower() % getLanguageCode():
            self.i18n.update({
                'UI_description'            : 'Автоматический серверный прицел',
                'UI_setting_lightTank_text' : 'для ЛТ',
                'UI_setting_mediumTank_text': 'для СТ',
                'UI_setting_heavyTank_text' : 'для ТТ',
                'UI_setting_SPG_text'       : 'для Арты',
                'UI_setting_AT-SPG_text'    : 'для ПТ',
            })
        self.data, self.i18n = g_gui.register_data(self.ids, self.dataDefault, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [
                g_gui.optionCheckBox(*self.p__getI18nParam('lightTank')),
                g_gui.optionCheckBox(*self.p__getI18nParam('mediumTank')),
                g_gui.optionCheckBox(*self.p__getI18nParam('heavyTank')),
                g_gui.optionCheckBox(*self.p__getI18nParam('SPG')),
                g_gui.optionCheckBox(*self.p__getI18nParam('AT-SPG')),
            ],
            'column2'        : []
        }

    def p__getI18nParam(self, name):
        # return varName, value, defaultValue, text, tooltip, defaultValueText
        tooltip = 'UI_setting_%s_tooltip' % name
        tooltip = self.i18n[tooltip] if tooltip in self.i18n else ''
        defaultValueText = 'UI_setting_%s_default' % name
        defaultValueText = self.i18n[defaultValueText] if defaultValueText in self.i18n else '%s' % self.dataDefault[name]
        return name, self.data[name], self.dataDefault[name], self.i18n['UI_setting_%s_text' % name], tooltip, defaultValueText

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class Support(object):

    @inject.log
    def waitCallback(self):
        if _config.data['enabled']:
            player = BigWorld.player()
            if not player:
                return
            try:
                vehicleType = Vehicle.getVehicleClassTag(BigWorld.player().getVehicleDescriptor().type.tags)
            except StandardError:
                vehicleType = None
            showServerMarker = vehicleType in _config.data and _config.data[vehicleType]
            if self.p__checkServerAimStatus(showServerMarker):
                inject.message('{0}: {1}'.format(_config.i18n['UI_description'], _config.i18n['UI_setting_%s_text' %vehicleType]))

    def startBattle(self):
        self.p__checkServerAimStatus()
        BigWorld.callback(5.0, self.waitCallback)

    def endBattle(self):
        self.p__checkServerAimStatus()

    def p__checkServerAimStatus(self, showServerMarker=None):
        player = BigWorld.player()
        if not player or not _config.data['enabled']:
            return
        try:
            if showServerMarker is None:
                showServerMarker = player.gunRotator.settingsCore.getSetting('useServerAim')
            player.gunRotator.showServerMarker = showServerMarker
            player.gunRotator._VehicleGunRotator__set_showServerMarker(showServerMarker)
            return True
        except StandardError:
            return


# start mod
_config = _Config()
support = Support()


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    support.startBattle()


@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
@inject.log
def hookDestroyGUI(func, *args):
    support.endBattle()
    func(*args)
