import sys
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QGridLayout, QFileDialog, QProgressBar, QTextEdit, QLineEdit, QScrollArea, QMenu, QRadioButton, QTabWidget, QHBoxLayout
)
from PyQt5.QtCore import QThread, QObject, pyqtSlot, pyqtSignal

class Worker(QObject):
    finished = pyqtSignal()  # Signal to indicate that the worker is finished
    error_occurred = pyqtSignal(str)  # Signal to indicate an error occurred

    def __init__(self, source_dirs, destination, mode):
        super().__init__()
        self.source_dirs = source_dirs
        self.destination = destination
        self.mode = mode
        self.running = True

    def run(self):
        for source in self.source_dirs:
            if not self.running:
                break  # Stop the process if cancel is requested
            if self.mode == "cp":
                command = f"cp -r {source} {self.destination}/"
            elif self.mode == "rsync":
                command = f"rsync -av {source}/ {self.destination}/"  # Rsync command

            result = subprocess.run(command, shell=True, capture_output=True)

            # Check for errors
            if result.returncode != 0:
                self.error_occurred.emit(f"Error backing up {source}: {result.stderr.decode()}")
                return
        
        self.finished.emit()  # Emit finished without arguments

    def stop(self):
        self.running = False

class SyncApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.worker = None
        self.thread = None
        self.source_buttons_cp = []  # List for cp source directories
        self.source_buttons_rsync = []  # List for rsync source directories
        self.destination = ""  # Variable to store the destination directory
        self.source_paths_cp = []  # List to store cp source paths
        self.source_paths_rsync = []  # List to store rsync source paths
        self.current_mode = None  # Keep track of the selected mode

    def init_ui(self):
        self.setWindowTitle("LibreWolf Sync")
        self.setFixedSize(800, 600)

        # Create the tab widget
        self.tabs = QTabWidget(self)
        self.layout = QVBoxLayout()

        # Add tabs
        self.offline_tab = QWidget()
        self.online_tab = QWidget()
        self.about_tab = QWidget()

        self.tabs.addTab(self.offline_tab, "Offline Backup")
        self.tabs.addTab(self.online_tab, "Online Backup")
        self.tabs.addTab(self.about_tab, "About")

        # Set up each tab
        self.setup_offline_tab()
        self.setup_online_tab()
        self.setup_about_tab()

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def setup_offline_tab(self):
        """Set up the UI for the offline backup tab."""
        self.offline_layout = QVBoxLayout()

        self.cp_section_label = QLabel("Select folders to back up using Copy (cp):")
        self.offline_layout.addWidget(self.cp_section_label)

        self.cp_scroll_area = QScrollArea()
        self.cp_scroll_area.setWidgetResizable(True)
        self.cp_scroll_area.setFixedHeight(150)

        self.cp_button_container = QWidget()
        self.cp_source_layout = QGridLayout(self.cp_button_container)
        self.cp_source_layout.setSpacing(5)
        self.cp_source_layout.setContentsMargins(0, 0, 0, 0)

        self.cp_scroll_area.setWidget(self.cp_button_container)
        self.offline_layout.addWidget(self.cp_scroll_area)

        self.add_source_cp_button = QPushButton("+")
        self.add_source_cp_button.setFixedSize(80, 80)
        self.add_source_cp_button.setStyleSheet("font-size: 24px;")
        self.add_source_cp_button.clicked.connect(self.add_source_cp_button_action)
        self.cp_source_layout.addWidget(self.add_source_cp_button, 0, 0)

        self.destination_label = QLabel("Select destination directory:")
        self.offline_layout.addWidget(self.destination_label)

        self.destination_input = QLineEdit(self)
        self.offline_layout.addWidget(self.destination_input)

        self.destination_button = QPushButton("Browse")
        self.destination_button.clicked.connect(self.select_destination)
        self.offline_layout.addWidget(self.destination_button)

        self.sync_button = QPushButton("Sync")
        self.sync_button.clicked.connect(self.sync)
        self.offline_layout.addWidget(self.sync_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_sync)
        self.offline_layout.addWidget(self.cancel_button)

        self.status_label = QLabel("")
        self.offline_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.offline_layout.addWidget(self.progress_bar)

        # Log window
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.offline_layout.addWidget(self.log_output)

        self.offline_tab.setLayout(self.offline_layout)

    def setup_online_tab(self):
        """Set up the UI for the online backup tab."""
        self.online_layout = QVBoxLayout()

        self.online_label = QLabel("Online Backup functionality will be implemented here.")
        self.online_layout.addWidget(self.online_label)

        self.online_tab.setLayout(self.online_layout)

    def setup_about_tab(self):
        """Set up the UI for the about tab."""
        self.about_layout = QVBoxLayout()

        self.about_label = QLabel("About this application:\n\nLibreWolf Sync is a backup utility.")
        self.about_layout.addWidget(self.about_label)

        self.about_tab.setLayout(self.about_layout)

    def add_source_cp_button_action(self):
        """Prompt to select a source folder for cp and create a new button for it."""
        self.add_source_button_action("cp")

    def add_source_button_action(self, mode):
        """Prompt to select a source folder and create a new button for it."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            folder_name = os.path.basename(directory)  # Get only the folder name
            source_button = QPushButton(folder_name)  # Create a button with the folder name
            source_button.setFixedSize(80, 80)  # Set a larger button size
            source_button.setStyleSheet("font-size: 12px;")
            source_button.setContextMenuPolicy(3)  # Enable context menu
            source_button.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, source_button, mode))

            # Add the new source button to the appropriate grid layout
            row = (len(self.source_buttons_cp) + 1) // 3
            col = (len(self.source_buttons_cp) + 1) % 3
            self.cp_source_layout.addWidget(source_button, row, col)
            self.source_buttons_cp.append(source_button)  # Keep track of the button
            self.source_paths_cp.append(directory)  # Store the full path

    def show_context_menu(self, pos, button, mode):
        """Show the context menu for the given button."""
        menu = QMenu(self)
        delete_action = menu.addAction("Delete")
        action = menu.exec_(button.mapToGlobal(pos))
        if action == delete_action:
            self.remove_source_button(button, self.source_buttons_cp, self.cp_source_layout, self.source_paths_cp)

    def remove_source_button(self, button, button_list, layout, path_list):
        """Remove the selected source button."""
        index = button_list.index(button)
        layout.removeWidget(button)
        button.deleteLater()  # Delete the button
        button_list.remove(button)  # Remove from the list
        path_list.pop(index)  # Remove the corresponding path

        # Re-layout the buttons to maintain grid integrity
        self.relayout_source_buttons(button_list, layout)

    def relayout_source_buttons(self, button_list, layout):
        """Reposition buttons in the grid after one has been removed."""
        for index, button in enumerate(button_list):
            row = index // 3
            col = index % 3
            layout.addWidget(button, row, col)

    def select_destination(self):
        """Open a dialog to select the destination directory."""
        self.destination = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if self.destination:
            self.destination_input.setText(self.destination)  # Update input field to show selected destination

    def sync(self):
        if self.destination and self.source_paths_cp:
            self.status_label.setText("Status: Running...")
            self.progress_bar.setValue(0)  # Reset the progress bar

            # Start the copy process in a separate thread
            self.thread = QThread()

            # Create a worker for cp
            if self.source_paths_cp:
                worker = Worker(self.source_paths_cp, self.destination, "cp")
                worker.moveToThread(self.thread)

                self.thread.started.connect(worker.run)
                worker.finished.connect(self.sync_finished)  # Connect finished without arguments
                worker.error_occurred.connect(self.handle_error)
                self.thread.finished.connect(self.thread.quit)

                self.thread.start()
        else:
            self.status_label.setText("Please select a destination directory and valid source folders.")
            self.status_label.setStyleSheet("color: red")

    def handle_error(self, error_message):
        """Handle errors emitted from the worker."""
        self.status_label.setText(f"Status: Error - {error_message}")
        self.status_label.setStyleSheet("color: red")
        self.log_output.append(error_message)  # Append error message to the log

    def cancel_sync(self):
        """Cancel the ongoing synchronization process."""
        if self.worker:
            self.worker.stop()  # Stop the worker from running
        self.status_label.setText("Status: Canceled.")
        self.log_output.append("Sync canceled.")  # Log the cancellation
        self.thread.quit()  # Quit the thread

    @pyqtSlot()
    def sync_finished(self):
        self.progress_bar.setValue(100)  # Set to 100% when done
        success_message = "Sync completed successfully."
        self.status_label.setText("Status: Done.")
        self.status_label.setStyleSheet("color: green")
        self.log_output.append(success_message)  # Append completion message to the log

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SyncApp()
    ex.show()
    sys.exit(app.exec_())