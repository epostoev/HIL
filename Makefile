IMAGE = my-docker-project_v_2
TAG = latest

PROJECT_DIR ?= $(shell pwd)
SDA_CONTAINER := $(shell docker ps --format '{{.Names}}' | grep -E 'sda-f898b5d|sda_drive' | head -1)

# Проверка что контейнер найден
ifeq ($(SDA_CONTAINER),)
$(error Контейнер стенда не найден. Запусти: docker ps)
endif




build:
	docker build -f $(PROJECT_DIR)/dockerfile -t $(IMAGE):$(TAG) $(PROJECT_DIR)

rebuild:
	docker build --no-cache -f $(PROJECT_DIR)/dockerfile -t $(IMAGE):$(TAG) $(PROJECT_DIR)

run:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		$(IMAGE):$(TAG)

run-sensing:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_sensing_nodes_running.py -v -s

test:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/$(FILE) -v -s

dev:
	docker run -it --rm \
		--name evgeny_dev \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG)

debug:
	docker run -it --rm \
		--name evgeny_debug \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		--entrypoint bash \
		$(IMAGE):$(TAG)

stop:
	docker stop evgeny_tests || true

clean:
	docker rm -f evgeny_tests || true
	docker rmi $(IMAGE):$(TAG) || true

allure_planning:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/allure-results:/workspace/allure-results \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_planning_nodes_running.py \
		       tests/fault_injection/test_planning_kill.py \
		-v -s \
		--alluredir=allure-results/planning

allure_sensing:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/allure-results:/workspace/allure-results \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_sensing_nodes_running.py \
		       tests/fault_injection/test_sensing_kill.py \
		-v -s \
		--alluredir=allure-results/sensing

allure_calibration:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/allure-results:/workspace/allure-results \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_calibration_nodes_running.py \
		       tests/fault_injection/test_calibration_kill.py \
		-v -s \
		--alluredir=allure-results/calibration

allure_hdmap:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/allure-results:/workspace/allure-results \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_hdmap_nodes_running.py \
		       tests/fault_injection/test_hdmap_kill.py \
		-v -s \
		--alluredir=allure-results/hdmap
allure_control:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/allure-results:/workspace/allure-results \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_control_nodes_running.py \
		       tests/fault_injection/test_control_kill.py \
		-v -s \
		--alluredir=allure-results/control
allure_localization:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/allure-results:/workspace/allure-results \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_localization_nodes_running.py \
		       tests/fault_injection/test_localization_kill.py \
		-v -s \
		--alluredir=allure-results/localization
allure_integration:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/allure-results:/workspace/allure-results \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_integration_nodes_running.py \
		       tests/fault_injection/test_integration_kill.py \
		-v -s \
		--alluredir=allure-results/integration
allure_perception:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/allure-results:/workspace/allure-results \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_perception_nodes_running.py \
		       tests/fault_injection/test_perception_kill.py \
		-v -s \
		--alluredir=allure-results/perception
allure_prediction:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/allure-results:/workspace/allure-results \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_prediction_nodes_running.py \
		       tests/fault_injection/test_prediction_kill.py \
		-v -s \
		--alluredir=allure-results/prediction
.PHONY: build rebuild run run-sensing test dev debug stop clean report-sensing report-sensing-kill report-sensing-kill_01 report-sensing_01