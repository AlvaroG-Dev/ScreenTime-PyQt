import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QLabel, QPushButton, QGroupBox, QFrame)
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QColor

class TimeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.min_value = 0
        self.max_value = 59
        self.active = False
        self.setAlignment(Qt.AlignCenter)
        self.update_style()
        self.main_window = None  # Referencia a la ventana principal
    
    def set_main_window(self, window):
        """Establece referencia a la ventana principal"""
        self.main_window = window
    
    def setRange(self, min_val, max_val):
        self.min_value = min_val
        self.max_value = max_val
    
    def update_style(self):
        color = "#4CAF50" if self.active else "#3A3A3A"
        self.setStyleSheet(f"""
            font-size: 40px;
            font-weight: bold;
            color: #FFFFFF;
            background-color: {color};
            border-radius: 10px;
            padding: 5px;
            min-width: 60px;
        """)
    
    def wheelEvent(self, event):
        self.active = True
        self.update_style()
        
        delta = event.angleDelta().y()
        if delta > 0 and self.value < self.max_value:
            self.value += 1
        elif delta < 0 and self.value > self.min_value:
            self.value -= 1
        
        self.setText(f"{self.value:02d}")
        
        # Notificar a la ventana principal para actualizar el tiempo
        if self.main_window:
            self.main_window.update_total_time()
        
        self.highlight_animation()
    
    def highlight_animation(self):
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.OutQuad)
        orig_rect = self.geometry()
        animation.setKeyValueAt(0.5, orig_rect.adjusted(-2, -2, 2, 2))
        animation.setEndValue(orig_rect)
        animation.start()
        
        QTimer.singleShot(300, lambda: [setattr(self, 'active', False), self.update_style()])

class ScreenTimeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_variables()
        self.setup_timers()
        self.apply_styles()
    
    def setup_ui(self):
        self.setWindowTitle("Screen Time Control")
        self.setFixedSize(700, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Sección izquierda (Contador)
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setSpacing(15)
        
        self.title = QLabel("TIMER")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.title.setAlignment(Qt.AlignCenter)
        
        # Contador HH:MM:SS
        self.time_layout = QHBoxLayout()
        self.time_layout.setSpacing(5)
        self.time_layout.setAlignment(Qt.AlignCenter)
        
        self.hour_label = TimeLabel()
        self.hour_label.setRange(0, 23)
        self.hour_label.setText("00")
        self.hour_label.set_main_window(self)  # Establecer referencia
        
        self.colon1 = QLabel(":")
        self.colon1.setStyleSheet("font-size: 40px;")
        
        self.minute_label = TimeLabel()
        self.minute_label.setRange(0, 59)
        self.minute_label.setText("00")
        self.minute_label.set_main_window(self)  # Establecer referencia
        
        self.colon2 = QLabel(":")
        self.colon2.setStyleSheet("font-size: 40px;")
        
        self.second_label = TimeLabel()
        self.second_label.setRange(0, 59)
        self.second_label.setText("00")
        self.second_label.set_main_window(self)  # Establecer referencia
        
        self.time_layout.addWidget(self.hour_label)
        self.time_layout.addWidget(self.colon1)
        self.time_layout.addWidget(self.minute_label)
        self.time_layout.addWidget(self.colon2)
        self.time_layout.addWidget(self.second_label)
        
        # Botones de control
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        self.button_layout.setAlignment(Qt.AlignCenter)
        
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.play_button.setFixedSize(60, 60)
        self.play_button.clicked.connect(self.start_timer)
        
        self.pause_button = QPushButton()
        self.pause_button.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.pause_button.setFixedSize(60, 60)
        self.pause_button.clicked.connect(self.pause_timer)
        
        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stop_button.setFixedSize(60, 60)
        self.stop_button.clicked.connect(self.stop_timer)
        
        self.button_layout.addWidget(self.play_button)
        self.button_layout.addWidget(self.pause_button)
        self.button_layout.addWidget(self.stop_button)
        
        left_layout.addWidget(self.title)
        left_layout.addLayout(self.time_layout)
        left_layout.addLayout(self.button_layout)
        
        # Sección derecha (Tiempos rápidos y ajustes)
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(15)
        
        # Tiempos rápidos
        self.presets_group = QGroupBox("Quick Presets")
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(10)
        
        presets = [("15m", 15), ("30m", 30), ("1h", 60), ("2h", 120)]
        for text, minutes in presets:
            btn = QPushButton(text)
            btn.setFixedSize(70, 50)
            btn.clicked.connect(lambda _, m=minutes: self.set_preset_time(m))
            presets_layout.addWidget(btn)
        
        self.presets_group.setLayout(presets_layout)
        
        # Ajustes
        self.settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        
        self.alert_toggle = QPushButton("30m Alerts: ON")
        self.alert_toggle.setCheckable(True)
        self.alert_toggle.setChecked(True)
        self.alert_toggle.setFixedHeight(50)
        self.alert_toggle.clicked.connect(self.toggle_alerts)
        settings_layout.addWidget(self.alert_toggle)
        
        self.settings_group.setLayout(settings_layout)
        
        right_layout.addWidget(self.presets_group)
        right_layout.addWidget(self.settings_group)
        
        self.main_layout.addWidget(left_frame)
        self.main_layout.addWidget(right_frame)
    
    def setup_variables(self):
        self.total_seconds = 0
        self.is_running = False
        self.alert_enabled = True
        self.alert_interval = 30 * 60  # 30 minutos en segundos
        self.break_time = 2 * 60  # 2 minutos de descanso
    
    def setup_timers(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        self.break_timer = QTimer(self)
        self.break_timer.timeout.connect(self.update_break_timer)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2B2B2B;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border-radius: 15px;
                padding: 8px;
                font-weight: bold;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
            QGroupBox {
                color: #AAAAAA;
                border: 1px solid #444444;
                border-radius: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
            }
        """)
    
    def update_total_time(self):
        """Actualiza el tiempo total cuando se modifican los valores"""
        hours = int(self.hour_label.text())
        minutes = int(self.minute_label.text())
        seconds = int(self.second_label.text())
        self.total_seconds = hours * 3600 + minutes * 60 + seconds
    
    def set_preset_time(self, minutes):
        self.hour_label.setText("00")
        self.minute_label.setText(f"{minutes:02d}")
        self.second_label.setText("00")
        self.update_total_time()
    
    def start_timer(self):
        if self.total_seconds > 0 and not self.is_running:
            self.is_running = True
            self.timer.start(1000)
            self.update_button_states(self.play_button)
    
    def pause_timer(self):
        if self.is_running:
            self.is_running = False
            self.timer.stop()
            self.update_button_states(self.pause_button)
    
    def stop_timer(self):
        self.is_running = False
        self.timer.stop()
        self.total_seconds = 0
        self.hour_label.setText("00")
        self.minute_label.setText("00")
        self.second_label.setText("00")
        self.update_button_states(self.stop_button)
    
    def update_button_states(self, active_button):
        for btn in [self.play_button, self.pause_button, self.stop_button]:
            btn.setStyleSheet("""
                background-color: %s;
                border-radius: 30px;
            """ % ("#4CAF50" if btn == active_button else "#3A3A3A"))
    
    def update_timer(self):
        if self.total_seconds > 0:
            self.total_seconds -= 1
            hours = self.total_seconds // 3600
            minutes = (self.total_seconds % 3600) // 60
            seconds = self.total_seconds % 60
            self.hour_label.setText(f"{hours:02d}")
            self.minute_label.setText(f"{minutes:02d}")
            self.second_label.setText(f"{seconds:02d}")
            
            if (self.alert_enabled and 
                self.total_seconds % self.alert_interval == 0 and 
                self.total_seconds > 0):
                self.trigger_break()
        else:
            self.stop_timer()
    
    def trigger_break(self):
        self.pause_timer()
        self.break_active = True
        self.break_timer.start(1000)
        self.set_break_style(True)
    
    def set_break_style(self, active):
        color = "#FF5555" if active else "#3A3A3A"
        for label in [self.hour_label, self.minute_label, self.second_label]:
            label.setStyleSheet(f"""
                font-size: 40px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: {color};
                border-radius: 10px;
                padding: 5px;
                min-width: 60px;
            """)
    
    def update_break_timer(self):
        if self.break_time > 0:
            self.break_time -= 1
        else:
            self.break_timer.stop()
            self.break_time = 2 * 60
            self.set_break_style(False)
            self.start_timer()
    
    def toggle_alerts(self):
        self.alert_enabled = not self.alert_enabled
        state = "ON" if self.alert_enabled else "OFF"
        self.alert_toggle.setText(f"30m Alerts: {state}")
        self.alert_toggle.setStyleSheet(f"""
            background-color: {'#4CAF50' if self.alert_enabled else '#3A3A3A'};
            font-weight: bold;
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ScreenTimeApp()
    window.show()
    sys.exit(app.exec_())