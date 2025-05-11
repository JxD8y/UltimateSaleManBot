from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,ContextTypes,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository
from BotHandlers.Admin import ItemManagment
import re

Repo = Repository.USMRepository

async def GlobalMessageHandler(update:Update,context:CallbackContext):
    if "current_state" in context.user_data:
        section = context.user_data["current_state"]
        m : re.Match = re.match("([a-z,_]*)\\$",section)
        if m is not None:
            sec = m.groups()[0]
            if(sec == ItemManagment.STATE):
                await ItemManagment.MessageDispatcher(update,context)
