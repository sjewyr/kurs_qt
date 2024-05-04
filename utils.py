def get_groups(connection):
    with connection as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT groupname, groupid FROM groups ORDER BY groupname;")
            groups = cursor.fetchall()
    return groups
