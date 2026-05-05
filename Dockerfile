FROM ros:jazzy-ros-base

LABEL description="Nuwa-HP60C / Angstrong Ascamera ROS2 depth camera driver"
LABEL maintainer="wangli@cityu.edu.hk"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    cmake build-essential \
    libgflags-dev libgoogle-glog-dev libusb-1.0-0-dev libeigen3-dev \
    libpcl-dev python3-colcon-common-extensions \
    ros-jazzy-pcl-conversions ros-jazzy-cv-bridge \
    ros-jazzy-image-transport ros-jazzy-camera-info-manager \
    ros-jazzy-tf2 ros-jazzy-tf2-ros ros-jazzy-sensor-msgs \
    ros-jazzy-geometry-msgs ros-jazzy-std-msgs \
    && rm -rf /var/lib/apt/lists/*

COPY ascamera /workspace/src/ascamera

RUN . /opt/ros/jazzy/setup.sh && \
    mkdir -p /workspace/ascam_ws/src && \
    cp -r /workspace/src/ascamera /workspace/ascam_ws/src/ && \
    cd /workspace/ascam_ws && \
    colcon build --symlink-install --packages-select ascamera 2>&1 | tail -5

RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && \
    echo "source /workspace/ascam_ws/install/setup.bash" >> ~/.bashrc

WORKDIR /workspace
CMD ["bash"]
