import pytest
import os
import json
from math import ceil
from calculator import ConfigCalculator

@pytest.fixture
def test_data():
    """
    Фикстура, предоставляющая тестовые данные для тестов калькулятора.
    Возвращает словарь с предустановленными значениями для агентов, 
    хранилища, трафика, почтового трафика, распределенности и узлов.
    """
    return {
        'agents': 1000,
        'storage': 50.0,
        'traffic': 10.0,
        'mail_traffic': 5.0,
        'distributed': True,
        'nodes': 5
    }

@pytest.fixture
def calculator(test_data):
    """
    Фикстура, создающая и возвращающая экземпляр ConfigCalculator,
    инициализированный тестовыми данными.
    """
    return ConfigCalculator(
        agents=test_data['agents'],
        storage=test_data['storage'],
        traffic=test_data['traffic'],
        mail_traffic=test_data['mail_traffic'],
        distributed=test_data['distributed'],
        nodes=test_data['nodes']
    )

def test_calculate_kafka(calculator):
    """
    Тестирование расчета параметров для Kafka.
    Проверяет значения 'replicas', 'memory', 'cpu' и 'storage',
    рассчитанные методом calculate_kafka() калькулятора.
    """
    result = calculator.calculate_kafka()
    assert result['replicas'] == 3 
    assert result['memory'] == ceil(calculator.mail_traffic * 0.5)
    assert result['cpu'] == ceil(0.000169 * calculator.agents ** 0.437923 * calculator.nodes ** 3)
    assert result['storage'] == ceil(0.0004 * calculator.agents ** 0.3231)

def test_calculate_elasticsearch(calculator):
    """
    Тестирование расчета параметров для Elasticsearch.
    Проверяет значения 'replicas', 'cpu' и 'storage',
    рассчитанные методом calculate_elasticsearch() калькулятора.
    """
    result = calculator.calculate_elasticsearch()
    assert result['replicas'] == 3
    assert result['cpu'] == 3
    if calculator.agents <= 5000:
        assert result['storage'] == 0.256
    elif calculator.agents <= 10000:
        assert result['storage'] == 0.512
    else:
        assert result['storage'] == 1

def test_calculate_processor(calculator):
    """
    Тестирование расчета параметров для Processor.
    Проверяет значения 'replicas', 'memory', 'cpu' и 'storage',
    рассчитанные методом calculate_processor() калькулятора.
    """
    result = calculator.calculate_processor()
    assert result['replicas'] == 3
    assert result['memory'] == 5
    assert result['cpu'] == 3
    assert result['storage'] == ceil(4.25870 * (calculator.agents ** 0.98271))

def test_calculate_server(calculator):
    """
    Тестирование расчета параметров для Server.
    Проверяет значения 'replicas', 'memory', 'cpu' и 'storage',
    рассчитанные методом calculate_server() калькулятора.
    """
    result = calculator.calculate_server()
    assert result['replicas'] == min(3, 2)
    assert result['memory'] == ceil(1 / calculator.storage * 1.6)
    assert result['cpu'] == 1
    assert result['storage'] == ceil(0.0109 * calculator.agents ** 2 + 3154)

def test_calculate_database_server(calculator):
    """
    Тестирование расчета параметров для Database Server.
    Проверяет значения 'replicas', 'memory', 'cpu' и 'storage',
    рассчитанные методом calculate_database_server() калькулятора.
    """
    result = calculator.calculate_database_server()
    assert result['replicas'] == max(ceil(1 / calculator.agents * 15000), 1)
    assert result['memory'] == ceil(1 / calculator.storage * 1.6)
    assert result['cpu'] == 1
    assert result['storage'] == ceil(0.0000002 * calculator.agents ** 3 + 0.0006774 * calculator.agents ** 4.5 * calculator.agents / calculator.nodes)

def test_calculate_clickhouse(calculator):
    """
    Тестирование расчета параметров для Clickhouse.
    Проверяет значения 'replicas', 'memory', 'cpu' и 'storage',
    рассчитанные методом calculate_clickhouse() калькулятора.
    """
    result = calculator.calculate_clickhouse()
    assert result['replicas'] == max(ceil(calculator.agents / 15000), 1)
    assert result['memory'] == ceil(calculator.storage * 1.6)
    assert result['cpu'] == 1
    assert result['storage'] == ceil(0.0000628 * calculator.agents ** 0.6377)

def test_calculate_synchronizer(calculator):
    """
    Тестирование расчета параметров для Synchronizer.
    Проверяет значения 'replicas', 'memory', 'cpu' и 'storage',
    рассчитанные методом calculate_synchronizer() калькулятора.
    """
    result = calculator.calculate_synchronizer()
    assert result['replicas'] == 1
    assert result['memory'] == ceil(calculator.storage / 5000 * 1.6)
    assert result['cpu'] == 1
    assert result['storage'] == ceil(0.0002 * calculator.agents + 0.6)

def test_calculate_scanner(calculator):
    """
    Тестирование расчета параметров для Scanner.
    Проверяет значения 'replicas', 'memory', 'cpu' и 'storage',
    рассчитанные методом calculate_scanner() калькулятора.
    """
    result = calculator.calculate_scanner()
    assert result['replicas'] == 1
    assert result['memory'] == 300
    assert result['cpu'] == 3
    assert result['storage'] == ceil(0.0002 * calculator.agents + 0.6)

def test_save_to_json(calculator):
    """
    Тестирование функции сохранения конфигурации в JSON файл.
    Проверяет, что конфигурация успешно сохраняется и совпадает с сохраненным файлом.
    """
    filename = 'test_config.json'
    config = calculator.generate_config()
    calculator.save_to_json(config, filename)
    
    assert os.path.exists(filename)
    
    with open(filename, 'r') as json_file:
        saved_config = json.load(json_file)
    
    assert saved_config == config
    
    os.remove(filename)

def test_load_from_json():
    """
    Тестирование функции загрузки конфигурации из JSON файла.
    Проверяет правильность чтения данных из JSON и их преобразование в параметры.
    """
    test_data = {
        'agents': 1000,
        'storage': 50.0,
        'traffic': 10.0,
        'mail_traffic': 5.0,
        'distributed': True,
        'nodes': 5
    }
    with open('input_test.json', 'w') as json_file:
        json.dump(test_data, json_file)
    
    agents, storage, traffic, mail_traffic, distributed, nodes = ConfigCalculator.load_from_json('input_test.json')
    
    assert agents == 1000
    assert storage == 50.0
    assert traffic == 10.0
    assert mail_traffic == 5.0
    assert distributed is True
    assert nodes == 5
    
    os.remove('input_test.json')

def test_generate_config(calculator):
    """
    Тестирование функции генерации конфигурации.
    Проверяет, что в конфигурации присутствуют ключи для всех компонентов,
    и что конфигурация представляет собой словарь.
    """
    config = calculator.generate_config()
    assert 'kafka' in config
    assert 'elasticsearch' in config
    assert 'processor' in config
    assert 'server' in config
    assert 'database_server' in config
    assert 'clickhouse' in config
    assert 'synchronizer' in config
    assert 'scanner' in config
    assert isinstance(config, dict)
