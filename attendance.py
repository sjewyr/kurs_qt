from PyQt5.QtWidgets import (
    QMainWindow,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QListWidgetItem,
    QListWidget,
)
import psycopg2


class AttendanceWindow(QMainWindow):
    def __init__(self, connection, group_id, date, seq):
        super().__init__()
        self.connection = connection
        self.group_id = group_id
        self.date = date
        self.seq = seq
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Посещаемость")
        self.setGeometry(100, 100, 300, 150)
        self.layout = QVBoxLayout()
        self.label = QLabel("Ошибка", self)
        self.list_widget = QListWidget(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)
        self.view_attendance()

    def view_attendance(self):
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    ("Select * from get_attendance_info(%s, %s, %s)"),
                    (self.group_id, self.date, self.seq),
                )
                data = cursor.fetchall()
                for row in data:
                    row = dict(row)
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT groupname FROM groups WHERE groupid = %s", (self.group_id,)
                )
                group = cursor.fetchone()
                cursor.execute(
                    "SELECT subject FROM groupattendance WHERE groupid = %s AND date = %s AND num = %s",
                    (self.group_id, self.date, self.seq),
                )
                subject = cursor.fetchone()
        if data:
            self.label.setText(
                f"Посещаемость группы {group[0]} на {self.seq} занятии {self.date} по предмету {subject[0]}"
            )
        else:
            self.label.setText(
                f"Занятие в группе {group[0]} на {self.seq} занятии {self.date} не запланировано"
            )
        self.list_widget.clear()
        # Создаем элементы списка
        for row in data:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)

            # Текстовая метка с именем
            label = QLabel(
                " ".join(
                    [row["firstname"], row["surname"], row["patronymic"], row["cardid"]]
                )
            )
            item_layout.addWidget(label)

            # ComboBox с текущим значением
            combo_box = QComboBox()
            combo_box.addItems(["Н", "У", "+"])
            combo_box.setCurrentText(row["status"])
            item_layout.addWidget(combo_box)
            if self.connection.user == "teacher":
                # Кнопка для отправки изменений в базу данных
                button = QPushButton("Отметить")
                button.clicked.connect(
                    lambda _, id=row[
                        "attendanceid"
                    ], combo_box=combo_box: self.update_attendance(
                        id, combo_box.currentText()
                    )
                )
                item_layout.addWidget(button)
            else:
                combo_box.setDisabled(True)

            # Устанавливаем item_widget в качестве виджета элемента
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

    def update_attendance(self, attendance_id, status):
        try:
            with self.connection as connection:
                with connection.cursor() as cursor:
                    print(status, attendance_id)
                    cursor.callproc("update_attendance", (attendance_id, status))
                    connection.commit()
        except Exception:
            print("Ошибка при обновлении данных")
