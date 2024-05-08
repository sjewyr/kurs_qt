from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QLineEdit,
)
from connection import ConnectionManager
import utils


class UpdateStudentWindow(QMainWindow):
    def __init__(self, connection: ConnectionManager, group_window, student_id):
        super().__init__()
        self.connection = connection
        self.group_window = group_window
        self.student_id = student_id
        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 600, 500)
        self.setFixedSize(600, 500)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Имя:"))
        self.first_name_edit = QLineEdit()
        self.layout.addWidget(self.first_name_edit)
        self.layout.addWidget(QLabel("Фамилия:"))
        self.last_name_edit = QLineEdit()
        self.layout.addWidget(self.last_name_edit)
        self.layout.addWidget(QLabel("Отчество:"))
        self.middle_name_edit = QLineEdit()
        self.layout.addWidget(self.middle_name_edit)
        self.layout.addWidget(QLabel("Группа:"))
        self.group_combo = QComboBox()
        self.group_combo.setEditable(True)
        self.group_combo.setInsertPolicy(QComboBox.NoInsert)
        self.group_combo.lineEdit().setClearButtonEnabled(True)
        self.layout.addWidget(self.group_combo)
        self.button = QPushButton("Обновить")
        self.layout.addWidget(self.button)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout)
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select firstname, surname, patronymic, groupid, cardid from students where studentid = %s",
                    (self.student_id,),
                )
                student = cursor.fetchone()
        groups = utils.get_groups(self.connection)
        for group in groups:
            self.group_combo.addItem(group[0], group[1])

        self.first_name_edit.setText(student[0])
        self.last_name_edit.setText(student[1])
        self.middle_name_edit.setText(student[2])
        self.group_combo.setCurrentIndex(self.group_combo.findData(student[3]))
        self.setWindowTitle(f"Обновление данных студента {student[4]}")
        self.result = QLabel(self)
        self.layout.addWidget(self.result)
        self.button.clicked.connect(self.update_student)

    def update_student(self):
        with self.connection as connection:
            first_name = self.first_name_edit.text()
            if not first_name.isalpha():
                self.first_name_edit.setFocus()
                self.result.setText("Имя должно содержать только буквы")
                return
            last_name = self.last_name_edit.text()
            if not last_name.isalpha():
                self.last_name_edit.setFocus()
                self.result.setText("Фамилия должна содержать только буквы")
                return
            middle_name = self.middle_name_edit.text()
            if not middle_name.isalpha() and middle_name != "":
                self.middle_name_edit.setFocus()
                self.result.setText("Отчество должна содержать только буквы")
                return
            group = self.group_combo.currentData()
            with connection.cursor() as cursor:
                cursor.execute(
                    "select * from update_student(%s, %s, %s, %s, %s)",
                    (self.student_id, first_name, last_name, middle_name, group),
                )
                connection.commit()
            self.group_window.show_group_info()
            self.close()
