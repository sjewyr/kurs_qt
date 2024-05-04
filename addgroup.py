from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QLineEdit,
    QDialog,
    QWidget,
    QHBoxLayout,
)
from connection import ConnectionManager


class AddGroupWindow(QMainWindow):
    def __init__(self, connection: ConnectionManager, group_window):
        super().__init__()
        self.setWindowTitle("Добавить группу")
        self.setGeometry(100, 100, 300, 100)
        self.connection = connection
        self.group_window = group_window
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)
        self.result = QLabel()
        self.layout.addWidget(QLabel("Введите название группы"))
        self.group_name_input = QLineEdit()
        self.layout.addWidget(self.group_name_input)
        self.add_group_button = QPushButton("Добавить")
        self.layout.addWidget(self.add_group_button)
        self.add_group_button.clicked.connect(self.add_group)
        self.layout.addWidget(self.result)

    def add_group(self):
        group_name = self.group_name_input.text()
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("select * from check_group_name(%s);", (group_name,))
                if cursor.fetchone()[0]:
                    self.result.setText("Группа с таким именем уже существует")
                    return
                cursor.execute("select * from create_group(%s);", (group_name,))
                connection.commit()
        self.group_window.update_groups()
        self.close()
