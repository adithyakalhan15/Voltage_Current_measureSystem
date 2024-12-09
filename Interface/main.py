import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QComboBox, QPushButton, QFrame
from PySide6.QtGui import QColor
from PySide6.QtCore import QTimer
from serial.tools.list_ports import comports
import serial

class ArduinoControlApp(QWidget):
    def __init__(self):
        super().__init__()

        self.serial_port = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Arduino Control App')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        port_label = QLabel('Select Port:')
        self.port_combo = QComboBox(self)
        self.port_combo.addItems(self.get_available_ports())

        baud_label = QLabel('Select Baud Rate:')
        self.baud_combo = QComboBox(self)
        self.baud_combo.addItems(['9600', '115200'])  # Add more baud rates if needed

        connect_button = QPushButton('Connect', self)
        connect_button.clicked.connect(self.connect_to_arduino)

        self.frame_voltage, self.label_voltage = self.create_display_frame('Voltage', QColor('red'))
        self.frame_current, self.label_current = self.create_display_frame('Current', QColor('blue'))
        self.frame_ucurrent, self.label_ucurrent = self.create_display_frame('Current', QColor('blue'))
        
        
        layout.addWidget(port_label)
        layout.addWidget(self.port_combo)
        layout.addWidget(baud_label)
        layout.addWidget(self.baud_combo)
        layout.addWidget(connect_button)
        layout.addWidget(self.frame_voltage)
        layout.addWidget(self.frame_current)
        layout.addWidget(self.frame_ucurrent)

        self.setLayout(layout)

        # Create a timer to read and update values from the serial port
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_serial_data)
        self.timer.start(100)  # Set the interval in milliseconds

    def get_available_ports(self):
        ports = [port.device for port in comports()]
        return ports

    def connect_to_arduino(self):
        port_name = self.port_combo.currentText()
        baud_rate = int(self.baud_combo.currentText())

        try:
            self.serial_port = serial.Serial(port_name, baud_rate)
            print(f'Connected to Arduino on {port_name} with baud rate {baud_rate}')
        except serial.SerialException as e:
            print(f'Error: {e}')

    def create_display_frame(self, label_text, color):
        frame = QFrame(self)
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        frame.setStyleSheet(f'QFrame {{ background-color: white; border: 2px solid {color.name()}; }}')
        layout = QVBoxLayout(frame)
        label = QLabel('N/A', frame)
        label.setStyleSheet(f'QLabel {{ color: {color.name()}; font-size: 20px; }}')
        layout.addWidget(label)
        return frame, label

    def read_serial_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                # Read the line from the serial port
                line = self.serial_port.readline().decode().strip()

                # Debugging statements
                print(f'Received line: {line}')

                # Check if the line starts with "Voltage:"
                if 'Values:' in line:
                # Extract the substring containing the values
                    values_str = line.split('Values:')[1].strip()

                # Split the values based on multiple spaces
                    values_list = values_str.split()

                    if len(values_list) == 3:
                    # Extract the two values
                        vin_str, mcin_str, ucin_str = values_list
                        vin = float(vin_str)
                        mcin = float(mcin_str)
                        ucin = float(ucin_str)
                        self.update_display_frame_voltage(vin, self.label_voltage)
                        self.update_display_frame_milicurrent(mcin, self.label_current)
                        self.update_display_frame_microcurrent(ucin, self.label_ucurrent)
                    else:
                        print(f'Invalid data format: {line}')
            except serial.SerialException as e:
                print(f'Error reading from serial port: {e}')

    # def update_display_frame(self, voltage, label):
    #     label.setText(f'{voltage:.2f} V')

    def update_display_frame_voltage(self, voltage, label):
        label.setText(f'{voltage:.2f} V')

    def update_display_frame_milicurrent(self, voltage, label):
        label.setText(f'{voltage:.2f} mA')
    
    def update_display_frame_microcurrent(self, voltage, label):
        label.setText(f'{voltage:.2f} uA')

    def closeEvent(self, event):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print('Serial port closed.')
        self.timer.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = ArduinoControlApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
