from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon
from Monitors import NetworkMonitor, CPUUsageMonitor, GPUUsageMonitor, DiskUsageMonitor

register_monitors = {
    "network": NetworkMonitor,
    "cpu": CPUUsageMonitor,
    "gpu": GPUUsageMonitor,
    "disk": DiskUsageMonitor
}


class TrayIcon(QSystemTrayIcon):
    """负责托盘图标功能"""
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window

        # 设置托盘图标
        self.setIcon(QIcon("resources/icons/icon.png"))

        # 构建托盘菜单
        self.menu = QMenu()
        self.create_actions()
        self.setContextMenu(self.menu)

        # 连接托盘图标单击事件
        self.activated.connect(self.on_tray_icon_clicked)

    def create_actions(self):
        """创建托盘菜单项"""
        network_action = QAction("网络", self, checkable=True)
        network_action.toggled.connect(self.on_network_toggled)
        self.menu.addAction(network_action)

        cpu_action = QAction("CPU", self, checkable=True)
        cpu_action.toggled.connect(self.on_cpu_toggled)
        self.menu.addAction(cpu_action)

        gpu_action = QAction("GPU", self, checkable=True)
        gpu_action.toggled.connect(self.on_gpu_toggled)
        self.menu.addAction(gpu_action)

        disk_action = QAction("Disk", self, checkable=True)
        disk_action.toggled.connect(self.on_disk_toggled)
        self.menu.addAction(disk_action)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.quit)
        self.menu.addAction(quit_action)

    def on_network_toggled(self, state):
        if state:
            self.add_action('network')
        else:
            self.remove_action('network')
        self.parent_window.update_ui()

    def on_cpu_toggled(self, state):
        if state:
            self.add_action('cpu')
        else:
            self.remove_action('cpu')
        self.parent_window.update_ui()

    def on_gpu_toggled(self, state):
        if state:
            self.add_action('gpu')
        else:
            self.remove_action('gpu')
        self.parent_window.update_ui()

    def on_disk_toggled(self, state):
        if state:
            self.add_action('disk')
        else:
            self.remove_action('disk')
        self.parent_window.update_ui()

    def add_action(self, action):
        if action not in self.parent_window.show_info:
            self.parent_window.show_info.append(action)
        if action not in self.parent_window.monitor:
            self.parent_window.monitor[action] = register_monitors[action]()

    def remove_action(self, action):
        if action in self.parent_window.show_info:
            self.parent_window.show_info.remove(action)
        if action in self.parent_window.monitor:
            self.parent_window.monitor.pop(action)

    def on_tray_icon_clicked(self, reason):
        """处理托盘图标的点击事件"""
        if reason == QSystemTrayIcon.Trigger:  # 左键单击
            if self.parent_window.isVisible():
                self.parent_window.hide()
            else:
                self.parent_window.show()

