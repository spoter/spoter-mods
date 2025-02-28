# -*- coding: utf-8 -*-
import sys
import traceback
import os
import argparse
import json
import subprocess
import codecs


# Настройка вывода в консоль для поддержки UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

def debug(message):
    """Вывод отладочных сообщений на английском языке."""
    if DEBUG_MODE:
        print(u"[DEBUG] {}".format(message))


def find_main_folder():
    """
    Поиск основной папки с модами.
    Проверяем наличие папки mod_mods_gui в родительской директории или текущей директории.
    """
    debug(u"Searching for main mods folder")
    possible_paths = [
        os.path.realpath(os.path.join('..', 'mod_mods_gui')),
        os.path.realpath('mod_mods_gui')
    ]
    for path in possible_paths:
        if os.path.isdir(path):
            debug(u"Found main folder: {}".format(path))
            return os.path.dirname(path)
    raise IOError(u"Main mods folder not found")


def parse_builder_output(output):
    """
    Парсинг вывода builder.py для извлечения результатов сборки.
    Возвращает словарь с результатами.
    """
    debug(u"Parsing builder output")
    result = {}
    for line in output.splitlines():
        if line.startswith('mod_'):
            parts = line.strip().split('|')
            if len(parts) == 3:
                mod_name = parts[0].strip()
                wg_path = parts[1].strip()
                ru_path = parts[2].strip()
                result[mod_name] = {
                    'wg_path': wg_path,
                    'ru_path': ru_path
                }
    return result


def build_mod(mod_name, client_version_ru, client_version_wg):
    """
    Запуск сборки одного мода.
    Возвращает словарь с результатами сборки.
    """
    debug(u"Building mod: {}".format(mod_name))
    script_path = os.path.realpath(os.path.join(MAIN_FOLDER, '.github', 'builder.py'))
    # УДАЛИТЬ
    os.chdir(os.path.dirname(script_path))
    print("[DEBUG] Changed working directory to:", os.getcwd())
    # УДАЛИТЬ

    # Формирование команды
    cmd_args = [
        'python', script_path,
        mod_name,
        client_version_ru,
        client_version_wg
    ]
    if DEBUG_MODE:
        cmd_args.append('--debug')

    debug(u"Command: {}".format(' '.join(cmd_args)))

    # Запуск процесса сборки
    process = subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    # Чтение и обработка вывода
    output, _ = process.communicate()
    output = output.decode('utf-8')

    if DEBUG_MODE:
        print(u"Build with output {}".format(output))

    if process.returncode != 0:
        raise RuntimeError(u"Build failed with code {}".format(process.returncode))

    return parse_builder_output(output)


def main():
    """Основная функция скрипта."""
    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(description='Create mod archives.')
    parser.add_argument('lesta_version', help='Client version for Lesta')
    parser.add_argument('wg_version', help='Client version for WG')
    parser.add_argument('updated_mods', nargs='+', help='List of mods to update')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    global DEBUG_MODE
    DEBUG_MODE = args.debug
    DEBUG_MODE = True

    # Получаем версии клиентов и список модов
    client_version_wg = args.wg_version
    client_version_ru = args.lesta_version
    updated_mods = args.updated_mods

    debug(u"Received arguments:")
    debug(u"  Lesta version: {}".format(client_version_ru))
    debug(u"  WG version: {}".format(client_version_wg))
    debug(u"  Mods to update: {}".format(updated_mods))

    print("[DEBUG] Current working directory:", os.getcwd())
    print("[DEBUG] Directory listing:", os.listdir(os.getcwd()))
    # Поиск основной папки с модами
    global MAIN_FOLDER
    MAIN_FOLDER = find_main_folder()
    debug(u"Main folder: {}".format(MAIN_FOLDER))

    # Инициализация результатов сборки
    build_results = {}

    print(u'\n----- Начало сборки -----')
    print(u' RU версия: {}'.format(client_version_ru))
    print(u' WG версия: {}'.format(client_version_wg))
    print(u' Моды для сборки: {}\n'.format(', '.join(updated_mods)))

    # Обработка каждого мода
    for mod_name in updated_mods:
        try:
            print(u"Обработка мода: {}".format(mod_name))
            mod_result = build_mod(mod_name, client_version_ru, client_version_wg)
            build_results[mod_name] = mod_result
            debug(u"Build success: {}".format(mod_result))
        except Exception as e:
            print(u"[ERROR] Ошибка при обработке мода {}: {}".format(mod_name, e))
            traceback.print_exc()
            sys.exit(1)

    # Вывод результатов
    print(u'\n----- Результаты сборки -----')
    print(json.dumps(build_results, ensure_ascii=False, indent=2))



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(u"[FATAL ERROR] Critical failure: {}".format(e))
        traceback.print_exc()
        sys.exit(1)