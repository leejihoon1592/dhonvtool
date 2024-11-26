# Import required libraries
import tkinter as tk
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QPushButton, QColorDialog, QSlider, QLabel, QCheckBox
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt
import win32gui
import win32con
import math

# Global settings
selected_rect = None
overlay = None
aim_color = QColor(0, 0, 255, 255)  # Default blue
point_color = QColor(0, 255, 0, 255)  # Default green
point_opacity = 255
aim_opacity = 255
point_visibility = [True] * 12  # Default: All points visible
point_size = 5  # Default point size
aim_length = 20  # Default aim length
aim_thickness = 2  # Default aim thickness


# Function to get window rect
def get_window_rect(hwnd):
    try:
        return win32gui.GetWindowRect(hwnd)
    except Exception as e:
        print(f"Error getting window rect: {e}")
        return None


# PyQt6 overlay window class
class PyQtOverlayWithAim(QMainWindow):
    def __init__(self, rect):
        super().__init__()
        self.setGeometry(*rect)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Make window transparent for clicks
        self.make_window_click_through()

    def make_window_click_through(self):
        hwnd = self.winId().__int__()  # Get the native window handle
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw red border
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(5)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        # Draw central crosshair
        crosshair_pen = QPen(aim_color)
        crosshair_pen.setWidth(aim_thickness)
        painter.setPen(crosshair_pen)
        center_x = self.width() // 2
        center_y = self.height() // 2
        painter.drawLine(center_x - aim_length, center_y, center_x + aim_length, center_y)  # Horizontal line
        painter.drawLine(center_x, center_y - aim_length, center_x, center_y + aim_length)  # Vertical line

        # Draw 12 points in clock positions
        circle_radius = 100
        angles = [60, 30, 0, 330, 300, 270, 240, 210, 180, 150, 120, 90]  # Angles for each clock position
        for i, angle in enumerate(angles):
            if not point_visibility[i]:
                continue
            radian_angle = math.radians(angle)
            point_x = center_x + int(circle_radius * math.cos(radian_angle))
            point_y = center_y - int(circle_radius * math.sin(radian_angle))
            point_color_with_opacity = point_color
            point_color_with_opacity.setAlpha(point_opacity)
            painter.setBrush(point_color_with_opacity)
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawEllipse(point_x - point_size, point_y - point_size, point_size * 2, point_size * 2)


# Main settings dialog
def open_settings(app, red_border):
    settings = QDialog()
    settings.setWindowTitle("설정")
    settings.setFixedSize(300, 250)

    layout = QVBoxLayout(settings)
    layout.setSpacing(5)  # Reduced spacing

    # Aim settings button
    aim_button = QPushButton("에임 설정", settings)
    aim_button.clicked.connect(lambda: open_aim_settings(app, red_border))
    layout.addWidget(aim_button)

    # Point settings button
    point_button = QPushButton("점 설정", settings)
    point_button.clicked.connect(lambda: open_point_settings(app, red_border))
    layout.addWidget(point_button)

    # Point arrangement button
    point_arrangement_button = QPushButton("점 배치", settings)
    point_arrangement_button.clicked.connect(lambda: open_point_arrangement(app, red_border))
    layout.addWidget(point_arrangement_button)

    settings.setLayout(layout)
    settings.exec()


# Aim settings dialog
def open_aim_settings(app, red_border):
    settings = QDialog()
    settings.setWindowTitle("에임 설정")
    settings.setFixedSize(300, 300)

    layout = QVBoxLayout(settings)
    layout.setSpacing(5)

    # Aim color button
    aim_color_button = QPushButton("에임 색상 변경", settings)
    aim_color_button.clicked.connect(lambda: change_aim_color(settings, red_border))
    layout.addWidget(aim_color_button)

    # Aim length slider
    aim_length_slider = QSlider(Qt.Orientation.Horizontal, settings)
    aim_length_slider.setRange(5, 100)
    aim_length_slider.setValue(aim_length)
    aim_length_slider.valueChanged.connect(lambda value: change_aim_length(value, red_border))
    layout.addWidget(QLabel("에임 길이 조정"))
    layout.addWidget(aim_length_slider)

    # Aim thickness slider
    aim_thickness_slider = QSlider(Qt.Orientation.Horizontal, settings)
    aim_thickness_slider.setRange(1, 10)
    aim_thickness_slider.setValue(aim_thickness)
    aim_thickness_slider.valueChanged.connect(lambda value: change_aim_thickness(value, red_border))
    layout.addWidget(QLabel("에임 두께 조정"))
    layout.addWidget(aim_thickness_slider)

    # Aim opacity slider
    aim_opacity_slider = QSlider(Qt.Orientation.Horizontal, settings)
    aim_opacity_slider.setRange(0, 255)
    aim_opacity_slider.setValue(aim_opacity)
    aim_opacity_slider.valueChanged.connect(lambda value: change_aim_opacity(value, red_border))
    layout.addWidget(QLabel("에임 투명도 조정"))
    layout.addWidget(aim_opacity_slider)

    settings.setLayout(layout)
    settings.exec()


# Point settings dialog
def open_point_settings(app, red_border):
    settings = QDialog()
    settings.setWindowTitle("점 설정")
    settings.setFixedSize(300, 300)

    layout = QVBoxLayout(settings)
    layout.setSpacing(5)

    # Point color button
    point_color_button = QPushButton("점 색상 변경", settings)
    point_color_button.clicked.connect(lambda: change_point_color(settings, red_border))
    layout.addWidget(point_color_button)

    # Point size slider
    point_size_slider = QSlider(Qt.Orientation.Horizontal, settings)
    point_size_slider.setRange(1, 20)
    point_size_slider.setValue(point_size)
    point_size_slider.valueChanged.connect(lambda value: change_point_size(value, red_border))
    layout.addWidget(QLabel("점 크기 조정"))
    layout.addWidget(point_size_slider)

    # Point opacity slider
    point_opacity_slider = QSlider(Qt.Orientation.Horizontal, settings)
    point_opacity_slider.setRange(0, 255)
    point_opacity_slider.setValue(point_opacity)
    point_opacity_slider.valueChanged.connect(lambda value: change_point_opacity(value, red_border))
    layout.addWidget(QLabel("점 투명도 조정"))
    layout.addWidget(point_opacity_slider)

    settings.setLayout(layout)
    settings.exec()


# Point arrangement dialog
def open_point_arrangement(app, red_border):
    settings = QDialog()
    settings.setWindowTitle("점 배치")
    settings.setFixedSize(400, 400)

    layout = QVBoxLayout(settings)
    layout.setSpacing(5)
    layout.addWidget(QLabel("점 배치 설정"))

    for i in range(12):
        checkbox = QCheckBox(f"{i + 1}시 점 표시", settings)
        checkbox.setChecked(point_visibility[i])
        checkbox.toggled.connect(lambda state, index=i: toggle_point_visibility(index, state, red_border))
        layout.addWidget(checkbox)

    settings.setLayout(layout)
    settings.exec()


# Functions for updating values
def change_aim_length(value, red_border):
    global aim_length
    aim_length = value
    red_border.update()


def change_aim_thickness(value, red_border):
    global aim_thickness
    aim_thickness = value
    red_border.update()


def change_point_size(value, red_border):
    global point_size
    point_size = value
    red_border.update()


# Functions for updating colors
def change_aim_color(settings, red_border):
    global aim_color
    color = QColorDialog.getColor(aim_color, settings, "에임 색상 선택")
    if color.isValid():
        aim_color = color
        red_border.update()


def change_point_color(settings, red_border):
    global point_color
    color = QColorDialog.getColor(point_color, settings, "점 색상 선택")
    if color.isValid():
        point_color = color
        red_border.update()


# Functions for updating opacity
def change_aim_opacity(value, red_border):
    global aim_opacity
    aim_color.setAlpha(value)
    red_border.update()


def change_point_opacity(value, red_border):
    global point_opacity
    point_opacity = value
    red_border.update()


# Toggle point visibility
def toggle_point_visibility(index, state, red_border):
    global point_visibility
    point_visibility[index] = state
    red_border.update()


# Main function for drawing window border
def draw_window_border():
    global selected_rect, overlay

    overlay = tk.Tk()
    overlay.attributes('-topmost', True)
    overlay.overrideredirect(True)

    canvas = tk.Canvas(overlay, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    hover_hwnd = None
    update_running = True

def draw_window_border():
    global selected_rect, overlay

    overlay = tk.Tk()
    overlay.attributes('-topmost', True)
    overlay.overrideredirect(True)

    canvas = tk.Canvas(overlay, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    hover_hwnd = None  # hover_hwnd 변수 선언
    update_running = True

    def update_hover():
        nonlocal hover_hwnd  # 상위 함수인 draw_window_border의 hover_hwnd 참조
        try:
            if not update_running or not overlay.winfo_exists():
                return  # 윈도우가 존재하지 않으면 종료

            x, y = overlay.winfo_pointerxy()
            hwnd = win32gui.WindowFromPoint((x, y))
            if hwnd != hover_hwnd:
                hover_hwnd = hwnd
                rect = get_window_rect(hwnd)
                if rect:
                    left, top, right, bottom = rect
                    overlay.geometry(f"{right - left}x{bottom - top}+{left}+{top}")
                    canvas.delete('all')
                    canvas.create_rectangle(0, 0, right - left, bottom - top, outline="blue", width=3)

            if update_running:  # 윈도우가 존재하는 동안만 반복 호출
                overlay.after(50, update_hover)
        except Exception as e:
            print(f"Error in update_hover: {e}")  # 예외를 잡아서 무시

    def on_click(event):
        nonlocal hover_hwnd, update_running
        update_running = False
        if hover_hwnd:
            rect = get_window_rect(hover_hwnd)
            if rect:
                global selected_rect
                selected_rect = rect
        overlay.destroy()
        create_red_border_with_buttons(selected_rect)

    overlay.bind("<Button-1>", on_click)
    update_hover()
    overlay.mainloop()



def create_red_border_with_buttons(rect):
    global overlay

    if rect:
        app = QApplication([])
        left, top, right, bottom = rect
        red_border = PyQtOverlayWithAim((left, top, right - left, bottom - top))
        red_border.show()

        control_window = tk.Tk()
        control_window.geometry(f"200x100+{right + 10}+{top}")
        control_window.title("Control Panel")

        tk.Button(control_window, text="재선택", command=lambda: restart_selection(control_window, red_border)).pack(pady=10)
        tk.Button(control_window, text="설정", command=lambda: open_settings(app, red_border)).pack(pady=10)

        control_window.mainloop()


def restart_selection(control_window, red_border):
    control_window.destroy()
    red_border.close()
    draw_window_border()


# Entry point
if __name__ == "__main__":
    draw_window_border()
