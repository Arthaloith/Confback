import sys
from PyQt5.QtWidgets import QApplication, QTabWidget, QVBoxLayout, QWidget
from offline_backup import OfflineBackup
from online_backup import OnlineBackup
from about import About

class SyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("LibreWolf Sync")
        self.setMinimumSize(1000, 800)  # Set minimum size instead of fixed size

        # Create the tab widget
        self.tabs = QTabWidget(self)

        # Add tabs
        self.tabs.addTab(OfflineBackup(), "Offline Backup")
        self.tabs.addTab(OnlineBackup(), "Online Backup")
        self.tabs.addTab(About(), "About")

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SyncApp()
    ex.show()
    sys.exit(app.exec_())