import yaml

# Открываем YAML-файл для чтения
with open('/home/sda/repos/sda/sda_config/hpc/single_head/main_cgroups/main.yaml', 'r') as file:
    # Используем safe_load для безопасности, чтобы предотвратить выполнение вредоносного кода
    data = yaml.safe_load(file)
print(f"\n{data}")