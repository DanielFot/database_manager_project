# Database Manager Project

This project is a small SQLite-based database manager for storing information about user projects, their statuses, and related skills.

## Features

- creates the required SQLite tables automatically
- fills the database with default statuses and skills
- adds new projects to the database
- links projects with skills
- gets project information, statuses, and skills
- updates or deletes saved project data

## Project Files

- `logic.py` contains the `DB_Manager` class and database operations
- `config.py` stores the database file name

## How to Run

Run the script to create the tables and insert the default data:

```bash
python logic.py
```

The database file is created according to the `DATABASE` value in `config.py`.
