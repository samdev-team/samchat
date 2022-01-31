# This file is part of SAM-Chat
#
# SAM-Chat is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# SAM-Chat is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with this
# program. If not, see <https://www.gnu.org/licenses/>.


from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea, QApplication,
                             QGridLayout, QMainWindow, QSpacerItem, QSizePolicy, QVBoxLayout, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
import sys
from samsocket import samsocket, Encryption, message

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        btn = QPushButton("Connect to server")
        btn.clicked.connect(self.connectionUI)

        init_layout = QVBoxLayout()

        init_layout.addWidget(btn)


        self.frame = QFrame()
        self.frame.setLayout(init_layout)

        self.setGeometry(0, 0, 900, 600)
        self.setWindowTitle('ZamChat')
        self.show()

    def connectionUI(self):
        pass

    def chatroomUI(self):
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.scroll_layout = QGridLayout()

        self.scroll_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))

        self.widget.setLayout(self.scroll_layout)
        # Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())


def joinroomUI(self):
    pass


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
