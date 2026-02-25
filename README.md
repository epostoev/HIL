# HIL Test Framework

Автоматизированный тестовый фреймворк для HIL-стенда.
Тестирование нод ROS 2 автономного транспортного средства.

## Структура проекта

tests/
├── conftest.py
├── framework/
│   ├── base_hil_test.py        # Базовый класс
│   ├── carapi_node.py          # Управление /carapi_node
│   └── trajectory_planner_node.py  # Управление /planning/trajectory_planner_node
└── fault_injection/
    ├── test_carapi_kill.py
    └── test_trajectory_planner_kill.py

## Запуск тестов

# Все тесты
pytest tests/ -v -s --log-cli-level=INFO

# Только fault injection
pytest tests/fault_injection/ -v -s --log-cli-level=INFO

## Требования

- Python 3.10+
- ROS 2 Humble
- Docker (контейнер sda-f898b5d)
- pytest, pytest-timeout, pytest-rerunfailures
```

---

## Итоговая картина проекта
```
tests/
├── conftest.py                          ✅
├── framework/
│   ├── base_hil_test.py                 ✅
│   ├── carapi_node.py                   ✅
│   └── trajectory_planner_node.py       ✅ (с последним фиксом)
└── fault_injection/
    ├── test_carapi_kill.py              ✅
    └── test_trajectory_planner_kill.py  ✅
