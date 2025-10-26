"""
Модуль для загрузки и обработки конфигурации из JSON файла
"""

import json
import os


class ConfigurationError(Exception):
    """Исключение для ошибок конфигурации"""
    pass


def load_configuration(config_file="config.json"):
    """
    Загружает конфигурацию из JSON файла

    Args:
        config_file (str): Путь к конфигурационному файлу

    Returns:
        dict: Словарь с параметрами конфигурации

    Raises:
        ConfigurationError: Если произошла ошибка при загрузке конфигурации
    """
    try:
        # Проверка существования файла
        if not os.path.exists(config_file):
            raise ConfigurationError(f"Конфигурационный файл '{config_file}' не найден")

        # Чтение файла
        with open(config_file, 'r', encoding='utf-8') as file:
            config_data = json.load(file)

        # Базовые проверки структуры
        if not isinstance(config_data, dict):
            raise ConfigurationError("Конфигурационный файл должен содержать JSON объект")

        return config_data

    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Ошибка парсинга JSON: {e}")
    except PermissionError as e:
        raise ConfigurationError(f"Нет прав доступа к файлу конфигурации: {e}")
    except Exception as e:
        raise ConfigurationError(f"Ошибка при чтении конфигурационного файла: {e}")


def create_sample_config():
    """Создает пример конфигурационного файла"""
    sample_config = {
        "package_name": "requests",
        "repository_url": "https://pypi.org/simple/",
        "test_repository_mode": False,
        "test_repository_path": "./test_repo",
        "max_dependency_depth": 3
    }

    with open("config.json", 'w', encoding='utf-8') as file:
        json.dump(sample_config, file, indent=4, ensure_ascii=False)

    print("Создан пример конфигурационного файла 'config.json'")


if __name__ == "__main__":
    create_sample_config()
