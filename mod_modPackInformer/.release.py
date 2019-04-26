# -*- coding: utf-8 -*-
import glob
import os
import shutil
import subprocess

import _build as build

ZIP = 'mods_modPackInformer.zip'

class Release(object):

    def __init__(self, build, zip):
        self.data = build
        self.zipPath = os.path.join('zip', zip)
        self.modsPath = os.path.join(self.data.build.OUT_PATH, 'mods')
        self.versionPath = os.path.join(self.modsPath, self.data.CLIENT_VERSION)
        self.configPath = os.path.join(self.modsPath, 'configs', os.path.splitext(os.path.basename(self.data.build.VERSION["config"]))[0])
        self.i18n = os.path.join(self.configPath, 'i18n')
        self.clearZip()
        self.packZip()
        self.clear()

    def packZip(self):
        subprocess.check_call(['powershell', 'mkdir', self.versionPath])
        subprocess.call('powershell robocopy %s %s %s /COPYALL' % (os.path.realpath('release'), os.path.realpath(self.versionPath), self.data.build.RELEASE))
        ps = '%s\%s' % (os.path.realpath(self.data.build.OUT_PATH), 'create-7zip.ps1')
        with open(ps, 'w') as xfile:
            xfile.write('function create-7zip([String] $aDirectory, [String] $aZipfile){ [string]$pathToZipExe = "C:\Program Files\\7-zip\\7z.exe"; [Array]$arguments = "a", "-tzip", "-ssw", "-mx9", "$aZipfile", "$aDirectory"; & $pathToZipExe $arguments; }\n'
                        'create-7zip "%s"  "%s"\n' % (os.path.realpath(self.modsPath), os.path.realpath(self.zipPath)))
        xfile.close()
        subprocess.call('powershell -executionpolicy bypass -command "& {Set-ExecutionPolicy AllSigned; %s; Set-ExecutionPolicy Undefined}"' % ps)

    def clearZip(self):
        try:
            shutil.rmtree('zip', True)
        except OSError:
            pass

    def clear(self):
        try:
            shutil.rmtree(self.data.build.OUT_PATH, True)
        except OSError:
            pass
        try:
            shutil.rmtree('release', True)
        except OSError:
            pass

Release(build, ZIP)