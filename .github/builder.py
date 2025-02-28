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
import sys
import traceback

# Настройка вывода в консоль для поддержки UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

# Определение режима отладки (по умолчанию OFF)
DEBUG_MODE = '--debug' in sys.argv

def debug(message):
    """Вывод отладочных сообщений на английском языке."""
    if DEBUG_MODE:
        print(u"[DEBUG] {}".format(message))

def find_main_folder():
    """
    Поиск основной директории проекта.
    Проверяем наличие папки мода в родительской директории или текущей директории.
    """
    debug(u"Searching for main folder")
    paths = [
        os.path.realpath(os.path.join('..', MOD_NAME)),
        os.path.realpath(MOD_NAME)
    ]
    for path in paths:
        if os.path.isdir(path):
            debug(u"Found main folder: {}".format(path))
            return os.path.dirname(path)
    raise IOError(u"Main folder not found")

# Чтение аргументов командной строки
if len(sys.argv) < 4:
    print(u"[ERROR] Недостаточно аргументов. Использование: python builder.py MOD_NAME CLIENT_VERSION_RU CLIENT_VERSION_WG [--debug]")
    sys.exit(1)

MOD_NAME = sys.argv[1]  # Название мода
CLIENT_VERSION_RU = sys.argv[2]  # Версия клиента для Lesta
CLIENT_VERSION_WG = sys.argv[3]  # Версия клиента для WG

MAIN_FOLDER = find_main_folder()

class Build(object):
    """
    Класс для сборки мода.
    Выполняет очистку временных директорий, чтение конфигурации,
    пересоздание структуры, обновление версий, компиляцию исходников
    и создание WOTMOD архива.
    """
    def __init__(self):
        # Инициализация директорий мода
        self.directory_base = os.path.join(MAIN_FOLDER, MOD_NAME)
        self.directory_temp = os.path.join(self.directory_base, '.out')
        self.directory_temp_compiled = os.path.join(self.directory_temp, 'res', 'scripts', 'client', 'gui', 'mods')
        self.directory_release = os.path.join(self.directory_base, 'release')
        self.directory_sources = os.path.join(self.directory_base, 'source')
        
        debug(u"Base directory: {}".format(self.directory_base))
        
        self.clear_temp()
        self.config = self.read_config()
        self.recreate_structures()
        self.create_wotmod_archive()
        self.clear_temp()

    def clear_temp(self):
        """Очистка временной директории сборки."""
        debug(u"Clearing temporary directory: {}".format(self.directory_temp))
        if os.path.exists(self.directory_temp):
            shutil.rmtree(self.directory_temp, ignore_errors=True)

    def read_config(self):
        """
        Чтение конфигурационного файла VERSION из каталога source.
        Формат файла — JSON, кодировка UTF-8.
        """
        config_path = os.path.join(self.directory_sources, 'VERSION')
        debug(u"Reading config from: {}".format(config_path))
        with codecs.open(config_path, 'r', 'utf-8') as f:
            data = json.load(f)
        return data

    def recreate_structures(self):
        """
        Пересоздание структуры директорий для сборки и обновление версий в файлах.
        Обновляются файлы: исходный код, meta, config и языковые файлы (i18n).
        """
        debug(u"Recreating directory structures.")
        # Создание необходимых директорий
        for path in [self.directory_temp, self.directory_temp_compiled, self.directory_release]:
            if not os.path.exists(path):
                os.makedirs(path)
                debug(u"Created directory: {}".format(path))
        
        # Формирование строки версии и списка файлов для обновления
        version_str = u'{:.2f}'.format(self.config.get("version", 0))
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        files_to_update = []
        if 'source' in self.config and self.config['source']:
            source_file = os.path.join(self.directory_sources, self.config['source'])
            files_to_update.append((source_file, u'self.version = ', u"'v{} ({})'".format(version_str, current_date)))
            files_to_update.append((source_file, u'self.version_id = ', re.sub(u'[.\s]', u'', version_str)))
            files_to_update.append((source_file, u'VERSION_MOD = ', u"'v{} ({})'".format(version_str, current_date)))
        if 'meta' in self.config and self.config['meta']:
            meta_file = os.path.join(self.directory_sources, self.config['meta'])
            files_to_update.append((meta_file, u'<version>', u'<version>{}</version>'.format(version_str)))
        if 'config' in self.config and self.config['config']:
            config_file = os.path.join(self.directory_sources, self.config['config'])
            files_to_update.append((config_file, u'"version": ', re.sub(u'[.\s]', u'', version_str)))
        if 'i18n' in self.config and self.config['i18n']:
            i18n_dir = os.path.join(self.directory_sources, self.config['i18n'])
            for file_path in glob.glob(os.path.join(i18n_dir, '*.*')):
                files_to_update.append((file_path, u'"version": ', re.sub(u'[.\s]', u'', version_str)))
        
        for file_tuple in files_to_update:
            self.update_file_with_new_version(*file_tuple)

    @staticmethod
    def update_file_with_new_version(path, search_str, replace_str):
        """
        Обновление версии в указанном файле.
        Если в строке обнаруживается search_str, она заменяется на строку с replace_str.
        """
        debug(u"Updating file: {}".format(path))
        if os.path.exists(path):
            try:
                with codecs.open(path, 'r+', 'utf-8') as f:
                    content = []
                    for line in f:
                        if search_str in line:
                            new_line = line.split(search_str)[0] + search_str + replace_str + u'\n'
                            content.append(new_line)
                        else:
                            content.append(line)
                    f.seek(0)
                    f.writelines(content)
                    f.truncate()
                debug(u"File updated successfully: {}".format(path))
            except Exception as e:
                debug(u"Error updating file {}: {}".format(path, e))
                raise
        else:
            debug(u"File not found: {}".format(path))

    def create_wotmod_archive(self):
        """
        Компиляция исходного Python-файла, копирование meta-файла и ресурсов,
        генерация LICENSE и создание WOTMOD архива с помощью 7z.exe.
        """
        debug(u"Building WOTMOD archive.")
        source_py = os.path.join(self.directory_sources, self.config.get("source", ""))
        if not os.path.exists(source_py):
            raise IOError(u"Source file not found: {}".format(source_py))
        try:
            subprocess.check_call(
                [COMPILE_EXE, '-m', 'compileall', source_py],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            debug(u"Compilation successful for: {}".format(source_py))
        except subprocess.CalledProcessError as e:
            debug(u"Compilation failed: {}".format(e))
            raise

        # Перемещение скомпилированного файла (.pyc)
        compiled_file = u"{}c".format(source_py)
        if not os.path.exists(compiled_file):
            raise IOError(u"Compiled file not found: {}".format(compiled_file))
        try:
            shutil.move(compiled_file, self.directory_temp_compiled)
            debug(u"Moved compiled file to: {}".format(self.directory_temp_compiled))
        except Exception as e:
            debug(u"Error moving compiled file: {}".format(e))
            raise

        # Копирование meta-файла в корень временной директории
        meta_source = os.path.join(self.directory_sources, self.config.get("meta", ""))
        try:
            shutil.copy2(os.path.realpath(meta_source), os.path.realpath(self.directory_temp))
            debug(u"Copied meta file to temporary directory.")
        except Exception as e:
            debug(u"Error copying meta file: {}".format(e))
            raise

        # Копирование ресурсов, если они указаны в конфигурации
        if 'resources' in self.config and self.config['resources']:
            for directory in self.config['resources']:
                source_dir = os.path.join(self.directory_sources, directory)
                dest_dir = os.path.join(self.directory_temp, 'res', directory)
                if os.path.exists(source_dir):
                    try:
                        if os.path.isdir(source_dir):
                            shutil.copytree(source_dir, dest_dir)
                        else:
                            shutil.copy2(source_dir, dest_dir)
                        debug(u"Copied resource from {} to {}".format(source_dir, dest_dir))
                    except Exception as e:
                        debug(u"Error copying resource {}: {}".format(source_dir, e))
                        raise

        # Создание файла LICENSE
        license_path = self.create_license()

        # Формирование имени архива и упаковка с помощью 7z.exe
        archive_name = os.path.join(
            self.directory_release,
            u'{}_{}.wotmod'.format(MOD_NAME, u'{:.2f}'.format(self.config.get("version", 0)))
        )
        seven_z = os.path.join(MAIN_FOLDER, '.github', '7z.exe')
        try:
            subprocess.check_call([
                seven_z, 'a', '-tzip', '-ssw', '-mx0',
                archive_name,
                os.path.join(self.directory_temp, 'res'),
                os.path.join(self.directory_temp, os.path.basename(self.config.get("meta", ""))),
                license_path
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            debug(u"WOTMOD archive created: {}".format(archive_name))
        except subprocess.CalledProcessError as e:
            debug(u"Error creating WOTMOD archive: {}".format(e))
            raise

    def create_license(self):
        """
        Генерация файла LICENSE из base64 строки.
        Файл записывается в каталоге временной сборки.
        """
        debug(u"Creating LICENSE file.")
        license_text = base64.b64decode(
            "DQogICAgICAgIERPIFdIQVQgVEhFIEZVQ0sgWU9VIFdBTlQgVE8gUFVCTElDIExJQ0VOU0UgDQogICAgICAgICAgICAgICAgICAgIFZlcnNpb24gMiwgRGVjZW1iZXIgMjAwNCANCg0KIENvcHlyaWdodCAoQykgMjAwNCBTYW0gSG9jZXZhciA8c2FtQGhvY2V2YXIubmV0PiANCg0KIEV2ZXJ5b25lIGlzIHBlcm1pdHRlZCB0byBjb3B5IGFuZCBkaXN0cmlidXRlIHZlcmJhdGltIG9yIG1vZGlmaWVkIA0KIGNvcGllcyBvZiB0aGlzIGxpY2Vuc2UgZG9jdW1lbnQsIGFuZCBjaGFuZ2luZyBpdCBpcyBhbGxvd2VkIGFzIGxvbmcgDQogYXMgdGhlIG5hbWUgaXMgY2hhbmdlZC4gDQoNCiAgICAgICAgICAgIERPIFdIQVQgVEhFIEZVQ0sgWU9VIFdBTlQgVE8gUFVCTElDIExJQ0VOU0UgDQogICBURVJNUyBBTkQgQ09ORElUSU9OUyBGT1IgQ09QWUlORywgRElTVFJJQlVUSU9OIEFORCBNT0RJRklDQVRJT04gDQoNCiAgMC4gWW91IGp1c3QgRE8gV0hBVCBUSEUgRlVDSyBZT1UgV0FOVCBUTy4NCg=="
        )
        license_path = os.path.join(self.directory_temp, 'LICENSE')
        try:
            with codecs.open(license_path, 'w', 'utf-8') as f:
                f.write(license_text.decode('utf-8'))
            debug(u"LICENSE file created at: {}".format(license_path))
            return license_path
        except Exception as e:
            debug(u"Error creating LICENSE file: {}".format(e))
            raise

class Release(object):
    """
    Класс для упаковки релизного архива мода.
    Формирует файловую структуру, копирует WOTMOD архив, конфигурацию,
    языковые файлы и дополнительные ресурсы, а затем создаёт финальный zip архив.
    """
    def __init__(self, build, client_version, lesta=False):
        self.build = build
        self.client_version = client_version
        self.lesta = lesta
        
        self.zip_dir = os.path.join(self.build.directory_base, 'zip')
        if not self.lesta:
            zip_name = u'{}.zip'.format(MOD_NAME)
        else:
            zip_name = u'{}_RU.zip'.format(MOD_NAME)
        self.zip_file_path = os.path.realpath(os.path.join(self.zip_dir, zip_name))
        
        self.mods_path = os.path.join(self.build.directory_temp, 'mods')
        self.version_path = os.path.join(self.mods_path, self.client_version)
        self.version_path_mod = os.path.join(self.mods_path, self.client_version, 'spoter')
        self.config_path = os.path.join(self.mods_path, 'configs', 'spoter',
                                        os.path.splitext(os.path.basename(self.build.config.get("config", "")))[0])
        if 'mod_mods_gui' in MOD_NAME:
            self.version_path_mod = os.path.join(self.mods_path, self.client_version)
            self.config_path = os.path.join(self.mods_path, 'configs',
                                            os.path.splitext(os.path.basename(self.build.config.get("config", "")))[0])
        self.i18n_path = os.path.join(self.config_path, 'i18n')
        
        debug(u"Initializing release packaging for version: {} (lesta={})".format(self.client_version, self.lesta))
        self.pack_zip()
        self.clear_temp()

    def pack_zip(self):
        """Упаковка файлов в zip архив релиза."""
        debug(u"Packing zip archive: {}".format(self.zip_file_path))
        # Создание необходимых директорий
        for path in [self.version_path_mod, self.i18n_path, self.zip_dir]:
            if not os.path.exists(path):
                os.makedirs(path)
                debug(u"Created directory: {}".format(path))
        if 'mod_mods_gui' not in MOD_NAME:
            extra_config_path = os.path.join(self.mods_path, 'configs', 'mods_gui', 'i18n')
            if not os.path.exists(extra_config_path):
                os.makedirs(extra_config_path)
                debug(u"Created extra i18n directory: {}".format(extra_config_path))
        
        # Копирование WOTMOD архива в папку с текущей версией
        wotmod_file = os.path.realpath(os.path.join(
            self.build.directory_release,
            u'{}_{}.wotmod'.format(MOD_NAME, u'{:.2f}'.format(self.build.config.get("version", 0)))
        ))
        if os.path.isfile(wotmod_file):
            try:
                shutil.copy2(wotmod_file, os.path.realpath(self.version_path_mod))
                debug(u"Copied wotmod file to version directory.")
            except Exception as e:
                debug(u"Error copying wotmod file: {}".format(e))
                raise
        
        # Копирование конфигурационного файла, если требуется
        config_source = os.path.realpath(os.path.join(self.build.directory_sources, self.build.config.get("config", "")))
        if os.path.isfile(config_source) and 'mod_mods_gui' not in MOD_NAME:
            try:
                shutil.copy2(config_source, os.path.realpath(self.config_path))
                debug(u"Copied config file to config directory.")
            except Exception as e:
                debug(u"Error copying config file: {}".format(e))
                raise
        
        # Копирование языковых файлов (i18n)
        i18n_source_pattern = os.path.realpath(os.path.join(self.build.directory_sources, self.build.config.get("i18n", ""), "*.*"))
        for file_path in glob.glob(i18n_source_pattern):
            if os.path.isfile(file_path):
                try:
                    shutil.copy2(file_path, os.path.realpath(self.i18n_path))
                    debug(u"Copied i18n file: {} to {}".format(file_path, self.i18n_path))
                except Exception as e:
                    debug(u"Error copying i18n file {}: {}".format(file_path, e))
                    raise
        
        # Обработка дополнительных ресурсов
        if 'mod_mods_gui' in MOD_NAME:
            additional_path = os.path.join(self.build.directory_sources, 'additional')
            if os.path.exists(additional_path):
                for pattern in [u"*.wotmod", u"*.txt_"]:
                    for file_path in glob.glob(os.path.join(additional_path, pattern)):
                        if os.path.isfile(file_path):
                            dest = self.version_path_mod if pattern == u"*.wotmod" else self.config_path
                            try:
                                shutil.copy2(file_path, os.path.realpath(dest))
                                debug(u"Copied additional file {} to {}".format(file_path, dest))
                            except Exception as e:
                                debug(u"Error copying additional file {}: {}".format(file_path, e))
                                raise
        else:
            additional_path = os.path.join(MAIN_FOLDER, 'mod_mods_gui', 'release')
            if os.path.exists(additional_path):
                for pattern in [u"*.wotmod", u"*.txt_"]:
                    for file_path in glob.glob(os.path.join(additional_path, pattern)):
                        if os.path.isfile(file_path):
                            dest = self.version_path_mod if pattern == u"*.wotmod" else os.path.join(self.mods_path, 'configs', 'mods_gui')
                            try:
                                shutil.copy2(file_path, os.path.realpath(dest))
                                debug(u"Copied additional file {} to {}".format(file_path, dest))
                            except Exception as e:
                                debug(u"Error copying additional file {}: {}".format(file_path, e))
                                raise
            extra_i18n_path = os.path.join(MAIN_FOLDER, 'mod_mods_gui', 'release', 'i18n')
            if os.path.exists(extra_i18n_path):
                for pattern in [u"*.json", u"*.html"]:
                    for file_path in glob.glob(os.path.join(extra_i18n_path, pattern)):
                        if os.path.isfile(file_path):
                            dest = os.path.join(self.mods_path, 'configs', 'mods_gui', 'i18n')
                            try:
                                shutil.copy2(file_path, os.path.realpath(dest))
                                debug(u"Copied additional i18n file {} to {}".format(file_path, dest))
                            except Exception as e:
                                debug(u"Error copying additional i18n file {}: {}".format(file_path, e))
                                raise
        
        additional_path = os.path.join(self.build.directory_sources, 'addons', 'mods', 'oldskool')
        if os.path.exists(additional_path):
            for file_path in glob.glob(os.path.join(additional_path, "*.wotmod")):
                if os.path.isfile(file_path):
                    dest = os.path.join(self.version_path, 'oldskool')
                    try:
                        shutil.copy2(file_path, dest)
                        debug(u"Copied oldskool mod file {} to {}".format(file_path, dest))
                    except Exception as e:
                        debug(u"Error copying oldskool mod file {}: {}".format(file_path, e))
                        raise
            additional_extra = os.path.join(MAIN_FOLDER, 'mod_mods_gui', 'release')
            if os.path.exists(additional_extra):
                for file_path in glob.glob(os.path.join(additional_extra, "*.txt_")):
                    if os.path.isfile(file_path):
                        dest = os.path.join(self.mods_path, 'configs', 'mods_gui')
                        try:
                            shutil.copy2(file_path, dest)
                            debug(u"Copied additional txt file {} to {}".format(file_path, dest))
                        except Exception as e:
                            debug(u"Error copying additional txt file {}: {}".format(file_path, e))
                            raise
        
        additional_path = os.path.join(self.build.directory_sources, 'addons', 'configs', 'oldskool')
        if os.path.exists(additional_path):
            for file_path in glob.glob(os.path.join(additional_path, "*.json")):
                if os.path.isfile(file_path):
                    dest = os.path.join(self.mods_path, 'configs', 'oldskool')
                    try:
                        shutil.copy2(file_path, dest)
                        debug(u"Copied oldskool config file {} to {}".format(file_path, dest))
                    except Exception as e:
                        debug(u"Error copying oldskool config file {}: {}".format(file_path, e))
                        raise
        
        # Упаковка итогового архива с помощью 7z.exe
        if os.path.isfile(self.zip_file_path):
            try:
                os.unlink(self.zip_file_path)
                debug(u"Deleted existing zip file: {}".format(self.zip_file_path))
            except Exception as e:
                debug(u"Error deleting existing zip file: {}".format(e))
                raise
        archive_exe = os.path.join(MAIN_FOLDER, '.github', '7z.exe')
        arc_cmd = [
            archive_exe, "a", "-tzip", "-ssw", "-mx9", "-aoa",
            self.zip_file_path,
            os.path.realpath(self.mods_path)
        ]
        try:
            subprocess.check_call(arc_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            debug(u"Zip archive created successfully: {}".format(self.zip_file_path))
        except subprocess.CalledProcessError as e:
            debug(u"Error creating zip archive: {}".format(e))
            raise

    def clear_temp(self):
        """
        Очистка временной директории после упаковки релиза.
        Используется директория сборки из Build.
        """
        debug(u"Clearing temporary directory after release packaging: {}".format(self.build.directory_temp if hasattr(self, 'build') else self.directory_temp))
        if hasattr(self, 'build'):
            if os.path.exists(self.build.directory_temp):
                shutil.rmtree(self.build.directory_temp, ignore_errors=True)
        else:
            if os.path.exists(self.directory_temp):
                shutil.rmtree(self.directory_temp, ignore_errors=True)

if __name__ == "__main__":
    try:
        # Создание сборки мода
        build = Build()
        # Упаковка релизных архивов для международной и русской версий
        release_wg = Release(build, CLIENT_VERSION_WG, lesta=False)
        release_ru = Release(build, CLIENT_VERSION_RU, lesta=True)
        # Вывод результатов: MOD_NAME|путь к архиву WG|путь к архиву RU
        print(u"{}|{}|{}".format(MOD_NAME, release_wg.zip_file_path, release_ru.zip_file_path))
        debug(u"Build process completed successfully.")
    except Exception as e:
        print(u"[ERROR] Build failed: {}".format(e))
        traceback.print_exc()
        sys.exit(1)