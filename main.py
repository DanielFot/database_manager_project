from pathlib import Path

from config import DATABASE, TOKEN
from logic import DB_Manager
from telebot import TeleBot, types
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


PHOTO_DIR = Path("project_photos")


def has_real_token():
    return TOKEN != "YOUR_TOKEN_HERE" and ":" in TOKEN


bot = TeleBot(TOKEN if has_real_token() else "0:TEST_TOKEN")
manager = DB_Manager(DATABASE)
hideBoard = types.ReplyKeyboardRemove()

cancel_button = "Отмена 🚫"


def cansel(message):
    bot.send_message(
        message.chat.id,
        "Действие отменено. Чтобы посмотреть команды, используй /info.",
        reply_markup=hideBoard,
    )


def no_projects(message):
    bot.send_message(
        message.chat.id,
        "📭 У тебя пока нет проектов.\nДобавь первый проект командой /new_project.",
    )


def gen_inline_markup(rows):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for row in rows:
        markup.add(InlineKeyboardButton(f"🔎 {row}", callback_data=row))
    return markup


def gen_markup(rows):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup


def get_user_project_names(user_id):
    return [project[2] for project in manager.get_projects(user_id)]


def save_project_photo(message, project_name):
    PHOTO_DIR.mkdir(exist_ok=True)
    project_id = manager.get_project_id(project_name, message.from_user.id)
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    extension = Path(file_info.file_path).suffix or ".jpg"
    file_name = f"user_{message.from_user.id}_project_{project_id}{extension}"
    file_path = PHOTO_DIR / file_name
    file_path.write_bytes(downloaded_file)
    return str(file_path)


attributes_of_projects = {
    "Имя проекта ✏️": ["Введите новое имя проекта", "project_name"],
    "Описание 📝": ["Введите новое описание проекта", "description"],
    "Ссылка 🔗": ["Введите новую ссылку на проект", "url"],
    "Фото 🖼️": ["Отправьте новое фото проекта", "photo"],
    "Статус 🧭": ["Выберите новый статус проекта", "status_id"],
}


def info_project(message, user_id, project_name):
    info = manager.get_project_info(user_id, project_name)
    if not info:
        bot.send_message(message.chat.id, "Проект не найден.")
        return

    info = info[0]
    skills = manager.get_project_skills(project_name) or "Навыки пока не добавлены"
    photo = info[3] or "Фото пока не добавлено"
    text = f"""📌 Проект: {info[0]}

📝 Описание:
{info[1]}

🔗 Ссылка:
{info[2]}

🖼️ Фото:
{photo}

🧭 Статус: {info[4]}
🧰 Навыки: {skills}
"""
    if info[3] and Path(info[3]).exists():
        with open(info[3], "rb") as photo_file:
            bot.send_photo(message.chat.id, photo_file, caption=text)
    else:
        bot.send_message(message.chat.id, text)


# Handles /start and shows the main greeting.
@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я Portfolio Bot.\nЯ помогу хранить проекты, ссылки, фото, статусы и навыки.",
    )
    info(message)


# Handles /info and explains every available bot command.
@bot.message_handler(commands=["info"])
def info(message):
    bot.send_message(
        message.chat.id,
        """📚 Команды Portfolio Bot

/new_project - добавить проект с названием, описанием, ссылкой и статусом
/projects - показать список проектов и открыть карточку проекта
/skills - добавить навык к выбранному проекту
/set_description - быстро изменить описание проекта
/set_photo - загрузить фото проекта на компьютер и сохранить путь в базе
/update_projects - изменить название, описание, ссылку, фото или статус проекта
/delete - удалить выбранный проект
/new_status - добавить новый статус в справочник
/rename_status - переименовать существующий статус
/new_skill - добавить новый навык в справочник
/rename_skill - переименовать существующий навык
/info - показать это меню

Можно также просто отправить название проекта, и я покажу его карточку.""",
    )


# Handles /new_project and starts project creation.
@bot.message_handler(commands=["new_project"])
def addtask_command(message):
    bot.send_message(message.chat.id, "🆕 Введите название проекта:")
    bot.register_next_step_handler(message, name_project)


def name_project(message):
    if message.text == cancel_button:
        cansel(message)
        return
    data = [message.from_user.id, message.text]
    bot.send_message(message.chat.id, "📝 Введите описание проекта:")
    bot.register_next_step_handler(message, description_project, data=data)


def description_project(message, data):
    if message.text == cancel_button:
        cansel(message)
        return
    data.append(message.text)
    bot.send_message(message.chat.id, "🔗 Введите ссылку на проект:")
    bot.register_next_step_handler(message, link_project, data=data)


def link_project(message, data):
    if message.text == cancel_button:
        cansel(message)
        return
    data.append(message.text)
    statuses = [x[0] for x in manager.get_statuses()]
    bot.send_message(
        message.chat.id,
        "🧭 Выберите текущий статус проекта:",
        reply_markup=gen_markup(statuses),
    )
    bot.register_next_step_handler(
        message, callback_project, data=data, statuses=statuses
    )


def callback_project(message, data, statuses):
    status = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if status not in statuses:
        bot.send_message(
            message.chat.id,
            "Такого статуса нет в списке. Выберите статус кнопкой.",
            reply_markup=gen_markup(statuses),
        )
        bot.register_next_step_handler(
            message, callback_project, data=data, statuses=statuses
        )
        return
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    bot.send_message(message.chat.id, "✅ Проект сохранен.", reply_markup=hideBoard)


# Handles /skills and starts adding a skill to a project.
@bot.message_handler(commands=["skills"])
def skill_handler(message):
    projects = get_user_project_names(message.from_user.id)
    if projects:
        bot.send_message(
            message.chat.id,
            "🧰 Выбери проект, которому нужно добавить навык:",
            reply_markup=gen_markup(projects),
        )
        bot.register_next_step_handler(message, skill_project, projects=projects)
    else:
        no_projects(message)


def skill_project(message, projects):
    project_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return

    if project_name not in projects:
        bot.send_message(
            message.chat.id,
            "У тебя нет такого проекта. Выбери проект из списка.",
            reply_markup=gen_markup(projects),
        )
        bot.register_next_step_handler(message, skill_project, projects=projects)
        return

    skills = [x[1] for x in manager.get_skills()]
    bot.send_message(message.chat.id, "Выбери навык:", reply_markup=gen_markup(skills))
    bot.register_next_step_handler(
        message, set_skill, project_name=project_name, skills=skills
    )


def set_skill(message, project_name, skills):
    skill = message.text
    if message.text == cancel_button:
        cansel(message)
        return

    if skill not in skills:
        bot.send_message(
            message.chat.id,
            "Такого навыка нет в списке. Выбери навык кнопкой.",
            reply_markup=gen_markup(skills),
        )
        bot.register_next_step_handler(
            message, set_skill, project_name=project_name, skills=skills
        )
        return
    manager.insert_skill(message.from_user.id, project_name, skill)
    bot.send_message(message.chat.id, f"✅ Навык {skill} добавлен проекту {project_name}.")


# Handles /projects and shows all projects for the current user.
@bot.message_handler(commands=["projects"])
def get_projects(message):
    projects = manager.get_projects(message.from_user.id)
    if projects:
        text = "\n".join([f"📌 {x[2]}\n🔗 {x[4]}\n" for x in projects])
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=gen_inline_markup([x[2] for x in projects]),
        )
    else:
        no_projects(message)


# Handles inline project buttons and opens the project card.
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    info_project(call.message, call.from_user.id, call.data)


# Handles /delete and starts project deletion.
@bot.message_handler(commands=["delete"])
def delete_handler(message):
    projects = get_user_project_names(message.from_user.id)
    if projects:
        bot.send_message(
            message.chat.id,
            "🗑️ Выбери проект, который нужно удалить:",
            reply_markup=gen_markup(projects),
        )
        bot.register_next_step_handler(message, delete_project, projects=projects)
    else:
        no_projects(message)


def delete_project(message, projects):
    project = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        cansel(message)
        return
    if project not in projects:
        bot.send_message(
            message.chat.id,
            "У тебя нет такого проекта. Выбери проект из списка.",
            reply_markup=gen_markup(projects),
        )
        bot.register_next_step_handler(message, delete_project, projects=projects)
        return
    project_id = manager.get_project_id(project, user_id)
    manager.delete_project(user_id, project_id)
    bot.send_message(message.chat.id, f"🗑️ Проект {project} удален.", reply_markup=hideBoard)


# Handles /set_description and starts quick description editing.
@bot.message_handler(commands=["set_description"])
def set_description_handler(message):
    projects = get_user_project_names(message.from_user.id)
    if projects:
        bot.send_message(
            message.chat.id,
            "📝 Выбери проект для нового описания:",
            reply_markup=gen_markup(projects),
        )
        bot.register_next_step_handler(message, choose_description_project, projects=projects)
    else:
        no_projects(message)


def choose_description_project(message, projects):
    if message.text == cancel_button:
        cansel(message)
        return
    if message.text not in projects:
        bot.send_message(message.chat.id, "Выбери проект из списка.", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, choose_description_project, projects=projects)
        return
    bot.send_message(message.chat.id, "Введите новое описание проекта:")
    bot.register_next_step_handler(message, save_description, project_name=message.text)


def save_description(message, project_name):
    if message.text == cancel_button:
        cansel(message)
        return
    manager.update_projects("description", (message.text, project_name, message.from_user.id))
    bot.send_message(message.chat.id, "✅ Описание обновлено.", reply_markup=hideBoard)


# Handles /set_photo and starts project photo upload.
@bot.message_handler(commands=["set_photo"])
def set_photo_handler(message):
    projects = get_user_project_names(message.from_user.id)
    if projects:
        bot.send_message(
            message.chat.id,
            "🖼️ Выбери проект для фото:",
            reply_markup=gen_markup(projects),
        )
        bot.register_next_step_handler(message, choose_photo_project, projects=projects)
    else:
        no_projects(message)


def choose_photo_project(message, projects):
    if message.text == cancel_button:
        cansel(message)
        return
    if message.text not in projects:
        bot.send_message(message.chat.id, "Выбери проект из списка.", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, choose_photo_project, projects=projects)
        return
    bot.send_message(message.chat.id, "Отправьте фото проекта:")
    bot.register_next_step_handler(message, save_photo, project_name=message.text)


def save_photo(message, project_name):
    if message.text == cancel_button:
        cansel(message)
        return
    if not message.photo:
        bot.send_message(message.chat.id, "Нужно отправить именно фото. Попробуйте еще раз.")
        bot.register_next_step_handler(message, save_photo, project_name=project_name)
        return
    file_path = save_project_photo(message, project_name)
    manager.update_projects("photo", (file_path, project_name, message.from_user.id))
    bot.send_message(message.chat.id, "✅ Фото сохранено.", reply_markup=hideBoard)


# Handles /update_projects and starts the general project update flow.
@bot.message_handler(commands=["update_projects"])
def update_project(message):
    projects = get_user_project_names(message.from_user.id)
    if projects:
        bot.send_message(
            message.chat.id,
            "⚙️ Выбери проект, который хочешь изменить:",
            reply_markup=gen_markup(projects),
        )
        bot.register_next_step_handler(
            message, update_project_step_2, projects=projects
        )
    else:
        no_projects(message)


def update_project_step_2(message, projects):
    project_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if project_name not in projects:
        bot.send_message(
            message.chat.id,
            "Выбери проект из списка.",
            reply_markup=gen_markup(projects),
        )
        bot.register_next_step_handler(
            message, update_project_step_2, projects=projects
        )
        return
    bot.send_message(
        message.chat.id,
        "Что изменить в проекте?",
        reply_markup=gen_markup(attributes_of_projects.keys()),
    )
    bot.register_next_step_handler(
        message, update_project_step_3, project_name=project_name
    )


def update_project_step_3(message, project_name):
    attribute = message.text
    reply_markup = None
    if message.text == cancel_button:
        cansel(message)
        return
    if attribute not in attributes_of_projects.keys():
        bot.send_message(
            message.chat.id,
            "Выбери действие из списка.",
            reply_markup=gen_markup(attributes_of_projects.keys()),
        )
        bot.register_next_step_handler(
            message, update_project_step_3, project_name=project_name
        )
        return
    if attribute == "Статус 🧭":
        reply_markup = gen_markup([x[0] for x in manager.get_statuses()])
    bot.send_message(
        message.chat.id, attributes_of_projects[attribute][0], reply_markup=reply_markup
    )
    bot.register_next_step_handler(
        message,
        update_project_step_4,
        project_name=project_name,
        attribute=attributes_of_projects[attribute][1],
    )


def update_project_step_4(message, project_name, attribute):
    update_info = message.text
    if attribute == "photo" and message.photo:
        update_info = save_project_photo(message, project_name)
    elif attribute == "photo" and update_info == cancel_button:
        cansel(message)
        return
    elif attribute == "status_id":
        rows = manager.get_statuses()
        if update_info in [x[0] for x in rows]:
            update_info = manager.get_status_id(update_info)
        elif update_info == cancel_button:
            cansel(message)
            return
        else:
            bot.send_message(
                message.chat.id,
                "Выбран неверный статус. Попробуй еще раз.",
                reply_markup=gen_markup([x[0] for x in rows]),
            )
            bot.register_next_step_handler(
                message,
                update_project_step_4,
                project_name=project_name,
                attribute=attribute,
            )
            return
    elif update_info == cancel_button:
        cansel(message)
        return
    manager.update_projects(attribute, (update_info, project_name, message.from_user.id))
    bot.send_message(message.chat.id, "✅ Обновления внесены.", reply_markup=hideBoard)


# Handles /new_status and creates a new status option.
@bot.message_handler(commands=["new_status"])
def new_status_handler(message):
    bot.send_message(message.chat.id, "🧭 Введите новый статус:")
    bot.register_next_step_handler(message, save_new_status)


def save_new_status(message):
    if message.text == cancel_button:
        cansel(message)
        return
    manager.insert_status(message.text)
    bot.send_message(message.chat.id, "✅ Статус добавлен.")


# Handles /rename_status and starts status renaming.
@bot.message_handler(commands=["rename_status"])
def rename_status_handler(message):
    statuses = [x[0] for x in manager.get_statuses()]
    bot.send_message(message.chat.id, "Выберите статус:", reply_markup=gen_markup(statuses))
    bot.register_next_step_handler(message, choose_status_to_rename, statuses=statuses)


def choose_status_to_rename(message, statuses):
    if message.text == cancel_button:
        cansel(message)
        return
    if message.text not in statuses:
        bot.send_message(message.chat.id, "Выбери статус из списка.", reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, choose_status_to_rename, statuses=statuses)
        return
    bot.send_message(message.chat.id, "Введите новое название статуса:")
    bot.register_next_step_handler(message, save_renamed_status, old_status=message.text)


def save_renamed_status(message, old_status):
    if message.text == cancel_button:
        cansel(message)
        return
    manager.update_status(old_status, message.text)
    bot.send_message(message.chat.id, "✅ Статус переименован.")


# Handles /new_skill and creates a new skill option.
@bot.message_handler(commands=["new_skill"])
def new_skill_handler(message):
    bot.send_message(message.chat.id, "🧰 Введите новый навык:")
    bot.register_next_step_handler(message, save_new_skill)


def save_new_skill(message):
    if message.text == cancel_button:
        cansel(message)
        return
    manager.insert_skill_name(message.text)
    bot.send_message(message.chat.id, "✅ Навык добавлен.")


# Handles /rename_skill and starts skill renaming.
@bot.message_handler(commands=["rename_skill"])
def rename_skill_handler(message):
    skills = [x[1] for x in manager.get_skills()]
    bot.send_message(message.chat.id, "Выберите навык:", reply_markup=gen_markup(skills))
    bot.register_next_step_handler(message, choose_skill_to_rename, skills=skills)


def choose_skill_to_rename(message, skills):
    if message.text == cancel_button:
        cansel(message)
        return
    if message.text not in skills:
        bot.send_message(message.chat.id, "Выбери навык из списка.", reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, choose_skill_to_rename, skills=skills)
        return
    bot.send_message(message.chat.id, "Введите новое название навыка:")
    bot.register_next_step_handler(message, save_renamed_skill, old_skill=message.text)


def save_renamed_skill(message, old_skill):
    if message.text == cancel_button:
        cansel(message)
        return
    manager.update_skill_name(old_skill, message.text)
    bot.send_message(message.chat.id, "✅ Навык переименован.")


# Handles any text that is not a command and tries to open a project by name.
@bot.message_handler(func=lambda message: True)
def text_handler(message):
    project = message.text
    if project in get_user_project_names(message.from_user.id):
        info_project(message, message.from_user.id, project)
        return
    bot.reply_to(message, "Нужна помощь? Открой меню /info.")


if __name__ == "__main__":
    manager.create_tables()
    manager.add_photo_column()
    manager.default_insert()
    if has_real_token():
        bot.infinity_polling()
    else:
        print("Set a real Telegram bot token in config.py before starting the bot.")
