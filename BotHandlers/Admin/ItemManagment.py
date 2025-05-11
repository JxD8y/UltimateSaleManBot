from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,ContextTypes,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository
import re

Repo : Repository.USMRepo = None
STATE = "admin_item_managment"

async def MessageDispatcher(update:Update,context:ContextTypes.DEFAULT_TYPE):
    section = context.user_data["current_state"]
    m : re.Match = re.match(".*\\$(.*)\\$.*",section)
    if m is not None:
        sec = m.groups()[0]
        if(sec == "AddItem"):
            await AddItemCallback(update,context)

async def CallbackDispatcher(update:Update,context:CallbackContext):
    section = update.callback_query.data
    m : re.Match = re.match(".*\\$(.*)",section)
    if m is not None:
        sec = m.groups()[0]

        if(sec == "add_item"):
            await AddItemCallback(update,context)
        elif(sec == "abort"):
            await AbortCallback(update,context)

async def ViewItemsMessage(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()

    if update.effective_chat.id not in Repo.Admins:
        return
    items = Repo.GetItems()
    context.user_data["current_state"] = f"{STATE}_view_items"
    if len(items) == 0:
        kb = [[InlineKeyboardButton("➕ Add item",callback_data=f"{STATE}$add_item"),
               InlineKeyboardButton("❌ Abort",callback_data=f"{STATE}$abort")]]
        await update.effective_chat.send_message("⚠️ No item available in inventory.",reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.effective_chat.send_message("🛒 Items available in database: ")

async def AddItemCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if context.user_data["current_state"] == f"{STATE}$AddItem$Name" and update.message is not None:
        context.user_data["item_name"] = update.message.text
        context.user_data["current_state"] = f"{STATE}$AddItem$Price"
        await update.effective_chat.send_message("💰 Please enter item price: ")

    elif context.user_data["current_state"] == f"{STATE}$AddItem$Price":

        context.user_data["item_price"] = str(update.message.text)
        context.user_data["current_state"] = f"{STATE}$AddItem$Quantity"
        await update.effective_chat.send_message("🛒 Please enter item quantity: ")
    
    elif context.user_data["current_state"] == f"{STATE}$AddItem$Quantity":

        context.user_data["item_quantity"] = str(update.message.text)
        context.user_data["current_state"] = f"{STATE}" # eNsure current state is reset to prevent middle function calls!
        name = context.user_data["item_name"]
        price = float(context.user_data["item_price"])
        quantity = float(context.user_data["item_quantity"])
        await update.effective_chat.send_message(f"🛒 So this is the item overall:\nName {name}\n\nPrice {price}\n\nQuantity {quantity}\n\nEstimated {price * quantity} worth of cash")
    else:
        context.user_data["current_state"] = f"{STATE}$AddItem$Name"
        await update.callback_query.answer()
        await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
        await update.effective_chat.send_message("Please enter item name: ")

    




async def AbortCallback(update:Update,context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Aborted")
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
