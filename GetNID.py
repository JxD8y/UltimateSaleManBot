from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler

###
### Mini application that will return any users it's number id
###
async def onEchoNumberIdStart(update: Update, context: CallbackContext):
    await update.effective_chat.send_message(f"hello {update.effective_chat.full_name}\nnumber id: {update.effective_user.id}")
def EchoNumberId(TOKEN :str):
    IndepApp = Application.builder().token(TOKEN).build()
    IndepApp.add_handler(CommandHandler("start",onEchoNumberIdStart))
    IndepApp.run_polling()

if __name__ == "__main__":
    token = input("TOKEN: ")
    EchoNumberId(token)