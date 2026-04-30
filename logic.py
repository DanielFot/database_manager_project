import sqlite3

from config import DATABASE


skills = [(_,) for _ in (["Python", "SQL", "API", "Telegram"])]
statuses = [
    (_,)
    for _ in (
        [
            "На этапе проектирования",
            "В процессе разработки",
            "Разработан. Готов к использованию.",
            "Обновлен",
            "Завершен. Не поддерживается",
        ]
    )
]


class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute(
                """CREATE TABLE IF NOT EXISTS status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT UNIQUE
                        )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT UNIQUE
                        )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            photo TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            UNIQUE(project_id, skill_id),
                            FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
                        )"""
            )
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    def default_insert(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            for skill in skills:
                cur.execute("SELECT skill_id FROM skills WHERE skill_name = ?", skill)
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO skills (skill_name) VALUES(?)", skill)
            for status in statuses:
                cur.execute("SELECT status_id FROM status WHERE status_name = ?", status)
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO status (status_name) VALUES(?)", status)
            conn.commit()

    def add_photo_column(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(projects)")
            columns = [column[1] for column in cur.fetchall()]
            if "photo" not in columns:
                cur.execute("ALTER TABLE projects ADD COLUMN photo TEXT")
                conn.commit()

    def insert_project(self, data):
        sql = """
        INSERT INTO projects (user_id, project_name, description, url, status_id)
        VALUES (?, ?, ?, ?, ?)
        """
        self.__executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill):
        sql = "SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?"
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        skill_id = self.__select_data(
            "SELECT skill_id FROM skills WHERE skill_name = ?", (skill,)
        )[0][0]
        data = [(project_id, skill_id)]
        sql = "INSERT OR IGNORE INTO project_skills VALUES(?, ?)"
        self.__executemany(sql, data)

    def insert_status(self, status_name):
        sql = "INSERT INTO status (status_name) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM status WHERE status_name = ?)"
        self.__executemany(sql, [(status_name, status_name)])

    def update_status(self, old_status_name, new_status_name):
        sql = "UPDATE status SET status_name = ? WHERE status_name = ?"
        self.__executemany(sql, [(new_status_name, old_status_name)])

    def insert_skill_name(self, skill_name):
        sql = "INSERT INTO skills (skill_name) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM skills WHERE skill_name = ?)"
        self.__executemany(sql, [(skill_name, skill_name)])

    def update_skill_name(self, old_skill_name, new_skill_name):
        sql = "UPDATE skills SET skill_name = ? WHERE skill_name = ?"
        self.__executemany(sql, [(new_skill_name, old_skill_name)])

    def get_statuses(self):
        sql = "SELECT status_name FROM status"
        return self.__select_data(sql)

    def get_status_id(self, status_name):
        sql = "SELECT status_id FROM status WHERE status_name = ?"
        res = self.__select_data(sql, (status_name,))
        if res:
            return res[0][0]
        return None

    def get_projects(self, user_id):
        sql = "SELECT * FROM projects WHERE user_id = ?"
        return self.__select_data(sql, data=(user_id,))

    def get_project_id(self, project_name, user_id):
        return self.__select_data(
            sql="SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?",
            data=(project_name, user_id),
        )[0][0]

    def get_skills(self):
        return self.__select_data(sql="SELECT * FROM skills")

    def get_project_skills(self, project_name):
        res = self.__select_data(
            sql="""SELECT skill_name FROM projects
JOIN project_skills ON projects.project_id = project_skills.project_id
JOIN skills ON skills.skill_id = project_skills.skill_id
WHERE project_name = ?""",
            data=(project_name,),
        )
        return ", ".join([x[0] for x in res])

    def get_project_info(self, user_id, project_name):
        sql = """
SELECT project_name, description, url, photo, status_name FROM projects
JOIN status ON
status.status_id = projects.status_id
WHERE project_name = ? AND user_id = ?
"""
        return self.__select_data(sql=sql, data=(project_name, user_id))

    def update_projects(self, param, data):
        allowed_params = {"project_name", "description", "url", "photo", "status_id"}
        if param not in allowed_params:
            raise ValueError("Invalid column name for update")
        sql = f"UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?"
        self.__executemany(sql, [data])

    def delete_project(self, user_id, project_id):
        sql = "DELETE FROM projects WHERE user_id = ? AND project_id = ?"
        self.__executemany(sql, [(user_id, project_id)])

    def delete_skill(self, project_id, skill_id):
        sql = "DELETE FROM project_skills WHERE skill_id = ? AND project_id = ?"
        self.__executemany(sql, [(skill_id, project_id)])


if __name__ == "__main__":
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    manager.add_photo_column()
    manager.default_insert()
