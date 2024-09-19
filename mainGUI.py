import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from SbmlDatabase import SbmlDatabase
from BiomodelsDownloader import BiomodelsDownloader
from visualize import GraphVisualizer

class FileUploaderApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('Untitled_design-removebg-preview.png'))
        self.setWindowTitle("BioGraph")

        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        # Create window and set co-ordinates
        window_width = int(screen_geometry.width() * 0.75)
        window_height = int(screen_geometry.height() * 0.75)
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        
        # Set window geometry
        self.setGeometry(x, y, window_width, window_height)

        self.file_count = 0
        self.setup_ui()

        # Setup database
        self.database = SbmlDatabase("localhost.ini", "biomodels", "Schemas/default_schema.json")
        self.downloader = BiomodelsDownloader(threads=5, curatedOnly=True)
        self.models = self.downloader.verifiy_models(10)
        self.database.import_models(self.models)
        self.model_ID = "" 


    def setup_ui(self):

        # Central Widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #0c120c; color: white;")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Overall Application Component setup
        app_name_label = QLabel("BioGraph")
        app_name_label.setStyleSheet("padding: 0px; font-size: 24px; font-weight: bold")
        app_icon_label = QLabel()
        app_icon_pixmap = QPixmap("Untitled_design-removebg-preview (2).png")
        app_icon_label.setPixmap(app_icon_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        
        # Top Bar Widget -> contains other widgets
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.addWidget(app_icon_label)
        top_bar_layout.addWidget(app_name_label)
        top_bar_layout.setContentsMargins(0,0,0,0)
        top_bar_layout.setStretchFactor(app_icon_label, 0)
        top_bar_layout.setStretchFactor(app_name_label, 30)
        top_bar.setStyleSheet("background-color: #0c120c; color: white; border: 0px solid black; border-radius: 1px")
        
        # Advanced Search Button
        self.dropdown_button = QPushButton("Advanced search")
        self.dropdown_button.setStyleSheet("QPushButton{ background-color: #0c120c; color: white; border-radius: 2px; padding: 10px; font-size: 12px; border-radius: 3px} QPushButton:hover{ background-color: #111c11 }")
        self.dropdown_button.clicked.connect(self.toggle_dropdown)
        top_bar_layout.addWidget(self.dropdown_button)
        top_bar_layout.setStretchFactor(self.dropdown_button, 5)

        # Schema Button
        dropdown_label = QLabel(" Schema:")
        self.schema_dropdown = QComboBox()
        self.schema_dropdown.addItems(["default_schema","attributeFactor","Simple","conversionFactor"])
        self.schema_dropdown.setStyleSheet("QPushButton{ background-color: #0c120c; color: white; border-radius: 2px; padding: 10px; font-size: 12px; border-radius: 3px} QPushButton:hover{ background-color: #111c11 }")
        self.schema_dropdown.currentTextChanged.connect(self.changeSchema)
        top_bar_layout.addWidget(dropdown_label)
        top_bar_layout.addWidget(self.schema_dropdown)
        top_bar_layout.setStretchFactor(self.schema_dropdown, 5)


        # Merge Button 
        self.merge_button = QPushButton("Merge")
        self.merge_button.setStyleSheet("QPushButton{ background-color: #0c120c; color: white; border-radius: 2px; padding: 10px; font-size: 12px; border-radius: 3px} QPushButton:hover{ background-color: #111c11 }")
        self.merge_button.clicked.connect(self.merge_dropdown)
        top_bar_layout.addWidget(self.merge_button)
        top_bar_layout.setStretchFactor(self.merge_button, 5)

        # Extra buttons -- no functionality
        buttons = ["Files", "Users", "Settings"]
        for button_text in buttons:
            button = QPushButton(button_text)
            button.setStyleSheet("QPushButton{ background-color: #0c120c; color: white; border-radius: 2px; padding: 10px; font-size: 12px; border-radius: 3px} QPushButton:hover{ background-color: #111c11 }")
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
        self.file_list.itemClicked.connect(self.toggle_file_display)
        self.file_list.setStyleSheet("QListWidget{ background-color: #0c120c; border: none}")
        left_layout.addWidget(QLabel("Uploaded Files:"))
        left_layout.addWidget(self.file_list)

        # Add other buttons to left sidebar -- no functionality
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
        # self.search_bar.setWindowIcon(QIcon("search-interface-symbol.png"))
        self.search_bar.setPlaceholderText("Search using a biomodel ID...")
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
        label = QLabel("Compound/Species")
        self.compound_input_box = QLineEdit()
        self.compound_input_box.setStyleSheet("""
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
        input_layout.addWidget(self.compound_input_box)
        dropdown_layout.addLayout(input_layout)
        
        input_layout = QVBoxLayout()
        label = QLabel("Compartment")
        self.compartment_input_box = QLineEdit()
        self.compartment_input_box.setStyleSheet("""
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
        input_layout.addWidget(self.compartment_input_box)
        dropdown_layout.addLayout(input_layout)
        
        input_layout = QVBoxLayout()
        search_button = QPushButton("Advanced Search")
        search_button.clicked.connect(self.advanced_search)
        #search_button.clicked.connect(self.toggle_widgets)
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
        input_layout.addWidget(search_button)
        dropdown_layout.addLayout(input_layout)
        
        # hiding dropdown menu
        self.dropdown_menu.setMaximumHeight(0)
        self.dropdown_menu.setMinimumHeight(0)

        # Initially hide the dropdown menu
        self.dropdown_menu.setMaximumHeight(0)
        self.dropdown_menu.setMinimumHeight(0)

        # Create merge menu
        self.merge_menu = QWidget()
        merge_layout = QHBoxLayout(self.merge_menu)
        merge_input_layout = QVBoxLayout()
        Mlabel = QLabel("Model 1")
        self.m1_input_box = QLineEdit()
        self.m1_input_box.setStyleSheet("""
        QLineEdit { 
            padding: 5px 5px; 
            font-size: 10px; 
            border-radius: 5px; 
            background-color: #111c11; 
            color: white}
        
        QLineEdit:hover{
            background-color: #132413}
            """)
        
        merge_input_layout.addWidget(Mlabel)
        merge_input_layout.addWidget(self.m1_input_box)
        merge_layout.addLayout(merge_input_layout)
        
        merge_input_layout = QVBoxLayout()
        Mlabel = QLabel("Model 2")
        self.m2_input_box = QLineEdit()
        self.m2_input_box.setStyleSheet("""
        QLineEdit { 
            padding: 5px 5px; 
            font-size: 10px; 
            border-radius: 5px; 
            background-color: #111c11; 
            color: white}
        
        QLineEdit:hover{
            background-color: #132413}
            """)
        
        merge_input_layout.addWidget(Mlabel)
        merge_input_layout.addWidget(self.m2_input_box)
        merge_layout.addLayout(merge_input_layout)
        
        merge_input_layout = QVBoxLayout()
        merge_button = QPushButton("Merge models")
        merge_button.clicked.connect(self.merge_models)
        
        merge_button.setStyleSheet("""
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

        # Add merge button to layout
        merge_input_layout.addWidget(merge_button)
        merge_layout.addLayout(merge_input_layout)
        
        # Hide merge dropdown menu
        self.merge_menu.setMaximumHeight(0)
        self.merge_menu.setMinimumHeight(0)

        # Initially hide the merge menu
        self.merge_menu.setMaximumHeight(0)
        self.merge_menu.setMinimumHeight(0)

        # Create file display widget for merge menu - result
        self.file_display = QWidget()
        self.file_display.setFixedHeight(70)
        self.file_display_layout = QHBoxLayout(self.file_display)
        self.file_name_label = QLabel()
        self.file_name_label.setStyleSheet("""
            QLabel {
                background-color: #111c11;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
                border-radius: 5px;
                border: none 
                                           
            }
        """)
        self.file_display.setStyleSheet("""
            QWidget {
                background-color: #111c11;
                border-radius: 5px;
                margin: 0px;
                border: 1px solid;
                border-color: #1a301a;
            }
        """)
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
        
        button2 = QPushButton("Find similar models")
            #button.setFont(QFont("Arial",20))
        button2.setStyleSheet("""
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
        #button.clicked.connect(self.set_id())
        button.clicked.connect(lambda: self.veiwGraph(self.model_ID))
        button2.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button2.clicked.connect(self.toggle_widgets)
       
        if self.file_name_label == "Model does not exist":
            self.file_display_layout.addWidget(self.file_name_label)
            self.file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.file_display_layout.addWidget(self.file_name_label)
            self.file_display_layout.addWidget(button2)
            self.file_display_layout.addWidget(button)

        self.file_display.hide()


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

        # Add widgets to right layout
        right_layout.addWidget(self.dropdown_menu)
        right_layout.addWidget(self.merge_menu)
        right_layout.addWidget(self.file_display)
        right_layout.addWidget(self.content_area)
        right_layout.setStretchFactor(search_widget, 0)
        right_layout.setStretchFactor(main_window, 100)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0,0,0,0)
        content_layout.addWidget(right_content)

        # Set initial visibility to False
        self.dropdown_visible = False
        self.merge_visible = False
        self.widgets_visible = False
        self.adv_widgets_visible = False
        self.current_file = None

        # Set up animation
        self.animation = QPropertyAnimation(self.dropdown_menu, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Set up merge animation
        self.merge_animation = QPropertyAnimation(self.merge_menu, b"maximumHeight")
        self.merge_animation.setDuration(300)
        self.merge_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def changeSchema(self, text):
        """Change database Schema"""
        self.database.change_schema("Schemas/" + text + ".json")

    def upload_files(self):
        """Add file to database"""

        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Upload", "", "XML Files (*.xml)")

        for file_path in files:
            file_name = file_path.split("/")[-1] # Strip folder 
            self.database.load_and_import_model(file_name[:-4]) # Strip file extension and import to database
            QMessageBox.information(self, "Success", f"{file_name} has been successfully uploaded to the database.")
            self.file_list.addItem(file_name)
            self.file_count += 1
        

    def advanced_search(self):
        """Depending on input provided, query model and return matches"""

        self.clear_widgets()
        compound = self.compound_input_box.text()
        compartment = self.compartment_input_box.text()

        # No input
        if compound == "" and compartment == "":
            return

        # Only search for compund
        if compartment == "":
            models = self.database.search_for_compound(compound)

        # Only search for compartment
        elif compound == "":
            models = self.database.search_for_compartment(compartment)

        # Search for compund in compartment
        else:
            models = self.database.search_compound_in_compartment(compound=compound, compartment=compartment)
        
        if models is None:
            models = ["NO MATCHING MODELS"]
        
        # Display result
        self.toggle_advanced_search(models) 


    def toggle_advanced_search(self, models):
        """Displat a list of models in a dropdown menu"""

        if self.adv_widgets_visible:
            self.clear_widgets()
            
        else:
            self.advanced_search_add_widgets(models)
            
        self.adv_widgets_visible = not self.adv_widgets_visible


    def advanced_search_add_widgets(self, models):
        for model in models:
            widget = QWidget()
            widget.setFixedHeight(70)  # Set only the height to be fixed
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            label = QLabel(model)
            
            widget.setStyleSheet("""
                QWidget {
                    background-color: #111c11;
                    border-radius: 5px;
                    margin: 2px;
                    padding: 5px;
                }
            """)

            layout = QHBoxLayout(widget)
            layout.addWidget(label)
            layout.addWidget(QWidget())  # Spacer
            layout.addWidget(QWidget())  # Spacer
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
            #button.clicked.connect(lambda: self.veiwGraph(pair[0]))
            button.clicked.connect(lambda checked, x = model:self.veiwGraph(x))

            layout.addWidget(button)
            self.content_layout.addWidget(widget)


    def perform_search(self):
        """Lookup if a model exists in a database"""

        search_term = self.search_bar.text()
        print(f"Searching for: {search_term}")
        self.clear_widgets()

        self.model_ID = search_term

        # Implement your search logic here
        if self.database.check_model_exists(search_term):
            self.show_search(search_term)
        else:
            self.show_search("Model does not exist")


    def merge_dropdown(self):
        """Dropdown menu for merge button"""

        #self.clear_widgets()
        if self.dropdown_visible: self.toggle_dropdown()

        # Animation and Visibility options 
        if self.merge_visible:
            self.merge_animation.setStartValue(self.merge_menu.height())
            self.merge_animation.setEndValue(0)
        else:
            self.merge_animation.setStartValue(0)
            self.merge_animation.setEndValue(100)
        
        self.merge_animation.start()
        self.merge_visible = not self.merge_visible


    def merge_models(self):
        """Query database to merge two models"""

        self.clear_widgets()

        model1 = self.m1_input_box.text()
        model2 = self.m2_input_box.text()

        # No input
        if model1 == "" or model2 == "":
            return

        newmodel = self.database.merge_biomodels(model_id1=model1, model_id2=model2)
        print(newmodel)
        self.merge_widget(newmodel)


    def merge_widget(self, model):
        """Setup merge button and its dropdown menu"""
        
        widget = QWidget()
        widget.setFixedHeight(70)  # Set only the height to be fixed
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        label = QLabel(model)
        
        widget.setStyleSheet("""
            QWidget {
                background-color: #111c11;
                border-radius: 5px;
                margin: 2px;
                padding: 5px;
            }
        """)

        layout = QHBoxLayout(widget)
        layout.addWidget(label)
        layout.addWidget(QWidget())  # Spacer
        layout.addWidget(QWidget())  # Spacer
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
        button.clicked.connect(lambda checked, x = model:self.veiwGraph(x))

        layout.addWidget(button)
        self.content_layout.addWidget(widget)


    def toggle_dropdown(self):
        """Switch a dropdown menu on or off and animate it"""

        #self.clear_widgets()
        if self.merge_visible: self.merge_dropdown()

        if self.dropdown_visible:
            self.animation.setStartValue(self.dropdown_menu.height())
            self.animation.setEndValue(0)
        else:
            self.animation.setStartValue(0)
            self.animation.setEndValue(100)
        
        self.animation.start()
        self.dropdown_visible = not self.dropdown_visible

    def toggle_widgets(self):
        """Set widget visible or invisible"""

        if self.widgets_visible:
            self.clear_widgets()
            self.add_widgets()
        else:
            self.add_widgets()
            
        self.widgets_visible = not self.widgets_visible


    def add_widgets(self):
        """Create a widget, if a model needs to listed"""
        similar_models = self.database.find_all_similar(self.model_ID, 10)

        for pair in similar_models:
            widget = QWidget()
            widget.setFixedHeight(70) 
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            label = QLabel(pair[0])
            simLabel = QLabel("similarity match:")
            perWidget = QWidget()
            perLabel = QLabel(f"{pair[1]}%")

            if (pair[1] >= 80):
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
            elif (60 <= pair[1] < 80):
                perWidget.setStyleSheet("""
                QWidget {
                    background-color: #111c11;
                    color: yellow;
                    font-size: 20px;
                    border-radius: 5px;
                    margin: 0px;
                    font-weight: bold;}
             """)
                
            elif (30 <= pair[1] <= 60):
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
                    padding: 5px;
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
            #button.clicked.connect(lambda: self.veiwGraph(pair[0]))
            button.clicked.connect(lambda checked, x = pair[0]:self.veiwGraph(x))

            layout.addWidget(button)
            self.content_layout.addWidget(widget)


    def clear_widgets(self):
        """Set visibility of all widgets to None"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


    def show_search(self, file_name):
        """Show search results for a file in the database"""
        self.file_name_label.setText(file_name)
        self.file_display.show()


    def toggle_file_display(self, item):
        """Turn File display on or off"""

        file_name = os.path.splitext(item.text())[0]  # Remove file extension
        
        if self.current_file == file_name:
            self.file_display.hide()
            self.clear_widgets()
            self.current_file = None
        else:
            self.file_name_label.setText(file_name)
            self.model_ID = file_name
            self.file_display.show()
            self.clear_widgets()
            self.current_file = file_name

    def veiwGraph(self, text):
        """Launch a matplotlib plot visualizing a graph"""
        visualiser = GraphVisualizer()
        visualiser.visualize(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileUploaderApp()
    window.show()
    sys.exit(app.exec())