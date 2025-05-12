from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,ContextTypes,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository
import re
from BotHandlers.Admin import UserOrderAck

Repo = Repository.USMRepository
STATE = "user_ordering"
async def CallbackDispatcher(update:Update,context:CallbackContext):
    section = update.callback_query.data
    m : re.Match = re.match(".*\\$([a-z A-Z 0-9]*)_?",section)
    if m is not None:
        sec = m.groups()[0]
        if(sec == "orderItem"):
            await OrderItemCallback(update,context)
        elif(sec == "abort"):
            await AbortCallback(update,context)
        

async def UserOrderMessage(update:Update,context:CallbackContext):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    await update.message.reply_text("Ok lets start shoping 🛒")
    items = Repo.GetItems()
    if len(items) == 0:
        await update.effective_chat.send_message("Sorry 😕 no item is available for selling currently!")
        return
    kb = []
    for item in items:
        if (int (item[1]) > 1):
            kb.append([InlineKeyboardButton(f"{item[2]} - {item[3]}$",callback_data=f"{STATE}$orderItem_{item[0]}")])
    kb.append([InlineKeyboardButton(f"👌 Done",callback_data=f"{STATE}$abort")])
    await update.effective_chat.send_message("🛒 Items available for shoping:",reply_markup=InlineKeyboardMarkup(kb))

async def OrderItemCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
    if m is None:
        await update.callback_query.answer()
        await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
        return
    id = int(m.groups()[0])
    number_id = update.effective_chat.id
    await UserOrderAck.ComfirmUserOrder(number_id,id,context.bot)
    await update.callback_query.answer()
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    await update.effective_chat.send_message("👌Your order will be processed...")

async def AbortCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)