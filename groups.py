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
)
import psycopg2
from connection import ConnectionManager
from grades import GradeWindow


class GroupWindow(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.setWindowTitle("Группы")
        self.setGeometry(100, 100, 800, 700)
        layout = QVBoxLayout()
        self.connection: ConnectionManager = connection
        self.group_combo = QComboBox(self)
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT groupname, groupid FROM groups")
                groups = cursor.fetchall()
                for group in groups:
                    self.group_combo.addItem(group[0], group[1])

        self.button = QPushButton("Информация о группе", self)
        self.button.clicked.connect(self.show_group_info)
        self.list_widget = QListWidget(self)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(layout)
        layout.addWidget(self.group_combo)
        layout.addWidget(self.button)
        layout.addWidget(self.list_widget)

    def show_group_info(self):
        self.list_widget.clear()
        group_id = self.group_combo.currentData()
        with self.connection as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    (
                        "select studentid, firstname, surname, patronymic, cardid from students where groupid = %s"
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
                    [row["firstname"], row["surname"], row["patronymic"], row["cardid"]]
                )
            )
            item_layout.addWidget(label)

            button = QPushButton("Перейти к оценкам")
            button.clicked.connect(lambda _, id=row["studentid"]: self.show_grades(id))
            item_layout.addWidget(button)

            # Устанавливаем item_widget в качестве виджета элемента
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

    def show_grades(self, id):
        self.grade_window = GradeWindow(self.connection, id)
        self.grade_window.show()
