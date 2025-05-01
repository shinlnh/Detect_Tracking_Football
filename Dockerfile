FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

# Cài thư viện hệ thống cần cho OpenCV, Tkinter, GUI
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-tk \
    ffmpeg \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /Football

# Copy toàn bộ project vào image
COPY . /Football

# Cài Python packages
RUN pip install --no-cache-dir \
    numpy \
    opencv-python \
    pillow \
    matplotlib \
    tqdm \
    ultralytics \
    filterpy \
    torchvision \
    pandas \
    seaborn

# Cài YOLOv5 nếu cần clone riêng (tùy bạn đã có chưa)
RUN git clone https://github.com/ultralytics/yolov5.git
WORKDIR /FootballApp/yolov5
RUN pip install -r requirements.txt

# Quay lại thư mục chính
WORKDIR /Football

# Chạy GUI app
CMD ["python", "GUI_Detect_Tracker.py"]