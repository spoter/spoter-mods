# -*- coding: utf-8 -*-
from AvatarInputHandler import gun_marker_ctrl
from gui.mods.mod_mods_gui import g_gui, inject


class _Config(object):
    def __init__(self):
        self.ids = 'artyCrosshair'
        self.version = 'v2.00 (2017-05-03)'
        self.version_id = 200
        self.author = 'by spoter, reven86'
        self.data = {
            'version': self.version_id,
            'enabled': True
        }
        self.i18n = {
            'version'                 : self.version_id,
            'UI_description'          : 'Arty Crosshair',
            'UI_setting_Label_text'   : 'Change Strategic crosshair to Arcade',
            'UI_setting_Label_tooltip': ''
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n)
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print '[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author)

    def template(self):
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'   : 'Label',
                'text'   : self.i18n['UI_setting_Label_text'],
                'tooltip': self.i18n['UI_setting_Label_tooltip'],
            }],
            'column2'        : []
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings)
        g_gui.update(self.ids, self.template)


config = _Config()


# noinspection PyProtectedMember
@inject.hook(gun_marker_ctrl, 'createGunMarker')
@inject.log
def hookedCreateGunMarker(func, isStrategic):
    status = isStrategic
    if config.data['enabled']:
        status = False
    return func(status)



'''
# noinspection PyProtectedMember
@inject.hook(control_modes._FlashGunMarker, 'updateAim')
@inject.log
def hookedCreateGunMarker(func, self):
    func(self)
    self._aim['strategic'] = self.settingsCore.getSetting('arcade')
    
'''
