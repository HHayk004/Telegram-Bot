from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)

    await show_main_menu(update, context, {
        "start": "Main menu of bot",
        "profile": "Generating Tinder-profile",
        "opener": "Message for meeting",
        "message": "Texting from your side",
        "date": "Char with famous people",
        "gpt" : "Dialogue with AI"
    })

async def gpt(update, context):
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_photo(update, context, "gpt")
    await send_text(update, context, text)

async def gpt_dialogue(update, context):
    text = update.message.text

    answer = await chatgpt.send_question("Write short and correct answer to next question:", text)
    await send_text(update, context, answer)

async def date(update, context):
    dialog.mode = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text, {
        "date_grande": "Arinana Grande",
        "date_robbie": "Margo Robbie",
        "date_zendaya": "Zendaya",
        "date_gosling": "Rayan Gosling",
        "date_hardy": "Tom Hardy"
    })

async def date_dialogue(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Man(woman) is typing...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update, context, query)
    await send_text(update, context, "Good choice. Invite man(woman) to the date. Ask him(her) 5 questions.")

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)

async def message(update, context):
    dialog.mode = "message"
    text = load_message("message")
    await send_photo(update, context, "message")
    await send_text(update, context, text)
    await send_text_buttons(update, context, text, {
        "message_next": "Next message",
        "message_date": "Invite to date"
    })
    dialog.list.clear()

async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)
    my_message = await send_text(update, context, "ChatGPT is thinking...")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)

async def message_dialogue(update, context):
    text = update.message.text
    dialog.list.append(text)

async def profile(update, context):
    dialog.mode = "profile"
    text = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "How old are you?")

async def profile_dialogue(update, context):
    text = update.message.text
    dialog.count += 1

    if (dialog.count == 1):
        dialog.user["age"] = text
        await send_text(update, context, "Where do you work?")
        
    elif (dialog.count == 2):
        dialog.user["occupation"] = text
        await send_text(update, context, "Do you have any hobby?")

    elif (dialog.count == 3):
        dialog.user["hobby"] = text
        await send_text(update, context, "What do you not like in people?")

    elif (dialog.count == 4):
        dialog.user["annoys"] = text
        await send_text(update, context, "What is your goal of our meeting?")

    elif (dialog.count == 5):
        dialog.user["occupation"] = text
        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "CharGPT is thinking...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def opener(update, context):
    dialog.mode = "opener"
    text = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "The name of girlfriend?")


async def opener_dialogue(update, context):
    text = update.message.text
    dialog.count += 1

    if (dialog.count == 1):
        dialog.user["name"] = text
        await send_text(update, context, "How old is she?")
        
    elif (dialog.count == 2):
        dialog.user["age"] = text
        await send_text(update, context, "Mark her appearance: 1-10 score")

    elif (dialog.count == 3):
        dialog.user["handsome"] = text
        await send_text(update, context, "Who is she?")

    elif (dialog.count == 4):
        dialog.user["occupation"] = text
        await send_text(update, context, "What is your goal of our meeting?")

    elif (dialog.count == 5):
        dialog.user["goals"] = text
        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "CharGPT is thinking...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)

async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialogue(update, context)

    elif dialog.mode == "date":
        await date_dialogue(update, context)

    elif dialog.mode == "message":
        await message_dialogue(update, context)

    elif dialog.mode == "profile":
        await profile_dialogue(update, context)

    elif dialog.mode == "opener":
        await opener_dialogue(update, context)

    else:    
        await send_text(update, context, "*Hi!*")
        await send_text(update, context, "_How are you?_")
        await send_text(update, context, "You write " + update.message.text)

        await send_photo(update, context, "avatar_main")
        await send_text_buttons(update, context, "Shall I run the process?", {
            "start": "Start the process",
            "stop": "Stop the process"
        })

async def hello_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    if query == "start":
        await send_text(update, context, "*The process started*")
    
    else:
        await send_text(update, context, "*The process stopped*")
        
dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.user = {}

chatgpt = ChatGptService(token="")

app = ApplicationBuilder().token("").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(hello_button))

app.run_polling()
