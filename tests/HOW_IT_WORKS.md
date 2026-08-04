# Пояснительная записка: как устроен тестовый фреймворк HIL

> Составлено статическим анализом кода (`Makefile`, `dockerfile`,
> `tests/conftest.py`, `tests/framework/*`). Не проверялось запуском на
> реальном стенде.

## 1. Общая архитектура: кто где выполняется

```
Хост-машина (реальный ПК/сервер рядом со стендом)
│
├── Контейнер СТЕНДА (SDA_CONTAINER, имя автоопределяется:
│   │                 "sda-f898b5d" или "sda_drive")
│   │
│   └── ROS 2 Humble + весь автопилотный стек:
│       sensing/*, perception/*, planning/*, control/*, calibration/*,
│       hdmap/*, prediction/*, /safety/mrm_request, /control/system, ...
│
└── Контейнер ТЕСТОВ (my-docker-project_v_2, запускается через `make run`
    │                  / `make test` / `make allure_*`)
    │
    ├── pytest + весь код из tests/
    ├── --pid=container:$(SDA_CONTAINER)  ← ОБЩИЙ PID-namespace со стендом
    ├── -v /var/run/docker.sock:...       ← умеет делать `docker exec`
    │                                        в контейнер стенда
    └── --network host
```

Ключевая деталь из `Makefile:17-22` (`DOCKER_RUN`):
```
docker run --rm \
    --pid=container:$(SDA_CONTAINER) \
    -e SDA_CONTAINER=$(SDA_CONTAINER) \
    -v /var/run/docker.sock:/var/run/docker.sock
```
Тестовый контейнер запускается с `--pid=container:$(SDA_CONTAINER)` — это
означает, что процессы тестового контейнера живут **в том же PID-namespace**,
что и процессы стенда. Это важно для понимания механизма `get_pid()`
(см. раздел 4) — и меняет один из выводов в `KNOWN_ISSUES.md` (см. раздел 9).

Сам тестовый образ собирается по `dockerfile`: Ubuntu + Docker CLI (чтобы
изнутри контейнера дергать `docker exec`) + ROS 2 Humble CLI-инструменты
(`ros2cli`, `ros2topic`, `ros2node`) + `pytest`, `allure-pytest` и т.д.
Сам ROS2-граф (все реальные ноды автопилота) физически крутится **внутри
контейнера стенда**, не внутри тестового контейнера — тестовый контейнер
только исполняет CLI-команды `ros2 ...` через `docker exec` в стенд.

## 2. Обнаружение контейнера стенда

`tests/framework/base_hil_test.py:7-28` — `_detect_container()`:
```python
candidates = ["sda-f898b5d", "sda_drive"]
result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], ...)
# ищем совпадение с running-контейнерами, иначе RuntimeError
DOCKER_CONTAINER = _detect_container()
```
Выполняется **на уровне импорта модуля** — то есть при самом первом
`import` из `tests.framework.base_hil_test` (а значит и при
`pytest --collect-only`). Если ни один контейнер-кандидат не запущен —
падает `RuntimeError` ещё до сбора тестов.

## 3. Жизненный цикл фикстур (`tests/conftest.py`)

### 3.1. Фикстуры отдельных нод — module-scoped, парные

Для каждой ноды — пара фикстур:
```python
@pytest.fixture(scope="module")
def imu1_imu_node():
    node = ImuNode()      # framework/sensing_nodes.py — обёртка над BaseHILTest
    node.setup()          # только логирование "начало теста"
    yield node
    node.teardown()       # только логирование "конец теста"

@pytest.fixture(scope="module")
def imu1_imu_node_alive(imu1_imu_node):
    if not imu1_imu_node.is_alive():
        pytest.skip("Нода /sensing/imu1/imu_node не запущена")
    return imu1_imu_node
```
- Первая фикстура (`imu1_imu_node`) — просто конструирует Python-объект-обёртку
  над реальной ROS2-нодой (без проверки, жива ли нода).
- Вторая (`_alive`) — оборачивает первую и делает `pytest.skip()`, если ноды
  нет в ROS graph. Именно `_alive`-версии используются в реальных тестах.
- `scope="module"` — общий инстанс на все тесты одного файла, не пересоздаётся
  на каждый тест.

Таких пар в `conftest.py` — по одной на каждую ноду проекта (sensing,
perception, planning, calibration, prediction, hdmap, control — см.
разделы файла с комментариями `# ===...=== Sensing`, `# Perception` и т.д.).
Есть баги copy-paste в части этих пар — см. `tests/fault_injection/KNOWN_ISSUES.md`.

### 3.2. Session-scoped autouse фикстуры — общие мониторы

```python
@pytest.fixture(scope="session", autouse=True)
def control_monitor():          # conftest.py:99-112
    monitor = ControlSystemMonitor()
    monitor.start()
    if not monitor.wait_ready(timeout=15):
        pytest.fail(...)
    yield monitor
    monitor.stop()

@pytest.fixture(scope="session", autouse=True)
def mrm_monitor():               # conftest.py:1676-1683
    monitor = MrmRequestMonitor(container=DOCKER_CONTAINER)
    monitor.start()
    if not monitor.wait_ready(timeout=15):
        pytest.fail(...)
    yield monitor
    monitor.stop()
```
`autouse=True` — стартуют автоматически **один раз на весь pytest-сьют**,
до первого теста, без явного упоминания в тестах. Любой тест может просто
принять `mrm_monitor` как параметр, и получит уже готовый, работающий
инстанс. Оба монитора держат фоновый поток + подпроцесс `docker exec ...
ros2 topic echo ...` (подробнее в разделе 5) — специально по одному
инстансу на сьют, чтобы не плодить `ros2 topic echo` подписчиков (SHM/DDS
resource exhaustion при множественных участниках графа).

### 3.3. Универсальная фабрика (`node_alive_factory`)

```python
@pytest.fixture(scope="module")
def node_alive_factory(request):        # conftest.py:1768-1791
    def factory(fixture_name: str):
        base_name = fixture_name.replace("_alive", "")
        node = request.getfixturevalue(base_name)
        if not node.is_alive():
            pytest.skip(...)
        return node
    return factory
```
Позволяет получить любую ноду по строковому имени фикстуры динамически
(`request.getfixturevalue`) вместо явного параметра — используется не
везде, в основном тесты берут `_alive`-фикстуры напрямую по имени
параметра или через `request.getfixturevalue(fixture_name)` внутри
`@pytest.mark.parametrize` (см. `test_sensing_kill.py:26`).

### 3.4. Как тест получает фикстуру — общая картина

```
pytest видит параметр функции теста → ищет одноимённую фикстуру
    → в файле теста → в conftest.py той же папки → вверх по дереву папок
    → находит в tests/conftest.py (единственный conftest.py в проекте)
```
Локальных `conftest.py` в подпапках (`fault_injection/`,
`fault_injection/sensing/`) нет — все фикстуры видны из корневого
`tests/conftest.py` благодаря стандартной иерархии обнаружения pytest.

## 4. Как ноды "находятся" — ДВА независимых механизма

Это важный момент: "нода" проверяется двумя совершенно разными способами
в зависимости от того, что нужно — они используют разные источники истины
и никак не связаны между собой на уровне кода.

### 4.1. Через ROS 2 граф (`is_alive()`) — топологическое имя

```python
# base_hil_test.py:38-42, 78-85
def is_alive(self) -> bool:
    return self.NODE_NAME in self.get_node_list()

def get_node_list(self) -> list[str]:
    result = self.run_ros("ros2 node list 2>/dev/null")
    return [n.strip() for n in result.stdout.split('\n') if n.strip()]
```
`run_ros()` — `docker exec {DOCKER_CONTAINER} bash -c "source
/rep/ros2/install/setup.bash && export ROS_DOMAIN_ID=1 && ros2 node
list"`. Возвращает список зарегистрированных в DDS-графе имён нод
(например `/sensing/imu1/imu_node`). `NODE_NAME` задаётся как
class-атрибут в каждом Node-классе (`framework/sensing_nodes.py`,
`framework/perception_nodes.py` и т.д.), например:
```python
class ImuNode(BaseHILTest):
    NODE_NAME = "/sensing/imu1/imu_node"
    PROCESS_NAME = "imu_driver/lib/imu_driver/imu_node"
```

### 4.2. Через Linux-процесс (`get_pid()` / `kill()`) — имя бинарника

```python
# base_hil_test.py:255-265
def get_pid(self) -> int | None:
    result = self.run_docker_command(
        f"ps aux | grep '{self.PROCESS_NAME}' | grep -v grep | grep -v python3"
    )
    if result.returncode == 0 and result.stdout.strip():
        pid = int(result.stdout.strip().split('\n')[0].split()[1])
        return pid
    return None
```
Это уже **не ROS-граф, а обычный список процессов ОС** внутри контейнера
стенда — ищется по подстроке `PROCESS_NAME` (путь к бинарнику/либе, не
ROS-имя). Используется для `kill -9`/`kill -6` в fault injection тестах
(`node.get_pid()` → `node.run_docker_command(f"kill -6 {pid}")`, см.
`test_sensing_kill.py:44-58`).

**Важная деталь про общий PID-namespace (раздел 1):** поскольку тестовый
контейнер запущен с `--pid=container:$(SDA_CONTAINER)`, процессы,
порождаемые самим Python-тестом (например тот самый `grep` из пайпа выше),
физически находятся в ТОЙ ЖЕ PID-namespace, что и стенд. Это значит, что
`ps aux`, выполненный через `docker exec $(SDA_CONTAINER) ps aux`, в
принципе может увидеть и процесс `grep`, порождённый на стороне теста —
именно поэтому `grep -v grep` в `get_pid()` не бесполезная защита, а
реально необходимая (при штатном запуске через `make`, где выставлен
`--pid=container:...`). *(Ранее в `KNOWN_ISSUES.md` я неверно
"скорректировала" этот вывод, предположив, что grep выполняется в
полностью изолированном namespace — эта деталь Makefile тогда ещё не была
разобрана; при желании поправлю формулировку там же.)*

### 4.3. Через ROS 2 топик (для мониторов состояния)

Третий источник — не про "жива ли нода", а про **данные, которые нода
публикует**: `ros2 topic echo <topic>` — либо разовый вызов
(`get_topic_field`/`get_topic_fields`, `base_hil_test.py:144-218`, с
`--once` и таймаутом), либо непрерывный фоновый монитор
(`MrmRequestMonitor`, `ControlSystemMonitor`) — см. раздел 5.

## 5. `MrmRequestMonitor` — непрерывный монитор топика `/safety/mrm_request`

```
docker exec SDA_CONTAINER bash -c "source .../setup.bash &&
    export ROS_DOMAIN_ID=1 && ros2 topic echo /safety/mrm_request"
        │
        ▼  (subprocess.Popen, stdout=PIPE, один процесс на всю сессию)
фоновый Python-поток (_read_loop)
        │  построчно читает stdout, буферизует до разделителя YAML "---"
        ▼
под threading.Lock():
    _latest_raw   ← весь текстовый блок последнего сообщения
    _latest_stamp ← "sec.nanosec", распарсено построчным startswith()
```
Публичный интерфейс, которым пользуются тесты:
- `wait_ready(timeout)` — дождаться первого сообщения при старте сьюта.
- `get_fields(["mrm_type", "shadow_mrm_type", "drive_mode"])` — снять
  срез текущих полей (для baseline/отчёта).
- `get_stamp()` — текущий timestamp последнего сообщения (берётся **до**
  инъекции отказа, чтобы не словить старое сообщение).
- `wait_for_mrm_type_change(from_value, to_value, before_stamp, timeout,
  poll_interval)` — поллит `_latest_stamp`, ждёт, пока придёт сообщение
  НОВЕЕ `before_stamp`, и проверяет, что `mrm_type` стало равно `to_value`.
  Возвращает `success/reaction_ms/mrm_type/...`.
- `get_error_codes()` — парсит вложенный список `error_codes: [{error_code,
  details}, ...]` из последнего сообщения.

Почему один инстанс на всю сессию, а не по одному на тест: каждый
`ros2 topic echo` — это отдельный DDS-участник (subscriber). Множество
таких участников за один прогон исчерпывает SHM-сегменты
(`/dev/shm`) — авторы обошли это, подняв ОДИН `docker exec ... ros2 topic
echo` процесс на весь сьют через `autouse=True` session-фикстуру
(`conftest.py:1676-1683`).

## 6. Обвязка docker exec — три похожих метода в `base_hil_test.py`

| Метод | Назначение | Транспорт DDS |
|---|---|---|
| `run_ros(cmd)` | Разовые команды (`ros2 node list`) | обычный (SHM+UDP) |
| `run_ros_in_docker(cmd)` | Топик-чтение в цикле сьюта | принудительно UDP-only через сгенерированный XML-профиль FastDDS (`fastdds_no_shm.xml`) — чтобы не плодить SHM-участников |
| `run_docker_command(cmd)` | Произвольная shell-команда (`ps aux`, `kill`) | не относится к ROS/DDS |

Все три в итоге собирают строку `docker exec {DOCKER_CONTAINER} bash -c
"..."` и выполняют через `subprocess.run(..., shell=True)`.

## 7. Как выглядит fault injection тест целиком (на примере kill-теста)

```
1. request.getfixturevalue(fixture_name)   → получить ноду (module-scoped)
2. node.is_alive()                          → pytest.skip, если не запущена
3. mrm_monitor.get_fields([...])            → снять baseline (для отчёта)
4. mrm_monitor.get_stamp()                  → зафиксировать stamp ДО отказа
5. node.get_pid() + kill -6/-9               → инъекция отказа
6. mrm_monitor.wait_for_mrm_type_change(...) → дождаться реакции MRM
7. mrm_monitor.get_error_codes()             → собрать диагностику
8. assert result["success"] и assert result["reaction_ms"] < SLA
9. teardown (fixture restart_autopilot_after) → убить процесс `drive`,
   подождать 120с, перезапустить, дождаться mrm_type 2→0 (conftest.py:1713-1752)
```
С 2026-08-04 шаги 2-8 живут в одном месте —
`tests/framework/kill_fault_injection.py::run_kill_fault_injection()`
(см. `KNOWN_ISSUES.md`, пункт 10) — все 9 `test_*_kill.py` файлов вызывают
эту функцию, оставляя себе только список нод и allure-метаданные (шаг 1
и teardown/фикстуры остаются в самих тестовых файлах, так как это разное
для каждого компонента/зависит от pytest-фикстур).

Relay-based (аппаратные) fault injection тесты устроены аналогично, но
вместо `kill -N` используется HTTP-вызов к физическому реле
(`tests/fault_injection/sensing/control_relay.py`) — черновик такого
теста лежит в `tests/fault_injection/sensing/test_camera.py`.

## 8. Отчётность

- **pytest-html** — кастомные колонки "Ожидаемый/Фактический
  результат/Время реакции" через хуки `pytest_html_results_table_header` /
  `_row` (`conftest.py:1701-1710`), значения проставляются тестом через
  `request.node.expected/actual/reaction_ms`.
- **allure-pytest** — `@allure.step`/`@allure.attach` внутри тестов
  формируют `allure-results/<component>/*.json` (см.
  `--alluredir=allure-results/<component>` в `Makefile`).
- **Allure TestOps (веб-сайт)** — отдельный шаг `make allure-upload-<component>`
  через `~/allurectl upload`, см. `Makefile:141-202`. Сервер и project_id
  сейчас — `https://testops.navio.auto` / `HIL_PROJECT_ID=24`
  (обновлено 2026-08-04, было `allure-testops.sberautotech.ru`).

## 9. Известные проблемы

Полный список найденных багов и техдолга — в
`tests/fault_injection/KNOWN_ISSUES.md`. На момент обновления этой записки
исправлены пункты 1–10 (сломанные фикстуры `*_alive`, `has_auto_restart`,
фильтр `get_pid()`, рассинхрон таймаута 60/120с, несоответствие assert'ов
заявленному SLA, дублирование кода между 9 kill-тестами — вынесено в
`framework/kill_fault_injection.py`, см. раздел 7 выше); пункты 11–14
(тройное дублирование парсинга `ros2 topic echo`, магические строки
`mrm_type`) — пока открыты.
