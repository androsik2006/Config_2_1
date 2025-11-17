#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей пакетов - Этап 2
"""

import sys
import os
import json
import urllib.request
import urllib.error
import argparse
from xml.etree import ElementTree


def get_user_input():
    """
    Получение параметров от пользователя через командную строку
    """
    parser = argparse.ArgumentParser(description='Анализ зависимостей Maven пакетов')

    parser.add_argument('--package', '-p',
                        help='Имя пакета в формате groupId:artifactId (например: org.springframework:spring-core)')

    parser.add_argument('--repository', '-r',
                        help='URL Maven репозитория')

    parser.add_argument('--depth', '-d', type=int,
                        help='Максимальная глубина анализа')

    parser.add_argument('--config', '-c', default='config.json',
                        help='Путь к конфигурационному файлу (по умолчанию: config.json)')

    return parser.parse_args()


def load_config_from_file(config_file):
    """
    Загрузка конфигурации из JSON файла
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Конфигурационный файл '{config_file}' не найден")
        return {}
    except Exception as e:
        print(f"Ошибка загрузки конфигурации из файла: {e}")
        return {}


def load_config_from_url(config_url):
    """
    Загрузка конфигурации из URL
    """
    try:
        print(f"Загрузка конфигурации из URL: {config_url}")

        with urllib.request.urlopen(config_url) as response:
            content = response.read().decode('utf-8')
            config_data = json.loads(content)

        print("Конфигурация успешно загружена из URL")
        return config_data

    except urllib.error.HTTPError as e:
        print(f"HTTP ошибка при загрузке конфигурации: {e.code} {e.reason}")
        return {}
    except urllib.error.URLError as e:
        print(f"Ошибка сети при загрузке конфигурации: {e.reason}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON конфигурации: {e}")
        return {}
    except Exception as e:
        print(f"Неожиданная ошибка при загрузке конфигурации: {e}")
        return {}


def create_configuration(args):
    """
    Создание конфигурации на основе аргументов командной строки и файла/URL
    """
    config = {}

    # Загружаем конфигурацию из файла или URL
    if args.config:
        if args.config.startswith('http://') or args.config.startswith('https://'):
            # Загрузка конфигурации из URL
            file_config = load_config_from_url(args.config)
        else:
            # Загрузка конфигурации из локального файла
            file_config = load_config_from_file(args.config)

        config.update(file_config)

    # Аргументы командной строки имеют приоритет над файлом/URL
    if args.package:
        config['package_name'] = args.package
    if args.repository:
        config['repository_url'] = args.repository
    if args.depth:
        config['max_dependency_depth'] = args.depth

    # Устанавливаем значения по умолчанию, если не заданы
    if 'package_name' not in config:
        config['package_name'] = 'org.springframework:spring-core'  # пример по умолчанию

    if 'repository_url' not in config:
        config['repository_url'] = 'https://repo1.maven.org/maven2'

    if 'max_dependency_depth' not in config:
        config['max_dependency_depth'] = 3

    if 'test_repository_mode' not in config:
        config['test_repository_mode'] = False

    return config


def display_configuration(config):
    """Вывод всех параметров конфигурации в формате ключ-значение"""
    print("=== КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ ===")
    for key, value in config.items():
        print(f"{key}: {value}")
    print("===============================")


def validate_configuration(config):
    """Валидация параметров конфигурации"""
    errors = []

    # Проверка имени пакета
    if not config.get('package_name'):
        errors.append("Имя пакета не указано")
    elif not isinstance(config['package_name'], str):
        errors.append("Имя пакета должно быть строкой")
    elif ':' not in config['package_name']:
        errors.append("Имя пакета должно быть в формате groupId:artifactId")

    # Проверка URL репозитория
    repo_url = config.get('repository_url')
    if not repo_url:
        errors.append("URL репозитория не указан")
    elif not isinstance(repo_url, str):
        errors.append("URL репозитория должен быть строкой")
    elif not (repo_url.startswith('http://') or repo_url.startswith('https://')):
        errors.append("URL репозитория должен начинаться с http:// или https://")

    # Проверка максимальной глубины анализа
    max_depth = config.get('max_dependency_depth')
    if max_depth is None:
        errors.append("Максимальная глубина анализа не указана")
    elif not isinstance(max_depth, int):
        errors.append("Максимальная глубина анализа должна быть целым числом")
    elif max_depth < 1:
        errors.append("Максимальная глубина анализа должна быть положительным числом")
    elif max_depth > 10:
        errors.append("Максимальная глубина анализа не может превышать 10")

    return errors


def parse_maven_metadata(content):
    """
    Парсинг Maven metadata для извлечения информации о последней версии
    """
    try:
        root = ElementTree.fromstring(content)
        versioning = root.find('versioning')
        if versioning is not None:
            latest = versioning.find('latest')
            if latest is not None and latest.text:
                return latest.text

            release = versioning.find('release')
            if release is not None and release.text:
                return release.text

        # Если не нашли latest/release, берем последнюю версию из versions
        versions_elem = versioning.find('versions') if versioning else None
        if versions_elem is not None:
            versions = [v.text for v in versions_elem.findall('version') if v.text]
            if versions:
                # Сортируем версии и берем последнюю
                versions.sort(key=lambda v: [int(x) for x in v.split('.') if x.isdigit()])
                return versions[-1]

        return None
    except Exception as e:
        raise DependencyError(f"Ошибка парсинга Maven metadata: {e}")


def get_package_metadata(package_name, repository_url):
    """
    Получение метаданных пакета из Maven репозитория
    """
    try:
        # Разбираем имя пакета на groupId и artifactId
        parts = package_name.split(':')
        if len(parts) != 2:
            raise DependencyError(f"Некорректный формат имени пакета: {package_name}. Ожидается: groupId:artifactId")

        group_id, artifact_id = parts

        # Формируем URL для metadata
        group_path = group_id.replace('.', '/')
        metadata_url = f"{repository_url}/{group_path}/{artifact_id}/maven-metadata.xml"

        print(f"Запрос метаданных: {metadata_url}")

        # Загружаем metadata
        with urllib.request.urlopen(metadata_url) as response:
            content = response.read().decode('utf-8')

        version = parse_maven_metadata(content)
        if not version:
            raise DependencyError(f"Не удалось определить версию для пакета {package_name}")

        return group_id, artifact_id, version

    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise DependencyError(f"Пакет {package_name} не найден в репозитории")
        else:
            raise DependencyError(f"HTTP ошибка при запросе метаданных: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise DependencyError(f"Ошибка сети при запросе метаданных: {e.reason}")
    except Exception as e:
        raise DependencyError(f"Ошибка при получении метаданных: {e}")


def get_pom_file(group_id, artifact_id, version, repository_url):
    """
    Получение POM файла пакета
    """
    try:
        group_path = group_id.replace('.', '/')
        pom_url = f"{repository_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"

        print(f"Запрос POM файла: {pom_url}")

        with urllib.request.urlopen(pom_url) as response:
            content = response.read().decode('utf-8')

        return content

    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise DependencyError(f"POM файл для {group_id}:{artifact_id}:{version} не найден")
        else:
            raise DependencyError(f"HTTP ошибка при запросе POM: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise DependencyError(f"Ошибка сети при запросе POM: {e.reason}")
    except Exception as e:
        raise DependencyError(f"Ошибка при получении POM: {e}")


def parse_dependencies_from_pom(pom_content):
    """
    Извлечение прямых зависимостей из POM файла
    """
    try:
        namespaces = {'maven': 'http://maven.apache.org/POM/4.0.0'}
        root = ElementTree.fromstring(pom_content)

        dependencies = []

        # Ищем секцию dependencies
        dependencies_elem = root.find('maven:dependencies', namespaces)
        if dependencies_elem is None:
            # Пробуем без namespace
            dependencies_elem = root.find('dependencies')

        if dependencies_elem is not None:
            dependency_elems = dependencies_elem.findall('maven:dependency', namespaces)
            if not dependency_elems:
                dependency_elems = dependencies_elem.findall('dependency')

            for dep_elem in dependency_elems:
                group_id_elem = dep_elem.find('maven:groupId', namespaces)
                if group_id_elem is None:
                    group_id_elem = dep_elem.find('groupId')

                artifact_id_elem = dep_elem.find('maven:artifactId', namespaces)
                if artifact_id_elem is None:
                    artifact_id_elem = dep_elem.find('artifactId')

                version_elem = dep_elem.find('maven:version', namespaces)
                if version_elem is None:
                    version_elem = dep_elem.find('version')

                if group_id_elem is not None and artifact_id_elem is not None:
                    group_id = group_id_elem.text
                    artifact_id = artifact_id_elem.text
                    version = version_elem.text if version_elem is not None else "UNKNOWN"

                    dependency_name = f"{group_id}:{artifact_id}"
                    dependencies.append({
                        'name': dependency_name,
                        'version': version,
                        'group_id': group_id,
                        'artifact_id': artifact_id
                    })

        return dependencies

    except Exception as e:
        raise DependencyError(f"Ошибка парсинга POM файла: {e}")


def get_direct_dependencies(package_name, repository_url):
    """
    Получение прямых зависимостей пакета
    """
    print(f"\n=== АНАЛИЗ ПАКЕТА: {package_name} ===")

    # Получаем метаданные пакета
    group_id, artifact_id, version = get_package_metadata(package_name, repository_url)
    print(f"Найдена версия: {version}")

    # Получаем POM файл
    pom_content = get_pom_file(group_id, artifact_id, version, repository_url)

    # Парсим зависимости
    dependencies = parse_dependencies_from_pom(pom_content)

    return dependencies


def display_dependencies(dependencies, package_name):
    """
    Вывод прямых зависимостей на экран
    """
    print(f"\n=== ПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА '{package_name}' ===")

    if not dependencies:
        print("Прямые зависимости не найдены")
        return

    for i, dep in enumerate(dependencies, 1):
        print(f"{i}. {dep['name']} : {dep['version']}")

    print(f"\nВсего найдено зависимостей: {len(dependencies)}")


class DependencyError(Exception):
    """Класс для ошибок связанных с зависимостями"""
    pass


def main():
    """Основная функция приложения"""
    try:
        # Получаем параметры от пользователя
        args = get_user_input()

        # Создаем конфигурацию
        config = create_configuration(args)

        # Валидация конфигурации
        validation_errors = validate_configuration(config)
        if validation_errors:
            print("Ошибки валидации конфигурации:")
            for error in validation_errors:
                print(f"  - {error}")
            sys.exit(1)

        # Вывод конфигурации
        display_configuration(config)

        # Получаем прямые зависимости
        repository_url = config['repository_url']
        package_name = config['package_name']

        dependencies = get_direct_dependencies(package_name, repository_url)

        # Выводим зависимости на экран (требование этапа 2)
        display_dependencies(dependencies, package_name)

        print("\nАнализ завершен успешно!")

    except DependencyError as e:
        print(f"Ошибка анализа зависимостей: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
