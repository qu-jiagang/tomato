import psutil
import pynvml


class NetworkMonitor:
    """负责网络速度的监控和计算"""
    def __init__(self):
        self.last_upload = 0
        self.last_download = 0
        self.update_last_data()

    def update_last_data(self):
        """更新网络的初始值"""
        data = psutil.net_io_counters()
        self.last_upload = data.bytes_sent
        self.last_download = data.bytes_recv

    def get_data(self):
        """计算当前的上传和下载速度"""
        current_data = psutil.net_io_counters()
        upload_speed = current_data.bytes_sent - self.last_upload
        download_speed = current_data.bytes_recv - self.last_download

        self.update_last_data()

        return upload_speed, download_speed

    @staticmethod
    def format_data(speed):
        if speed < 1024 ** 2:
            return f"{speed / 1024:.1f} KB/s"
        else:
            return f"{speed / 1024 ** 2:.1f} MB/s"


class CPUUsageMonitor:
    """负责CPU利用率的监控和计算"""
    def __init__(self):
        self.last_cpu_time = psutil.cpu_times()

    def get_data(self):
        """计算当前的CPU利用率"""
        current_cpu_time = psutil.cpu_times()
        total_time = sum(current_cpu_time) - sum(self.last_cpu_time)
        idle_time = current_cpu_time.idle - self.last_cpu_time.idle

        # 更新上一次的数据
        self.last_cpu_time = current_cpu_time

        if total_time == 0:
            return 0.0
        
        return (total_time - idle_time) / total_time * 100

    @staticmethod
    def format_data(usage):
        return f"{usage:.1f}%"


class GPUUsageMonitor:
    """负责GPU利用率的监控和计算"""
    def __init__(self):
        # 初始化 pynvml 库
        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()  # 获取 GPU 的数量
        except pynvml.NVMLError as e:
            print(f"Failed to initialize NVML: {e}")
            self.device_count = 0

    def get_data(self):
        gpu_data = []
        for i in range(self.device_count):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)  # 获取 GPU 句柄
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)  # 获取利用率
                gpu_data.append({
                    "gpu_id": i,
                    "gpu_utilization": utilization.gpu,  # GPU 核心利用率（整数，单位是百分比）
                    "memory_utilization": utilization.memory,  # 显存利用率（整数，单位是百分比）
                })
            except pynvml.NVMLError as e:
                print(f"Failed to get GPU {i} data: {e}")
        return gpu_data

    @staticmethod
    def format_data(gpu_data):
        formatted_data = []
        for gpu in gpu_data:
            formatted_data.append(
                f"GPU {gpu['gpu_id']}: Usage {gpu['gpu_utilization']}%, Memory {gpu['memory_utilization']}%"
            )
        if not formatted_data:
            return "No Nvidia GPU found"
        return "\n".join(formatted_data)

    def __del__(self):
        try:
            pynvml.nvmlShutdown()
        except pynvml.NVMLError as e:
            print(f"Failed to shut down NVML: {e}")


class DiskUsageMonitor:
    """负责硬盘读写速度的监控和计算"""
    def __init__(self):
        self.last_read = 0
        self.last_write = 0
        self.update_last_data()

    def update_last_data(self):
        """更新硬盘的初始值"""
        data = psutil.disk_io_counters()
        self.last_read = data.read_bytes
        self.last_write = data.write_bytes

    def get_data(self):
        """计算当前的读写速度"""
        current_data = psutil.disk_io_counters()
        read_speed = current_data.read_bytes - self.last_read
        write_speed = current_data.write_bytes - self.last_write

        self.update_last_data()

        return read_speed, write_speed

    @staticmethod
    def format_data(speed):
        if speed < 1024 ** 2:
            return f"{speed / 1024:.1f} KB/s"
        else:
            return f"{speed / 1024 ** 2:.1f} MB/s"