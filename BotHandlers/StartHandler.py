from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository
#This Module will handle user start command there will be two handlers ADMIN and USeR

Repo : Repository.USMRepo = None
STATE_VNAME = "current_state"

async def StartHandler(update:Update,context: CallbackContext):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    num_id = update.effective_chat.id
    if num_id in Repo.Admins:
        await _AdminStartHandler(update,context)
    else:
        await _UserStartHandler(update,context)

async def _AdminStartHandler(update:Update,context: CallbackContext):
    STATE = "admin_start_menu"
    keyboardButtons = [["👥 View Users","🛒 View Items"],["👥 About"]]
    context.user_data["current_state"] = STATE
    await update.message.reply_text(f"Hello {update.effective_chat.first_name}😀\nHave nice they managing users chief!",reply_markup=ReplyKeyboardMarkup(keyboardButtons,one_time_keyboard=True))

async def _UserStartHandler(update:Update,context: CallbackContext):
    STATE = "user_start_menu"
    num_id = update.effective_chat.id
    user = Repo.GetUser(num_id)
    if(user is None):
        Repo.AddUser(num_id,update.effective_chat.first_name,str(update.message.date))
    else:
        if STATE_VNAME in context.user_data:
            state = context.user_data["current_state"]
            if state == "order_payment": #Alert user if try to restart in order_payment state
                await update.effective_chat.send_message("❌ Cannot restart bot at this moment")
                return
    context.user_data[STATE_VNAME] = STATE
    keyboardButtons = [["🕝 View History","🛒 Order Something"],["👥 About"]]
    await update.message.reply_text(f"Hello {update.effective_chat.first_name} 😀\nHow can i help you today?",reply_markup=ReplyKeyboardMarkup(keyboardButtons,one_time_keyboard=True))
        

