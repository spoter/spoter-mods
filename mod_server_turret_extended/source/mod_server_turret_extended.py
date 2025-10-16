# -*- coding: utf-8 -*-
# Относительный путь: mods/<game-version>/spoter/mod_server_turret_extended.py
"""
Мод для улучшения точности прицеливания и автоматического управления колёсным режимом.
Включает в себя функции для синхронизации с сервером и автоматического переключения режимов колёсной техники.
"""

import math

# Стандартные библиотеки
# noinspection PyUnresolvedReferences
import BigWorld
import CommandMapping
import Keys
import VehicleGunRotator
import gun_rotation_shared
from Avatar import MOVEMENT_FLAGS, PlayerAvatar
from constants import VEHICLE_SETTING, VEHICLE_SIEGE_STATE
from gui import InputHandler
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

# Сторонние зависимости
# noinspection PyUnresolvedReferences
from gui.mods.mod_mods_gui import g_gui, inject

# Различные версии клиента
try:
    # EU-клиент
    # wot 2.0.0.0
    from AvatarInputHandler.player_notifications.siege_mode.sound_notifications import SoundNotifications
except ImportError:
    # LESTA-клиент
    # noinspection PyUnresolvedReferences,PyPep8Naming
    from AvatarInputHandler.siege_mode_player_notifications import SOUND_NOTIFICATIONS as SoundNotifications


class Config(object):
    """
    Класс конфигурации мода.
    Содержит настройки, значения по умолчанию и локализацию интерфейса.
    """
    
    def __init__(self):
        """
        Инициализация конфигурации мода.
        Устанавливает идентификатор, версию, автора, кнопки и параметры по умолчанию.
        """
        self.ids = 'serverTurretExtended'
        self.version = 'v3.15 (2025-10-16)'
        self.version_id = 315
        self.author = 'by spoter, reven86'
        self.buttons = {
            'buttonAutoMode': [Keys.KEY_R, [Keys.KEY_LALT, Keys.KEY_RALT]],
            'buttonMaxMode': [Keys.KEY_R, [Keys.KEY_LCONTROL, Keys.KEY_RCONTROL]]
        }
        self.data = {
            'version'              : self.version_id,
            'enabled'              : True,
            'activateMessage'      : False,
            'fixAccuracyInMove'    : True,
            'serverTurret'         : False,
            'fixWheelCruiseControl': True,
            'autoActivateWheelMode': True,
            'maxWheelMode'         : True,
            'buttonAutoMode'       : self.buttons['buttonAutoMode'],
            'buttonMaxMode'        : self.buttons['buttonMaxMode'],
        }
        self.i18n = {
            'version'                                 : self.version_id,
            'UI_description'                          : 'Improved accuracy & auto mode for wheeled vehicles',
            'UI_setting_activateMessage_text'         : 'Show activation message',
            'UI_setting_activateMessage_tooltip'      : '{HEADER}Info:{/HEADER}{BODY}Show the activation message in battle.{/BODY}',
            'UI_setting_fixAccuracyInMove_text'       : 'Keep aim accuracy after stopping',
            'UI_setting_fixAccuracyInMove_tooltip'    : '{HEADER}Info:{/HEADER}{BODY}When you move and then stop, preserve the current aim to avoid extra aim bloom caused by stopping.{/BODY}',
            'UI_setting_serverTurret_text'            : 'Turret sync (server reticle)',
            'UI_setting_serverTurret_tooltip'         : '{HEADER}Info:{/HEADER}{BODY}Align the turret to the server reticle coordinates. Requires the Server Reticle option enabled in the game settings.{/BODY}',
            'UI_battle_activateMessage'               : 'Improved accuracy & auto mode for wheeled vehicles: activated',
            'UI_setting_fixWheelCruiseControl_text'   : 'Wheeled vehicles: cruise control fix',
            'UI_setting_fixWheelCruiseControl_tooltip': '{HEADER}Info:{/HEADER}{BODY}Prevents the vehicle from stopping when switching wheeled mode while cruise control is on.{/BODY}',
            'UI_setting_maxWheelMode_text'            : 'Wheeled vehicles: keep maximum speed',
            'UI_setting_maxWheelMode_tooltip'         : '{HEADER}Info:{/HEADER}{BODY}At top speed, stay in speed mode and do not drop out when maneuvering.{/BODY}',
            'UI_setting_buttonMaxMode_text'           : 'Hotkey: keep maximum speed',
            'UI_setting_buttonMaxMode_tooltip'        : '',
            'UI_setting_autoActivateWheelMode_text'   : 'Wheeled vehicles: auto speed/maneuver mode',
            'UI_setting_autoActivateWheelMode_tooltip': '{HEADER}Info:{/HEADER}{BODY}Automatically switches between speed and maneuverability modes.{/BODY}',
            'UI_setting_buttonAutoMode_text'          : 'Hotkey: auto speed mode',
            'UI_setting_buttonAutoMode_tooltip'       : '',
            'UI_battle_ON'                            : 'ON',
            'UI_battle_OFF'                           : 'OFF',
        }
        self.data, self.i18n = g_gui.register_data(self.ids, self.data, self.i18n, 'spoter')
        g_gui.register(self.ids, self.template, self.data, self.apply)
        print('[LOAD_MOD]:  [%s %s, %s]' % (self.ids, self.version, self.author))

    def template(self):
        """
        Создает шаблон интерфейса настроек мода.
        
        Returns:
            dict: Структура интерфейса настроек
        """
        return {
            'modDisplayName' : self.i18n['UI_description'],
            'settingsVersion': self.version_id,
            'enabled'        : self.data['enabled'],
            'column1'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_serverTurret_text'],
                'value'  : self.data['serverTurret'],
                'tooltip': self.i18n['UI_setting_serverTurret_tooltip'],
                'varName': 'serverTurret'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_fixAccuracyInMove_text'],
                'value'  : self.data['fixAccuracyInMove'],
                'tooltip': self.i18n['UI_setting_fixAccuracyInMove_tooltip'],
                'varName': 'fixAccuracyInMove'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_fixWheelCruiseControl_text'],
                'value'  : self.data['fixWheelCruiseControl'],
                'tooltip': self.i18n['UI_setting_fixWheelCruiseControl_tooltip'],
                'varName': 'fixWheelCruiseControl'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_activateMessage_text'],
                'value'  : self.data['activateMessage'],
                'tooltip': self.i18n['UI_setting_activateMessage_tooltip'],
                'varName': 'activateMessage'
            }],
            'column2'        : [{
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_setting_buttonAutoMode_text'],
                'tooltip'     : self.i18n['UI_setting_buttonAutoMode_tooltip'],
                'value'       : self.data['buttonAutoMode'],
                'defaultValue': self.buttons['buttonAutoMode'],
                'varName'     : 'buttonAutoMode'
            }, {
                'type'        : 'HotKey',
                'text'        : self.i18n['UI_setting_buttonMaxMode_text'],
                'tooltip'     : self.i18n['UI_setting_buttonMaxMode_tooltip'],
                'value'       : self.data['buttonMaxMode'],
                'defaultValue': self.buttons['buttonMaxMode'],
                'varName'     : 'buttonMaxMode'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_maxWheelMode_text'],
                'value'  : self.data['maxWheelMode'],
                'tooltip': self.i18n['UI_setting_maxWheelMode_tooltip'],
                'varName': 'maxWheelMode'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_autoActivateWheelMode_text'],
                'value'  : self.data['autoActivateWheelMode'],
                'tooltip': self.i18n['UI_setting_autoActivateWheelMode_tooltip'],
                'varName': 'autoActivateWheelMode'
            }]
        }

    def apply(self, settings):
        """
        Применяет новые настройки мода.
        
        Args:
            settings (dict): Новые настройки интерфейса
        """
        self.data = g_gui.update_data(self.ids, settings, 'spoter')
        g_gui.update(self.ids, self.template)


class MovementControl(object):
    """
    Класс для управления движением и режимами колёсной техники.
    Отвечает за переключение между режимами и обработку пользовательского ввода.
    """
    
    def __init__(self):
        """
        Инициализирует контроллер движения.
        Устанавливает начальные значения таймера и callback.
        """
        self.timer = None
        self.callback = None

    @staticmethod
    def move_pressed(avatar, is_down, key):
        """
        Обрабатывает нажатие клавиш движения.
        
        Args:
            avatar: Объект аватара игрока
            is_down (bool): Флаг нажатия клавиши
            key: Код нажатой клавиши
        """
        if CommandMapping.g_instance.isFiredList((
                CommandMapping.CMD_MOVE_FORWARD,
                CommandMapping.CMD_MOVE_FORWARD_SPEC,
                CommandMapping.CMD_MOVE_BACKWARD,
                CommandMapping.CMD_ROTATE_LEFT,
                CommandMapping.CMD_ROTATE_RIGHT
        ), key):
            avatar.moveVehicle(0, is_down)

    def start_battle(self):
        """
        Запускает функциональность мода при начале боя.
        Регистрирует обработчики событий клавиатуры и запускает периодическую проверку.
        """
        InputHandler.g_instance.onKeyDown += self.key_pressed
        InputHandler.g_instance.onKeyUp += self.key_pressed
        self.timer = BigWorld.time()
        SoundNotifications.TRANSITION_TIMER = 'siege_mode_transition_timer'
        if self.callback is None:
            self.callback = BigWorld.callback(0.1, self.on_callback)

    def end_battle(self):
        """
        Останавливает функциональность мода при окончании боя.
        Отключает обработчики событий и останавливает периодическую проверку.
        """
        if self.callback is not None:
            BigWorld.cancelCallback(self.callback)
            self.callback = None
        InputHandler.g_instance.onKeyDown -= self.key_pressed
        InputHandler.g_instance.onKeyUp -= self.key_pressed

    def on_callback(self):
        """
        Периодическая функция для проверки необходимости изменения режима движения.
        Вызывается каждые 0.1 секунды.
        """
        if config.data['enabled'] and config.data['autoActivateWheelMode']:
            self.change_movement()
        self.callback = BigWorld.callback(0.1, self.on_callback)

    @staticmethod
    def key_pressed(event):
        """
        Обрабатывает нажатия клавиш для переключения режимов.
        
        Args:
            event: Объект события клавиатуры
        """
        if not config.data['enabled']:
            return
            
        # Проверка нажатия комбинации клавиш для максимальной скорости
        if g_gui.get_key(config.data['buttonMaxMode']) and event.isKeyDown():
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle and vehicle.isAlive() and vehicle.isWheeledTech and vehicle.typeDescriptor.hasSiegeMode:
                config.data['maxWheelMode'] = not config.data['maxWheelMode']
                message = '%s: %s' % (
                    config.i18n['UI_setting_maxWheelMode_text'],
                    config.i18n['UI_battle_ON'] if config.data['maxWheelMode'] else config.i18n['UI_battle_OFF']
                )
                inject.message(message, '#8378FC')
                
        # Проверка нажатия комбинации клавиш для автоматического режима
        if g_gui.get_key(config.data['buttonAutoMode']) and event.isKeyDown():
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle and vehicle.isAlive() and vehicle.isWheeledTech and vehicle.typeDescriptor.hasSiegeMode:
                config.data['autoActivateWheelMode'] = not config.data['autoActivateWheelMode']
                message = '%s: %s' % (
                    config.i18n['UI_setting_autoActivateWheelMode_text'],
                    config.i18n['UI_battle_ON'] if config.data['autoActivateWheelMode'] else config.i18n['UI_battle_OFF']
                )
                inject.message(message, '#8378FC')

    def change_movement(self):
        """
        Проверяет условия движения и при необходимости изменяет режим техники.
        Анализирует текущее состояние техники и пользовательский ввод для определения
        оптимального режима колёсной техники.
        """
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        
        # Проверка, что игрок находится на колёсной технике с осадным режимом
        if not (vehicle and vehicle.isAlive() and vehicle.isWheeledTech and vehicle.typeDescriptor.hasSiegeMode):
            return
            
        flags = player.makeVehicleMovementCommandByKeys()
        
        # Логика для обычного режима (DISABLED - манёвренный режим)
        if vehicle.siegeState == VEHICLE_SIEGE_STATE.DISABLED:
            # Проверка круиз-контроля
            # noinspection PyProtectedMember
            if player._PlayerAvatar__cruiseControlMode:
                return self.change_siege(True)
                
            # Проверка поворотов - не меняем режим при поворотах
            if flags & MOVEMENT_FLAGS.ROTATE_RIGHT or flags & MOVEMENT_FLAGS.ROTATE_LEFT or flags & MOVEMENT_FLAGS.BLOCK_TRACKS:
                return
                
            # Переключаемся в скоростной режим при движении вперед или назад
            if flags & MOVEMENT_FLAGS.FORWARD or flags & MOVEMENT_FLAGS.BACKWARD:
                return self.change_siege(True)
                
        # Логика для скоростного режима (ENABLED - скоростной режим)
        elif vehicle.siegeState == VEHICLE_SIEGE_STATE.ENABLED:
            # Проверяем, включен ли круиз-контроль
            # noinspection PyProtectedMember
            if not player._PlayerAvatar__cruiseControlMode:
                real_speed = int(vehicle.speedInfo.value[0] * 3.6)

                # Переключаемся в манёвренный режим при поворотах (при допустимой скорости)
                if (flags & MOVEMENT_FLAGS.ROTATE_RIGHT or flags & MOVEMENT_FLAGS.ROTATE_LEFT) and self.check_speed_limits(vehicle, real_speed):
                    return self.change_siege(False)
                    
                # Переключаемся в манёвренный режим при нажатии пробела
                if flags & MOVEMENT_FLAGS.BLOCK_TRACKS:
                    return self.change_siege(False)
                    
                # При низкой скорости проверяем дополнительные условия для переключения
                if 20 > real_speed > -20:
                    # Если не нажаты клавиши движения
                    cmd_list = (
                        CommandMapping.CMD_MOVE_FORWARD,
                        CommandMapping.CMD_MOVE_FORWARD_SPEC,
                        CommandMapping.CMD_MOVE_BACKWARD
                    )
                    if not CommandMapping.g_instance.isActiveList(cmd_list):
                        return self.change_siege(False)
                        
                    # Если движемся назад и хотим вперед
                    if real_speed < 0 and flags & MOVEMENT_FLAGS.FORWARD:
                        return self.change_siege(False)
                        
                    # Если движемся вперед и хотим назад
                    if real_speed > 0 and flags & MOVEMENT_FLAGS.BACKWARD:
                        return self.change_siege(False)

    def change_siege(self, status):
        """
        Изменяет режим колесной техники.
        
        Args:
            status (bool): True для скоростного режима, False для маневренного режима
        """
        # Отключаем звук перехода в режим
        SoundNotifications.TRANSITION_TIMER = ''
        # Передаем команду на сервер
        BigWorld.player().cell.vehicle_changeSetting(VEHICLE_SETTING.SIEGE_MODE_ENABLED, status)
        # Обновляем таймер
        self.timer = BigWorld.time()

    @staticmethod
    def check_speed_limits(vehicle, speed):
        """
        Проверяет, не превышает ли скорость допустимые пределы для смены режима.
        
        Args:
            vehicle: Объект техники
            speed (int): Текущая скорость техники
            
        Returns:
            bool: True, если скорость в пределах лимитов или опция maxWheelMode отключена
        """
        if not config.data['maxWheelMode']:
            return True
            
        speed_limits = vehicle.typeDescriptor.defaultVehicleDescr.physics['speedLimits']
        forward_limit = int(speed_limits[0] * 3.6)
        backward_limit = -int(speed_limits[1] * 3.6)
        
        return forward_limit > speed > backward_limit

    @staticmethod
    def fix_siege_mode_cruise_control():
        """
        Исправляет взаимодействие круиз-контроля с осадным режимом.
        Устанавливает корректные звуковые события для режима.
        
        Returns:
            bool: True, если техника поддерживает осадный режим
        """
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        
        # Проверка техники на наличие осадного режима
        result = vehicle and vehicle.isAlive() and vehicle.isWheeledTech and vehicle.typeDescriptor.hasSiegeMode
        
        if result:
            sound_state_change = vehicle.typeDescriptor.type.siegeModeParams['soundStateChange']
            vehicle.appearance.engineAudition.setSiegeSoundEvents(
                sound_state_change.isEngine,
                sound_state_change.npcOn,
                sound_state_change.npcOff
            )
            
        return result


class Support(object):
    """
    Вспомогательный класс для дополнительной функциональности мода.
    """
    
    @staticmethod
    @inject.log
    def message():
        """
        Показывает сообщение об активации мода в бою.
        """
        inject.message(config.i18n['UI_battle_activateMessage'])

    def start_battle(self):
        """
        Выполняет действия при начале боя.
        """
        if config.data['enabled'] and config.data['activateMessage']:
            BigWorld.callback(5.0, self.message)


# Переопределение функций декодирования для правильной работы прицела
def decode_restricted_value_from_uint(code, bits, min_bound, max_bound):
    """
    Декодирует ограниченное значение из целого числа.
    
    Args:
        code: Закодированное значение
        bits (int): Количество бит
        min_bound: Минимальное значение
        max_bound: Максимальное значение
        
    Returns:
        float: Декодированное значение
    """
    code -= 0.5
    t = float(code) / ((1 << bits) - 1)
    return min_bound + t * (max_bound - min_bound)


def decode_angle_from_uint(code, bits):
    """
    Декодирует угол из целого числа.
    
    Args:
        code: Закодированное значение
        bits (int): Количество бит
        
    Returns:
        float: Декодированный угол
    """
    code -= 0.5
    return math.pi * 2.0 * code / (1 << bits) - math.pi


# Инициализация мода
config = Config()
movement_control = MovementControl()
support = Support()


# Перехват обработчиков событий игры

@inject.hook(PlayerAvatar, 'handleKey')
@inject.log
def hook_player_avatar_handle_key(func, *args):
    """
    Перехватывает обработку нажатий клавиш для исправления точности при движении.
    
    Args:
        func: Оригинальная функция
        *args: Аргументы функции
        
    Returns:
        Результат вызова оригинальной функции
    """
    if config.data['enabled'] and config.data['fixAccuracyInMove']:
        self, is_down, key, mods = args
        movement_control.move_pressed(self, is_down, key)
    return func(*args)


@inject.hook(VehicleGunRotator.VehicleGunRotator, 'setShotPosition')
@inject.log
def hook_vehicle_gun_rotator_set_shot_position(func, self, vehicle_id, shot_pos, shot_vec, dispersion_angle, force_value_refresh=False):
    """
    Перехватывает позицию выстрела для синхронизации с сервером.
    
    Args:
        func: Оригинальная функция
        self: Объект ротатора орудия
        vehicle_id: ID техники
        shot_pos: Позиция выстрела
        shot_vec: Вектор выстрела
        dispersion_angle: Угол разброса
        force_value_refresh (bool): Принудительное обновление значений
        
    Returns:
        Результат вызова оригинальной функции
    """
    if config.data['enabled']:
        if self._avatar.vehicle and config.data['serverTurret']:
            self._VehicleGunRotator__turretYaw, self._VehicleGunRotator__gunPitch = self._avatar.vehicle.getServerGunAngles()
            force_value_refresh = True
    return func(self, vehicle_id, shot_pos, shot_vec, dispersion_angle, force_value_refresh)


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def hook_start_gui(func, *args):
    """
    Перехватывает запуск GUI для инициализации мода.
    
    Args:
        func: Оригинальная функция
        *args: Аргументы функции
        
    Returns:
        Результат вызова оригинальной функции
    """
    func(*args)
    support.start_battle()
    movement_control.start_battle()


@inject.hook(PlayerAvatar, '_PlayerAvatar__destroyGUI')
@inject.log
def hook_destroy_gui(func, *args):
    """
    Перехватывает уничтожение GUI для завершения работы мода.
    
    Args:
        func: Оригинальная функция
        *args: Аргументы функции
        
    Returns:
        Результат вызова оригинальной функции
    """
    movement_control.end_battle()
    func(*args)


@inject.hook(PlayerAvatar, 'updateSiegeStateStatus')
@inject.log
def update_siege_state_status(func, self, vehicle_id, status, time_left):
    """
    Перехватывает обновление состояния осадного режима.
    
    Args:
        func: Оригинальная функция
        self: Объект аватара игрока
        vehicle_id: ID техники
        status: Статус осадного режима
        time_left: Оставшееся время
        
    Returns:
        Результат вызова оригинальной функции
    """
    if not movement_control.fix_siege_mode_cruise_control():
        return func(self, vehicle_id, status, time_left)
        
    type_descr = self._PlayerAvatar__updateVehicleStatus(vehicle_id)
    if not type_descr or not self.vehicle or vehicle_id != self.vehicle.id:
        return
        
    self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.SIEGE_MODE, (status, time_left))
    self._PlayerAvatar__onSiegeStateUpdated(vehicle_id, status, time_left)


# Замена функций декодирования для корректной работы серверного прицела
gun_rotation_shared.decodeRestrictedValueFromUint = decode_restricted_value_from_uint
gun_rotation_shared.decodeAngleFromUint = decode_angle_from_uint
