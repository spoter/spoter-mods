# -*- coding: utf-8 -*-
import Math
import math

from gui.mods.mod_mods_gui import g_gui, inject

import BattleReplay
import BigWorld
import GUI
from Avatar import PlayerAvatar
from AvatarInputHandler import gun_marker_ctrl, mathUtils
from AvatarInputHandler.AimingSystems.SniperAimingSystem import SniperAimingSystem
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera, _InputInertia
from AvatarInputHandler.DynamicCameras.SniperCamera import SniperCamera
from AvatarInputHandler.DynamicCameras.StrategicCamera import StrategicCamera
from AvatarInputHandler.gun_marker_ctrl import _DefaultGunMarkerController, _GunMarkerController, _GunMarkersDPFactory, _GunMarkersDecorator, _MARKER_FLAG, _MARKER_TYPE, _SPGGunMarkerController, _calcScale, _makeWorldMatrix
from VehicleGunRotator import VehicleGunRotator
from constants import SERVER_TICK_LENGTH
from gui.Scaleform.daapi.view.battle.shared.crosshair import gm_factory
from helpers import EffectsList, dependency
from skeletons.account_helpers.settings_core import ISettingsCore


class _Config(object):
    def __init__(self):
        self.ids = 'dispersionCircle'
        self.version = 'v3.00 (2017-05-17)'
        self.version_id = 300
        self.author = 'by StranikS_Scan'
        self.data = {
            'enabled'              : True,
            'ReplaceOriginalCircle': True,
            'UseServerDispersion'  : True,
            'DispersionCircleScale': 1.0,
            'HorizontalStabilizer' : True,
            'Remove_DynamicEffects': True,
            'Remove_DamageEffects' : False,
            'version'              : self.version_id
        }
        self.i18n = {
            'UI_description'                          : 'Dispersion Circle',
            'UI_setting_ReplaceOriginalCircle_text'   : 'Replace aiming circle to dispersion circle',
            'UI_setting_ReplaceOriginalCircle_tooltip': '{HEADER}Info:{/HEADER}{BODY}Replace the original aiming circle to dispersion circle (To improve accuracy){/BODY}',
            'UI_setting_UseServerDispersion_text'     : 'Use server side circle of dispersion',
            'UI_setting_UseServerDispersion_tooltip'  : '{HEADER}Info:{/HEADER}{BODY}Change client to server circle of dispersion(not working in replays){/BODY}',
            'UI_setting_DispersionCircleScale_text'   : 'Scale dispersion circle (UI)',
            'UI_setting_DispersionCircleScale_format' : 'x',
            'UI_setting_HorizontalStabilizer_text'    : 'Activate: Horizontal sight stabilization',
            'UI_setting_HorizontalStabilizer_tooltip' : '',
            'UI_setting_Remove_DynamicEffects_text'   : 'Remove dynamic effects and smoothing',
            'UI_setting_Remove_DynamicEffects_tooltip': '',
            'UI_setting_Remove_DamageEffects_text'    : 'Remove hitting effects on the tank',
            'UI_setting_Remove_DamageEffects_tooltip' : '',
            'version'                                 : self.version_id
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
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_UseServerDispersion_text'],
                'value'  : self.data['UseServerDispersion'],
                'tooltip': self.i18n['UI_setting_UseServerDispersion_tooltip'],
                'varName': 'UseServerDispersion'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_ReplaceOriginalCircle_text'],
                'value'  : self.data['ReplaceOriginalCircle'],
                'tooltip': self.i18n['UI_setting_ReplaceOriginalCircle_tooltip'],
                'varName': 'ReplaceOriginalCircle'
            }, {
                'type'        : 'Slider',
                'text'        : self.i18n['UI_setting_DispersionCircleScale_text'],
                'minimum'     : 0.1,
                'maximum'     : 5.0,
                'snapInterval': 0.1,
                'value'       : self.data['DispersionCircleScale'],
                'format'      : '{{value}}%s' % self.i18n['UI_setting_DispersionCircleScale_format'],
                'varName'     : 'DispersionCircleScale'
            }],
            'column2'        : [{
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_HorizontalStabilizer_text'],
                'value'  : self.data['HorizontalStabilizer'],
                'tooltip': self.i18n['UI_setting_HorizontalStabilizer_tooltip'],
                'varName': 'HorizontalStabilizer'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_Remove_DynamicEffects_text'],
                'value'  : self.data['Remove_DynamicEffects'],
                'tooltip': self.i18n['UI_setting_Remove_DynamicEffects_tooltip'],
                'varName': 'Remove_DynamicEffects'
            }, {
                'type'   : 'CheckBox',
                'text'   : self.i18n['UI_setting_Remove_DamageEffects_text'],
                'value'  : self.data['Remove_DamageEffects'],
                'tooltip': self.i18n['UI_setting_Remove_DamageEffects_tooltip'],
                'varName': 'Remove_DamageEffects'
            }]
        }

    def apply(self, settings):
        self.data = g_gui.update_data(self.ids, settings)
        g_gui.update(self.ids, self.template)
        if not self.data['ReplaceOriginalCircle']:
            gun_marker_ctrl.useClientGunMarker = lambda: True
            gun_marker_ctrl.useServerGunMarker = lambda: True
            gun_marker_ctrl.useDefaultGunMarkers = lambda: False
            gm_factory._FACTORIES_COLLECTION = (gm_factory._DevControlMarkersFactory, gm_factory._OptionalMarkersFactory, gm_factory._EquipmentMarkersFactory)


class new_DefaultGunMarkerController(_GunMarkerController):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, gunMakerType, dataProvider, enabledFlag=_MARKER_FLAG.UNDEFINED):
        super(new_DefaultGunMarkerController, self).__init__(gunMakerType, dataProvider, enabledFlag=enabledFlag)
        self.__replSwitchTime = 0.0
        self.__curSize = 0.0
        self.__screenRatio = 0.0

    def enable(self):
        super(new_DefaultGunMarkerController, self).enable()
        self.__updateScreenRatio()
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            self.__replSwitchTime = 0.2

    def update(self, markerType, pos, dir, sizeVector, relaxTime, collData):
        super(new_DefaultGunMarkerController, self).update(markerType, pos, dir, sizeVector, relaxTime, collData)
        positionMatrix = Math.Matrix()
        positionMatrix.setTranslate(pos)
        self._updateMatrixProvider(positionMatrix, relaxTime)
        size = sizeVector[0]  # !!!
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            s = replayCtrl.getArcadeGunMarkerSize()
            if s != -1.0:
                size = s
        elif replayCtrl.isRecording:
            if replayCtrl.isServerAim and self._gunMarkerType == _MARKER_TYPE.SERVER:
                replayCtrl.setArcadeGunMarkerSize(size)
            elif self._gunMarkerType == _MARKER_TYPE.CLIENT:
                replayCtrl.setArcadeGunMarkerSize(size)
        worldMatrix = _makeWorldMatrix(positionMatrix)
        self.__curSize = _calcScale(worldMatrix, size) * self.__screenRatio * config.data['DispersionCircleScale'] / 2.3  # !!!
        if self.__replSwitchTime > 0.0:
            self.__replSwitchTime -= relaxTime
            self._dataProvider.updateSize(self.__curSize, 0.0)
        else:
            self._dataProvider.updateSize(self.__curSize, relaxTime)

    def onRecreateDevice(self):
        self.__updateScreenRatio()

    def __updateScreenRatio(self):
        self.__screenRatio = GUI.screenResolution()[0] * 0.5


class DispersionCircle(object):
    @staticmethod
    def gunMarkersDecoratorSetPosition(*args):
        func, position, markerType = args
        if not config.data['ReplaceOriginalCircle']:
            if markerType == _MARKER_TYPE.CLIENT:
                func._GunMarkersDecorator__clientMarker.setPosition(position)
            if config.data['UseServerDispersion']:
                if markerType == _MARKER_TYPE.SERVER:
                    func._GunMarkersDecorator__serverMarker.setPosition(position)
            elif markerType == _MARKER_TYPE.CLIENT:
                func._GunMarkersDecorator__serverMarker.setPosition(position)
        else:
            if config.data['UseServerDispersion']:
                if markerType == _MARKER_TYPE.SERVER:
                    func._GunMarkersDecorator__clientMarker.setPosition(position)
            elif markerType == _MARKER_TYPE.CLIENT:
                func._GunMarkersDecorator__clientMarker.setPosition(position)
            if markerType == _MARKER_TYPE.SERVER:
                func._GunMarkersDecorator__serverMarker.setPosition(position)

    @staticmethod
    def gunMarkersDecoratorUpdate(*args):
        self, markerType, position, dir, size, relaxTime, collData = args
        if not config.data['ReplaceOriginalCircle']:
            if markerType == _MARKER_TYPE.CLIENT:
                self._GunMarkersDecorator__clientState = (position, relaxTime, collData)
                if self._GunMarkersDecorator__gunMarkersFlags & _MARKER_FLAG.CLIENT_MODE_ENABLED:
                    self._GunMarkersDecorator__clientMarker.update(markerType, position, dir, size, relaxTime, collData)
            if config.data['UseServerDispersion']:
                if markerType == _MARKER_TYPE.SERVER:
                    self._GunMarkersDecorator__serverState = (position, relaxTime, collData)
                    if self._GunMarkersDecorator__gunMarkersFlags & _MARKER_FLAG.SERVER_MODE_ENABLED:
                        self._GunMarkersDecorator__serverMarker.update(markerType, position, dir, size, relaxTime, collData)
            elif markerType == _MARKER_TYPE.CLIENT:
                self._GunMarkersDecorator__serverState = (position, relaxTime, collData)
                if self._GunMarkersDecorator__gunMarkersFlags & _MARKER_FLAG.SERVER_MODE_ENABLED:
                    self._GunMarkersDecorator__serverMarker.update(markerType, position, dir, size, relaxTime, collData)
        else:
            if config.data['UseServerDispersion']:
                if markerType == _MARKER_TYPE.SERVER:
                    self._GunMarkersDecorator__clientState = (position, relaxTime, collData)
                    if self._GunMarkersDecorator__gunMarkersFlags & _MARKER_FLAG.CLIENT_MODE_ENABLED:
                        self._GunMarkersDecorator__clientMarker.update(markerType, position, dir, size, relaxTime, collData)
            elif markerType == _MARKER_TYPE.CLIENT:
                self._GunMarkersDecorator__clientState = (position, relaxTime, collData)
                if self._GunMarkersDecorator__gunMarkersFlags & _MARKER_FLAG.CLIENT_MODE_ENABLED:
                    self._GunMarkersDecorator__clientMarker.update(markerType, position, dir, size, relaxTime, collData)
            if markerType == _MARKER_TYPE.SERVER:
                self._GunMarkersDecorator__serverState = (position, relaxTime, collData)
                if self._GunMarkersDecorator__gunMarkersFlags & _MARKER_FLAG.SERVER_MODE_ENABLED:
                    self._GunMarkersDecorator__serverMarker.update(markerType, position, dir, size, relaxTime, collData)

    @staticmethod
    def createGunMarker(isStrategic):
        factory = _GunMarkersDPFactory()
        if isStrategic:
            clientMarker = _SPGGunMarkerController(_MARKER_TYPE.CLIENT, factory.getClientSPGProvider())
            serverMarker = _SPGGunMarkerController(_MARKER_TYPE.SERVER, factory.getServerSPGProvider())
        else:
            clientMarker = _DefaultGunMarkerController(_MARKER_TYPE.CLIENT, factory.getClientProvider()) if not config.data['ReplaceOriginalCircle'] else new_DefaultGunMarkerController(_MARKER_TYPE.CLIENT, factory.getClientProvider())
            serverMarker = new_DefaultGunMarkerController(_MARKER_TYPE.SERVER, factory.getServerProvider())
        return _GunMarkersDecorator(clientMarker, serverMarker)

    @staticmethod
    def arcadeCameraInit(self):
        if not config.data['Remove_DynamicEffects']: return
        self._ArcadeCamera__dynamicCfg['accelerationSensitivity'] = 0.0
        self._ArcadeCamera__dynamicCfg['frontImpulseToPitchRatio'] = 0.0
        self._ArcadeCamera__dynamicCfg['sideImpulseToRollRatio'] = 0.0
        self._ArcadeCamera__dynamicCfg['sideImpulseToYawRatio'] = 0.0
        self._ArcadeCamera__dynamicCfg['accelerationThreshold'] = 0.0
        self._ArcadeCamera__dynamicCfg['accelerationMax'] = 0.0
        self._ArcadeCamera__dynamicCfg['maxShotImpulseDistance'] = 0.0
        self._ArcadeCamera__dynamicCfg['maxExplosionImpulseDistance'] = 0.0
        self._ArcadeCamera__dynamicCfg['zoomExposure'] = 0.0
        for x in self._ArcadeCamera__dynamicCfg['impulseSensitivities']:
            self._ArcadeCamera__dynamicCfg['impulseSensitivities'][x] = 0.0
        for x in self._ArcadeCamera__dynamicCfg['impulseLimits']:
            self._ArcadeCamera__dynamicCfg['impulseLimits'][x] = (0.0, 0.0)
        for x in self._ArcadeCamera__dynamicCfg['noiseSensitivities']:
            self._ArcadeCamera__dynamicCfg['noiseSensitivities'][x] = 0.0
        for x in self._ArcadeCamera__dynamicCfg['noiseLimits']:
            self._ArcadeCamera__dynamicCfg['noiseLimits'][x] = (0.0, 0.0)

    @staticmethod
    def sniperCameraInit(self):
        if not config.data['Remove_DynamicEffects']: return
        self._SniperCamera__dynamicCfg['accelerationSensitivity'] = Math.Vector3(0.0, 0.0, 0.0)
        self._SniperCamera__dynamicCfg['accelerationThreshold'] = 0.0
        self._SniperCamera__dynamicCfg['accelerationMax'] = 0.0
        self._SniperCamera__dynamicCfg['maxShotImpulseDistance'] = 0.0
        self._SniperCamera__dynamicCfg['maxExplosionImpulseDistance'] = 0.0
        self._SniperCamera__dynamicCfg['impulsePartToRoll'] = 0.0
        self._SniperCamera__dynamicCfg['pivotShift'] = Math.Vector3(0, -0.5, 0)
        for x in self._SniperCamera__dynamicCfg['impulseSensitivities']:
            self._SniperCamera__dynamicCfg['impulseSensitivities'][x] = 0.0
        for x in self._SniperCamera__dynamicCfg['impulseLimits']:
            self._SniperCamera__dynamicCfg['impulseLimits'][x] = (0.0, 0.0)
        for x in self._SniperCamera__dynamicCfg['noiseSensitivities']:
            self._SniperCamera__dynamicCfg['noiseSensitivities'][x] = 0.0
        for x in self._SniperCamera__dynamicCfg['noiseLimits']:
            self._SniperCamera__dynamicCfg['noiseLimits'][x] = (0.0, 0.0)

    @staticmethod
    def strategicCameraInit(self):
        if not config.data['Remove_DynamicEffects']: return
        for x in self._StrategicCamera__dynamicCfg['impulseSensitivities']:
            self._StrategicCamera__dynamicCfg['impulseSensitivities'][x] = 0.0
        for x in self._StrategicCamera__dynamicCfg['impulseLimits']:
            self._StrategicCamera__dynamicCfg['impulseLimits'][x] = (0.0, 0.0)
        for x in self._StrategicCamera__dynamicCfg['noiseSensitivities']:
            self._StrategicCamera__dynamicCfg['noiseSensitivities'][x] = 0.0
        for x in self._StrategicCamera__dynamicCfg['noiseLimits']:
            self._StrategicCamera__dynamicCfg['noiseLimits'][x] = (0.0, 0.0)

    @staticmethod
    def enableHorizontalStabilizerRuntime(self):
        yawConstraint = math.pi * 2.1 if config.data['HorizontalStabilizer'] else 0.0
        self._SniperAimingSystem__yprDeviationConstraints.x = yawConstraint

    @staticmethod
    def glide(*args):
        self, posDelta = args
        self._InputInertia__deltaEasing.reset(posDelta, Math.Vector3(0.0), 0.001)

    @staticmethod
    def glideFov(*args):
        self, newRelativeFocusDist = args
        minMulti, maxMulti = self._InputInertia__minMaxZoomMultiplier
        endMulti = mathUtils.lerp(minMulti, maxMulti, newRelativeFocusDist)
        self._InputInertia__zoomMultiplierEasing.reset(self._InputInertia__zoomMultiplierEasing.value, endMulti, 0.001)


@inject.hook(_GunMarkerController, 'update')
@inject.log
def gunMarkerControllerUpdate(func, *args):
    if config.data['enabled']:
        args[0]._position = args[2]
        return
    func(*args)


@inject.hook(_GunMarkersDecorator, 'setPosition')
@inject.log
def gunMarkersDecoratorSetPosition(func, self, position, markerType=_MARKER_TYPE.CLIENT):
    if config.data['enabled']:
        dispersionCircle.gunMarkersDecoratorSetPosition(self, position, markerType)
        return
    func(self, position, markerType)


@inject.hook(_GunMarkersDecorator, 'update')
@inject.log
def gunMarkersDecoratorUpdate(func, *args):
    if config.data['enabled']:
        dispersionCircle.gunMarkersDecoratorUpdate(*args)
        return
    func(*args)


@inject.hook(gun_marker_ctrl, 'createGunMarker')
@inject.log
def createGunMarker(func, *args):
    if config.data['enabled']:
        return dispersionCircle.createGunMarker(args[0])
    return func(*args)


@inject.hook(ArcadeCamera, '__init__')
@inject.log
def arcadeCameraInit(func, self, dataSec, defaultOffset=None):
    func(self, dataSec, defaultOffset)
    if config.data['enabled']:
        dispersionCircle.arcadeCameraInit(self)


@inject.hook(SniperCamera, '__init__')
@inject.log
def sniperCameraInit(func, self, dataSec, defaultOffset=None, binoculars=None):
    func(self, dataSec, defaultOffset, binoculars)
    if config.data['enabled']:
        dispersionCircle.sniperCameraInit(self)


@inject.hook(StrategicCamera, '__init__')
@inject.log
def strategicCameraInit(func, *args):
    func(*args)
    if config.data['enabled']:
        dispersionCircle.strategicCameraInit(args[0])


@inject.hook(SniperAimingSystem, 'enableHorizontalStabilizerRuntime')
@inject.log
def enableHorizontalStabilizerRuntime(func, *args):
    if config.data['enabled']:
        dispersionCircle.enableHorizontalStabilizerRuntime(args[0])
        return
    func(*args)


@inject.hook(_InputInertia, 'glide')
@inject.log
def glide(func, *args):
    if config.data['enabled'] and config.data['Remove_DynamicEffects']:
        dispersionCircle.glide(*args)
        return
    func(*args)


@inject.hook(_InputInertia, 'glideFov')
@inject.log
def glideFov(func, *args):
    if config.data['enabled'] and config.data['Remove_DynamicEffects']:
        dispersionCircle.glideFov(*args)
        return
    func(*args)


@inject.hook(Math, 'PyOscillator')
@inject.log
def PyOscillator(func, *args):
    if config.data['enabled'] and config.data['Remove_DynamicEffects']:
        return func(1e-05, (1e-05, 1e-05, 1e-05), (1e-05, 1e-05, 1e-05), (0.0, 0.0, 0.0))
    func(*args)


@inject.hook(Math, 'PyNoiseOscillator')
@inject.log
def PyNoiseOscillator(func, *args):
    if config.data['enabled'] and config.data['Remove_DynamicEffects']:
        return func(1e-05, (1e-05, 1e-05, 1e-05), (1e-05, 1e-05, 1e-05))
    func(*args)


@inject.hook(Math, 'PyRandomNoiseOscillatorFlat')
@inject.log
def PyRandomNoiseOscillatorFlat(func, *args):
    if config.data['enabled'] and config.data['Remove_DynamicEffects']:
        return func(1e-05, 1e-05, 1e-05)
    func(*args)


@inject.hook(Math, 'PyRandomNoiseOscillatorSpherical')
@inject.log
def PyRandomNoiseOscillatorSpherical(func, *args):
    if config.data['enabled'] and config.data['Remove_DynamicEffects']:
        return func(1e-05, 1e-05, 1e-05, (0.0, 0.0, 0.0))
    func(*args)


@inject.hook(EffectsList._FlashBangEffectDesc, 'create')
@inject.log
def flashBangEffectDescCreate(func, *args):
    if config.data['enabled'] and config.data['Remove_DamageEffects']:
        return
    func(*args)


@inject.hook(EffectsList._ShockWaveEffectDesc, 'create')
@inject.log
def shockWaveEffectDescCreate(func, *args):
    if config.data['enabled'] and config.data['Remove_DamageEffects']:
        return
    func(*args)


@inject.hook(VehicleGunRotator, 'setShotPosition')
@inject.log
def setShotPosition(func, *args):
    if config.data['enabled'] and config.data['UseServerDispersion']:
        self, vehicleID, shotPos, shotVec, dispersionAngle = args
        if self._VehicleGunRotator__clientMode and self._VehicleGunRotator__showServerMarker:
            return func(*args)
        dispersionAngles = {0: dispersionAngle, 1: dispersionAngle}
        markerPos, markerDir, markerSize, idealMarkerSize, collData = self._VehicleGunRotator__getGunMarkerPosition(shotPos, shotVec, self._VehicleGunRotator__dispersionAngles)
        self._VehicleGunRotator__avatar.inputHandler.updateGunMarker2(markerPos, markerDir, (markerSize, idealMarkerSize), SERVER_TICK_LENGTH, collData)
        return
    func(*args)


@inject.hook(PlayerAvatar, 'enableServerAim')
@inject.log
def enableServerAim(func, *args):
    if config.data['enabled']:
        func(args[0], config.data['UseServerDispersion'])
        return
    func(*args)


@inject.hook(VehicleGunRotator, 'applySettings')
@inject.log
def enableServerAim(func, *args):
    if config.data['enabled']:
        func(args[0], {})
        return
    func(*args)


@inject.hook(PlayerAvatar, '_PlayerAvatar__startGUI')
@inject.log
def startGUI(func, *args):
    func(*args)
    if config.data['enabled']:
        BigWorld.player().enableServerAim(config.data['UseServerDispersion'])


config = _Config()
dispersionCircle = DispersionCircle()
