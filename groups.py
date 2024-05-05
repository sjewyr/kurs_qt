from PyQt5.QtWidgets import (
    QMainWindow,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QWidget,
    QHBoxLayout,
    QListWidgetItem,
    QMessageBox,
)
import psycopg2
from connection import ConnectionManager
from grades import GradeWindow
from addgroup import AddGroupWindow
from updategroup import UpdateGroupWindow
from updatestudent import UpdateStudentWindow
from add_student import AddStudentWindow
from utils import get_groups


class GroupWindow(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.setWindowTitle("Группы")
        self.setGeometry(100, 100, 800, 700)
        layout = QVBoxLayout()
        self.connection: ConnectionManager = connection
        self.group_combo = QComboBox(self)
        self.group_combo.setEditable(True)
        self.group_combo.setInsertPolicy(QComboBox.NoInsert)
        self.group_combo.lineEdit().setClearButtonEnabled(True)
        self.update_groups()

        self.button = QPushButton("Информация о группе", self)
        self.button.clicked.connect(self.show_group_info)
        self.list_widget = QListWidget(self)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(layout)
        layout.addWidget(self.group_combo)
        layout.addWidget(self.button)
        layout.addWidget(self.list_widget)
        if self.connection.user == "teacher":
            self.add_group_button = QPushButton("Добавить группу", self)
            self.delete_group_button = QPushButton("Удалить группу", self)
            self.update_group_button = QPushButton("Переименовать группу", self)
            layout.addWidget(self.add_group_button)
            self.add_group_button.clicked.connect(self.add_group)
            layout.addWidget(self.delete_group_button)
            self.delete_group_button.clicked.connect(self.delete_group)
            layout.addWidget(self.update_group_button)
            self.update_group_button.clicked.connect(self.update_group)

    def add_group(self):
        self.add_group_window = AddGroupWindow(self.connection, self)
        self.add_group_window.show()

    def show_group_info(self):
        self.list_widget.clear()
        group_id = self.group_combo.currentData()
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    (
                        "select studentid, firstname, surname, patronymic, cardid from students where groupid = %s ORDER BY surname"
                    ),
                    (group_id,),
                )
                data = cursor.fetchall()
        for row in data:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)

            # Текстовая метка с именем
            label = QLabel(
                " ".join(
                    [row["surname"], row["firstname"], row["patronymic"], row["cardid"]]
                )
            )
            item_layout.addWidget(label)

            button = QPushButton("Перейти к оценкам")
            button.clicked.connect(lambda _, id=row["studentid"]: self.show_grades(id))
            item_layout.addWidget(button)
            if self.connection.user == "teacher":
                button = QPushButton("Изменить")
                button.clicked.connect(
                    lambda _, id=row["studentid"]: self.update_student(id)
                )
                item_layout.addWidget(button)
                button = QPushButton("Удалить")
                button.clicked.connect(
                    lambda _, id=row["studentid"]: self.delete_student(id)
                )
                item_layout.addWidget(button)

            # Устанавливаем item_widget в качестве виджета элемента
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

        item = QListWidgetItem()
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        button = QPushButton("Добавить студента")
        button.clicked.connect(self.add_student)
        item_layout.addWidget(button)
        item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)

    def show_grades(self, id):
        self.grade_window = GradeWindow(self.connection, id)
        self.grade_window.show()

    def update_groups(self):
        self.group_combo.clear()
        groups = get_groups(self.connection)
        for group in groups:
            self.group_combo.addItem(group[0], group[1])

    def delete_group(self):
        confirm = QMessageBox()
        confirm.setWindowTitle("Удаление группы")
        confirm.setText("Вы уверены, что хотите удалить группу?")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm.setDefaultButton(QMessageBox.No)

        response = confirm.exec_()
        if response == QMessageBox.No:
            return
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select * from delete_group(%s)", (self.group_combo.currentData(),)
                )
                cursor.connection.commit()
                print("Yahoo")
        self.group_combo.removeItem(self.group_combo.currentIndex())
        self.update_groups()

    def update_group(self):
        self.update_group_window = UpdateGroupWindow(
            self.connection, self, self.group_combo.currentData()
        )
        self.update_group_window.show()

    def update_student(self, id):
        self.update_student_window = UpdateStudentWindow(self.connection, self, id)
        self.update_student_window.show()

    def delete_student(self, id):
        confirm = QMessageBox()
        confirm.setWindowTitle("Удаление студента")
        confirm.setText("Вы уверены, что хотите удалить студента?")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm.setDefaultButton(QMessageBox.No)
        response = confirm.exec_()
        if response == QMessageBox.No:
            return
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("select * from delete_student(%s)", (id,))
                cursor.connection.commit()

        self.show_group_info()

    def add_student(self):
        self.add_student_window = AddStudentWindow(
            self.connection, self, self.group_combo.currentData()
        )
        self.add_student_window.show()
