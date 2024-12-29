# Real-Time System Monitor

This project is a lightweight real-time system monitor implemented using PyQt5. It provides a floating window and a system tray icon to display the following system metrics:

- **Network Speed** (upload and download)
- **CPU Usage**
- **GPU Utilization** (NVIDIA GPUs only)

The application is designed to be minimal, with a clean and transparent floating window that can be dragged and repositioned, and a tray icon for easy access to system metrics.

---

## Features

1. **Network Monitoring**:
   - Displays real-time upload and download speeds.
   - Speeds are formatted in human-readable units (KB/s or MB/s).

2. **CPU Monitoring**:
   - Shows real-time CPU usage as a percentage.

3. **GPU Monitoring**:
   - Displays real-time GPU utilization and memory usage for NVIDIA GPUs.
   - Uses the `pynvml` library to gather GPU data.

4. **Floating Window**:
   - Frameless and transparent window that stays on top of other applications.
   - Can be dragged and repositioned using the mouse.

5. **System Tray Icon**:
   - Allows switching between network, CPU, and GPU monitoring.
   - Includes a "Quit" option to exit the application.

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

## Usage

### Running the Application
1. Clone the repository or download the script.
2. Ensure the required Python libraries are installed.
3. Run the script:

   ```bash
   python system_monitor.py
The floating window will appear, displaying the default metric (network speed). The system tray icon will also be available.
Interactions
Floating Window:
Drag: Left-click and drag to move the window.
Double-click: Double-click the window to close it.
System Tray Icon:
Right-click the tray icon to open the context menu.
Switch between monitoring modes (network, CPU, GPU) by selecting the respective options.
Select "Quit" from the menu to exit the application.
File Structure
system_monitor.py: Main application script.
figures/: Directory containing icons for network, CPU, GPU, and the tray icon.
icon.png: Application and tray icon.
upload.png: Upload speed icon.
download.png: Download speed icon.
cpu.png: CPU usage icon.
gpu.png: GPU usage icon.
Notes
GPU Monitoring: If no NVIDIA GPU is detected, the application will display "No Nvidia GPU found" for GPU metrics.
Transparency: The floating window is semi-transparent for a non-intrusive user experience.
Cross-Platform: The application is designed to work on Windows, macOS, and Linux, but GPU monitoring requires NVIDIA GPUs and drivers.
Screenshots
Floating Window
Displays network speed, CPU usage, or GPU utilization based on the selected mode.
System Tray Icon
Access options to toggle metrics and quit the application.
License
This project is open-source and available under the MIT License.

Feel free to modify, share, and use it for personal or commercial purposes!