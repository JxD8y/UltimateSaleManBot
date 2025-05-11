from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import BotHandlers.AboutMessageHandler
import BotHandlers.Admin
import BotHandlers.Admin.ItemManagment
import BotHandlers.Admin.UserManagment
import BotHandlers.GlobalCallbackHandler
import BotHandlers.GlobalMessageHandler
import BotHandlers.User.HandleOrder
import BotHandlers.ErrorHandler
import BotHandlers.StartHandler
import BotHandlers.User.HistoryHandler
import Repository

Repo : Repository.USMRepo = None
App : Application = None
TOKEN = "7283654416:AAF9o3BfG-VZSEwID2NOyALO-KBatjaWHYg"


#Two user possible conv : View History , Order 
#Three Admin possible conv: see user info , ack payment (Starts when user initiate a transfer!) , manage items

def init():
    Repo = Repository.USMRepo("ultimate.db")
    Repository.SetRepo(Repo)
    print(Repository.GetRepo().Admins)
    if(len(Repo.Admins) == 0):
        Repo.AppendAdmin(7896978882,"J's") #Hard coded admin

    App = Application.builder().token(TOKEN).build()
    App.add_error_handler(BotHandlers.ErrorHandler.HandleUserErrorCallback)
    App.add_handler(CommandHandler("start",BotHandlers.StartHandler.StartHandler))
    #Handle menu items in user mode:
    App.add_handler(MessageHandler(filters.TEXT & filters.Regex("🕝 View History"),BotHandlers.User.HistoryHandler.UserHistoryMessage))
    App.add_handler(MessageHandler(filters.TEXT & filters.Regex("🛒 Order Something"),BotHandlers.User.HandleOrder.UserOrderMessage))
    #global Query handler acting as dispatcher
    App.add_handler(CallbackQueryHandler(BotHandlers.GlobalCallbackHandler.GlobalCallbackHandler))
    #Handle Admin
    App.add_handler(MessageHandler(filters.TEXT & filters.Regex("👥 View Users"),BotHandlers.Admin.UserManagment.ViewUsersMessage))
    App.add_handler(MessageHandler(filters.TEXT & filters.Regex("🛒 View Items"),BotHandlers.Admin.ItemManagment.ViewItemsMessage))
    #About message handler
    App.add_handler(MessageHandler(filters.TEXT & filters.Regex("👥 About"),BotHandlers.AboutMessageHandler.AboutHandler))
    #Global message handler
    App.add_handler(MessageHandler(filters.TEXT ,BotHandlers.GlobalMessageHandler.GlobalMessageHandler))
    
    App.run_polling()

if __name__ == "__main__":
    init()