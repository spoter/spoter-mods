# -*- coding: utf-8 -*-
import codecs
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import base64

CLIENT_VERSION = '1.5.0.0'
BUILD = 'auto'
NAME = 'spoter.repair_extended_auto'
ADD_LICENSE = True


class Build(object):
    OUT_PATH = '.out'
    PYC_PATH = os.path.join(OUT_PATH, 'res', 'scripts', 'client', 'gui', 'mods')
    BUILD_PATH = os.path.join('source', BUILD)
    VERSION = None
    RELEASE = '%s.wotmod' % NAME
    DATE = datetime.datetime.now().strftime("%Y-%m-%d")
    CONFIG_NAME = None

    def __init__(self):
        self.clear()
        if not os.path.exists('release'): subprocess.check_call(['powershell', 'mkdir', 'release'])
        self.readVersion()
        self.createFileDict()
        self.packWotmod()
        self.clear()
        print 'created: %s v%s (%s) to %s' % (self.RELEASE, self.VERSION["version"], self.DATE, CLIENT_VERSION)

    def clear(self):
        try:
            shutil.rmtree(self.OUT_PATH, True)
        except OSError:
            pass

    def readVersion(self):
        filePath = os.path.join(self.BUILD_PATH, 'VERSION')
        with codecs.open(filePath, 'r', encoding='utf-8') as versionFile:
            data = versionFile.read().decode('utf-8')
            versionFile.close()
        self.VERSION = json.loads(data)

    def createFileDict(self):
        version = '{:.2f}'.format(float(self.VERSION["version"]))
        files = []
        if self.VERSION["source"]:
            files.append((os.path.join(self.BUILD_PATH, self.VERSION["source"]), 'self.version = ', "'v%s (%s)'" % (version, self.DATE)))
            files.append((os.path.join(self.BUILD_PATH, self.VERSION["source"]), 'self.version_id = ', re.sub('[.\s]', '', '%s' % version)))
        if self.VERSION["meta"]:
            files.append((os.path.join(self.BUILD_PATH, self.VERSION["meta"]), '<version>', '%s</version>' % version))
        if self.VERSION["config"]:
            files.append((os.path.join(self.BUILD_PATH, self.VERSION["config"]), '"version": ', re.sub('[.\s]', '', '%s' % version)))
        if self.VERSION["i18n"]:
            for path in glob.glob(os.path.join(self.BUILD_PATH, self.VERSION["i18n"], "*.json")):
                files.append((path, '"version": ', re.sub('[.\s]', '', '%s' % version)))
        for path in files:
            self.updateFiles(*path)

    def updateFiles(self, path, string, text):
        with open(path, 'a+') as xfile:
            data = xfile.readlines()
            newData = []
            for line in data:
                if 'self.ids = ' in line:
                    self.configName = re.split('self.ids = ', line)[1]
                if string in line:
                    newData.append('%s%s%s\n' % (re.split(string, line)[0], string, text))
                    continue
                newData.append(line)
        xfile.close()
        with open(path, 'w') as xfile:
            xfile.writelines(newData)
        xfile.close()

    def packWotmod(self):
        self.RELEASE = '%s_%s.wotmod' % (NAME, '{:.2f}'.format(float(self.VERSION["version"])))
        subprocess.check_call(['powershell', 'mkdir', self.PYC_PATH])

        py = '%s' % os.path.join(self.BUILD_PATH, self.VERSION["source"])
        pyc = '%sc' % self.VERSION["source"]
        ps = '%s\%s' % (os.path.realpath(self.OUT_PATH), 'create-7zip.ps1')
        metaPath = '%s' % os.path.join(self.BUILD_PATH, os.path.dirname(self.VERSION["meta"]))
        metaFile = os.path.basename(self.VERSION["meta"])

        subprocess.check_call(['python', '-m', 'compileall', py])
        subprocess.call('powershell robocopy %s %s %s /COPYALL /MOV' % (os.path.realpath(self.BUILD_PATH), os.path.realpath(self.PYC_PATH), pyc))
        subprocess.call('powershell robocopy %s %s %s /COPYALL' % (os.path.realpath(metaPath), os.path.realpath(self.OUT_PATH), metaFile))
        if self.VERSION["resources"]:
            for directory in self.VERSION["resources"]:
                if os.path.exists(os.path.join(self.BUILD_PATH, directory)):
                    subprocess.call('powershell robocopy %s %s /COPYALL /E' % (os.path.realpath(os.path.join(self.BUILD_PATH, directory)), os.path.realpath(os.path.join(self.OUT_PATH, 'res', directory))))

        with open(ps, 'w') as xfile:
            xfile.write('function create-7zip([String] $aDirectory, [String] $aZipfile){ [string]$pathToZipExe = "C:\Program Files\\7-zip\\7z.exe"; [Array]$arguments = "a", "-tzip", "-ssw", "-mx0", "$aZipfile", "$aDirectory"; & $pathToZipExe $arguments; }\n'
                        'create-7zip "%s"  "%s"\n'
                        'create-7zip "%s"  "%s"\n' % (os.path.realpath(os.path.join(self.OUT_PATH, 'res')), os.path.realpath(os.path.join('release', self.RELEASE)),
                                                      os.path.realpath(os.path.join(self.OUT_PATH, metaFile)), os.path.realpath(os.path.join('release', self.RELEASE))))
            if ADD_LICENSE:
                xfile.write('create-7zip "%s"  "%s"\n' % (self.createLicense(), os.path.realpath(os.path.join('release', self.RELEASE))))

        xfile.close()
        subprocess.call('powershell -executionpolicy bypass -command "& {Set-ExecutionPolicy AllSigned; %s; Set-ExecutionPolicy Undefined}"' % ps)

    def createLicense(self):
        b64 = "DQogICAgICAgIERPIFdIQVQgVEhFIEZVQ0sgWU9VIFdBTlQgVE8gUFVCTElDIExJQ0VOU0UgDQogICAgICAgICAgICAgICAgICAgIFZlcnNpb24gMiwgRGVjZW1iZXIgMjAwNCANCg0KIENvcHlyaWdodCAoQykgMjAwNCBTYW0gSG9jZXZhciA8c2FtQGhvY2V2YXIubmV0PiANCg0KIEV2ZXJ5b25lIGlzIHBlcm1pdHRlZCB0byBjb3B5IGFuZCBkaXN0cmlidXRlIHZlcmJhdGltIG9yIG1vZGlmaWVkIA0KIGNvcGllcyBvZiB0aGlzIGxpY2Vuc2UgZG9jdW1lbnQsIGFuZCBjaGFuZ2luZyBpdCBpcyBhbGxvd2VkIGFzIGxvbmcgDQogYXMgdGhlIG5hbWUgaXMgY2hhbmdlZC4gDQoNCiAgICAgICAgICAgIERPIFdIQVQgVEhFIEZVQ0sgWU9VIFdBTlQgVE8gUFVCTElDIExJQ0VOU0UgDQogICBURVJNUyBBTkQgQ09ORElUSU9OUyBGT1IgQ09QWUlORywgRElTVFJJQlVUSU9OIEFORCBNT0RJRklDQVRJT04gDQoNCiAgMC4gWW91IGp1c3QgRE8gV0hBVCBUSEUgRlVDSyBZT1UgV0FOVCBUTy4NCg=="
        output_name = os.path.realpath(os.path.join(self.OUT_PATH, 'LICENSE'))
        data = base64.b64decode(b64)
        with open(output_name, "wb") as output_file:
            output_file.write(data)
        output_file.close()
        return output_name


build = Build()
