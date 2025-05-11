from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler

#Following function only handle user interaction based errors
#-raised by telegram
async def HandleUserErrorCallback(update:Update, context:CallbackContext):
    print(f"[-]Error in {context.error} NUM_ID: {update.effective_chat.id}")
    await update.effective_chat.send_message("There was an error try again.")
    if update.callback_query is not None:
        await update.callback_query.answer("fail")