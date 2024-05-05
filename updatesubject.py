from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QLabel,
    QWidget,
)

from connection import ConnectionManager


class UpdateSubjectWindow(QMainWindow):
    def __init__(self, connection, subject_window, subject_id, subject):
        super(UpdateSubjectWindow, self).__init__()
        self.connection: ConnectionManager = connection
        self.subject_window = subject_window
        self.subject_id = subject_id
        self.subject = subject
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Обновление предмета")
        self.setFixedSize(300, 100)
        self.layout = QVBoxLayout()
        self.name_label = QLabel("Название предмета")
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.subject)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_edit)
        self.button = QPushButton("Обновить")
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.update_subject)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout)
        self.result = QLabel()
        self.layout.addWidget(self.result)

    def update_subject(self):
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select * from check_subject_name(%s)", (self.name_edit.text(),)
                )
                check = cursor.fetchone()[0]
                if check:
                    self.result.setText("Предмет с таким названием уже существует")
                    return

                else:
                    cursor.execute(
                        "UPDATE subject SET subject = %s WHERE subjectid = %s",
                        (self.name_edit.text(), self.subject_id),
                    )
                    cursor.connection.commit()
                    self.subject_window.view_subjects()
                    self.close()
