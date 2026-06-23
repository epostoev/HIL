import yaml
from pathlib import Path


def load_nodes_by_component(yaml_path: str | Path) -> dict[str, list[str]]:
    """
    Парсит yaml файл и возвращает словарь:
    {
        "perception":   ["/perception/detector_3d", "/perception/boom_barrier_detector", ...],
        "planning":     ["/planning/lane_tracer_node", ...],
        "localization": ["/lidar_localization", ...],
        ...
    }

    Рекурсивно обходит все вложенные секции (3d_pipeline, other, online и т.д.)
    и собирает все теги в плоский список для каждого компонента верхнего уровня.
    Пропускает теги которые не начинаются с '/' (например 'default_tag').
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    result = {}

    for component, content in data.items():
        if not isinstance(content, dict):
            continue

        nodes = _collect_tags(content)

        if nodes:
            result[component] = nodes

    return result


def _collect_tags(data: dict) -> list[str]:
    """
    Рекурсивно собирает все теги из вложенных секций словаря.
    Возвращает только теги начинающиеся с '/' (ROS node paths).
    """
    nodes = []

    for key, value in data.items():
        if key == "tags" and isinstance(value, list):
            for tag in value:
                if isinstance(tag, str) and tag.startswith("/"):
                    nodes.append(tag)
        elif isinstance(value, dict):
            nodes.extend(_collect_tags(value))

    return nodes


if __name__ == "__main__":
    import sys
    import json

    yaml_path = sys.argv[1] if len(sys.argv) > 1 else "evolved.param.yaml"

    components = load_nodes_by_component(yaml_path)

    for component, nodes in components.items():
        print(f"\n[{component}] — {len(nodes)} нод:")
        for node in nodes:
            print(f"  {node}")

    print("\n--- JSON ---")
    print(json.dumps(components, indent=2, ensure_ascii=False))