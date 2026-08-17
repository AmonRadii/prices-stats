import sys
import os
import statistics

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QFormLayout, 
    QMessageBox, QGroupBox, QFileDialog
)

import openpyxl

class PriceAnalyzerApp(QMainWindow):
    """
    Main window application for analyzing item prices.

    Provides a Graphical User Interface (GUI) to input item names and prices,
    displays an itemized list, and calculates statistical metrics (minimum,
    maximum, and median prices) in real time.

    Attributes:
        items (list[tuple[str, float]]): Storage for added items as tuples 
            of (item_name, price).
        name_input (QLineEdit): Widget for entering item names.
        price_input (QLineEdit): Widget for entering item prices.
        add_btn (QPushButton): Button triggering item validation and addition.
        list_widget (QListWidget): Graphical list displaying item entries.
        delete_btn (QPushButton): Button to remove the currently selected item.
        clear_btn (QPushButton): Button to purge all items from memory and UI.
        min_label (QLabel): Label displaying the calculated minimum price.
        max_label (QLabel): Label displaying the calculated maximum price.
        median_label (QLabel): Label displaying the calculated median price.
    """


    def __init__(self):
        """Initializes the main application window, data storage, and UI.

        Sets baseline window constraints (title and minimum geometry), 
        creates the internal list repository for storing item-price pairs, 
        and invokes the layout construction sequence.
        """        
        super().__init__()
        self.setWindowTitle("prices-stats")
        self.setMinimumSize(400, 500)

        # List for tuples: (name, price)
        self.items = []
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

        # 1. Input Form
        input_group = QGroupBox("Product Addition")
        input_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g: Laptop")

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("e.g: 2000.50")

        input_layout.addRow("Name:", self.name_input)
        input_layout.addRow("Price:", self.price_input)

        self.add_btn = QPushButton("Add product")
        self.add_btn.clicked.connect(self.add_item)
        input_layout.addRow(self.add_btn)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # 2. Product List
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        # 3.Control Buttons
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

        # 3. Statistics Block
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
        # If one of the interactive buttons has focus, its function is executed.
        self.name_input.returnPressed.connect(self.price_input.setFocus)
        self.price_input.returnPressed.connect(self.add_item)

        # 3. Deletion via the "Delete" key (works only when the list has focus)
        delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.list_widget)
        delete_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        delete_shortcut.activated.connect(self.delete_selected)

        # 4. Global Save shortcut (Ctrl+S / Cmd+S)
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.save_shortcut.activated.connect(self.save_to_excel)

        # Set focus on the first field
        self.name_input.setFocus()


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

        # Data saving
        self.items.append((name, price))
        self.list_widget.addItem(f"{name} — {price:.2f}")

        # Reset fields
        self.name_input.clear()
        self.price_input.clear()
        self.name_input.setFocus()
        
        self.update_stats()

    def delete_selected(self):
        """
        Removes the currently selected product from both the UI list and internal storage.

        Retrieves the index of the highlighted row in the list widget. If a valid 
        selection exists (index >= 0), removes the corresponding entry from the 
        graphical list, pops the matching item tuple from the internal data list 
        by index, and triggers a statistics recalculation.
        """
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.takeItem(current_row)
            self.items.pop(current_row)
            self.update_stats()

    def clear_all(self):
        """
        Removes all stored products from both internal storage and the UI.

        Purges the internal list repository, clears all entries from the 
        graphical list widget, and triggers a recalculation to reset 
        all statistical labels to default placeholders.
        """
        self.items.clear()
        self.list_widget.clear()
        self.update_stats()

    def update_stats(self):
        """
        Recalculates and updates the statistical price metrics displayed in the UI.

        Extracts numeric price values from the internal item collection and computes
        the minimum, maximum, and median values. Formats the calculated metrics to 
        two decimal places and updates the corresponding display labels.

        If the items list is empty, resets all statistical labels to default 
        dash placeholders ('—').
        """
        if not self.items:
            self.min_label.setText("—")
            self.max_label.setText("—")
            self.median_label.setText("—")
            return

        prices = [price for _, price in self.items]

        min_price = min(prices)
        max_price = max(prices)
        median_price = statistics.median(prices)

        self.min_label.setText(f"{min_price:.2f}")
        self.max_label.setText(f"{max_price:.2f}")
        self.median_label.setText(f"{median_price:.2f}")


    def save_to_excel(self):
        """
        Exports stored items and statistical metrics to an Excel (.xlsx) file.

        Opens a native file save dialog starting in the current working directory.
        Generates a structured .xlsx spreadsheet containing product names, prices,
        and summary metrics (Minimum, Maximum, Median).
        """
        if not self.items:
            QMessageBox.warning(self, "Warning", "There are no items to save.")
            return

        # 1. Start dialog in the program's working directory
        initial_dir = os.getcwd()
        default_filepath = os.path.join(initial_dir, "prices_report.xlsx")

        # 2. Open native GUI file picker
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Price Report",
            default_filepath,
            "Excel Files (*.xlsx)"
        )

        # If the user canceled the dialog window
        if not file_path:
            return

        # Explicitly enforce .xlsx extension
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'

        # 3. Excel generation sequence
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Prices Analysis"

            # Table Header
            ws.append(["Product", "Price"])

            # Product Rows
            prices = []
            for name, price in self.items:
                ws.append([name, price])
                prices.append(price)

            # Visual Separator
            ws.append([])

            # Summary Statistics
            ws.append(["Minimum Price", min(prices)])
            ws.append(["Maximum Price", max(prices)])
            ws.append(["Median Price", statistics.median(prices)])

            wb.save(file_path)
            QMessageBox.information(
                self, 
                "Success", 
                f"File successfully saved to:\n{file_path}"
            )

        except Exception as err:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save file:\n{str(err)}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PriceAnalyzerApp()
    window.show()
    sys.exit(app.exec())