## Установка
Для установки необходимо создать виртуальное окружение, установить зависимости и восстановить базу данных из бэкапа с именем students  

# Установка зависимостей
python -m venv venv  
venv\Scripts\activate  
pip install -r requirements.txt  
# Восстановление из бекапа  
cd "c:\Program Files\PostgreSQL\16\bin"  
createdb -U USERNAME students  
psql.exe -U postgres -d students -f BACKUP_FILE_PATH\roles.sql
psql.exe -U postgres -d students -f BACKUP_FILE_PATH\backup.sql

