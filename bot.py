# ============================================================
# КОНФЛИКТ-СИМУЛЯТОР v5.0 (статистика без прогресс-баров)
# ============================================================

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# ============================================================
# НАСТРОЙКИ
# ============================================================
BOT_TOKEN = "8992148041:AAG5p6UwlzTsrP6PT-0KQY47MoGvqznPz9A"   # ← замените!

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============================================================
# СООТВЕТСТВИЕ СТИЛЕЙ
# ============================================================
STYLE_LABELS = {
    "Соперничество": "Докажу, что я прав",
    "Избегание": "Промолчу / уйду от разговора",
    "Приспособление": "Уступлю, чтобы не ссориться",
    "Компромисс": "Договоримся по-честному",
    "Сотрудничество": "Найдём решение вместе"
}

# ============================================================
# СЦЕНАРИИ
# ============================================================
SCENARIOS = {
    "friend_thing": {
        "title": "🎧 Друг взял твою вещь без спроса",
        "description": (
            "Ты приходишь домой и видишь, что твой друг взял твои наушники "
            "без разрешения. Он уже ушёл. Ты пишешь ему в мессенджере."
        ),
        "relation_start": 70,
        "choices": [
            {
                "style": "Соперничество",
                "text": "«Ты вообще обнаглел! Верни немедленно, иначе я тебе больше ничего не дам!»",
                "consequence": "Друг обиделся. Вы поссорились на неделю. Он вернул наушники, но осадок остался.",
                "relation_change": -30
            },
            {
                "style": "Избегание",
                "text": "«Ладно, ничего страшного...» (а внутри ты злишься)",
                "consequence": "Ты промолчал, но обида копится. В следующий раз он снова возьмёт без спроса.",
                "relation_change": -10
            },
            {
                "style": "Приспособление",
                "text": "«Да забирай, мне не жалко» (хотя тебе неприятно)",
                "consequence": "Друг привыкает, что твои границы можно нарушать. Ты чувствуешь себя использованным.",
                "relation_change": -15
            },
            {
                "style": "Компромисс",
                "text": "«Ок, но в следующий раз предупреди. Мне тоже нужны наушники.»",
                "consequence": "Друг согласился. Вы договорились. Отношения сохранились.",
                "relation_change": +5
            },
            {
                "style": "Сотрудничество",
                "text": "«Я расстроился, что ты не спросил. Мне важно, чтобы мои вещи спрашивали. Давай в следующий раз ты предупредишь, и я с радостью дам.»",
                "consequence": "Друг извинился. Вы стали ближе, потому что ты честно сказал о своих чувствах.",
                "relation_change": +20
            }
        ]
    },
    "parents_party": {
        "title": "🎉 Родители не пускают на вечеринку",
        "description": (
            "Ты хочешь пойти на вечеринку к другу, но родители против. "
            "Они говорят: «Там будут взрослые ребята, мы волнуемся»."
        ),
        "relation_start": 60,
        "choices": [
            {
                "style": "Соперничество",
                "text": "«Вы меня не понимаете! Я всё равно пойду!»",
                "consequence": "Скандал. Родители запретили выходить из дома на месяц.",
                "relation_change": -35
            },
            {
                "style": "Избегание",
                "text": "«Ладно, не пойду» (и молча ушёл в комнату)",
                "consequence": "Ты остался дома, но обида на родителей осталась. Вы не поговорили.",
                "relation_change": -15
            },
            {
                "style": "Приспособление",
                "text": "«Хорошо, я останусь» (хотя очень хотел пойти)",
                "consequence": "Ты уступил, но чувствуешь разочарование. Родители даже не поняли, как это было важно для тебя.",
                "relation_change": -10
            },
            {
                "style": "Компромисс",
                "text": "«Давайте я пойду на два часа, буду писать каждые полчаса, и вы меня встретите.»",
                "consequence": "Родители согласились. Ты пошёл, они были спокойны.",
                "relation_change": +10
            },
            {
                "style": "Сотрудничество",
                "text": "«Я понимаю, что вы волнуетесь. Для меня это важно, потому что там будут мои друзья. Давайте вместе придумаем, как сделать так, чтобы вы были спокойны, а я пошёл.»",
                "consequence": "Родители оценили твою зрелость. Вы договорились: ты идёшь, но с условиями, которые устроили всех.",
                "relation_change": +25
            }
        ]
    },
    "teacher_grade": {
        "title": "📝 Учитель несправедливо поставил двойку",
        "description": (
            "Ты готовился к контрольной, но учитель поставил двойку. "
            "Ты уверен, что ответил правильно."
        ),
        "relation_start": 50,
        "choices": [
            {
                "style": "Соперничество",
                "text": "«Это несправедливо! Вы всегда ко мне придираетесь!»",
                "consequence": "Учитель разозлился. Вызвал родителей. Оценку не изменил.",
                "relation_change": -40
            },
            {
                "style": "Избегание",
                "text": "«Ладно, промолчу» (и обиделся на учителя)",
                "consequence": "Оценка осталась. Ты потерял мотивацию учиться.",
                "relation_change": -20
            },
            {
                "style": "Приспособление",
                "text": "«Извините, я, наверное, ошибся» (хотя не ошибся)",
                "consequence": "Ты признал вину, которой не было. Учитель не узнал правду.",
                "relation_change": -10
            },
            {
                "style": "Компромисс",
                "text": "«Можно я покажу черновик? Мне кажется, там была ошибка в подсчётах.»",
                "consequence": "Учитель посмотрел черновик и поставил тройку. Не идеально, но лучше.",
                "relation_change": +5
            },
            {
                "style": "Сотрудничество",
                "text": "«Я готовился и хочу понять, где ошибся. Можно я покажу решение и мы разберём?»",
                "consequence": "Учитель оценил твой подход. Вы разобрали ошибку. Оценку он пересмотрел.",
                "relation_change": +15
            }
        ]
    },
    "friend_secret": {
        "title": "🤫 Друг рассказал твой секрет",
        "description": (
            "Ты доверил другу секрет, а он рассказал его другим. "
            "Теперь об этом знают в классе."
        ),
        "relation_start": 80,
        "choices": [
            {
                "style": "Соперничество",
                "text": "«Ты предатель! Я тебе больше никогда ничего не расскажу!»",
                "consequence": "Друг обиделся в ответ. Вы перестали общаться. Секрет всё равно известен.",
                "relation_change": -50
            },
            {
                "style": "Избегание",
                "text": "«Ничего, бывает...» (и перестал с ним общаться)",
                "consequence": "Ты не сказал, что чувствуешь. Дружба угасла сама собой.",
                "relation_change": -25
            },
            {
                "style": "Приспособление",
                "text": "«Ладно, проехали» (хотя тебе больно)",
                "consequence": "Ты проглотил обиду. Друг не понял, что сделал больно. Доверие потеряно.",
                "relation_change": -20
            },
            {
                "style": "Компромисс",
                "text": "«Мне неприятно, что ты рассказал. Давай ты извинишься перед теми, кому рассказал.»",
                "consequence": "Друг извинился. Но осадок остался.",
                "relation_change": -5
            },
            {
                "style": "Сотрудничество",
                "text": "«Мне больно, что ты так поступил. Почему ты это сделал? Для меня важно понимать, могу ли я тебе доверять.»",
                "consequence": "Друг объяснил, что не подумал. Вы честно поговорили. Дружба стала крепче.",
                "relation_change": +15
            }
        ]
    },
    "bully_classmate": {
        "title": "😠 Одноклассник обзывается",
        "description": (
            "Один из одноклассников постоянно обзывается и смеётся над тобой. "
            "Сегодня он снова начал при всех."
        ),
        "relation_start": 30,
        "choices": [
            {
                "style": "Соперничество",
                "text": "«Сам такой! Отстань от меня!» (и толкнул его)",
                "consequence": "Началась драка. Вас обоих вызвали к директору. Родителей вызвали в школу.",
                "relation_change": -30
            },
            {
                "style": "Избегание",
                "text": "Молча ушёл, сделав вид, что не слышал.",
                "consequence": "Он продолжит обзываться, потому что понял, что ты не даёшь отпор.",
                "relation_change": -5
            },
            {
                "style": "Приспособление",
                "text": "«Да, я такой, и что?» (с грустной улыбкой)",
                "consequence": "Ты сделал вид, что тебе всё равно, но внутри обидно. Он не остановится.",
                "relation_change": -10
            },
            {
                "style": "Компромисс",
                "text": "«Слушай, давай без обзывательств. Что ты хочешь этим доказать?»",
                "consequence": "Он растерялся. В следующий раз, возможно, подумает, прежде чем обзываться.",
                "relation_change": +10
            },
            {
                "style": "Сотрудничество",
                "text": "«Мне неприятно, когда ты так говоришь. Если тебе что-то не нравится во мне — скажи прямо, без оскорблений.»",
                "consequence": "Он удивился, но замолчал. Возможно, впервые задумался о своём поведении.",
                "relation_change": +20
            }
        ]
    },
    "friend_debt": {
        "title": "💰 Друг не вернул долг",
        "description": (
            "Ты одолжил другу деньги месяц назад. Он обещал вернуть через неделю, "
            "но до сих пор не вернул. Ты напоминаешь ему."
        ),
        "relation_start": 60,
        "choices": [
            {
                "style": "Соперничество",
                "text": "«Ты вообще обнаглел! Я тебе больше никогда не одолжу!»",
                "consequence": "Друг обиделся и сказал, что вернёт, но вы поссорились. Деньги он всё равно не вернул.",
                "relation_change": -35
            },
            {
                "style": "Избегание",
                "text": "«Ладно, потом отдашь...» (и не напоминаешь больше)",
                "consequence": "Деньги ты, скорее всего, не увидишь. Друг понял, что можно не возвращать.",
                "relation_change": -15
            },
            {
                "style": "Приспособление",
                "text": "«Да ладно, забудь, не нужны мне эти деньги» (хотя они тебе нужны)",
                "consequence": "Ты остался без денег и без уважения к себе. Друг не оценил жертву.",
                "relation_change": -10
            },
            {
                "style": "Компромисс",
                "text": "«Слушай, мне нужны эти деньги. Давай ты вернёшь половину сейчас, а остальное — через неделю.»",
                "consequence": "Друг согласился вернуть частями. Ты получил часть денег и сохранил отношения.",
                "relation_change": +10
            },
            {
                "style": "Сотрудничество",
                "text": "«Я понимаю, что у тебя могут быть трудности. Но для меня важно, чтобы ты вернул долг. Давай обсудим, как это сделать удобно для нас обоих.»",
                "consequence": "Друг честно рассказал о своих проблемах. Вы договорились о графике возврата. Доверие сохранилось.",
                "relation_change": +20
            }
        ]
    },
    "sibling_compare": {
        "title": "👨‍👩‍👧 Родители сравнивают с братом/сестрой",
        "description": (
            "Родители постоянно говорят: «Вот твой брат — молодец, а ты...» "
            "Сегодня это снова повторилось за ужином."
        ),
        "relation_start": 50,
        "choices": [
            {
                "style": "Соперничество",
                "text": "«Если я такой плохой — зачем я вам вообще нужен?!»",
                "consequence": "Родители обиделись. Разговор закончился скандалом. Проблема не решена.",
                "relation_change": -30
            },
            {
                "style": "Избегание",
                "text": "Молча встал из-за стола и ушёл в комнату.",
                "consequence": "Ты показал обиду, но не объяснил, что чувствуешь. Родители не поняли, в чём дело.",
                "relation_change": -15
            },
            {
                "style": "Приспособление",
                "text": "«Да, я знаю, что я хуже...» (и опустил глаза)",
                "consequence": "Ты подтвердил их слова, но это разрушает твою самооценку. Проблема осталась.",
                "relation_change": -10
            },
            {
                "style": "Компромисс",
                "text": "«Мне неприятно, когда меня сравнивают. Давайте лучше обсудим, что я могу улучшить.»",
                "consequence": "Родители немного смутились. Разговор стал конструктивнее.",
                "relation_change": +5
            },
            {
                "style": "Сотрудничество",
                "text": "«Я понимаю, что вы хотите, чтобы я был лучше. Но когда меня сравнивают с братом, мне становится больно. Я хочу, чтобы вы видели мои успехи, а не только его.»",
                "consequence": "Родители задумались. Впервые за долгое время вы поговорили честно. Они пообещали изменить подход.",
                "relation_change": +25
            }
        ]
    }
}

# ============================================================
# КЛАВИАТУРЫ
# ============================================================
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎭 Выбрать конфликт", callback_data="choose_scenario")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(text="💡 Советы", callback_data="tips")],
        [InlineKeyboardButton(text="ℹ️ О проекте", callback_data="about")]
    ])


def scenarios_menu():
    buttons = []
    for key, scenario in SCENARIOS.items():
        buttons.append([InlineKeyboardButton(
            text=scenario["title"],
            callback_data=f"scenario_{key}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def choices_menu(scenario_key):
    """Меню выбора с живыми названиями стилей"""
    scenario = SCENARIOS[scenario_key]
    buttons = []
    for i, choice in enumerate(scenario["choices"]):
        label = STYLE_LABELS.get(choice["style"], choice["style"])
        buttons.append([InlineKeyboardButton(
            text=f"{i+1}. {label}",
            callback_data=f"choice_{scenario_key}_{i}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="choose_scenario")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# СТАТИСТИКА
# ============================================================
user_stats = {}


def update_stats(user_id: int, style: str):
    if user_id not in user_stats:
        user_stats[user_id] = {}
    user_stats[user_id][style] = user_stats[user_id].get(style, 0) + 1


# ============================================================
# ОБРАБОТЧИКИ
# ============================================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я — *Конфликт-Симулятор*.\n\n"
        "Я помогу тебе научиться решать конфликты так, "
        "чтобы отношения становились крепче, а не разрушались.\n\n"
        "🎭 Выбирай ситуацию и смотри, к чему приведёт твой выбор.\n"
        "📊 Веди статистику своих решений.\n"
        "💡 Получай советы по разрешению конфликтов.\n\n"
        "В основе — модель Томаса-Киллмена: 5 стилей поведения в конфликте.\n\n"
        "Готов начать?",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📖 *Как пользоваться ботом:*\n\n"
        "1. Нажми «🎭 Выбрать конфликт»\n"
        "2. Выбери одну из ситуаций\n"
        "3. Прочитай описание\n"
        "4. Выбери свою реакцию\n"
        "5. Посмотри последствия и уровень отношений\n\n"
        "Команды:\n"
        "/start — главное меню\n"
        "/help — эта справка\n"
        "/stats — твоя статистика",
        parse_mode="Markdown"
    )


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_stats or not user_stats[user_id]:
        await message.answer(
            "📊 У тебя пока нет статистики.\n\n"
            "Пройди хотя бы один конфликт, чтобы я мог проанализировать твои решения.",
            reply_markup=main_menu()
        )
        return

    stats = user_stats[user_id]
    total = sum(stats.values())
    dominant = max(stats, key=stats.get)
    dominant_percent = round(stats[dominant] / total * 100)

    text = "📊 *Твоя статистика:*\n\n"
    for style, count in sorted(stats.items(), key=lambda x: -x[1]):
        percent = round(count / total * 100)
        label = STYLE_LABELS.get(style, style)
        text += f"• *{label}*: {count} ({percent}%)\n\n"

    text += f"🎯 *Твой доминирующий стиль:* {STYLE_LABELS.get(dominant, dominant)} ({dominant_percent}%)\n\n"

    if dominant == "Сотрудничество":
        text += "🏆 Отлично! Ты умеешь находить решения, которые устраивают всех. Продолжай в том же духе!"
    elif dominant == "Компромисс":
        text += "👍 Хорошо! Ты умеешь договариваться. Но попробуй иногда искать win-win решения — это эффективнее."
    elif dominant == "Соперничество":
        text += "⚠️ Ты часто идёшь напролом. Это может разрушать отношения. Попробуй технику «Я-сообщений»."
    elif dominant == "Избегание":
        text += "⚠️ Ты часто уходишь от конфликтов. Проблемы копятся. Попробуй говорить о своих чувствах открыто."
    elif dominant == "Приспособление":
        text += "⚠️ Ты часто уступаешь в ущерб себе. Это может привести к выгоранию. Учись отстаивать свои границы."

    text += "\n\n💡 Нажми «Советы», чтобы узнать, как развить навык."

    await message.answer(text, reply_markup=main_menu(), parse_mode="Markdown")


@dp.callback_query(F.data == "choose_scenario")
async def show_scenarios(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎭 *Выбери конфликтную ситуацию:*\n\n"
        "Прочитай описание и выбери свою реакцию.",
        reply_markup=scenarios_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "👋 Главное меню. Что хочешь сделать?",
        reply_markup=main_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ *О проекте*\n\n"
        "Этот бот создан как итоговый проект по теме "
        "«Как конфликты помогают расти».\n\n"
        "🎯 *Цель:* научить старшеклассников выбирать "
        "конструктивные стратегии поведения в конфликте.\n\n"
        "🧠 *Научная основа:* модель Томаса-Киллмена (1974), "
        "описывающая 5 стилей поведения в конфликте.\n\n"
        "👩🏻‍💻 *Автор:* Михалёва Варвара Алексеевна\n"
        "🏫 *Школа:* МКОУ Бутырская школа",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_stats or not user_stats[user_id]:
        await callback.message.edit_text(
            "📊 У тебя пока нет статистики.\n\n"
            "Пройди хотя бы один конфликт.",
            reply_markup=main_menu()
        )
    else:
        stats = user_stats[user_id]
        total = sum(stats.values())
        text = "📊 *Твоя статистика:*\n\n"
        for style, count in sorted(stats.items(), key=lambda x: -x[1]):
            percent = round(count / total * 100)
            label = STYLE_LABELS.get(style, style)
            text += f"• *{label}*: {count} ({percent}%)\n\n"
        await callback.message.edit_text(
            text,
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    await callback.answer()


@dp.callback_query(F.data == "tips")
async def show_tips(callback: CallbackQuery):
    text = (
        "💡 *Техники конструктивного разрешения конфликтов:*\n\n"
        "1️⃣ *Правило 5 секунд*\n"
        "Перед тем как ответить в конфликте, сделай паузу 5 секунд. "
        "Это даст префронтальной коре включиться, а амигдале — успокоиться.\n\n"
        "2️⃣ *Я-сообщения*\n"
        "Говори о своих чувствах, а не обвиняй.\n"
        "❌ «Ты меня бесишь!»\n"
        "✅ «Я чувствую злость, когда ты так делаешь»\n\n"
        "3️⃣ *Активное слушание*\n"
        "Повтори то, что сказал собеседник: "
        "«Правильно ли я понял, что ты хочешь...»\n\n"
        "4️⃣ *Поиск win-win*\n"
        "Спроси: «Что мы оба можем сделать, чтобы решить это?»\n\n"
        "5️⃣ *Отделяй человека от проблемы*\n"
        "Борись не с человеком, а с проблемой."
    )
    await callback.message.edit_text(
        text,
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("scenario_"))
async def show_scenario(callback: CallbackQuery):
    scenario_key = callback.data.replace("scenario_", "")
    scenario = SCENARIOS.get(scenario_key)

    if not scenario:
        await callback.answer("Сценарий не найден")
        return

    text = (
        f"*{scenario['title']}*\n\n"
        f"{scenario['description']}\n\n"
        f"*Как ты поступишь?*"
    )

    await callback.message.edit_text(
        text,
        reply_markup=choices_menu(scenario_key),
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("choice_"))
async def handle_choice(callback: CallbackQuery):
    parts = callback.data.split("_")
    scenario_key = "_".join(parts[1:-1])
    choice_index = int(parts[-1])

    scenario = SCENARIOS.get(scenario_key)
    if not scenario:
        await callback.answer("Ошибка")
        return

    choice = scenario["choices"][choice_index]
    update_stats(callback.from_user.id, choice["style"])

    relation_start = scenario["relation_start"]
    relation_end = max(0, min(100, relation_start + choice["relation_change"]))

    good_styles = ["Сотрудничество", "Компромисс"]
    if choice["style"] in good_styles:
        emoji = "✅"
        verdict = "Это конструктивный выбор!"
    else:
        emoji = "⚠️"
        verdict = "Этот стиль может осложнить ситуацию."

    if choice["relation_change"] > 0:
        change_text = f"📈 +{choice['relation_change']}%"
    elif choice["relation_change"] < 0:
        change_text = f"📉 {choice['relation_change']}%"
    else:
        change_text = "➖ 0%"

    label = STYLE_LABELS.get(choice["style"], choice["style"])

    text = (
        f"{emoji} *Ты выбрал: {label}*\n\n"
        f"*Твоя реакция:*\n{choice['text']}\n\n"
        f"*Последствие:*\n{choice['consequence']}\n\n"
        f"*Уровень отношений:*\n{relation_end}% ({change_text})\n\n"
        f"*Вывод:* {verdict}\n\n"
        f"💡 Помни: лучший стиль — *{STYLE_LABELS['Сотрудничество']}*. "
        f"Он требует больше усилий, но сохраняет отношения."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎭 Другой конфликт", callback_data="choose_scenario")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
    ])

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()


# ============================================================
# ЗАПУСК
# ============================================================
async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
