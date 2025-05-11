from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository

STATE_VNAME = "current_state"

async def AboutHandler(update:Update,context: CallbackContext):
    await update.effective_chat.send_message("USM (ultra sale bot) is a base scheme bot only used for research purposes")