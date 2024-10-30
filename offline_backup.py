import os
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QGridLayout, QFileDialog, QProgressBar, QTextEdit, QLineEdit, QScrollArea, QMenu
)
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

class Worker(QObject):
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(int)

    def __init__(self, source_dirs, destination, mode):
        super().__init__()
        self.source_dirs = source_dirs
        self.destination = destination
        self.mode = mode
        self.running = True

    def run(self):
        for source in self.source_dirs:
            if not self.running:
                break

            if self.mode == "cp":
                command = f"cp -r {source} {self.destination}/"
            else:  # rsync
                command = f"rsync -ah --progress {source}/ {self.destination}/"

            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_output(output)
                    self.parse_progress(output)

            result = process.communicate()
            if process.returncode != 0:
                self.error_occurred.emit(f"Error backing up {source}: {result[1].strip()}")
                return
        self.finished.emit()

    def parse_progress(self, output):
        if "to-check" in output or "bytes" in output:
            parts = output.split()
            for part in parts:
                if part.endswith('%'):
                    try:
                        percent = int(part[:-1])
                        self.progress_update.emit(percent)
                    except ValueError:
                        continue
        else:
            self.progress_update.emit(0)

    def log_output(self, output):
        print(output.strip())

    def stop(self):
        self.running = False

class OfflineBackup(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker_cp = None
        self.worker_rsync = None
        self.thread = None
        self.cp_source_buttons = []
        self.rsync_source_buttons = []
        self.destination = ""
        self.cp_source_paths = []
        self.rsync_source_paths = []

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Copy Mode Section
        self.cp_section_label = QLabel("Select folders to back up using Copy (cp):")
        self.layout.addWidget(self.cp_section_label)

        self.cp_scroll_area = QScrollArea()
        self.cp_scroll_area.setWidgetResizable(True)
        self.cp_scroll_area.setFixedHeight(150)

        self.cp_button_container = QWidget()
        self.cp_source_layout = QGridLayout(self.cp_button_container)
        self.cp_source_layout.setSpacing(5)
        self.cp_source_layout.setContentsMargins(0, 0, 0, 0)

        self.cp_scroll_area.setWidget(self.cp_button_container)
        self.layout.addWidget(self.cp_scroll_area)

        self.add_cp_source_button = QPushButton("+")
        self.add_cp_source_button.setFixedSize(80, 80)
        self.add_cp_source_button.setStyleSheet("font-size: 24px;")
        self.add_cp_source_button.clicked.connect(self.add_cp_source_button_action)
        self.cp_source_layout.addWidget(self.add_cp_source_button, 0, 0)

        # Rsync Mode Section
        self.rsync_section_label = QLabel("Select folders to back up using Rsync:")
        self.layout.addWidget(self.rsync_section_label)

        self.rsync_scroll_area = QScrollArea()
        self.rsync_scroll_area.setWidgetResizable(True)
        self.rsync_scroll_area.setFixedHeight(150)

        self.rsync_button_container = QWidget()
        self.rsync_source_layout = QGridLayout(self.rsync_button_container)
        self.rsync_source_layout.setSpacing(5)
        self.rsync_source_layout.setContentsMargins(0, 0, 0, 0)

        self.rsync_scroll_area.setWidget(self.rsync_button_container)
        self.layout.addWidget(self.rsync_scroll_area)

        self.add_rsync_source_button = QPushButton("+")
        self.add_rsync_source_button.setFixedSize(80, 80)
        self.add_rsync_source_button.setStyleSheet("font-size: 24px;")
        self.add_rsync_source_button.clicked.connect(self.add_rsync_source_button_action)
        self.rsync_source_layout.addWidget(self.add_rsync_source_button, 0, 0)

        # Destination Directory
        self.destination_label = QLabel("Select destination directory:")
        self.layout.addWidget(self.destination_label)

        self.destination_input = QLineEdit(self)
        self.layout.addWidget(self.destination_input)

        self.destination_button = QPushButton("Browse")
        self.destination_button.clicked.connect(self.select_destination)
        self.layout.addWidget(self.destination_button)

        # Sync and Cancel Buttons
        self.sync_button = QPushButton("Sync")
        self.sync_button.clicked.connect(self.sync)
        self.layout.addWidget(self.sync_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_sync)
        self.layout.addWidget(self.cancel_button)

        # Status and Progress
        self.status_label = QLabel("")
        self.layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)

        # Log Output
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.layout.addWidget(self.log_output)

        self.setLayout(self.layout)

    def add_cp_source_button_action(self):
        """Prompt to select a source folder for cp and create a new button for it."""
        self.add_source_button_action("cp")

    def add_rsync_source_button_action(self):
        """Prompt to select a source folder for rsync and create a new button for it."""
        self.add_source_button_action("rsync")

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
            if mode == "cp":
                row = (len(self.cp_source_buttons) + 1) // 3
                col = (len(self.cp_source_buttons) + 1) % 3
                self.cp_source_layout.addWidget(source_button, row, col)
                self.cp_source_buttons.append(source_button)  # Keep track of the button
                self.cp_source_paths.append(directory)  # Store the full path
            else:
                row = (len(self.rsync_source_buttons) + 1) // 3
                col = (len(self.rsync_source_buttons) + 1) % 3
                self.rsync_source_layout.addWidget(source_button, row, col)
                self.rsync_source_buttons.append(source_button)  # Keep track of the button
                self.rsync_source_paths.append(directory)  # Store the full path

    def show_context_menu(self, pos, button, mode):
        """Show the context menu for the given button."""
        menu = QMenu(self)
        delete_action = menu.addAction("Delete")
        action = menu.exec_(button.mapToGlobal(pos))
        if action == delete_action:
            self.remove_source_button(button, mode)

    def remove_source_button(self, button, mode):
        """Remove the selected source button."""
        if mode == "cp":
            index = self.cp_source_buttons.index(button)
            self.cp_source_layout.removeWidget(button)
            button.deleteLater()  # Delete the button
            self.cp_source_buttons.remove(button)  # Remove from the list
            self.cp_source_paths.pop(index)  # Remove the corresponding path
            self.relayout_source_buttons(self.cp_source_buttons, self.cp_source_layout)
        else:
            index = self.rsync_source_buttons.index(button)
            self.rsync_source_layout.removeWidget(button)
            button.deleteLater()  # Delete the button
            self.rsync_source_buttons.remove(button)  # Remove from the list
            self.rsync_source_paths.pop(index)  # Remove the corresponding path
            self.relayout_source_buttons(self.rsync_source_buttons, self.rsync_source_layout)

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
        if self.thread and self.thread.isRunning():
            self.status_label.setText("Status: Sync is already in progress.")
            return

        if self.destination and (self.cp_source_paths or self.rsync_source_paths):
            self.status_label.setText("Status: Running...")
            self.progress_bar.setValue(0)  # Reset the progress bar

            self.thread = QThread()

            # Create worker for cp
            if self.cp_source_paths:
                self.worker_cp = Worker(self.cp_source_paths, self.destination, "cp")
                self.worker_cp.moveToThread(self.thread)
                self.thread.started.connect(self.worker_cp.run)
                self.worker_cp.finished.connect(self.cleanup)
                self.worker_cp.error_occurred.connect(self.handle_error)
                self.worker_cp.progress_update.connect(self.update_progress)

            # Create worker for rsync
            if self.rsync_source_paths:
                self.worker_rsync = Worker(self.rsync_source_paths, self.destination, "rsync")
                self.worker_rsync.moveToThread(self.thread)
                self.thread.started.connect(self.worker_rsync.run)
                self.worker_rsync.finished.connect(self.cleanup)
                self.worker_rsync.error_occurred.connect(self.handle_error)
                self.worker_rsync.progress_update.connect(self.update_progress)

            # Start the thread
            self.thread.start()
        else:
            self.status_label.setText("Please select a destination directory and valid source folders.")
            self.status_label.setStyleSheet("color: red")

    @pyqtSlot(int)
    def update_progress(self, percent):
        """Update the progress bar based on the emitted signal."""
        self.progress_bar.setValue(percent)

    def handle_error(self, error_message):
        """Handle errors emitted from the worker."""
        self.status_label.setText(f"Status: Error - {error_message}")
        self.status_label.setStyleSheet("color: red")
        self.log_output.append(error_message)  # Append error message to the log

    def cancel_sync(self):
        """Cancel the ongoing synchronization process."""
        if self.thread and self.thread.isRunning():
            if hasattr(self, 'worker_cp'):
                self.worker_cp.stop()
            if hasattr(self, 'worker_rsync'):
                self.worker_rsync.stop()
            self.thread.quit()
            self.thread.wait()  # Wait for the thread to finish
            self.status_label.setText("Status: Canceled.")
            self.log_output.append("Sync canceled.")  # Log the cancellation
        else:
            self.log_output.append("No active sync process to cancel.")  # Log if no active thread

    @pyqtSlot()
    def cleanup(self):
        # Set progress bar to 100% when done
        self.progress_bar.setValue(100)  
        success_message = "Sync completed successfully."
        self.status_label.setText("Status: Done.")
        self.status_label.setStyleSheet("color: green")
        self.log_output.append(success_message)  # Append completion message to the log

        if self.thread is not None:
            self.thread.quit()  # Quit the thread if it exists
            self.thread.wait()  # Wait until the thread has properly finished
            self.thread = None  # Reset the thread reference