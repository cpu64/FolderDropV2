import sys
from PyQt6.QtWidgets import QApplication

from app.host.ui.main import MainWindow


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(600, 400)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
