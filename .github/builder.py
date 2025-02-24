# coding=utf-8
import codecs
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import base64
import sys
import traceback

# Входные параметры: name, version-ru, version-wg
MOD_NAME = sys.argv[1] # название мода, соответствует названию папки мода в файловой структуре относительно текущей папки
CLIENT_VERSION_RU = sys.argv[2] # Леста версия клиента
CLIENT_VERSION_WG = sys.argv[3] # Международная версия клиента
compile_exe = 'python'

# класс сборки мода
class Build(object):
    directoryBase = os.path.realpath('./../%s' %(MOD_NAME)) # Директория мода формата './../mod_testBuild', реальный путь вида 'D:\github.com\spoter-mods\mod_testBuild'
    directoryTemp = os.path.join(directoryBase, '.out') # Временная директория для сборки 'mod_testBuild/.out'
    directoryTempCompiled = os.path.join(directoryTemp, 'res', 'scripts', 'client', 'gui', 'mods')  # Временная директория для компилированного мода 'mod_testBuild/.out/res/scripts/client/gui/mods'
    directoryRelease = os.path.join(directoryBase, 'release') # Директория в которой хранится релизный архив мода 'mod_testBuild/release'
    directorySources = os.path.join(directoryBase, 'source') # Директория исходников 'mod_testBuild/source'

    def __init__(self):
        self.clear_temp()
        self.config = self.read_mod_version_config_file()
        self.recreate_structures()
        self.create_wotmod_archive()
        self.clear_temp()


    def clear_temp(self):
        # чистим временную директорию
        try:
            shutil.rmtree(self.directoryTemp, True)
        except OSError:
            print(OSError)

    def read_mod_version_config_file(self):
        path = os.path.join(self.directorySources, 'VERSION')
        # читаем конфиг мода из файла 'mod_testBuild/source/VERSION'
        # формат json в кодировке utf-8
        with codecs.open(path, 'r', encoding='utf-8') as versionFile:
            data = json.loads('%s' %versionFile.read())
        versionFile.close()
        return data

    def recreate_structures(self):
        # Пересоздаём структуру перед сборкой
        try:
            # временную папку
            os.makedirs(self.directoryTemp)
        except OSError:
            if not os.path.isdir(self.directoryTemp):
                raise
        try:
            # временную папку для компиляции
            os.makedirs(self.directoryTempCompiled)
        except OSError:
            if not os.path.isdir(self.directoryTempCompiled):
                raise
        try:
            # релизную папку
            os.makedirs(self.directoryRelease)
        except OSError:
            if not os.path.isdir(self.directoryRelease):
                raise

        files = [] # список для генерации файловой структуры мода
        version = '{:.2f}'.format(self.config["version"]) # переменная для текущей версии мода '3.04'

        # читаем из конфига список файлов мода и собираем структуру мода, вписывая изменения версии
        if 'source' in self.config and self.config['source']:
            path = os.path.join(self.directorySources, self.config['source'])
            files.append((path, 'self.version = ', "'v{} ({})'".format(version, datetime.datetime.now().strftime('%Y-%m-%d'))))
            files.append((path, 'self.version_id = ', re.sub('[.\s]', '', '{}'.format(version))))
            files.append((path, 'VERSION_MOD = '.format(MOD_NAME), "'v{} ({})'".format(version, datetime.datetime.now().strftime('%Y-%m-%d'))))


        if 'meta' in self.config and self.config['meta']:
            path = os.path.join(self.directorySources, self.config['meta'])
            files.append((path, '<version>', '%s</version>' % version))

        if 'config' in self.config and self.config['config']:
            path = os.path.join(self.directorySources, self.config['config'])
            files.append((path, '"version": ',re.sub('[.\s]', '', '{}'.format(version))))

        if 'i18n' in self.config and self.config['i18n']:
            for path in glob.glob(os.path.join(self.directorySources, self.config['i18n'], '*.*')):
                files.append((path, '"version": ', re.sub('[.\s]', '', '{}'.format(version))))


        # проходим по структуре, внося изменения версии перед сборкой
        for path in files:
            self.update_file_with_new_version(*path)

    @staticmethod
    def update_file_with_new_version(path, string, text):
        path = os.path.realpath(path)
        if os.path.exists(path):
            with open(path, 'r+') as xfile:
                data = []
                for line in xfile.readlines():
                    if string in line:
                        data.append('{}{}{}\n'.format(re.split(string, line)[0], string, text))
                        continue
                    data.append(line)
                xfile.close()
            with open(path, 'w') as xfile:
                xfile.writelines(data)
            xfile.close()

    def create_wotmod_archive(self):
        py = '%s' % os.path.join(self.directorySources, self.config["source"]) # путь до файла исходника './mod_testBuild/source/mod_testBuild.py'
        subprocess.check_call([compile_exe, '-m', 'compileall', py], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # компилируем, используя Python 2.7
        shutil.move('{}c'.format(py), self.directoryTempCompiled) # перемещаем во временную папку для компилированного мода
        shutil.copy2(os.path.realpath(os.path.join(self.directorySources, self.config["meta"])), os.path.realpath(self.directoryTemp)) # перемещаем во временную папку в корень
        if 'resources' in self.config and self.config['resources']: # копируем ресурсы для мода
            for directory in self.config['resources']:
                source_dir = os.path.join(self.directorySources, directory) # исходный путь
                dest_dir = os.path.realpath(os.path.join(self.directoryTemp, 'res', directory)) # путь назначения
                if os.path.exists(source_dir): # проверка на наличие файлов\папок и копирование при наличии
                    if os.path.isdir(source_dir):
                        shutil.copytree(source_dir, dest_dir)
                    else:
                        shutil.copy2(source_dir, dest_dir)
        wotmod_name = os.path.realpath(os.path.join(self.directoryRelease, '{}_{:.2f}.wotmod'.format(MOD_NAME, self.config["version"])))
        arc_path = [os.path.realpath('7z.exe'), "a", "-tzip", "-ssw", "-mx0", wotmod_name] # Вызов архиватора из './.github/7z.exe a -tzip -ssw -mx0 ./mod_testBuild/release/mod_testBuild_3.12.wotmod'
        subprocess.check_call(arc_path + [os.path.realpath(os.path.join(self.directoryTemp, 'res'))], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # пакуем './mod_testBuild/.out/res'
        subprocess.check_call(arc_path + [os.path.realpath(os.path.join(self.directoryTemp, os.path.basename(self.config["meta"])))], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # пакуем './mod_testBuild/.out/meta.xml'
        subprocess.check_call(arc_path + [self.create_license()], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # создаем файл лицензии и пакуем его './mod_testBuild/.out/LICENSE'


    def create_license(self):
        b64 = "DQogICAgICAgIERPIFdIQVQgVEhFIEZVQ0sgWU9VIFdBTlQgVE8gUFVCTElDIExJQ0VOU0UgDQogICAgICAgICAgICAgICAgICAgIFZlcnNpb24gMiwgRGVjZW1iZXIgMjAwNCANCg0KIENvcHlyaWdodCAoQykgMjAwNCBTYW0gSG9jZXZhciA8c2FtQGhvY2V2YXIubmV0PiANCg0KIEV2ZXJ5b25lIGlzIHBlcm1pdHRlZCB0byBjb3B5IGFuZCBkaXN0cmlidXRlIHZlcmJhdGltIG9yIG1vZGlmaWVkIA0KIGNvcGllcyBvZiB0aGlzIGxpY2Vuc2UgZG9jdW1lbnQsIGFuZCBjaGFuZ2luZyBpdCBpcyBhbGxvd2VkIGFzIGxvbmcgDQogYXMgdGhlIG5hbWUgaXMgY2hhbmdlZC4gDQoNCiAgICAgICAgICAgIERPIFdIQVQgVEhFIEZVQ0sgWU9VIFdBTlQgVE8gUFVCTElDIExJQ0VOU0UgDQogICBURVJNUyBBTkQgQ09ORElUSU9OUyBGT1IgQ09QWUlORywgRElTVFJJQlVUSU9OIEFORCBNT0RJRklDQVRJT04gDQoNCiAgMC4gWW91IGp1c3QgRE8gV0hBVCBUSEUgRlVDSyBZT1UgV0FOVCBUTy4NCg=="
        output_name = os.path.realpath(os.path.join(self.directoryTemp, 'LICENSE'))
        data = base64.b64decode(b64)
        with open(output_name, "wb") as output_file:
            output_file.write(data)
        output_file.close()
        return output_name

class Release(object):

    def __init__(self, build, name, version, lesta = False):
        self.data = build
        self.clear()
        self.zipDirPath = os.path.join(self.data.directoryBase, 'zip')
        zip_name = '{}.zip' if not lesta else '{}_RU.zip'
        self.zipFilePath = os.path.realpath(os.path.join(self.zipDirPath, zip_name.format(name)))
        self.modsPath = os.path.join(self.data.directoryTemp, 'mods')
        self.versionPath = os.path.join(self.modsPath, version)
        self.versionPathMod = os.path.join(self.modsPath, version, 'spoter')
        self.configPath = os.path.join(self.modsPath, 'configs', 'spoter', os.path.splitext(os.path.basename(self.data.config["config"]))[0])
        if 'mod_mods_gui' in MOD_NAME:
            self.versionPathMod = os.path.join(self.modsPath, version)
            self.configPath = os.path.join(self.modsPath, 'configs',os.path.splitext(os.path.basename(self.data.config["config"]))[0])
        self.i18n = os.path.join(self.configPath, 'i18n')
        self.packZip()
        self.clear()

    def packZip(self):
        try:
            # папку для текущей версии
            os.makedirs(self.versionPathMod)
        except OSError:
            if not os.path.isdir(self.versionPathMod):
                raise
        try:
            # папку конфигов
            os.makedirs(self.i18n)
        except OSError:
            if not os.path.isdir(self.i18n):
                raise
        try:
            # релизную папку итогового архива
            os.makedirs(self.zipDirPath)
        except OSError:
            if not os.path.isdir(self.zipDirPath):
                raise
        if 'mod_mods_gui' not in MOD_NAME:
            path = os.path.realpath(os.path.join(self.modsPath, 'configs', 'mods_gui', 'i18n'))
            try:
                # папку конфигов
                os.makedirs(path)
            except OSError:
                if not os.path.isdir(path):
                    raise


        file_path = os.path.realpath(os.path.join(self.data.directoryRelease, '{}_{:.2f}.wotmod'.format(MOD_NAME, self.data.config["version"]))) # работаем с wotmod архивом
        if os.path.isfile(file_path):
            shutil.copy2(file_path, os.path.realpath(self.versionPathMod)) # перемещаем во временную папку с учётом номера версии
        file_path = os.path.realpath(os.path.join(self.data.directorySources, self.data.config["config"])) # работаем с конфигом мода
        if os.path.isfile(file_path) and 'mod_mods_gui' not in MOD_NAME:
            shutil.copy2(file_path, os.path.realpath(self.configPath)) # копируем во временную папку конфигов

        for path in glob.glob(os.path.realpath(os.path.join(self.data.directorySources, self.data.config["i18n"], "*.*"))): # копируем языковые конфиги во временную папку
            if os.path.isfile(path):
                shutil.copy2(path, os.path.realpath(self.i18n))

        if 'mod_mods_gui' in MOD_NAME: # работаем если выбрано ядро модов
            additional_path = os.path.realpath(os.path.join(self.data.directorySources, 'additional')) # копируем дополнительные ресурсы
            if os.path.exists(additional_path):
                for path in glob.glob(os.path.join(additional_path, "*.wotmod")):
                    if os.path.isfile(path):
                        shutil.copy2(path, os.path.realpath(self.versionPath))
                for path in glob.glob(os.path.join(additional_path, "*.txt_")):
                    if os.path.isfile(path):
                        shutil.copy2(path, os.path.realpath(self.configPath))
        else:
            additional_path = os.path.realpath('../mod_mods_gui/release')
            if os.path.exists(additional_path):
                for path in glob.glob(os.path.join(additional_path, "*.wotmod")):
                    if os.path.isfile(path):
                        shutil.copy2(path, os.path.realpath(self.versionPath))
                for path in glob.glob(os.path.join(additional_path, "*.txt_")):
                    if os.path.isfile(path):
                        shutil.copy2(path, os.path.realpath(os.path.join(self.modsPath, 'configs', 'mods_gui')))
            additional_path = os.path.realpath('../mod_mods_gui/release/i18n')
            if os.path.exists(additional_path):
                for path in glob.glob(os.path.join(additional_path, "*.json")):
                    if os.path.isfile(path):
                        shutil.copy2(path, os.path.realpath(os.path.join(self.modsPath, 'configs', 'mods_gui', 'i18n')))
                for path in glob.glob(os.path.join(additional_path, "*.html")):
                    if os.path.isfile(path):
                        shutil.copy2(path, os.path.realpath(os.path.join(self.modsPath, 'configs', 'mods_gui', 'i18n')))

        additional_path = os.path.realpath(os.path.join(self.data.directorySources, 'addons/mods/oldskool')) # копируем дополнительные ресурсы  для мода отметок
        if os.path.exists(additional_path):
            for path in glob.glob(os.path.join(additional_path, "*.wotmod")):
                if os.path.isfile(path):
                    shutil.copy2(path, os.path.realpath(os.path.join(self.versionPath, 'oldskool')))
            additional_path = os.path.realpath('../mod_mods_gui/release')
            if os.path.exists(additional_path):
                for path in glob.glob(os.path.join(additional_path, "*.txt_")):
                    if os.path.isfile(path):
                        shutil.copy2(path, os.path.realpath(os.path.join(self.modsPath, 'configs', 'mods_gui')))

        additional_path = os.path.realpath(os.path.join(self.data.directorySources, 'addons/configs/oldskool'))  # копируем дополнительные ресурсы конфигов для мода отметок
        if os.path.exists(additional_path):
            for path in glob.glob(os.path.join(additional_path, "*.json")):
                if os.path.isfile(path):
                    shutil.copy2(path, os.path.realpath(os.path.join(self.modsPath, 'configs', 'oldskool')))


        # Упаковываем итоговый архив, перезаписывая если уже существует
        if os.path.isfile(self.zipFilePath):
            os.unlink(self.zipFilePath)
        arc_path = [os.path.realpath('7z.exe'), "a", "-tzip", "-ssw", "-mx9", "-aoa", self.zipFilePath, os.path.realpath(self.modsPath)]  # Вызов архиватора из './.github/7z.exe a -tzip -ssw -mx0 ./mod_testBuild/zip/mod_testBuild.zip'
        subprocess.check_call(arc_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  # пакуем итоговый архив './mod_testBuild/zip/mod_testBuild.zip'


    def clear(self):
        try:
            shutil.rmtree(self.data.directoryTemp, True)
        except OSError:
            pass

try:
    build = Build()

    Release(build, MOD_NAME, CLIENT_VERSION_WG)
    Release(build, MOD_NAME, CLIENT_VERSION_RU, True)

    if 'mod_mods_gui' not in MOD_NAME: # чистим за собой если не ядро
        directoryBase = os.path.realpath('./../%s' %(MOD_NAME)) # Директория мода формата './../mod_testBuild', реальный путь вида 'D:\github.com\spoter-mods\mod_testBuild'
        directoryRelease = os.path.join(directoryBase, 'release') # Директория в которой хранится релизный архив мода 'mod_testBuild/release'
        try:
            shutil.rmtree(directoryRelease, True)
        except OSError:
            pass
    print('./{} :OK'.format(MOD_NAME))
except Exception as e:
    print('./{} : BAD'.format(MOD_NAME))
    print('ERROR: {}'.format(e))
    traceback.print_exc()
