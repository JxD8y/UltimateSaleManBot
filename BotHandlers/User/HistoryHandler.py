from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository

Repo = Repository.USMRepository

async def UserHistoryMessage(update:Update,context:CallbackContext):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    
    orders = Repo.GetOrders(update.effective_chat.id)

    if(len(orders) == 0):
        await update.effective_chat.send_message("⚠️ You have no orders")
        return
    
    message = "🛒 Your orders summery:\n"

    for order in orders:
        item_id = order[3]
        item = Repo.GetItem(item_id)
        state = order[4]
        s = ""
        if(int(state) == 0):
            s = "❓"
        elif(int(state) == 1):
            s = "✅"
        elif(int(state) == 2):
            s = "❌"
        message += f"{s}: 🛒 Order of {item[2]} x1 🕝 in {order[1]}\n"
    
    await update.effective_chat.send_message(message)
        
    
