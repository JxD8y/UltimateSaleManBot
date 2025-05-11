from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository

Repo = Repository.USMRepository
STATE = "user_ordering"
async def UserOrderMessage(update:Update,context:CallbackContext):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    await update.message.reply_text("Ok lets start shoping 🛒")
    items = Repo.GetItems()
    if len(items) == 0:
        await update.effective_chat.send_message("Sorry 😕 no item is available for selling currently!")
        