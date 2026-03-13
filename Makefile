IMAGE = my-docker-project_v_2
TAG = latest

PROJECT_DIR ?= $(shell pwd)
SDA_CONTAINER ?= sda-f898b5d

build:
	docker build -f $(PROJECT_DIR)/dockerfile -t $(IMAGE):$(TAG) $(PROJECT_DIR)

rebuild:
	docker build --no-cache -f $(PROJECT_DIR)/dockerfile -t $(IMAGE):$(TAG) $(PROJECT_DIR)

# Запуск на текущем хосте — тесты уже внутри образа
run:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		$(IMAGE):$(TAG)

# Запуск конкретного файла: make test FILE=test_trajectory_planner_kill.py
test:
	docker run --rm \
		--name evgeny_tests \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		$(IMAGE):$(TAG) \
		pytest project/ros2_control/tests/fault_injection/$(FILE) -v -s

# Разработка — монтируем локальную папку поверх образа чтобы видеть изменения сразу
dev:
	docker run --rm \
		--name evgeny_dev \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/project:/workspace/project \
		$(IMAGE):$(TAG)

# Отладка — интерактивный bash
debug:
	docker run -it --rm \
		--name evgeny_debug \
		--network host \
		--pid=container:$(SDA_CONTAINER) \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PROJECT_DIR)/project:/workspace/project \
		--entrypoint bash \
		$(IMAGE):$(TAG)

stop:
	docker stop evgeny_tests || true

clean:
	docker rm -f evgeny_tests || true
	docker rmi $(IMAGE):$(TAG) || true

.PHONY: build rebuild run test dev debug stop clean