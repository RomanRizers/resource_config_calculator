"""
Реализация калькулятора для вычисления конфигурации ресурсов
для различных сервисов на основе входных параметров.

Пользователь может вводить данные, как вручную, так и загружать
их с помощью JSON-файла. Вывод реализован в консоль, а также в
файл config.json

Данный формат предоставляет пользователю гибкость вода данных,
что делает процесс более удобным и универсальным. Вывод обеспечивает
как наглядность, так и возможность дальнейшего использования или
хранения конфигурации. 
"""

import json
import math

class ConfigCalculator:
    """Класс для вычисления конфигурации ресурсов для различных сервисов на основе входных параметров."""
    def __init__(self, agents, storage, traffic, mail_traffic, distributed, nodes):
        self.agents = agents
        self.storage = storage
        self.traffic = traffic
        self.mail_traffic = mail_traffic
        self.distributed = distributed
        self.nodes = nodes

    def calculate_kafka(self):
        return {
            "replicas": 3 if self.distributed else 1,
            "memory": math.ceil(self.mail_traffic * 0.5) if self.distributed else 100,
            "cpu": math.ceil(0.000169 * self.agents ** 0.437923 * self.nodes ** 3),
            "storage": math.ceil(0.0004 * self.agents ** 0.3231)
        }

    def calculate_elasticsearch(self):
        return {
            "replicas": 3 if self.distributed else 1,
            "memory": 0,
            "cpu": 3,
            "storage": (
                0.256 if self.agents <= 5000 else
                0.512 if self.agents <= 10000 else
                1
            )
        }

    def calculate_processor(self):
        return {
            "replicas": 3 if self.agents > 0 and self.distributed else 0,
            "memory": 5 if self.distributed else 100,
            "cpu": 3,
            "storage": math.ceil(4.25870 * (self.agents ** 0.98271)) if self.agents > 0 else 0
        }

    def calculate_server(self):
        return {
            "replicas": min(3, 2) if self.agents > 0 else 0,
            "memory": math.ceil(1 / self.storage * 1.6) if self.distributed else 100,
            "cpu": 1,
            "storage": math.ceil(0.0109 * self.agents ** 2 + 3154) if self.nodes > 0 else 0
        }

    def calculate_database_server(self):
        return {
            "replicas": max(math.ceil(1 / self.agents * 15000), 1) if self.agents > 0 and self.distributed else 1,
            "memory": math.ceil(1 / self.storage * 1.6) if self.distributed else 100,
            "cpu": 1,
            "storage": math.ceil(0.0000002 * self.agents ** 3 + 0.0006774 * self.agents ** 4.5 * self.agents / self.nodes) if self.nodes > 0 else 0
        }

    def calculate_clickhouse(self):
        return {
            "replicas": max(math.ceil(self.agents / 15000), 1) if self.agents > 0 and self.distributed == 1 else 1,
            "memory": math.ceil(self.storage * 1.6) if self.distributed else 100,
            "cpu": 1,
            "storage": math.ceil(0.0000628 * self.agents ** 0.6377) if self.distributed > 0 else 0
        }

    def calculate_synchronizer(self):
        return {
            "replicas": 1 if self.agents > 0 else 0,
            "memory": math.ceil(self.storage / 5000 * 1.6) if self.distributed else 100,
            "cpu": 1,
            "storage": math.ceil(0.0002 * self.agents + 0.6) if self.distributed > 0 else 0
        }

    def calculate_scanner(self):
        return {
            "replicas": 1 if self.agents > 0 else 0,
            "memory": 300,
            "cpu": 3,
            "storage": math.ceil(0.0002 * self.agents + 0.6) if self.distributed > 0 else 0
        }

    def generate_config(self):
        config = {
            "kafka": self.calculate_kafka(),
            "elasticsearch": self.calculate_elasticsearch(),
            "processor": self.calculate_processor(),
            "server": self.calculate_server(),
            "database_server": self.calculate_database_server(),
            "clickhouse": self.calculate_clickhouse(),
            "synchronizer": self.calculate_synchronizer(),
            "scanner": self.calculate_scanner(),
        }
        return config

    def save_to_json(self, config, filename='config.json'):
        with open(filename, 'w') as json_file:
            json.dump(config, json_file, indent=4)

    @staticmethod
    def load_from_json(filename='input.json'):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            return (data['agents'], data['storage'], data['traffic'], data['mail_traffic'], data['distributed'], data['nodes'])

if __name__ == "__main__":
    input_method = input("Выберите метод ввода (1 - ручной ввод, 2 - ввод из JSON файла): ")

    if input_method == '1':
        # Ввод данных от пользователя вручную
        agents = int(input("Введите количество агентов: "))
        storage = float(input("Введите объем хранилища (в ГБ): "))
        traffic = float(input("Введите объем трафика: "))
        mail_traffic = float(input("Введите объем почтового трафика: "))
        distributed = bool(int(input("Распределенная система? (1 - да, 0 - нет): ")))
        nodes = int(input("Введите количество узлов: "))
    elif input_method == '2':
        agents, storage, traffic, mail_traffic, distributed, nodes = ConfigCalculator.load_from_json()
    else:
        print("Неверный ввод.")
        exit()

    calculator = ConfigCalculator(agents, storage, traffic, mail_traffic, distributed, nodes)
    config = calculator.generate_config()

    print("Сгенерированный конфигурационный файл:")
    print(json.dumps(config, indent=4))

    calculator.save_to_json(config)
    print("Конфигурация сохранена в файл 'config.json'")
