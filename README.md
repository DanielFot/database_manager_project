# Database Manager Project

This project is a small SQLite-based database manager for storing information about user projects, their statuses, and related skills.

## Features

- creates the required SQLite tables automatically
- fills the database with default statuses and skills
- adds new projects to the database
- links projects with skills
- gets project information, statuses, and skills
- updates or deletes saved project data
- includes a populated `projects.db` file with saved project entries

## Project Files

- `logic.py` contains the `DB_Manager` class and database operations
- `config.py` stores the database file name
- `projects.db` contains the current saved project data

## How to Run

Run the script to create the tables and insert the default data:

```bash
python logic.py
```

The database file is created according to the `DATABASE` value in `config.py`.

## Notes

The repository keeps `projects.db` under version control so the current project information is included in GitHub.
The separate `test_projects.db` file is not tracked.
