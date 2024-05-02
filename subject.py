from PyQt5.QtWidgets import (
    QMainWindow,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QWidget,
    QListWidgetItem,
    QHBoxLayout,
)
from addgrade import AddGradeWindow
from connection import ConnectionManager
import psycopg2


class SubjectWindow(QMainWindow):
    def __init__(self, connection, subject: str, student_id: int, grade_window=None):
        super().__init__()
        self.subject = subject
        self.student_id = student_id
        self.connection: ConnectionManager = connection
        self.grade_window = grade_window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.subject)
        self.setGeometry(100, 100, 600, 500)
        self.layout = QVBoxLayout()
        self.list_widget = QListWidget(self)
        self.layout.addWidget(self.list_widget)
        if self.connection.user == "teacher":
            self.add_button = QPushButton("Добавить оценку", self)
            self.add_button.clicked.connect(self.add_grade)
            self.layout.addWidget(self.add_button)
            self.list_widget.itemDoubleClicked.connect(self.update_grade)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout)
        self.show_grades()

    def get_grades(self):
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "SELECT gradeid, grade, comment FROM (select * from grades where subject = %s) g where studentid = %s",
                    (
                        self.subject,
                        self.student_id,
                    ),
                )
                grades = cursor.fetchall()
                for grade in grades:
                    grade = dict(grade)
        print(grades)
        return grades

    def show_grades(self):
        self.list_widget.clear()
        grades = self.get_grades()
        for grade in grades:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)

            item_layout.addWidget(QLabel(str(grade["grade"])))
            item_layout.addWidget(QLabel(grade["comment"]))
            if self.connection.user == "teacher":
                button = QPushButton("Удалить", self)
                button.clicked.connect(
                    lambda _, gradeid=grade["gradeid"]: self.delete_grade(gradeid)
                )
                item_layout.addWidget(button)
            list_item = QListWidgetItem()
            list_item.setData(1, grade["gradeid"])

            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

    def delete_grade(self, gradeid):
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM grades WHERE gradeid = %s", (gradeid,))
                connection.commit()
        self.grade_window.show_grades()
        self.show_grades()

    def update_grade(self, list_item: QListWidgetItem):
        gradeid = list_item.data(1)
        self.UpdategradeWindow = AddGradeWindow(
            self.connection,
            self.student_id,
            gradeid=gradeid,
            subject=self.subject,
            previous=self,
        )
        self.UpdategradeWindow.show()

    def add_grade(self):
        self.UpdategradeWindow = AddGradeWindow(
            self.connection, self.student_id, subject=self.subject, previous=self
        )
        self.UpdategradeWindow.show()
