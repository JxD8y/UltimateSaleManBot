from telegram import Bot, InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,ContextTypes,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository
import re

Repo = Repository.USMRepository
STATE = "admin_ack"

async def CallbackDispatcher(update:Update,context:CallbackContext):
    section = update.callback_query.data
    m : re.Match = re.match(".*\\$([a-z A-Z 0-9]*)_?",section)
    if m is not None:
        sec = m.groups()[0]
        if (sec == "acceptOrder"):
            await AcceptOrderCallback(update,context)
        elif (sec == "denyOrder"):
            await DenyOrderCallback(update,context)

async def ComfirmUserOrder(number_id,item_id,bot:Bot):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()

    chat = await bot.get_chat(number_id)
    name = chat.first_name
    id = chat.username
    item = Repo.GetItem(item_id)
    order_id = int(Repo.CreateOrder(number_id,int(item[0])))
    kb = [[InlineKeyboardButton("✅ Accept order",callback_data=f"{STATE}$acceptOrder_{order_id}"),InlineKeyboardButton("❌ Deny order",callback_data=f"{STATE}$denyOrder_{order_id}")]]
    for admin in Repo.Admins:
        admin_chat = await bot.get_chat(admin)
        await admin_chat.send_message(f"🛒 Awaiting order:\nName: {name}\nUsername: @{id}\nℹ️ Item: {item[2]}\n💰 Price: {item[3]}$\n🪄 Current in stock: {item[1]}",reply_markup=InlineKeyboardMarkup(kb))

async def AcceptOrderCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    await update.callback_query.answer()
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?([0-9]*)",update.callback_query.data)
    if m is None:
        await update.callback_query.answer()
        await update.effective_chat.send_message("❌ Selected option does not exist anymore!")
        return
    
    order_id = int(m.groups()[0])
    order = Repo.GetOrder(order_id)
    Repo.SetOrderState(order_id,1)
    await update.effective_chat.send_message("✅ Order accepted")
    number_id = order[2]
    chat = await context.bot.get_chat(number_id)
    await chat.send_message("✅ Your order accepted and will be shipped to you!")

async def DenyOrderCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    await update.callback_query.answer()
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?([0-9]*)",update.callback_query.data)
    if m is None:
        await update.callback_query.answer()
        await update.effective_chat.send_message("❌ Selected option does not exist anymore!")
        return
    
    order_id = int(m.groups()[0])
    order = Repo.GetOrder(order_id)
    Repo.SetOrderState(order_id,2)
    await update.effective_chat.send_message("❌ Order denied")
    number_id = order[2]
    chat = await context.bot.get_chat(number_id)
    await chat.send_message("❌ Your order denied\nContact admin for more information.")