# Tomato

This project is a lightweight real-time system monitor implemented using PyQt5. It provides a floating window and a system tray icon to display the following system metrics:

- **Network Speed** (upload and download)
- **CPU Usage**
- **GPU Utilization** (NVIDIA GPUs only)
- **Disk R&W**

The application is designed to be minimal, with a clean and transparent floating window that can be dragged and repositioned, and a tray icon for easy access to system metrics.

---

## Requirements

To run the project, the following dependencies must be installed:

### Python Libraries:
- **PyQt5**: `pip install pyqt5`
- **psutil**: `pip install psutil`
- **pynvml** (for GPU monitoring): `pip install pynvml`

### Hardware Requirements:
- GPU monitoring requires an NVIDIA GPU and the NVIDIA Management Library (NVML) to be available.

---
