# Portfolio Bot

> A bright Telegram bot for storing your personal portfolio projects, links, skills, statuses, and project photos in one place.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-0F80CC?style=for-the-badge&logo=sqlite&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Portfolio](https://img.shields.io/badge/Project-Portfolio%20Manager-FF7A59?style=for-the-badge)

## About the Project

Portfolio Bot helps collect all your projects in one Telegram interface.  
You can save a project name, description, GitHub link, current status, related skills, and even a photo for each project.

This project combines:

- a Telegram bot interface in `main.py`
- SQLite database logic in `logic.py`
- a ready-to-use local database in `projects.db`
- project images stored in `project_photos/`

## Preview

Here is an example of a project image saved by the bot:

![Portfolio Bot Project Preview](project_photos/user_148391004_project_10.jpg)

## Features

- `📁` create and store portfolio projects
- `📝` edit project descriptions quickly
- `🔗` save project links
- `🖼️` attach a photo to a project
- `🧠` connect projects with skills
- `🧭` manage project statuses
- `🗑️` delete projects you no longer need
- `💾` keep everything in SQLite

## Bot Commands

| Command | Description |
| --- | --- |
| `/start` | Start the bot |
| `/info` | Show the help menu |
| `/new_project` | Add a new project |
| `/projects` | Show all saved projects |
| `/skills` | Add a skill to a chosen project |
| `/set_description` | Update a project description |
| `/set_photo` | Upload a project photo |
| `/update_projects` | Edit project name, description, link, photo, or status |
| `/delete` | Delete a selected project |
| `/new_status` | Add a new status |
| `/rename_status` | Rename an existing status |
| `/new_skill` | Add a new skill |
| `/rename_skill` | Rename an existing skill |

## Project Structure

```text
database_manager_project/
|-- config.py
|-- logic.py
|-- main.py
|-- projects.db
|-- project_photos/
`-- README.md
```

## Quick Start

1. Install Python 3.11 or newer.
2. Install the Telegram library:

```bash
pip install pyTelegramBotAPI
```

3. Open `config.py` and replace `YOUR_TOKEN_HERE` with your Telegram bot token.
4. Start the bot:

```bash
python main.py
```

## Notes

- `projects.db` is tracked in the repository, so the saved project data is included on GitHub.
- `test_projects.db` is not tracked.
- If `config.py` still contains `YOUR_TOKEN_HERE`, the bot will not start polling until you add a real token.
