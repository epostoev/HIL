FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Базовые инструменты (без docker.io)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    python3-pip \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Docker CLI версия 24.0.7 — совместима с хостом (API 1.43)
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli=5:24.0.7-1~ubuntu.22.04~jammy && \
    rm -rf /var/lib/apt/lists/*

# ROS2 Humble
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
    http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
    | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt-get update && apt-get install -y \
    ros-humble-ros-base \
    ros-humble-ros2cli \
    ros-humble-ros2topic \
    ros-humble-ros2node \
    ros-humble-ros2service \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# Python зависимости
RUN pip3 install \
    pytest \
    pytest-timeout \
    pytest-rerunfailures \
    pytest-html \
    allure-pytest \
    pyyaml \
    psutil \
    --index-url https://artifactory.sberautotech.ru/artifactory/api/pypi/pypi/simple/ \
    --trusted-host artifactory.sberautotech.ru

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

COPY tests/ /workspace/tests/

WORKDIR /workspace

CMD ["pytest", "tests/fault_injection/", "-v", "-s"]
