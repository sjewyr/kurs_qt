from PyQt5.QtWidgets import (
    QMainWindow,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QListWidget,
    QWidget,
    QListWidgetItem,
)

from addgrade import AddGradeWindow
from connection import ConnectionManager
import psycopg2

from subject import SubjectWindow


class GradeWindow(QMainWindow):
    def __init__(self, connection: ConnectionManager, student_id: int):
        super().__init__()
        self.connection = connection
        self.student_id = student_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Оценки")
        self.setGeometry(100, 100, 800, 700)
        self.layout = QVBoxLayout()
        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self.show_grade_info)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout)

        self.layout.addWidget(self.list_widget)
        if self.connection.user == "teacher":
            self.add_button = QPushButton("Добавить оценку", self)
            self.add_button.clicked.connect(self.add_grade)
            self.layout.addWidget(self.add_button)
        self.show_grades()

    def show_grades(self):
        self.list_widget.clear()
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "select distinct subject from grades where studentid = %s",
                    (self.student_id,),
                )
                subjects = cursor.fetchall()
                for subject in subjects:
                    item_widget = QWidget()
                    item_layout = QHBoxLayout(item_widget)
                    cursor.execute(
                        "select grade from grades where studentid = %s and subject = %s",
                        (self.student_id, subject[0]),
                    )
                    grades = cursor.fetchall()
                    slabel = QLabel(subject[0])
                    item_layout.addWidget(slabel)
                    label = QLabel(
                        " ".join(str(grades[i][0]) for i in range(len(grades)))
                    )
                    item_layout.addWidget(label)

                    list_item = QListWidgetItem()
                    list_item.setData(1, subject[0])
                    list_item.setSizeHint(item_widget.sizeHint())
                    self.list_widget.addItem(list_item)
                    self.list_widget.setItemWidget(list_item, item_widget)

    def show_grade_info(self, item: QListWidgetItem):
        self.subject_window = SubjectWindow(
            self.connection, item.data(1), self.student_id, grade_window=self
        )
        self.subject_window.show()

    def add_grade(self):
        self.add_grade_window = AddGradeWindow(
            self.connection, self.student_id, previous=self
        )
        self.add_grade_window.show()
