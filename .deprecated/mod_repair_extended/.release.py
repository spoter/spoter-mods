# -*- coding: utf-8 -*-
import glob
import os
import shutil
import subprocess

ZIP_AUTO = 'mods_repair_extended_cheat.zip'

try:
    shutil.rmtree('zip', True)
except OSError:
    pass

class Release(object):

    def __init__(self, build, zip):
        self.data = build
        self.zipPath = os.path.join('zip', zip)
        self.modsPath = os.path.join(self.data.build.OUT_PATH, 'mods')
        self.versionPath = os.path.join(self.modsPath, self.data.CLIENT_VERSION, 'spoter')
        self.configPath = os.path.join(self.modsPath, 'configs', 'spoter', os.path.splitext(os.path.basename(self.data.build.VERSION["config"]))[0])
        self.i18n = os.path.join(self.configPath, 'i18n')
        self.packZip()
        self.clear()

    def packZip(self):
        subprocess.check_call(['powershell', 'mkdir', self.versionPath])
        subprocess.check_call(['powershell', 'mkdir', self.i18n])
        #copy *.wotmod
        subprocess.call('powershell robocopy %s %s %s /COPYALL' % (os.path.realpath('release'), os.path.realpath(self.versionPath), self.data.build.RELEASE))
        #copy config
        subprocess.call('powershell robocopy %s %s %s /COPYALL' % (os.path.realpath(os.path.join(self.data.build.BUILD_PATH, os.path.dirname(self.data.build.VERSION["config"]))), os.path.realpath(self.configPath), os.path.basename(self.data.build.VERSION["config"])))
        #copy i18n files
        for path in glob.glob(os.path.join(self.data.build.BUILD_PATH, self.data.build.VERSION["i18n"], "*.json")):
            subprocess.call('powershell robocopy %s %s %s /COPYALL' % (os.path.join(self.data.build.BUILD_PATH, self.data.build.VERSION["i18n"]), os.path.realpath(self.i18n), os.path.basename(path)))
        #copy mod_mods_gui core
        if os.path.exists('../mod_mods_gui/release'):
            subprocess.call('powershell robocopy %s %s %s /COPYALL' %(os.path.realpath('../mod_mods_gui/release'), os.path.join(self.modsPath, self.data.CLIENT_VERSION), '*.wotmod') )
        if os.path.exists('../mod_mods_gui/release/i18n'):
            subprocess.call('powershell robocopy %s %s %s /COPYALL' %(os.path.realpath('../mod_mods_gui/release/i18n'), os.path.join(self.modsPath, 'configs', 'mods_gui', 'i18n'), '*.json') )
        ps = '%s\%s' % (os.path.realpath(self.data.build.OUT_PATH), 'create-7zip.ps1')
        with open(ps, 'w') as xfile:
            xfile.write('function create-7zip([String] $aDirectory, [String] $aZipfile){ [string]$pathToZipExe = "C:\Program Files\\7-zip\\7z.exe"; [Array]$arguments = "a", "-tzip", "-ssw", "-mx9", "$aZipfile", "$aDirectory"; & $pathToZipExe $arguments; }\n'
                        'create-7zip "%s"  "%s"\n' % (os.path.realpath(self.modsPath), os.path.realpath(self.zipPath)))
        xfile.close()
        subprocess.call('powershell -executionpolicy bypass -command "& {Set-ExecutionPolicy AllSigned; %s; Set-ExecutionPolicy Undefined}"' % ps)

    def clear(self):
        try:
            shutil.rmtree(self.data.build.OUT_PATH, True)
        except OSError:
            pass
import _build_auto as auto
Release(auto, ZIP_AUTO)

try:
    shutil.rmtree('release', True)
except OSError:
    pass