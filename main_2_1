#!/usr/bin/env python3
"""
Минимальный прототип инструмента визуализации графа зависимостей пакетов
"""

import sys
import os
from config_loader import load_configuration, ConfigurationError


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

    # Проверка URL репозитория или пути к тестовому репозиторию
    if config.get('test_repository_mode'):
        test_path = config.get('test_repository_path')
        if not test_path:
            errors.append("В режиме тестового репозитория должен быть указан test_repository_path")
        elif not isinstance(test_path, str):
            errors.append("Путь к тестовому репозиторию должен быть строкой")
    else:
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


def main():
    """Основная функция приложения"""
    try:
        # Загрузка конфигурации
        config = load_configuration()

        # Валидация конфигурации
        validation_errors = validate_configuration(config)
        if validation_errors:
            print("Ошибки валидации конфигурации:")
            for error in validation_errors:
                print(f"  - {error}")
            sys.exit(1)

        # Вывод конфигурации
        display_configuration(config)

        # Симуляция анализа зависимостей (для демонстрации)
        print(f"\nАнализ зависимостей для пакета '{config['package_name']}'...")
        if config['test_repository_mode']:
            print(f"Используется тестовый репозиторий: {config['test_repository_path']}")
        else:
            print(f"Используется репозиторий: {config['repository_url']}")
        print(f"Максимальная глубина анализа: {config['max_dependency_depth']}")

        print("\nАнализ завершен успешно!")

    except ConfigurationError as e:
        print(f"Ошибка конфигурации: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
