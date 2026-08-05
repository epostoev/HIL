# Known Issues — существующие HIL fault injection тесты

> Отчёт подготовлен статическим анализом кода (без запуска тестов на стенде).
> Дата: 2026-08-03.
> Область: `tests/conftest.py`, `tests/framework/base_hil_test.py`,
> `tests/fault_injection/test_*_kill.py`.

## Реальные баги (ломают конкретные сценарии)

1. **[ИСПРАВЛЕНО 2026-08-04] `conftest.py:420-469` — 4 сломанные fixture `*_alive`.**
   `sda_process_monitor_node_alive`, `v2x_publisher_node_alive`,
   `rosbag2_recorder_node_alive`, `mrm_arbiter_node_alive` принимали параметр
   `hal_node`, но в теле проверяли `.is_alive()` у module-level функции-фикстуры
   (например `sda_process_monitor_node`), а не у вызванного инстанса ноды.
   При обращении — `AttributeError: 'function' object has no attribute 'is_alive'`.
   Copy-paste без замены имени переменной.
   Исправлено: каждая фикстура теперь принимает и проверяет свою собственную
   ноду (`sda_process_monitor_node_alive(sda_process_monitor_node)`,
   `v2x_publisher_node_alive(v2x_publisher_node)`,
   `rosbag2_recorder_node_alive(rosbag2_recorder_node)`,
   `mrm_arbiter_node_alive(mrm_arbiter_node)`). Не запускалось на стенде —
   требуется ручная проверка.

2. **[ИСПРАВЛЕНО 2026-08-04] `conftest.py:246-265` — дублирование имени fixture
   `camera_decoder_node_alive`.**
   Была определена дважды (:247 и :262). Вторая версия проверяла
   `crash_video_recorder_node`, а не камеру. Python молча переопределял первую —
   любой тест, ожидающий проверку камеры, реально проверял crash_video_recorder.
   Исправлено: вторая фикстура переименована в `crash_video_recorder_node_alive`
   и принимает/проверяет `crash_video_recorder_node`. Первая (:247) осталась
   как есть и теперь корректно доступна под именем `camera_decoder_node_alive`.
   **Важно:** черновик `tests/fault_injection/sensing/test_camera.py` уже
   использует `camera_decoder_node_alive` (ожидая проверку камеры) — до этого
   исправления он фактически получал бы crash_video_recorder из-за
   затирания. После правки черновик работает как задумано. Не запускалось на
   стенде — требуется ручная проверка.

3. **[ИСПРАВЛЕНО 2026-08-04] `conftest.py:390-409` — то же с `can_hal_node_alive`.**
   Определена дважды; вторая версия проверяла `crash_detector_node` вместо `hal_node`,
   при этом называлась так же, как первая (`can_hal_node_alive`), — вторая
   молча перекрывала первую.
   Исправлено: вторая фикстура переименована в `crash_detector_node_alive`
   и принимает/проверяет `crash_detector_node` (первая `can_hal_node_alive`
   для `hal_node` оставлена как есть — с ней проблем не было, кроме коллизии
   имени). Проверено grep'ом — ни один тест пока не ссылался на
   `can_hal_node_alive` или несуществующий `crash_detector_node_alive` по
   имени, так что переименование ничего не ломает. Не запускалось на стенде —
   требуется ручная проверка.

4. **[ИСПРАВЛЕНО 2026-08-04] `conftest.py:508` — `perception_box_segmentation_fusion_node_alive` проверяла чужую ноду.**
   `if not perception_boom_barrier_detector_node.is_alive()` — copy-paste от
   предыдущего блока фикстур, должно быть `perception_box_segmentation_fusion_node`.
   Исправлено: теперь проверяет `perception_box_segmentation_fusion_node.is_alive()`.
   Не запускалось на стенде — требуется ручная проверка.

5. **[ИСПРАВЛЕНО 2026-08-04] `conftest.py:613` — опечатка `erception_detector_3d_node_alive`** (пропущена `p`).
   Фикстура с "логичным" именем `perception_detector_3d_node_alive` не существовала —
   обращение по нему упало бы с `fixture not found`. Сама логика проверки
   (`perception_detector_3d_node.is_alive()`) была верной, проблема только в имени.
   Исправлено: фикстура переименована в `perception_detector_3d_node_alive`.
   Ни один тест не ссылался ни на опечатанное, ни на правильное имя — переименование
   безопасно. Не запускалось на стенде — требуется ручная проверка.

6. **[ИСПРАВЛЕНО 2026-08-04] `node.has_auto_restart` использовался до инициализации.**
   Баг оказался не локальным для `test_sensing_kill.py:118-156` — та же пара
   "`node.has_auto_restart = True` только в ветке `if node.is_alive():`,
   затем `if node.has_auto_restart:` дальше по коду" встречается во **всех
   8** kill-тестах (`test_control_kill.py:147/182`,
   `test_calibration_kill.py:151/186`, `test_hdmap_kill.py:141/176`,
   `test_planning_kill.py:135/170`, `test_localization_kill.py:114/149`,
   `test_integration_kill.py:123/158`, `test_perception_kill.py:144/179`,
   `test_prediction_kill.py:135/170`). Если нода **не** авторестартанула
   (важный негативный кейс) — атрибут никогда не был установлен, и
   `if node.has_auto_restart:` падал `AttributeError` уже после прохождения
   основного assert. Именно для интересного случая ("нода не
   восстановилась") тест крашился не с тем сообщением.
   Исправлено в одном месте — `framework/base_hil_test.py`,
   `BaseHILTest.__init__`: добавлено `self.has_auto_restart = False` как
   значение по умолчанию. Все ноды наследуются от `BaseHILTest` и вызывают
   `super().__init__()` (проверено grep'ом по `sensing_nodes.py`,
   `perception_nodes.py`), поэтому фикс закрывает баг сразу во всех 8
   файлах без правки каждого по отдельности. Не запускалось на стенде —
   требуется ручная проверка.

7. **[ИСПРАВЛЕНО 2026-08-04] `base_hil_test.py:255-260` — `get_pid()` без фильтра `grep -v grep -v python3`.**
   `run_docker_command` собирает `docker_cmd = f"docker exec {CONTAINER}
   {cmd}"` одной строкой и запускает через `subprocess.run(docker_cmd,
   shell=True, ...)` (:249-252) — конвейер `|` разбирает шелл того
   окружения, где выполняется сам pytest, т.е. **тестового Docker-контейнера**
   (`my-docker-project_v_2`), а не контейнера стенда — `ps aux` уходит внутрь
   стенда через `docker exec`, `grep` остаётся в тестовом контейнере.

   **Уточнение (после разбора `Makefile`, см. `tests/HOW_IT_WORKS.md`):**
   тестовый контейнер запускается с `--pid=container:$(SDA_CONTAINER)`
   (`Makefile:20`) — то есть его процессы **явно посажены в тот же
   PID-namespace, что и стенд**. При таком штатном способе запуска (через
   `make run`/`make test`/`make allure_*`) исходный диагноз из этого пункта
   был верным: `grep`, порождённый тестовым процессом, физически находится
   в той же PID-namespace, что и стенд, и может реально попасть в вывод
   `ps aux`, выполненного через `docker exec SDA_CONTAINER ps aux`. Моя более
   ранняя "коррекция" этого пункта (о том, что grep технически не может
   поймать сам себя, так как работает в отдельном namespace) была
   ошибочной — на тот момент `Makefile` ещё не был разобран. Риск реален
   именно при штатном запуске с `--pid=container:...`; при гипотетическом
   запуске pytest вне такого контейнера (без разделения PID-namespace) риска
   самосовпадения не было бы, но `grep -v python3` всё равно был бы нужен
   из-за второго реального риска — нескольких строк, одновременно матчащих
   `PROCESS_NAME` (например, python3-обёртка лаунчера ROS2 плюс сам
   скомпилированный процесс ноды), из-за чего `split('\n')[0]` мог взять не
   ту строку.

   Исправлено (первая попытка, 2026-08-04): восстановлен фильтр
   `| grep -v grep | grep -v python3`.

   **[РЕГРЕССИЯ, найдена на реальном прогоне 2026-08-05, исправлена в тот же день]**
   Первый прогон `make allure_integration` после рефакторинга (пункт 10)
   показал 3 упавших теста: `hal_node`, `sda_process_monitor_node`,
   `v2x_publisher_node` — `get_pid()` возвращал `None`
   ("Процесс не найден"), из-за чего отправлялось `kill -6 None` (no-op),
   нода реально не убивалась, и `wait_for_mrm_type_change` корректно
   таймаутился с `success=False`. Диагностика на стенде
   (`docker exec sda-f898b5d bash -c "ps aux | grep '...' | grep -v grep"`)
   показала:
   ```
   /usr/bin/python3 /rep/ros2/install/v2x_publisher/lib/v2x_publisher/v2x_publisher --ros-args ...
   ```
   Это **единственная и легитимная** строка процесса для python3-нод
   (`rclpy`), и `grep -v python3` вырезал именно её — моё обоснование
   фикса от 2026-08-04 ("python3-обёртка лаунчера создаёт лишние строки
   рядом с настоящим бинарником") оказалось верным только для C++-нод; для
   Python-нод единственный процесс — это и есть `python3 <путь>`, отдельного
   бинарника нет, вырезать эту строку нельзя.
   Исправлено окончательно: `grep -v python3` убран, оставлен только
   `grep -v grep` (обоснование которого — общий PID-namespace через
   `--pid=container:$(SDA_CONTAINER)` — подтверждённым риском не
   опровергнуто и остаётся в силе). Итоговая команда:
   `ps aux | grep '{PROCESS_NAME}' | grep -v grep`.
   Остаточный риск (не устранён): если несколько строк всё равно совпадут
   после фильтрации (например, несколько worker-процессов одной ноды),
   `[0]` по-прежнему выберет первую в порядке вывода `ps aux`, без явного
   предупреждения в лог. Повторный прогон на стенде после этого исправления
   ещё не выполнялся.

   **Побочная находка (не устранена, отдельная тема):** в логе неудачных
   попыток видно `"Нода жива True" → "drive.py перезапустил ноду. Fault
   tolerance: ПОДТВЕРЖДЁН ✅"`, хотя нода вообще не была убита (`kill -6
   None` — no-op). Текущая проверка авторестарта (`node.is_alive()` через
   3с после kill) не отличает "нода никогда не умирала" от "нода упала и
   переподнялась" — при полностью безуспешной инъекции отказа лог всё
   равно рапортует "Fault tolerance подтверждён", что вводит в заблуждение.

8. **[ИСПРАВЛЕНО 2026-08-04] `conftest.py:1743 vs 1752` — рассинхрон таймаута и текста ошибки.**
   `wait_for_mrm_type_change(..., timeout=120.0, ...)`, но
   `pytest.fail("Автопилот не перезапустился за 60 секунд")` — сообщение
   врёт про 60с при реальном таймауте 120с, вводит в заблуждение при разборе падения.
   Подтверждено (со слов команды): реальный таймаут действительно должен
   быть 120с — ноды после перезапуска не успевают восстановиться за 60с.
   Исправлено: текст сообщения приведён в соответствие с кодом
   ("не перезапустился за 120 секунд"), сам таймаут (120.0) не менялся.
   Не запускалось на стенде — требуется ручная проверка.

## Корректность assert'ов (тест "проходит", но не то проверяет)

9. **[ИСПРАВЛЕНО 2026-08-04]** Во всех `*_kill.py` тестах `request.node.expected`
   декларирует SLA по времени реакции (`"mrm_type: 0 → 2. Время реакции <
   5000ms"` — в 8 файлах; `"< 500ms"` — в `test_integration_kill.py:30`),
   но фактический `wait_for_mrm_type_change(timeout=10.0, ...)` ждёт до
   **10 секунд**, и нигде не assert'ился `result["reaction_ms"] < SLA`. Тест
   мог пройти "зелёным" при реакции 8с (для 5000ms-файлов), хотя заявленный
   SLA нарушен.
   Исправлено во всех 9 kill-тестах (`test_sensing_kill.py`,
   `test_control_kill.py`, `test_hdmap_kill.py`, `test_calibration_kill.py`,
   `test_perception_kill.py`, `test_planning_kill.py`,
   `test_prediction_kill.py`, `test_localization_kill.py`,
   `test_integration_kill.py`) — сразу после `assert result["success"]`
   добавлен отдельный `allure.step` с явным `assert result["reaction_ms"] <
   {SLA}`, значение SLA взято из соответствующего `request.node.expected`
   каждого файла (5000ms везде, кроме `test_integration_kill.py` — там 500ms).
   `timeout=10.0` в `wait_for_mrm_type_change` не менялся — это по-прежнему
   верхняя граница ожидания, а не сам SLA; теперь SLA проверяется отдельным
   assert'ом поверх него. Не запускалось на стенде — требуется ручная
   проверка (в частности, что реальная реакция стенда действительно
   укладывается в 5000ms/500ms, иначе тесты станут падать чаще, чем раньше).

## Дублирование / технический долг

10. **[ИСПРАВЛЕНО 2026-08-04] 9 файлов `*_kill.py`** (`test_control_kill.py`,
    `test_calibration_kill.py`, `test_hdmap_kill.py`, `test_localization_kill.py`,
    `test_planning_kill.py`, `test_integration_kill.py`, `test_perception_kill.py`,
    `test_prediction_kill.py`, `test_sensing_kill.py`) были почти построчно
    идентичны (~150-190 строк каждый), отличаясь только списком нод, SLA
    (5000ms везде, кроме `test_integration_kill.py` — там 500ms) и
    allure-метаданными (epic/feature/story/описание).
    Исправлено: общее тело сценария ("kill -6 → снять baseline → зафиксировать
    stamp → kill → дождаться mrm_type 0→2 → собрать error_codes → проверить
    авторестарт → assert success/SLA → заполнить отчёт") вынесено в новый
    файл `tests/framework/kill_fault_injection.py` —
    `run_kill_fault_injection(node, node_name, mrm_monitor, request, sla_ms)`.
    Каждый из 9 файлов теперь оставляет себе только: список `NODES`,
    allure-декораторы класса (epic/feature/story/title/description) и
    docstring (там, где они были — не у всех файлов они были изначально, я
    не добавляла отсутствовавшие декораторы, чтобы не выйти за рамки задачи),
    получение `node` из фикстуры (в части файлов — с `allure.dynamic.title`
    и `allure.step`-обёрткой, в другой части — без, сохранила стиль каждого
    файла как было), и один вызов хелпера. `import json`/`import time` из
    9 файлов убраны (перенесены в новый модуль, там же были и нужны).

    **Побочная находка при переписывании `test_perception_kill.py`:** класс
    назывался `TestIPerceptionKill`, метод — `test_integration_kill` (явный
    copy-paste из `test_integration_kill.py`, не переименованный). Ничего в
    проекте не ссылалось на это имя напрямую (проверено grep'ом, в т.ч. по
    `Makefile` — там пути к файлам, не к classId/methodId) — переименовала
    в `TestPerceptionKill`/`test_perception_kill` заодно, раз файл и так
    переписывался.

    Проверено статически: `python3 -m py_compile` на всех 10 файлах (9
    переписанных + новый хелпер) — синтаксис корректен; каждый из 9 файлов
    и сам хелпер успешно импортируются напрямую (`importlib.import_module`)
    без докер-стенда — эти файлы больше не тянут за собой
    `_detect_container()` на этапе импорта (в отличие от `conftest.py`,
    который по-прежнему требует докер при коллекции сьюта). Полноценный
    прогон на стенде не выполнялся — нужна ручная проверка, в первую
    очередь того, что allure-степы и `request.node.expected/actual` в
    HTML/Allure-отчёте выглядят так же, как до рефакторинга.

11. **Парсинг `ros2 topic echo` дублирован минимум трижды**: в
    `MrmRequestMonitor.get_fields/_read_loop`, в
    `base_hil_test.get_topic_field/get_topic_fields`, и, вероятно, в
    `ControlSystemMonitor`. Логику построчного `startswith(field+":")` стоит
    вынести в общую утилиту — иначе изменение формата вывода ROS2 придётся
    чинить в 3+ местах отдельно.

12. **Три похожих метода docker exec** в `base_hil_test.py` — `run_ros`,
    `run_ros_in_docker`, `run_docker_command` — с частично дублирующейся
    сборкой команды и разными XML/env профилями.

13. **`_detect_container()` (`base_hil_test.py:7-25`) выполняется на уровне
    импорта модуля.** Если стенд не поднят, `pytest --collect-only` не
    отработает вообще (падает `RuntimeError` при импорте `conftest.py`) —
    нельзя посмотреть список тестов без живого docker-контейнера.

14. **Магические строки `"0"`/`"2"` для `mrm_type`** разбросаны по всем тестам
    без enum/констант — непонятно без контекста, что означает каждое значение.

## Мелкое

- `test_sensing_kill.py:109` пишет JSON-лог по фиксированному пути
  `/tmp/error_codes_{node_name}.json` без очистки — коллизия при параллельном
  запуске (xdist) или совпадении имён нод между файлами.
- У `test_sensing_kill.py` нет `@allure.severity(...)`, в отличие от остальных
  7 kill-файлов — несогласованные метаданные для триажа в Allure.

## Контекст (fault injection через реле)

- `tests/fault_injection/sensing/control_relay.py` — единственное реле в
  проекте, один фиксированный IP (`192.168.1.120`), без маппинга канал→компонент.
  Назначение (что именно обесточивается) нигде явно не задокументировано.
- `tests/fault_injection/sensing/test_camera.py` был пустым стабом — заполнен
  черновиком relay-based fault injection тестов (не запускался, требует
  ручной проверки на стенде).
