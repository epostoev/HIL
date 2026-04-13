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

report-sensing:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/reports:/workspace/reports \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_sensing_nodes_running.py -v -s \
		--html=reports/sensing_nodes_running.html \
		--self-contained-html

report-sensing-kill:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/reports:/workspace/reports \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_sensing_kill.py -v -s \
		--html=reports/sensing_kill.html \
		--self-contained-html

report-sensing-kill_01:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/reports:/workspace/reports \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_sensing_kill_01.py -v -s \
		--html=reports/sensing_kill_01.html \
		--self-contained-html

report-sensing-kill_02:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/reports:/workspace/reports \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_sensing_kill_02.py -v -s \
		--html=reports/sensing_kill_02.html \
		--self-contained-html

report-sensing_01:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/reports:/workspace/reports \
		-v $(PROJECT_DIR)/tests:/workspace/tests \
		$(IMAGE):$(TAG) \
		pytest tests/fault_injection/test_sensing_nodes_running_01.py -v -s \
		--html=reports/sensing_nodes_running_01.html \
		--self-contained-html
		

.PHONY: build rebuild run run-sensing test dev debug stop clean report-sensing report-sensing-kill report-sensing-kill_01 report-sensing_01