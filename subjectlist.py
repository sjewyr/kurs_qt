from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QListWidget,
    QLineEdit,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
)
import psycopg2

from connection import ConnectionManager
from updatesubject import UpdateSubjectWindow


class SubjectListWindow(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.connection: ConnectionManager = connection
        self.init_ui()

    def init_ui(self):
        self.setGeometry(300, 300, 350, 500)
        self.setWindowTitle("Предметы")
        layout = QVBoxLayout()
        self.list = QListWidget()
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(layout)
        layout.addWidget(self.list)
        if self.connection.user == "teacher":
            self.add_button = QPushButton(self)
            self.add_edit = QLineEdit(self)
            self.add_layout = QHBoxLayout()
            layout.addLayout(self.add_layout)
            self.add_layout.addWidget(self.add_edit)
            self.add_layout.addWidget(self.add_button)
            self.add_button.setText("Добавить предмет")
            self.list.itemDoubleClicked.connect(self.update_subject)
            self.add_button.clicked.connect(self.add_subject)
            self.result = QLabel(self)
            layout.addWidget(self.result)
        self.view_subjects()

    def view_subjects(self):
        self.list.clear()
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("select subjectid, subject from subject")
                subjects = cursor.fetchall()
                for subject in subjects:
                    item_widget = QWidget()
                    item_layout = QHBoxLayout(item_widget)
                    label = QLabel()
                    label.setText(subject["subject"])
                    item_layout.addWidget(label)
                    if self.connection.user == "teacher":
                        button = QPushButton("Удалить")
                        item_layout.addWidget(button)
                        button.clicked.connect(
                            lambda _, id=subject["subjectid"]: self.delete_subject(id)
                        )

                    item = QListWidgetItem()
                    item.setData(1, [subject["subjectid"], subject["subject"]])

                    item.setSizeHint(item_widget.sizeHint())
                    self.list.addItem(item)
                    self.list.setItemWidget(item, item_widget)

    def delete_subject(self, id):
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("delete from subject where subjectid = %s", (id,))
                cursor.connection.commit()
                self.view_subjects()

    def add_subject(self):
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "select * from check_subject_name(%s)", (self.add_edit.text(),)
                )
                check = cursor.fetchone()[0]
                if check:
                    self.result.setText("Предмет с таким именем уже существует")
                    return
                cursor.execute(
                    "insert into subject (subject) values (%s)", (self.add_edit.text(),)
                )
                cursor.connection.commit()
                self.view_subjects()

    def update_subject(self, item):
        self.update_subject_window = UpdateSubjectWindow(
            self.connection, self, item.data(1)[0], item.data(1)[1]
        )
        self.update_subject_window.show()
