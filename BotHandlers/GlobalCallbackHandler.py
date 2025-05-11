from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository
from BotHandlers.Admin import ItemManagment
from BotHandlers.Admin import UserManagment
import re

Repo = Repository.USMRepository

async def GlobalCallbackHandler(update:Update,context:CallbackContext):
    if update.callback_query is not None:
        section = update.callback_query.data
        m : re.Match = re.match("([a-z,_]*)\\$",section)
        if m is not None:
            sec = m.groups()[0]

            if(sec == ItemManagment.STATE):
                await ItemManagment.CallbackDispatcher(update,context)
            elif(sec == UserManagment.STATE):
                await UserManagment.CallbackDispatcher(update,context)

