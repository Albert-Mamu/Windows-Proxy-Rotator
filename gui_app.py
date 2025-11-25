import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTextEdit, QSpinBox, QComboBox,
                             QGroupBox, QProgressBar, QTableWidget, QTableWidgetItem,
                             QHeaderView, QWidget, QMessageBox, QFileDialog, QTabWidget,
                             QLineEdit, QCheckBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPalette, QColor

from proxy_rotator import ProxyRotator
from system_proxy import WindowsSystemProxy

class ProxyRotatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rotator = ProxyRotator()
        self.system_proxy = WindowsSystemProxy()
        self.init_ui()
        self.update_display()
        
        # Auto-update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)
    
    def init_ui(self):
        self.setWindowTitle("AlbertAI - Advanced Proxy Rotator v2.0")
        self.setGeometry(100, 100, 1000, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("Advanced Proxy Rotator")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Supports: HTTP, HTTPS, SOCKS4, SOCKS5 with Authentication")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Main Tab
        main_tab = QWidget()
        tabs.addTab(main_tab, "Control Panel")
        
        # Proxy Management Tab
        manage_tab = QWidget()
        tabs.addTab(manage_tab, "Proxy Management")
        
        # Advanced Tab
        advanced_tab = QWidget()
        tabs.addTab(advanced_tab, "Advanced Settings")
        
        self.setup_main_tab(main_tab)
        self.setup_manage_tab(manage_tab)
        self.setup_advanced_tab(advanced_tab)
    
    def setup_main_tab(self, parent):
        layout = QVBoxLayout(parent)
        
        # Status Group
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.status_label)
        
        self.proxy_count_label = QLabel("Loaded Proxies: 0")
        status_layout.addWidget(self.proxy_count_label)
        
        self.current_proxy_label = QLabel("Current Proxy: None")
        status_layout.addWidget(self.current_proxy_label)
        
        self.system_proxy_label = QLabel("System Proxy: Disabled")
        status_layout.addWidget(self.system_proxy_label)
        
        # Protocol distribution
        self.protocol_stats_label = QLabel("Protocols: HTTP: 0, HTTPS: 0, SOCKS4: 0, SOCKS5: 0")
        status_layout.addWidget(self.protocol_stats_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Control Group
        control_group = QGroupBox("Rotation Control")
        control_layout = QVBoxLayout()
        
        # Rotation interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Rotation Interval (seconds):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(10, 3600)
        self.interval_spin.setValue(300)
        self.interval_spin.valueChanged.connect(self.update_rotation_interval)
        interval_layout.addWidget(self.interval_spin)
        
        # Protocol filter
        interval_layout.addWidget(QLabel("Protocol Filter:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["All", "HTTP", "HTTPS", "SOCKS4", "SOCKS5"])
        interval_layout.addWidget(self.protocol_combo)
        
        interval_layout.addStretch()
        control_layout.addLayout(interval_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Rotation")
        self.start_btn.clicked.connect(self.start_rotation)
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Rotation")
        self.stop_btn.clicked.connect(self.stop_rotation)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        button_layout.addWidget(self.stop_btn)
        
        self.rotate_now_btn = QPushButton("Rotate Now")
        self.rotate_now_btn.clicked.connect(self.rotate_now)
        self.rotate_now_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        button_layout.addWidget(self.rotate_now_btn)
        
        self.enable_system_btn = QPushButton("Enable System Proxy")
        self.enable_system_btn.clicked.connect(self.enable_system_proxy)
        self.enable_system_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")
        button_layout.addWidget(self.enable_system_btn)
        
        self.disable_system_btn = QPushButton("Disable System Proxy")
        self.disable_system_btn.clicked.connect(self.disable_system_proxy)
        button_layout.addWidget(self.disable_system_btn)
        
        control_layout.addLayout(button_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Current Proxy Details
        details_group = QGroupBox("Current Proxy Details")
        details_layout = QVBoxLayout()
        
        self.proxy_details_text = QTextEdit()
        self.proxy_details_text.setReadOnly(True)
        self.proxy_details_text.setMaximumHeight(100)
        details_layout.addWidget(self.proxy_details_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Log Group
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
    
    def setup_manage_tab(self, parent):
        layout = QVBoxLayout(parent)
        
        # Proxy List Group
        list_group = QGroupBox("Proxy List")
        list_layout = QVBoxLayout()
        
        # Table for proxies
        self.proxy_table = QTableWidget()
        self.proxy_table.setColumnCount(6)
        self.proxy_table.setHorizontalHeaderLabels(["IP", "Port", "Protocol", "Username", "Password", "Status"])
        self.proxy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.proxy_table.setSelectionBehavior(QTableWidget.SelectRows)
        list_layout.addWidget(self.proxy_table)
        
        # Proxy actions
        action_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load Proxies")
        self.load_btn.clicked.connect(self.load_proxies)
        action_layout.addWidget(self.load_btn)
        
        self.validate_btn = QPushButton("Validate All")
        self.validate_btn.clicked.connect(self.validate_proxies)
        action_layout.addWidget(self.validate_btn)
        
        self.import_btn = QPushButton("Import Proxies")
        self.import_btn.clicked.connect(self.import_proxies)
        action_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Export Valid")
        self.export_btn.clicked.connect(self.export_proxies)
        action_layout.addWidget(self.export_btn)
        
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_proxies)
        action_layout.addWidget(self.remove_btn)
        
        list_layout.addLayout(action_layout)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Add proxy manually
        add_group = QGroupBox("Add Proxy Manually")
        add_layout = QVBoxLayout()
        
        # Manual input form
        form_layout = QHBoxLayout()
        
        form_layout.addWidget(QLabel("IP:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.1.1")
        form_layout.addWidget(self.ip_input)
        
        form_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("8080")
        form_layout.addWidget(self.port_input)
        
        form_layout.addWidget(QLabel("Protocol:"))
        self.protocol_input = QComboBox()
        self.protocol_input.addItems(["http", "https", "socks4", "socks5"])
        form_layout.addWidget(self.protocol_input)
        
        add_layout.addLayout(form_layout)
        
        # Authentication form
        auth_layout = QHBoxLayout()
        
        auth_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("optional")
        auth_layout.addWidget(self.username_input)
        
        auth_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("optional")
        self.password_input.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.password_input)
        
        add_layout.addLayout(auth_layout)
        
        # Add button
        self.add_manual_btn = QPushButton("Add Proxy")
        self.add_manual_btn.clicked.connect(self.add_proxy_manual)
        self.add_manual_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        add_layout.addWidget(self.add_manual_btn)
        
        # Bulk add
        bulk_layout = QHBoxLayout()
        bulk_layout.addWidget(QLabel("Bulk Add (ip:port:user:pass):"))
        self.bulk_input = QTextEdit()
        self.bulk_input.setMaximumHeight(60)
        self.bulk_input.setPlaceholderText("192.168.1.1:8080:user:pass\n192.168.1.2:1080::\n10.0.0.1:3128")
        bulk_layout.addWidget(self.bulk_input)
        
        self.add_bulk_btn = QPushButton("Add Bulk")
        self.add_bulk_btn.clicked.connect(self.add_proxy_bulk)
        bulk_layout.addWidget(self.add_bulk_btn)
        
        add_layout.addLayout(bulk_layout)
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
    
    def setup_advanced_tab(self, parent):
        layout = QVBoxLayout(parent)
        
        # Validation settings
        validation_group = QGroupBox("Validation Settings")
        validation_layout = QVBoxLayout()
        
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Validation Timeout (seconds):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 60)
        self.timeout_spin.setValue(15)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        validation_layout.addLayout(timeout_layout)
        
        workers_layout = QHBoxLayout()
        workers_layout.addWidget(QLabel("Max Validation Workers:"))
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 50)
        self.workers_spin.setValue(10)
        workers_layout.addWidget(self.workers_spin)
        workers_layout.addStretch()
        validation_layout.addLayout(workers_layout)
        
        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)
        
        # System settings
        system_group = QGroupBox("System Proxy Settings")
        system_layout = QVBoxLayout()
        
        self.auto_system_proxy = QCheckBox("Automatically enable system proxy on rotation")
        system_layout.addWidget(self.auto_system_proxy)
        
        self.bypass_local = QCheckBox("Bypass proxy for local addresses")
        self.bypass_local.setChecked(True)
        system_layout.addWidget(self.bypass_local)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Application control
        app_group = QGroupBox("Application Control")
        app_layout = QHBoxLayout()
        
        app_layout.addWidget(QLabel("Application Path:"))
        self.app_path_input = QLineEdit()
        self.app_path_input.setPlaceholderText("C:\\Path\\To\\Application.exe")
        app_layout.addWidget(self.app_path_input)
        
        self.browse_app_btn = QPushButton("Browse")
        self.browse_app_btn.clicked.connect(self.browse_application)
        app_layout.addWidget(self.browse_app_btn)
        
        self.launch_app_btn = QPushButton("Launch with Proxy")
        self.launch_app_btn.clicked.connect(self.launch_with_proxy)
        app_layout.addWidget(self.launch_app_btn)
        
        app_group.setLayout(app_layout)
        layout.addWidget(app_group)
        
        layout.addStretch()
    
    def update_display(self):
        """Update all display elements"""
        # Proxy counts
        total_proxies = self.rotator.get_proxy_count()
        self.proxy_count_label.setText(f"Loaded Proxies: {total_proxies}")
        
        # Protocol statistics
        http_count = len(self.rotator.get_proxies_by_protocol('http'))
        https_count = len(self.rotator.get_proxies_by_protocol('https'))
        socks4_count = len(self.rotator.get_proxies_by_protocol('socks4'))
        socks5_count = len(self.rotator.get_proxies_by_protocol('socks5'))
        
        self.protocol_stats_label.setText(
            f"Protocols: HTTP: {http_count}, HTTPS: {https_count}, SOCKS4: {socks4_count}, SOCKS5: {socks5_count}"
        )
        
        # Current proxy
        current = self.rotator.get_current_proxy()
        if current:
            proxy_url = self.rotator.format_proxy_url(current)
            self.current_proxy_label.setText(f"Current Proxy: {proxy_url}")
            
            # Update proxy details
            details = f"IP: {current['ip']} | Port: {current['port']} | Protocol: {current.get('protocol', 'http')}"
            if current.get('username'):
                details += f" | Username: {current['username']}"
            if current.get('password'):
                details += f" | Password: {'*' * len(current['password'])}"
            
            self.proxy_details_text.setPlainText(details)
        else:
            self.current_proxy_label.setText("Current Proxy: None")
            self.proxy_details_text.clear()
        
        # System proxy status
        system_status = self.system_proxy.get_current_proxy()
        if system_status and system_status['enabled']:
            auth_info = ""
            if system_status.get('username'):
                auth_info = f" (User: {system_status['username']})"
            self.system_proxy_label.setText(f"System Proxy: Enabled ({system_status['server']}{auth_info})")
        else:
            self.system_proxy_label.setText("System Proxy: Disabled")
        
        # Rotation status
        if self.rotator.is_rotating:
            self.status_label.setText("Status: Rotation Active")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            self.status_label.setText("Status: Stopped")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def update_proxy_table(self):
        """Update proxy table with current proxy list"""
        self.proxy_table.setRowCount(len(self.rotator.proxies))
        
        for row, proxy in enumerate(self.rotator.proxies):
            self.proxy_table.setItem(row, 0, QTableWidgetItem(proxy['ip']))
            self.proxy_table.setItem(row, 1, QTableWidgetItem(proxy['port']))
            self.proxy_table.setItem(row, 2, QTableWidgetItem(proxy.get('protocol', 'http')))
            self.proxy_table.setItem(row, 3, QTableWidgetItem(proxy.get('username', '')))
            
            # Mask password
            password = proxy.get('password', '')
            masked_password = '*' * len(password) if password else ''
            self.proxy_table.setItem(row, 4, QTableWidgetItem(masked_password))
            
            # Status (to be updated during validation)
            status_item = QTableWidgetItem("Pending")
            self.proxy_table.setItem(row, 5, status_item)
    
    def update_rotation_interval(self):
        self.rotator.set_rotation_interval(self.interval_spin.value())
        self.log(f"Rotation interval updated to {self.interval_spin.value()} seconds")
    
    def start_rotation(self):
        self.rotator.start_rotation()
        self.log("Proxy rotation started")
    
    def stop_rotation(self):
        self.rotator.stop_rotation()
        self.log("Proxy rotation stopped")
    
    def rotate_now(self):
        proxy = self.rotator.rotate_proxy()
        if proxy:
            proxy_url = self.rotator.format_proxy_url(proxy)
            self.log(f"Manual rotation to: {proxy_url}")
            
            if self.auto_system_proxy.isChecked():
                self.enable_system_proxy()
        else:
            self.log("Rotation failed: No proxies available")
    
    def enable_system_proxy(self):
        current = self.rotator.get_current_proxy()
        if current:
            if self.system_proxy.enable_system_proxy(current):
                proxy_url = self.rotator.format_proxy_url(current)
                self.log(f"System proxy enabled: {proxy_url}")
            else:
                self.log("Failed to enable system proxy")
        else:
            QMessageBox.warning(self, "Warning", "No active proxy selected")
    
    def disable_system_proxy(self):
        if self.system_proxy.disable_system_proxy():
            self.log("System proxy disabled")
        else:
            self.log("Failed to disable system proxy")
    
    def load_proxies(self):
        self.rotator.load_proxies()
        self.update_proxy_table()
        self.log(f"Loaded {self.rotator.get_proxy_count()} proxies")
    
    def validate_proxies(self):
        # Update checker settings
        self.rotator.checker.timeout = self.timeout_spin.value()
        
        valid_count = len(self.rotator.validate_proxies())
        self.update_proxy_table()
        self.log(f"Proxy validation complete: {valid_count} valid proxies")
    
    def import_proxies(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Proxies", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.rotator.proxy_file = file_path
            self.load_proxies()
            self.log(f"Proxies imported from {file_path}")
    
    def export_proxies(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Valid Proxies", "", "Text Files (*.txt)")
        if file_path:
            valid_proxies = [p for p in self.rotator.proxies if self.rotator.checker.check_proxy(p)]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for proxy in valid_proxies:
                    f.write(f"{proxy['raw_line']}\n")
            
            self.log(f"Exported {len(valid_proxies)} valid proxies to {file_path}")
    
    def remove_proxies(self):
        selected_rows = self.proxy_table.selectionModel().selectedRows()
        if selected_rows:
            # Remove from end to avoid index issues
            for row in sorted(selected_rows, reverse=True):
                if row.row() < len(self.rotator.proxies):
                    removed_proxy = self.rotator.proxies.pop(row.row())
                    self.log(f"Removed proxy: {removed_proxy['ip']}:{removed_proxy['port']}")
            
            self.update_proxy_table()
            
            # Update file
            with open(self.rotator.proxy_file, 'w', encoding='utf-8') as f:
                for proxy in self.rotator.proxies:
                    f.write(f"{proxy['raw_line']}\n")
    
    def add_proxy_manual(self):
        ip = self.ip_input.text().strip()
        port = self.port_input.text().strip()
        protocol = self.protocol_input.currentText()
        username = self.username_input.text().strip() or None
        password = self.password_input.text().strip() or None
        
        if not ip or not port:
            QMessageBox.warning(self, "Error", "IP and Port are required")
            return
        
        # Create proxy data
        proxy_data = {
            'ip': ip,
            'port': port,
            'protocol': protocol,
            'username': username,
            'password': password,
            'raw_line': f"{ip}:{port}:{username}:{password}" if username and password else f"{ip}:{port}:{username}" if username else f"{ip}:{port}"
        }
        
        if self.rotator.add_proxy(proxy_data):
            self.update_proxy_table()
            self.clear_manual_form()
            self.log(f"Added proxy: {ip}:{port} ({protocol})")
        else:
            QMessageBox.warning(self, "Error", "Failed to add proxy")
    
    def add_proxy_bulk(self):
        bulk_text = self.bulk_input.toPlainText().strip()
        if not bulk_text:
            return
        
        lines = [line.strip() for line in bulk_text.split('\n') if line.strip()]
        added_count = 0
        
        for line in lines:
            proxy = self.rotator.parse_proxy_line(line)
            if proxy and self.rotator.add_proxy(proxy):
                added_count += 1
        
        self.update_proxy_table()
        self.bulk_input.clear()
        self.log(f"Added {added_count} proxies from bulk input")
    
    def clear_manual_form(self):
        self.ip_input.clear()
        self.port_input.clear()
        self.username_input.clear()
        self.password_input.clear()
    
    def browse_application(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Application", "", "Executable Files (*.exe);;All Files (*)")
        if file_path:
            self.app_path_input.setText(file_path)
    
    def launch_with_proxy(self):
        app_path = self.app_path_input.text().strip()
        current_proxy = self.rotator.get_current_proxy()
        
        if not app_path or not os.path.exists(app_path):
            QMessageBox.warning(self, "Error", "Invalid application path")
            return
        
        if not current_proxy:
            QMessageBox.warning(self, "Error", "No active proxy selected")
            return
        
        if self.system_proxy.set_proxy_for_app(self.rotator.format_proxy_url(current_proxy), app_path):
            self.log(f"Launched {app_path} with proxy")
        else:
            self.log(f"Failed to launch {app_path} with proxy")
    
    def log(self, message: str):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

def main():
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = ProxyRotatorGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()