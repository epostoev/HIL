import requests

DEVICE_IP  = "192.168.1.120"
HTTP_PORT = "80"

API_LOGIN = "admin"
API_PASSWORD = "admin"

def relay_on():
    url = f"http://192.168.1.120/protect/rb15n.cgi"
    response = requests.get(url, auth=(API_LOGIN, API_PASSWORD), timeout=5)
    return response

def relay_off():
    url = f"http://192.168.1.120/protect/rb15f.cgi"
    response = requests.get(url, auth=(API_LOGIN, API_PASSWORD), timeout=5)
    return response

if __name__ == "__main__":
    print(f"Включаем реле")
    relay_on()
    print("Готово")
    input("Нажмите Enter что бы выключить реле")
    print(f"Выключаем реле")
    relay_off()
    print("Готово")

