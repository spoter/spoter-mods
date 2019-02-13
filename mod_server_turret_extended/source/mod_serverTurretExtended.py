# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

import BigWorld
import CommandMapping
import VehicleGunRotator
from Avatar import PlayerAvatar


class _Config(object):
    def __init__(self):
        self.ids = 'serverTurretExtended'
        self.version = 'v1.19 (2019-02-13)'
        self.version_id = 119
        self.author = 'by spoter, reven86'
        self.data = {
            'version'             : self.version_id,
            'enabled'             : True,
            'activate_message'    : False,
            'fix_accuracy_in_move': True,
            'server_turret'       : True
        }
        self.i18n = {
            'version'                                : self.version_id,
            'UI_description'                         : 'Server Turret and Fix Accuracy',
            'UI_setting_activate_message_text'       : 'Show Activation Message',
            'UI_setting_activate_message_tooltip'    : '{HEADER}Info:{/HEADER}{BODY}Show Activation Message in battle{/BODY}',
            'UI_setting_fix_accuracy_in_move_text'   : 'Fix Accuracy',
            'UI_setting_fix_accuracy_in_move_tooltip': '{HEADER}Info:{/HEADER}{BODY}When you tank move and then stop, used fix accuracy to not lost aiming{/BODY}',
            'UI_setting_server_turret_text'          : 'Server Turret',
            'UI_setting_server_turret_tooltip'       : '{HEADER}Info:{/HEADER}{BODY}Move Turret to Server Aim coordinates (need enabled Server Sight in game settings){/BODY}',
            'UI_battle_activate_message'             : '"Muzzle chaos": Activated'
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
                'text'   : self.i18n['UI_setting_server_turret_text'],
                'value'  : self.data['server_turret'],
                'tooltip': self.i18n['UI_setting_server_turret_tooltip'],
                'varName': 'server_turret'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_fix_accuracy_in_move_text'],
                'value'  : self.data['fix_accuracy_in_move'],
                'tooltip': self.i18n['UI_setting_fix_accuracy_in_move_tooltip'],
                'varName': 'fix_accuracy_in_move'
            }],
            'column2'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_activate_message_text'],
                'value'  : self.data['activate_message'],
                'tooltip': self.i18n['UI_setting_activate_message_tooltip'],
                'varName': 'activate_message'
            }]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class MovementControl(object):
    @staticmethod
    def move_pressed(avatar, is_down, key):
        if CommandMapping.g_instance.isFiredList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD, CommandMapping.CMD_ROTATE_LEFT, CommandMapping.CMD_ROTATE_RIGHT), key):
            avatar.moveVehicle(0, is_down)


class Support(object):
    @staticmethod
    @inject.log
    def message():
        inject.message(_config.i18n['UI_battle_activate_message'])

    def start_battle(self):
        if _config.data['enabled'] and _config.data['activate_message']:
            BigWorld.callback(5.0, self.message)


# start mod

_config = _Config()
movement_control = MovementControl()
support = Support()


@inject.hook(PlayerAvatar, 'handleKey')
@inject.log
def hookPlayerAvatarHandleKey(func, *args):
    if _config.data['enabled'] and _config.data['fix_accuracy_in_move']:
        self, is_down, key, mods = args
        movement_control.move_pressed(self, is_down, key)
    return func(*args)


@inject.hook(VehicleGunRotator.VehicleGunRotator, 'setShotPosition')
@inject.log
def hookVehicleGunRotatorSetShotPosition(func, self, vehicleID, shotPos, shotVec, dispersionAngle, forceValueRefresh=False):
    if _config.data['enabled'] and _config.data['server_turret'] and not BigWorld.player().inputHandler.isSPG:
        if self._VehicleGunRotator__clientMode and self._VehicleGunRotator__showServerMarker and not forceValueRefresh:
            forceValueRefresh = True
    return func(self, vehicleID, shotPos, shotVec, dispersionAngle, forceValueRefresh)


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hookStartGUI(func, *args):
    func(*args)
    support.start_battle()
