from PyQt5.QtWidgets import (
    QMainWindow,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QTableWidgetItem,
    QTableWidget,
    QHeaderView,
)
from PyQt5.QtCore import Qt
import psycopg2
import psycopg2.extras

from connection import ConnectionManager


class StudentInfoWindow(QMainWindow):
    def __init__(self, connection):
        super(StudentInfoWindow, self).__init__()
        self.connection: ConnectionManager = connection
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(1250, 500)
        self.setWindowTitle("Информация о студенте")
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignTop)
        self.combo_layout = QHBoxLayout()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self._layout)
        self._layout.addLayout(self.combo_layout)
        self.label = QLabel("Номер студенческого билета")
        self.combo_layout.addWidget(self.label)
        self.student_combo = QComboBox()
        self.student_combo.setEditable(True)
        self.student_combo.setInsertPolicy(QComboBox.NoInsert)
        self.student_combo.lineEdit().setClearButtonEnabled(True)
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("select cardid, studentid from students")
                students = cursor.fetchall()
                for student in students:
                    self.student_combo.addItem(str(student[0]), str(student[1]))
        self.combo_layout.addWidget(self.student_combo)
        self.student_combo.currentIndexChanged.connect(self.update_info)
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._layout.addWidget(self.table_widget)
        self.update_info(0)

    def update_info(self, index):
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "select * from get_student_info(%s)",
                    (self.student_combo.itemData(index),),
                )
                student = cursor.fetchone()
                student = dict(student)

                cursor.execute(
                    "select * from get_average_grade(%s)",
                    (self.student_combo.itemData(index),),
                )
                avg_grade = dict(cursor.fetchone())
                cursor.execute(
                    "select * from get_total_attendance(%s)",
                    (self.student_combo.itemData(index),),
                )
                total_attendance = dict(cursor.fetchone())
                cursor.execute(
                    "select * from get_total_misses(%s)",
                    (self.student_combo.itemData(index),),
                )
                total_misses = dict(cursor.fetchone())

                student.update(avg_grade)
                student.update(total_attendance)
                student.update(total_misses)

        self.table_widget.setRowCount(1)
        self.table_widget.setColumnCount(len(student))
        if student["get_average_grade"] is None:
            student["get_average_grade"] = "Нет данных"
        headers = [
            "Имя",
            "Фамилия",
            "Отчество",
            "Группа",
            "Студ. билет",
            "Отличник",
            "Есть долги",
            "Ср. оценка",
            "Кол-во посещений",
            "Кол-во пропусков",
        ]
        # Заполняем таблицу данными о студенте
        for i, (key, value) in enumerate(student.items()):
            if value == True and type(value) == bool:
                value = "Да"
            elif value == False and type(value) == bool:
                value = "Нет"
            item = QTableWidgetItem(str(value))
            self.table_widget.setItem(0, i, item)
            self.table_widget.setHorizontalHeaderItem(i, QTableWidgetItem(headers[i]))
