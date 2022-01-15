from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea, QApplication,
                             QGridLayout, QMainWindow, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QGridLayout()

        self.scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))
        for i in range(30):
            object = QLabel(f"TextLabel {i}")
            image = QLabel()
            pixmap = QPixmap('unknown.png')
            pixmap= pixmap.scaled(50, 50)
            image.setPixmap(pixmap)
            object.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.vbox.addWidget(image)
            self.vbox.addWidget(object)

        self.widget.setLayout(self.vbox)

        # Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

        self.setGeometry(0, 0, 900, 600)
        self.setWindowTitle('ZamChat')
        self.show()

        return


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
