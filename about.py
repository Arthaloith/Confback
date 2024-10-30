from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QSize

class About(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # About information
        about_label = QLabel(
            "About Config Backup\n\n"
            "Config Backup is a versatile backup utility designed to help users easily "
            "manage their configuration files and directories. With a user-friendly interface, "
            "Config Backup allows you to create, restore, and manage backups effortlessly.\n\n"
            "Key Features:\n"
            "- Easy folder selection\n"
            "- Support for multiple backup methods\n"
            "- Intuitive user interface\n"
            "- Detailed logs and status updates"
        )
        about_label.setFont(QFont("Arial", 12))
        about_label.setWordWrap(True)
        layout.addWidget(about_label)

        # Author information
        author_label = QLabel("Author: Arthaloith")
        author_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(author_label)

        # Contact information
        contact_label = QLabel("Contact me:")
        contact_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(contact_label)

        # Horizontal layout for icons
        contact_layout = QHBoxLayout()

        # GitHub icon
        github_icon = QLabel()
        github_pixmap = QPixmap("resources/git.png").scaled(QSize(32, 32), aspectRatioMode=True)
        github_icon.setPixmap(github_pixmap)
        github_icon.setFixedSize(32, 32)
        github_label = QLabel('<a href="https://github.com/johndoe">GitHub</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setStyleSheet("font-size: 10pt; text-decoration: underline; color: blue;")
        
        contact_layout.addWidget(github_icon)
        contact_layout.addWidget(github_label)

        # Twitter icon
        twitter_icon = QLabel()
        twitter_pixmap = QPixmap("resources/twit.png").scaled(QSize(32, 32), aspectRatioMode=True)
        twitter_icon.setPixmap(twitter_pixmap)
        twitter_icon.setFixedSize(32, 32)
        twitter_label = QLabel('<a href="https://twitter.com/johndoe">Twitter</a>')
        twitter_label.setOpenExternalLinks(True)
        twitter_label.setStyleSheet("font-size: 10pt; text-decoration: underline; color: blue;")

        contact_layout.addWidget(twitter_icon)
        contact_layout.addWidget(twitter_label)

        layout.addLayout(contact_layout)

        self.setLayout(layout)