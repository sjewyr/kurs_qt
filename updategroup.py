from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
)
from connection import ConnectionManager


class UpdateGroupWindow(QMainWindow):
    def __init__(self, connection, group_window, group_id):
        super(UpdateGroupWindow, self).__init__()
        self.connection: ConnectionManager = connection
        self.group_window = group_window
        self.group_id = group_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Обновление группы")
        self.setFixedSize(300, 100)
        self.result = QLabel()
        self.layout = QVBoxLayout()
        self.group_name = QLineEdit()
        self.layout.addWidget(self.group_name)
        self.button = QPushButton("Обновить")
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select groupname from groups where groupid = %s", (self.group_id,)
                )
                group = cursor.fetchone()[0]
                self.group_name.setText(group)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.result)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout)
        self.button.clicked.connect(self.update_group)

    def update_group(self):
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select * from check_group_name(%s)", (self.group_name.text(),)
                )
                check = cursor.fetchone()[0]
                if check:
                    self.result.setText("Группа с таким именем уже существует")
                    return
                cursor.execute(
                    "select * from update_group(%s, %s)",
                    (self.group_id, self.group_name.text()),
                )
                connection.commit()
                self.group_window.update_groups()
                self.close()
