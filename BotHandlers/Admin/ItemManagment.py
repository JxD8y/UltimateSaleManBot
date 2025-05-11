from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,filters,ContextTypes,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository
import re

Repo : Repository.USMRepo = None
STATE = "admin_item_managment"

async def MessageDispatcher(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in Repo.Admins:
        return
    section = context.user_data["current_state"]
    m : re.Match = re.match(".*\\$(.*)\\$.*",section)
    if m is not None:
        sec = m.groups()[0]
        if(sec == "AddItem"):
            await AddItemCallback(update,context)
        elif(sec == "editItem"):
            await EditItemCallback(update,context)

async def CallbackDispatcher(update:Update,context:CallbackContext):
    if update.effective_chat.id not in Repo.Admins:
        return
    section = update.callback_query.data
    m : re.Match = re.match(".*\\$([a-z A-Z 0-9]*)_?",section)
    if m is not None:
        sec = m.groups()[0]
        if(sec == "addItem"):
            await AddItemCallback(update,context)
        elif(sec == "abort"):
            await AbortCallback(update,context)
        elif(sec == "itemview"):
            await ViewItemCallback(update,context)
        elif(sec == "editItem"):
            await EditItemCallback(update,context)
        elif(sec == "deleteItem"):
            await DeleteItemCallback(update,context)

async def ViewItemsMessage(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()

    if update.effective_chat.id not in Repo.Admins:
        return
    items = Repo.GetItems()
    context.user_data["current_state"] = f"{STATE}_view_items"
    if len(items) == 0:
        kb = [[InlineKeyboardButton("➕ Add item",callback_data=f"{STATE}$addItem"),
               InlineKeyboardButton("❌ Abort",callback_data=f"{STATE}$abort")]]
        await update.effective_chat.send_message("⚠️ No item available in inventory.",reply_markup=InlineKeyboardMarkup(kb))
    else:
        kb = []
        for item in items:
            kb.append([InlineKeyboardButton(item[2],callback_data=f"{STATE}$itemview_{item[0]}")])
        kb.append([InlineKeyboardButton("➕ Add item",callback_data=f"{STATE}$addItem"),
               InlineKeyboardButton("❌ Abort",callback_data=f"{STATE}$abort")])
        await update.effective_chat.send_message("🛒 Items available in database: ",reply_markup=InlineKeyboardMarkup(kb))

async def AddItemCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    #!! CONTROL FLOW OF THIS FUNCTION IS NOT LINEAR !!
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
        await update.effective_chat.send_message(f"🛒 So this is the item overall:\n\nℹ️Name {name}\n\n💰Price {price}\n\nℹ️Quantity {quantity}\n\nEstimated {price * quantity}$ worth of cash")
        Repo.AddItem(name,price,quantity)
        await update.effective_chat.send_message("✅Item added successfully")

    else:
        if update.callback_query is not None:
            context.user_data["current_state"] = f"{STATE}$AddItem$Name"
            await update.callback_query.answer()
            await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
        await update.effective_chat.send_message("Please enter item name: ")

async def ViewItemCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()

    if update.callback_query is not None:
        #parsing out the item id to edit:
        m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
        if m is None:
            await update.callback_query.answer()
            await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
            return
        id = int(m.groups()[0])
        item = Repo.GetItem(id)
        await update.callback_query.answer()
        await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
        kb = [[InlineKeyboardButton("🖊 Edit item",callback_data=f"{STATE}$editItem_{id}"),
               InlineKeyboardButton("🗑 Delete item",callback_data=f"{STATE}$deleteItem_{id}"),
               InlineKeyboardButton("❌ Abort",callback_data=f"{STATE}$abort")]]
        
        await update.effective_chat.send_message(f"🛒 Item info\n\nℹ️Name {item[2]}\n\n💰Price {item[3]}\n\nℹ️Quantity {item[2]}",reply_markup=InlineKeyboardMarkup(kb))

async def EditItemCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
        global Repo
        if Repo is None:
            Repo = Repository.GetRepo()

        if context.user_data["current_state"] == f"{STATE}$editItem$Name" and update.message is not None:
            context.user_data["item_name"] = update.message.text
            context.user_data["current_state"] = f"{STATE}$editItem$Price"
            await update.effective_chat.send_message(f"💰Choose new price or send ! to keep it")

        elif context.user_data["current_state"] == f"{STATE}$editItem$Price":
            context.user_data["item_price"] = str(update.message.text)
            context.user_data["current_state"] = f"{STATE}$editItem$Quantity"
            await update.effective_chat.send_message("🛒 Choose new quantity or send ! to keep it: ")
        
        elif context.user_data["current_state"] == f"{STATE}$editItem$Quantity":
            context.user_data["item_quantity"] = str(update.message.text)
            context.user_data["current_state"] = f"{STATE}"
            name = context.user_data["item_name"]
            price = context.user_data["item_price"]
            quantity = context.user_data["item_quantity"]
            id = context.user_data["item_id"]
            item = Repo.GetItem(id)
            if(name == "!"):
                name = item[2]
            if(price == "!"):
                price = item[3]
            if(quantity == "!"):
                quantity = item[1]
            await update.effective_chat.send_message(f"🛒 So this is the item overall:\n\nℹ️Name {name}\n\n💰Price {price}\n\nℹ️Quantity {quantity}")
            Repo.UpdateItem(id,name,price,quantity)
            await update.effective_chat.send_message("✅Item updated successfully")

        else:
            if update.callback_query is not None:
                m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
                if m is None:
                    await update.callback_query.answer()
                    await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
                    return
                
                id = int(m.groups()[0])
                item = Repo.GetItem(id)
                await update.callback_query.answer()
                await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
                await update.effective_chat.send_message(f"Choose new name or send ! to keep it")
                context.user_data["current_state"] = f"{STATE}$editItem$Name"
                context.user_data["item_id"] = id


async def DeleteItemCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    
    if update.callback_query is not None:

        m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
        if m is None:
            await update.callback_query.answer()
            await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
            return
        
        id = int(m.groups()[0])
        item = Repo.GetItem(id)
        await update.callback_query.answer()
        await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
        Repo.DeleteItem(id)
        await update.effective_chat.send_message(f"ℹ️ Item removed successfully")
        context.user_data["current_state"] = STATE


async def AbortCallback(update:Update,context: ContextTypes.DEFAULT_TYPE):
    context.user_data["current_state"] = STATE
    await update.callback_query.answer("Aborted")
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
