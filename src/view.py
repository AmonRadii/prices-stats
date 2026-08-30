import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QFormLayout, 
    QMessageBox, QGroupBox, QFileDialog, QDialogButtonBox
)

from model import PriceModel
from navigator import KeyboardNavigator
from exporter import ExcelExporter


class PriceAnalyzerApp(QMainWindow):
    """Application GUI."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("prices-stats")
        self.setMinimumSize(400, 500)

        self.model = PriceModel()
        
        self.init_ui()
        self.setup_navigation()


    def init_ui(self):
        """
        Constructs and arranges the user interface components.
        Sets up the central widget with a vertical layout and initializes four main UI sections:
        1. An input form group for entering product names and prices.
        2. A list widget for displaying added items.
        3. Control buttons for deleting selected items or clearing the list.
        4. A statistics panel for displaying calculated price metrics.
        """ 
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. Input
        input_group = QGroupBox("Product Addition")
        input_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g: Laptop")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("e.g: 2000.50")
        self.add_btn = QPushButton("Add product")
        self.add_btn.clicked.connect(self.add_item)

        input_layout.addRow("Name:", self.name_input)
        input_layout.addRow("Price:", self.price_input)
        input_layout.addRow(self.add_btn)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # 2. List
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        # 3. Control buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_to_excel)
        self.delete_btn = QPushButton("Delete selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.clear_btn = QPushButton("Clean all")
        self.clear_btn.clicked.connect(self.clear_all)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.clear_btn)
        main_layout.addLayout(btn_layout)

        # 4. Statistics
        stats_group = QGroupBox("Price Analysis")
        stats_layout = QFormLayout()
        self.min_label = QLabel("—")
        self.max_label = QLabel("—")
        self.median_label = QLabel("—")

        stats_layout.addRow("Minimum Price:", self.min_label)
        stats_layout.addRow("Maximum Price:", self.max_label)
        stats_layout.addRow("Median Price:", self.median_label)
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)


    def setup_navigation(self):
        """Keyboard navigation logic config."""
        
        # 1. Focus order when pressing "Tab"
        self.setTabOrder(self.name_input, self.price_input)
        self.setTabOrder(self.price_input, self.add_btn)
        self.setTabOrder(self.add_btn, self.list_widget)
        self.setTabOrder(self.list_widget, self.save_btn)
        self.setTabOrder(self.save_btn, self.delete_btn)
        self.setTabOrder(self.delete_btn, self.clear_btn)    
        self.setTabOrder(self.clear_btn, self.name_input)

        # 2. "Enter" button logic
        # When the name input field has focus, the focus shifts to the price input field.
        # If the price input field has focus, the product is added to the list.
        # If one of the interactive buttons has focus, its function is executed
        self.name_input.returnPressed.connect(lambda: self.price_input.setFocus(Qt.FocusReason.TabFocusReason))
        self.price_input.returnPressed.connect(self.add_item)

        # Global Shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self.list_widget).activated.connect(self.delete_selected)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_to_excel)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(self.close)

        # Navigator initialization
        self.navigator = KeyboardNavigator({
            'name': self.name_input,
            'price': self.price_input,
            'add': self.add_btn,
            'list': self.list_widget,
            'save': self.save_btn,
            'delete': self.delete_btn,
            'clear': self.clear_btn
        }, parent=self)

        for widget in self.navigator.w.values():
            widget.installEventFilter(self.navigator)

        self.name_input.setFocus(Qt.FocusReason.TabFocusReason)

    # --- UI event handlers ---

    def closeEvent(self, event):
        """
        Handles the window close event and prompts the user for confirmation.
        Displays a custom confirmation dialog when the user attempts to close 
        the window (e.g., via the Escape key or window controls). Prompts whether 
        to save data, discard changes, or cancel the exit action.

        Args:
            event (QCloseEvent): The Qt close event object.

        Returns:
            None
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Exit")
        msg_box.setText("Do you want to save changes before exiting?")

        save_btn = msg_box.addButton("Save", QMessageBox.ButtonRole.ActionRole)
        discard_btn = msg_box.addButton("Exit without saving", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        msg_box.setDefaultButton(save_btn)
        msg_box.exec()

        clicked = msg_box.clickedButton()

        if clicked == save_btn:
            if self.save_to_excel():
                event.accept()
            else:
                event.ignore()
        elif clicked == discard_btn:
            event.accept()
        else:
            event.ignore()


    def add_item(self):
        """
        Validates user input and appends a new product entry to the collection.

        Extracts and sanitizes text from the name and price input fields. 
        Normalizes decimal comma separators to dots and falls back to a default 
        name if none is provided. Performs input validation to ensure the price 
        is a non-empty, non-negative floating-point number, displaying warning 
        dialogs if validation fails.

        Upon successful validation:
        1. Stores the item tuple (name, price) in the internal items list.
        2. Adds a formatted entry to the UI list widget.
        3. Clears both input fields.
        4. Triggers an update of the statistical metrics.
        """
        name = self.name_input.text().strip() or "Unnamed product"
        price_str = self.price_input.text().strip().replace(',', '.')

        if not price_str:
            QMessageBox.warning(self, "Error", "Enter the product price.")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "The price must be a non-negative number.")
            return

        self.model.add_item(name, price)
        self.list_widget.addItem(f"{name} — {price:.2f}")
        self.name_input.clear()
        self.price_input.clear()
        self.name_input.setFocus(Qt.FocusReason.TabFocusReason)
        
        self.update_stats_ui()


    def delete_selected(self):
        """
        Removes the currently selected product from both the UI list and internal storage.

        Retrieves the index of the highlighted row in the list widget. If a valid 
        selection exists (index >= 0), removes the corresponding entry from the 
        graphical list, pops the matching item tuple from the internal data list 
        by index, and triggers a statistics recalculation.
        """
        row = self.list_widget.currentRow()
        if row >= 0:
            self.model.remove_item(row)
            self.list_widget.takeItem(row)
            self.update_stats_ui()


    def clear_all(self):
        """
        Removes all stored products from both internal storage and the UI.

        Purges the internal list repository, clears all entries from the 
        graphical list widget, and triggers a recalculation to reset 
        all statistical labels to default placeholders.
        """
        self.model.clear()
        self.list_widget.clear()
        self.update_stats_ui()


    def update_stats_ui(self):
        """
        Recalculates and updates the statistical price metrics displayed in the UI.

        Extracts numeric price values from the internal item collection and computes
        the minimum, maximum, and median values. Formats the calculated metrics to 
        two decimal places and updates the corresponding display labels.

        If the items list is empty, resets all statistical labels to default 
        dash placeholders ('—').
        """
        stats = self.model.get_statistics()
        if stats["min"] is None:
            self.min_label.setText("—")
            self.max_label.setText("—")
            self.median_label.setText("—")
        else:
            self.min_label.setText(f"{stats['min']:.2f}")
            self.max_label.setText(f"{stats['max']:.2f}")
            self.median_label.setText(f"{stats['median']:.2f}")


    def save_to_excel(self) -> bool:
        """Saves the current product list and price statistics to an Excel (.xlsx) file.

        Validates data availability, prompts the user to select a save location via a 
        file dialog (defaulting to the user's home directory), delegates XLSX generation 
        to `ExcelExporter`, and notifies the user of the result using `QMessageBox`.

        Returns:
            bool: True if the file was successfully exported;
                  False if the product list is empty, the dialog was canceled by the user, 
                  or an export error occurred.
        """
        if not self.model.get_items():
            QMessageBox.warning(self, "Warning", "There are no items to save.")
            return False

        # Automatically define home directory of current user (~/prices_report.xlsx)
        default_path = os.path.join(os.path.expanduser("~"), "prices_report.xlsx")

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Price Report", 
            default_path, 
            "Excel Files (*.xlsx)"
        )
        if not file_path:
            return False
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'

        success = ExcelExporter.export(
            file_path, 
            self.model.get_items(), 
            self.model.get_statistics()
        )
        if success:
            QMessageBox.information(self, "Success", f"File successfully saved to:\n{file_path}")
            return True
        else:
            QMessageBox.critical(self, "Error", "Failed to save the file.")
            return False