"""
Управление конфигом камер через TZTEK (192.168.1.101:8080).

TZTEK -- устройство, обрабатывающее видеопоток с каждой физической
камеры. Позволяет прочитать и переписать конфиг конкретной камеры по её
имени (leopard120_1..leopard120_8).

Механизм fault injection (проверено вручную инженером стенда 2026-08-28):
1. GET  /config?camera=<name>  -- вернуть ТЕКУЩИЙ конфиг камеры (JSON).
2. POST /config?camera=<name>  с тем же JSON, но с "port" изменённым на
   заведомо неправильный (7000 вместо реального, обычно 8000) -- камера
   перестаёт присылать поток по ожидаемому адресу, что в итоге долетает
   как ошибка в /safety/mrm_request.

Сама "порча"/"починка" конфига в этот модуль не зашита -- это только
тонкие обёртки над GET/POST. Логика "прочитать -> испортить порт ->
записать -> ... -> вернуть оригинал обратно" будет собираться в самом
тесте, чтобы вся последовательность действий была видна и понятна при
отладке, а не спрятана внутри одной функции.
"""
import requests

DEVICE_IP = "192.168.1.101"
HTTP_PORT = 8080

BASE_URL = f"http://{DEVICE_IP}:{HTTP_PORT}"

BROKEN_PORT = 7000  # фиксированный "плохой" порт, одинаковый для всех камер


def list_cameras() -> list[str]:
    """GET /list -- список имён всех камер, известных TZTEK."""
    response = requests.get(f"{BASE_URL}/list", timeout=5)
    return response.json()


def get_camera_config(camera_name: str) -> dict:
    """
    GET /config?camera=<name> -- текущий конфиг камеры целиком.

    Возвращает dict (весь JSON распарсен). Этот же dict -- готовый
    "хороший" конфиг, который можно позже отправить обратно через
    set_camera_config(), чтобы восстановить камеру после инъекции отказа.
    """
    response = requests.get(
        f"{BASE_URL}/config", params={"camera": camera_name}, timeout=5
    )
    return response.json()


def set_camera_config(camera_name: str, config: dict) -> requests.Response:
    """
    POST /config?camera=<name> -- записать новый конфиг камеры.

    Возвращает сырой Response (а не распарсенный JSON) -- чтобы вызывающий
    код мог проверить status_code, как это уже делается для реле в
    control_relay.py (allure.attach(f"status_code={response.status_code}")).
    """
    response = requests.post(
        f"{BASE_URL}/config", params={"camera": camera_name}, json=config, timeout=5
    )
    return response


if __name__ == "__main__":
    cameras = list_cameras()
    print(f"Камеры на TZTEK: {cameras}")

    camera_name = input(f"Имя камеры для ручной проверки {cameras}: ")

    original_config = get_camera_config(camera_name)
    print(f"Текущий конфиг {camera_name}:\n{original_config}")

    broken_config = dict(original_config)
    broken_config["port"] = BROKEN_PORT

    input(f"Нажмите Enter, чтобы сломать {camera_name} (port -> {BROKEN_PORT})")
    resp = set_camera_config(camera_name, broken_config)
    print(f"Сломано, status_code={resp.status_code}")

    input("Нажмите Enter, чтобы восстановить исходный конфиг")
    resp = set_camera_config(camera_name, original_config)
    print(f"Восстановлено, status_code={resp.status_code}")
