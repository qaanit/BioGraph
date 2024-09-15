import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class FileUploaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('Untitled_design-removebg-preview.png'))
        self.setWindowTitle("BioGraph")
        #self.setGeometry(100, 100, 1200, 800)

        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        window_width = int(screen_geometry.width() * 0.75)
        window_height = int(screen_geometry.height() * 0.75)
        
        # Calculate position
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        # Set window geometry
        self.setGeometry(x, y, window_width, window_height)

        self.file_count = 0
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #0c120c; color: white;")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top bar with title
        top_bar = QWidget()
        
        top_bar_layout = QHBoxLayout(top_bar)
        app_name_label = QLabel("BioGraph")
        app_name_label.setStyleSheet("padding: 0px; font-size: 24px; font-weight: bold")
        app_icon_label = QLabel()
        app_icon_pixmap = QPixmap("Untitled_design-removebg-preview (2).png")
        app_icon_label.setPixmap(app_icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        top_bar_layout.addWidget(app_icon_label)

        top_bar_layout.addWidget(app_name_label)
        top_bar_layout.setContentsMargins(0,0,0,0)
        top_bar_layout.setStretchFactor(app_icon_label, 0)
        top_bar_layout.setStretchFactor(app_name_label, 30)
        top_bar.setStyleSheet("background-color: #0c120c; color: white; border: 0px solid black; border-radius: 1px")
        
        self.dropdown_button = QPushButton("Advanced search")
        self.dropdown_button.setStyleSheet("QPushButton{ background-color: #0c120c; color: white; border-radius: 2px; padding: 5px; font-size: 12px; border-radius: 3px} QPushButton:hover{ background-color: #111c11 }")
        self.dropdown_button.clicked.connect(self.toggle_dropdown)
        top_bar_layout.addWidget(self.dropdown_button)

        buttons = ["Analytics", "Files", "Users", "Settings"]
        for button_text in buttons:
            button = QPushButton(button_text)
            button.setStyleSheet("QPushButton{ background-color: #0c120c; color: white; border-radius: 2px; padding: 5px; font-size: 12px; border-radius: 3px} QPushButton:hover{ background-color: #111c11 }")
            top_bar_layout.addWidget(button)
            top_bar_layout.setStretchFactor(button, 5)
        main_layout.addWidget(top_bar)

        # Main content area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        main_layout.addWidget(content_widget)

        # Left sidebar
        left_sidebar = QWidget()
        left_layout = QVBoxLayout(left_sidebar)
        left_layout.setContentsMargins(0,0,0,0)
        left_sidebar.setFixedWidth(250)

        # Upload button at the top of the left sidebar
        upload_button = QPushButton("  Upload Files")
        upload_button.clicked.connect(self.upload_files)
        upload_button.setIcon(QIcon("plus.png"))
        upload_button.setStyleSheet("""
            QPushButton {
                background-color: #266324;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        left_layout.addWidget(upload_button)

        # File list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.display_file_name)
        self.file_list.setStyleSheet("QListWidget{ background-color: #0c120c; border: none}")
        left_layout.addWidget(QLabel("Uploaded Files:"))
        left_layout.addWidget(self.file_list)

        # Add other buttons to left sidebar
        '''
        buttons = ["Dashboard", "Analytics", "Files", "Users", "Settings"]
        for button_text in buttons:
            button = QPushButton(button_text)
            button.setStyleSheet("QPushButton{ background-color: #111c11; color: white; border-radius: 2px; padding: 5px}")
            left_layout.addWidget(button)
        '''

        content_layout.addWidget(left_sidebar)

        # Right main content
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)

        # Search bar spanning the entire width of the main window
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        self.search_bar = QLineEdit()
        self.search_bar.setWindowIcon(QIcon("search-interface-symbol.png"))
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setStyleSheet("""
            QLineEdit { 
                padding: 10px 10px; 
                font-size: 16px; 
                border-radius: 5px; 
                background-color: #111c11; 
                color: white}
            
            QLineEdit:hover{
                background-color: #132413}
                """)
        search_layout.addWidget(self.search_bar)
        
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.perform_search)
        search_button.clicked.connect(self.toggle_widgets)
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #1a301a;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #213d20;
            }
        """)
        search_layout.addWidget(search_button)
        search_layout.setContentsMargins(0,0,0,6)
        right_layout.addWidget(search_widget)

        # Create dropdown menu
        self.dropdown_menu = QWidget()
        dropdown_layout = QHBoxLayout(self.dropdown_menu)
        
        input_layout = QVBoxLayout()
        label = QLabel("Node")
        input_box = QLineEdit()
        input_box.setStyleSheet("""
        QLineEdit { 
            padding: 5px 5px; 
            font-size: 10px; 
            border-radius: 5px; 
            background-color: #111c11; 
            color: white}
        
        QLineEdit:hover{
            background-color: #132413}
            """)
        input_layout.addWidget(label)
        input_layout.addWidget(input_box)
        dropdown_layout.addLayout(input_layout)
        
        input_layout = QVBoxLayout()
        label = QLabel("Edge")
        input_box = QLineEdit()
        input_box.setStyleSheet("""
        QLineEdit { 
            padding: 5px 5px; 
            font-size: 10px; 
            border-radius: 5px; 
            background-color: #111c11; 
            color: white}
        
        QLineEdit:hover{
            background-color: #132413}
            """)
        input_layout.addWidget(label)
        input_layout.addWidget(input_box)
        dropdown_layout.addLayout(input_layout)
        
        input_layout = QVBoxLayout()
        label = QLabel("Property")
        input_box = QLineEdit()
        input_box.setStyleSheet("""
        QLineEdit { 
            padding: 5px 5px; 
            font-size: 10px; 
            border-radius: 5px; 
            background-color: #111c11; 
            color: white}
        
        QLineEdit:hover{
            background-color: #132413}
            """)
        input_layout.addWidget(label)
        input_layout.addWidget(input_box)
        dropdown_layout.addLayout(input_layout)
        
        self.dropdown_menu.setMaximumHeight(0)
        self.dropdown_menu.setMinimumHeight(0)
        
        # Create main content area
        self.content_area = QScrollArea()
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        #self.content_layout = QVBoxLayout(self.content_widget)
        self.content_area.setWidgetResizable(True)
        self.content_area.setWidget(self.content_widget)

        # style main area
        self.content_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0c120c;
            }
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 5px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #111c11;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: pink;
            }
        """)
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: #0c120c;
            }
        """)

        # Main window content
        main_window = QFrame()
        main_window.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        main_window_layout = QVBoxLayout(main_window)

        # File counter
        self.file_counter_label = QLabel("Upload or search for a biological model to view it's graph")
        self.file_counter_label.setStyleSheet("font-size: 10px; color: grey;")
        self.file_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_window_layout.addWidget(self.file_counter_label, alignment=Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(self.dropdown_menu)
        right_layout.addWidget(self.content_area)
        right_layout.setStretchFactor(search_widget, 0)
        right_layout.setStretchFactor(main_window, 100)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0,0,0,0)
        content_layout.addWidget(right_content)

        self.dropdown_visible = False
        self.widgets_visible = False

        # Set up animation
        self.animation = QPropertyAnimation(self.dropdown_menu, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def upload_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Upload")
        for file_path in files:
            file_name = file_path.split("/")[-1]
            self.file_list.addItem(file_name)
            self.file_count += 1
        #self.file_counter_label.setText(f"Files Uploaded: {self.file_count}")

    def perform_search(self):
        search_term = self.search_bar.text()
        print(f"Searching for: {search_term}")
        # Implement your search logic here

    def toggle_dropdown(self):
        if self.dropdown_visible:
            self.animation.setStartValue(self.dropdown_menu.height())
            self.animation.setEndValue(0)
        else:
            self.animation.setStartValue(0)
            self.animation.setEndValue(100)
        
        self.animation.start()
        self.dropdown_visible = not self.dropdown_visible

    def toggle_widgets(self):
        if self.widgets_visible:
            self.clear_widgets()
        else:
            self.add_widgets()
        self.widgets_visible = not self.widgets_visible

    def add_widgets(self):
        for i in range(4):
            widget = QWidget()
            widget.setFixedHeight(70)  # Set only the height to be fixed
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            label = QLabel(f"BIOMD000000{i+1}")
            simLabel = QLabel("similarity match:")
            perWidget = QWidget()
            perLabel = QLabel(f"{(100-i*10) + i}%")
            
            if ((100-i*10) >= 90):
                perWidget.setStyleSheet("""
                QWidget {
                    background-color: #111c11;
                    color: green;
                    font-size: 20px;
                    border-radius: 5px;
                    margin: 0px;
                    padding: 0px 0px;
                    font-weight: bold;}
             """)
            elif (70 <= (100-i*10) < 90):
                perWidget.setStyleSheet("""
                QWidget {
                    background-color: #111c11;
                    color: yellow;
                    font-size: 20px;
                    border-radius: 5px;
                    margin: 0px;
                    font-weight: bold;}
             """)
                
            elif (50 <= (100-i*10) <= 70):
                perWidget.setStyleSheet("""
                QWidget {
                    background-color: #111c11;
                    color: orange;
                    font-size: 20px;
                    border-radius: 5px;
                    margin: 0px;
                    font-weight: bold;}
             """)
                
            else:
                perWidget.setStyleSheet("""
                QWidget {
                    background-color: #111c11;
                    color: red;
                    font-size: 20px;
                    border-radius: 5px;
                    margin: 0px;
                    font-weight: bold;}
             """)

            widget.setStyleSheet("""
                QWidget {
                    background-color: #111c11;
                    border-radius: 5px;
                    margin: 2px;
                }
            """)
            perLayout = QHBoxLayout(perWidget)
            perLayout.addWidget(perLabel)
            layout = QHBoxLayout(widget)
            layout.addWidget(label)
            layout.addWidget(QWidget())  # Spacer
            layout.addWidget(QWidget())  # Spacer
            layout.addWidget(simLabel)
            layout.addWidget(perWidget)
            button = QPushButton("View graph in browser")
            #button.setFont(QFont("Arial",20))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #1a301a;
                    padding: 10px 10px;
                    color: white;
                    font-size: 10px;
                    border: none;
                }
                                 
                QPushButton:hover {
                background-color: #213d20;
                }
                                 """)
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            layout.addWidget(button)
            self.content_layout.addWidget(widget)

    def clear_widgets(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def display_file_name(self, item):
        file_name = os.path.splitext(item.text())[0]  # Remove file extension
        self.clear_widgets()
        label = QLabel(file_name)
        widget = QWidget()
        widget.setFixedHeight(70)  # Set only the height to be fixed
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        widget.setStyleSheet("""
                QWidget {
                    background-color: #111c11;
                    border-radius: 5px;
                    margin: 2px;
                }
            """)
        #label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: white;
                
            }
        """)
        layout = QHBoxLayout(widget)
        layout.addWidget(label)
        button = QPushButton("View graph in browser")
            #button.setFont(QFont("Arial",20))
        button.setStyleSheet("""
            QPushButton {
                background-color: #1a301a;
                padding: 10px 10px;
                color: white;
                font-size: 10px;
                border: none;
            }
                                
            QPushButton:hover {
            background-color: #213d20;
            }
                                """)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(button)
        self.content_layout.addWidget(widget)
'''
class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle('Loading')
        #self.setFixedSize(300, 100)
        #layout = QVBoxLayout()

        self.setWindowIcon(QIcon('Untitled_design-removebg-preview.png'))
        self.setWindowTitle("BioGraph")
        #self.setGeometry(100, 100, 1200, 800)

        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        window_width = int(screen_geometry.width() * 0.75)
        window_height = int(screen_geometry.height() * 0.75)
        
        # Calculate position
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        # Set window geometry
        self.setGeometry(x, y, window_width, window_height)
        
        self.setStyleSheet("background-color: #0c120c; color: white;")

        layout = QHBoxLayout()
        left = QWidget()
        left_layout = QHBoxLayout(left)
        layout.addWidget(left)

        centre = QWidget()
        centre.setStyleSheet("background-color: blue")
        centre_layout = QHBoxLayout(centre)
        label = QLabel("hello world")
        centre_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar()
        centre_layout.addWidget(self.progress)
        layout.addWidget(centre)

        right = QWidget()
        layout.addWidget(right)

        self.setLayout(layout)

        self.progress_value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)  # Update every 50ms

    def update_progress(self):
        self.progress_value += 1
        self.progress.setValue(self.progress_value)
        if self.progress_value >= 100:
            self.timer.stop()
            self.close()
            self.home_screen = FileUploaderApp()
            self.home_screen.show()
'''
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileUploaderApp()
    #window = LoadingScreen()
    window.show()
    sys.exit(app.exec())