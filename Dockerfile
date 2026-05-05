FROM ros:jazzy-ros-base

LABEL description="All-in-one: Nuwa-HP60C depth camera + MyCobot Pro 450 arm control"
LABEL maintainer="wangli@cityu.edu.hk"
LABEL version="1.0"

ENV DEBIAN_FRONTEND=noninteractive

# Install system deps
RUN apt update && apt install -y \
    cmake build-essential git \
    libgflags-dev libgoogle-glog-dev libusb-1.0-0-dev libeigen3-dev \
    libpcl-dev python3-colcon-common-extensions \
    ros-jazzy-pcl-conversions ros-jazzy-cv-bridge \
    ros-jazzy-image-transport ros-jazzy-camera-info-manager \
    ros-jazzy-tf2 ros-jazzy-tf2-ros ros-jazzy-sensor-msgs \
    ros-jazzy-geometry-msgs ros-jazzy-std-msgs \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for arm control
RUN pip3 install pymycobot opencv-python numpy --break-system-packages

# Copy SDK source (user must provide this)
COPY ascamera /workspace/src/ascamera

# Build ROS2 ascamera package
RUN . /opt/ros/jazzy/setup.sh && \
    mkdir -p /workspace/ascam_ws/src && \
    cp -r /workspace/src/ascamera /workspace/ascam_ws/src/ && \
    cd /workspace/ascam_ws && \
    colcon build --symlink-install --packages-select ascamera 2>&1 | tail -3

# Copy arm control scripts
COPY mycobot_bridge.py /workspace/mycobot_bridge.py

# Source ROS2 in bashrc
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && \
    echo "source /workspace/ascam_ws/install/setup.bash" >> ~/.bashrc

WORKDIR /workspace
CMD ["bash"]
