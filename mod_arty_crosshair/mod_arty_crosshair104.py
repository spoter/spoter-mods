# -*- coding: utf-8 -*-
from AvatarInputHandler import control_modes
from gui.mods.mod_mods_gui import g_gui, inject

class _Config(object):
    def __init__(self):
        self.ids = 'arty_crosshair'
        self.version = '1.04 (18.11.2016)'
        self.version_id = 104
        self.author = 'by spoter, reven86'
        self.data = {
            'version': self.version_id,
            'enabled': True
        }
        self.i18n = {
            'version': self.version_id,
        }

    def load(self):
        print '[LOAD_MOD]:  [%s v%s, %s]' % (self.ids, self.version, self.author)
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n)

config = _Config()

@inject.log
def init():
    config.load()

# noinspection PyProtectedMember
@inject.hook(control_modes._GunControlMode, '_GunControlMode__createGunMarker')
@inject.log
def hookedCreateGunMarker(func, self, mode, isStrategic):
    status = isStrategic
    if config.data['enabled']:
        status = False
    func(self, mode, status)

# noinspection PyProtectedMember
@inject.hook(control_modes._FlashGunMarker, 'updateAim')
@inject.log
def hookedCreateGunMarker(func, self):
    func(self)
    self._aim['strategic'] = self.settingsCore.getSetting('arcade')
    
