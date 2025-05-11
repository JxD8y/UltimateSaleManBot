from telegram import InlineKeyboardButton,InlineKeyboardMarkup ,ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import Application,ContextTypes,filters,CommandHandler,MessageHandler,CallbackQueryHandler,CallbackContext,ConversationHandler
import Repository
import re

Repo = Repository.USMRepository
STATE = "admin_user_managment"

async def CallbackDispatcher(update:Update,context:CallbackContext):
    if update.effective_chat.id not in Repo.Admins:
        return
    section = update.callback_query.data
    m : re.Match = re.match(".*\\$([a-z A-Z 0-9]*)_?",section)
    if m is not None:
        sec = m.groups()[0]
        if(sec == "userView"):
            await ViewUserCallback(update,context)
        elif(sec == "abort"):
            await AbortUserOpCallback(update,context)
        elif(sec == "mkAdmin"):
            await PromoteAdminCallback(update,context)
        elif(sec == "revokeAdmin"):
            await RevokeAdminCallback(update,context)
        elif(sec == "deleteUser"):
            await DeleteUserCallback(update,context)
        elif(sec == "deactiveUser"):
            await DeactivateCallback(update,context)
        elif(sec == "activeUser"):
            await ActivateCallback(update,context)

async def ViewUsersMessage(update:Update,context:CallbackContext):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    users = Repo.GetUsers()

    if update.effective_chat.id not in Repo.Admins:
        return
    
    if(len(users) == 0):
        await update.effective_chat.send_message("⚠️ No user found in database")
        return
    kb = []
    for user in users:
        is_active = user[2] == 1
        name = ""
        if is_active:
            name = user[1]
        else:
            name = f"❌ {user[1]}"
        kb.append([InlineKeyboardButton(name,callback_data=f"{STATE}$userView_{user[0]}")])
    
    await update.effective_chat.send_message("👥 List of users: ",reply_markup=InlineKeyboardMarkup(kb))

async def ViewUserCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
    if m is None:
        await update.callback_query.answer()
        await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
        return
    id = int(m.groups()[0])

    is_admin = Repo.GetAdmin(id) is not None
    user = Repo.GetUser(id)
    await update.callback_query.answer()
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    active_button : InlineKeyboardButton = None
    admin_button : InlineKeyboardButton = None
    if not is_admin:
        admin_button = InlineKeyboardButton("🪄 Promote Admin",callback_data=f"{STATE}$mkAdmin_{id}")
    else:
        admin_button = InlineKeyboardButton("❌ Revoke Admin",callback_data=f"{STATE}$revokeAdmin_{id}")
    if(user[2] == 1):
        active_button = InlineKeyboardButton("❌ Deactivate user",callback_data=f"{STATE}$deactiveUser_{id}")
    else:
        active_button = InlineKeyboardButton("✅ Activate user",callback_data=f"{STATE}$activeUser_{id}")
    kb = [[active_button],
          [InlineKeyboardButton("🗑 Delete user",callback_data=f"{STATE}$deleteUser_{id}")],
          [admin_button],
          [InlineKeyboardButton("👍 Done",callback_data=f"{STATE}$abort_{id}")]]
    await context.bot.send_message(update.effective_chat.id,f"👤Information about {user[1]}:\nNumber id: {user[0]}\nSignup Date: {user[3]}",reply_markup=InlineKeyboardMarkup(kb))

async def AbortUserOpCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    await update.callback_query.answer()

async def PromoteAdminCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
    if m is None:
        await update.callback_query.answer()
        await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
        return
    id = int(m.groups()[0])
    is_admin = Repo.GetAdmin(id) is not None
    if(is_admin):
        await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
        await update.callback_query.answer("User is already admin")
        return
    Repo.AppendAdmin(id,update.effective_chat.first_name)
    await update.effective_chat.send_message("✅ He is admin now!")
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    await update.callback_query.answer()

async def RevokeAdminCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
    if m is None:
        await update.callback_query.answer()
        await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
        return
    id = int(m.groups()[0])
    is_admin = Repo.GetAdmin(id) is not None
    if(not is_admin):
        await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
        await update.callback_query.answer("User is not admin")
        return
    Repo.RemoveAdmin(id,update.effective_chat.first_name)
    await update.effective_chat.send_message("❌ Now he is not admin!")
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    await update.callback_query.answer()

async def DeleteUserCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
    if m is None:
        await update.callback_query.answer()
        await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
        return
    id = int(m.groups()[0])
    Repo.DeleteUser(id)
    await update.effective_chat.send_message("✅ User removed from database")
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    await update.callback_query.answer()

async def ActivateCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
    if m is None:
        await update.callback_query.answer()
        await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
        return
    id = int(m.groups()[0])
    user = Repo.GetUser(id)
    is_active = user[2] == 1
    if(is_active):
        await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
        await update.callback_query.answer("User is active")
        return
    Repo.SetUserActiveState(id,True)
    await update.effective_chat.send_message("✅ User activated")
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    await update.callback_query.answer()

async def DeactivateCallback(update:Update,context:ContextTypes.DEFAULT_TYPE):
    global Repo
    if Repo is None:
        Repo = Repository.GetRepo()
    m : re.Match = re.match(".*\\$[a-z A-Z 0-9]*_?(.*)",update.callback_query.data)
    if m is None:
        await update.callback_query.answer()
        await update.effective_chat.send_message("❌ Selected item does not exist anymore!")
        return
    id = int(m.groups()[0])
    user = Repo.GetUser(id)
    is_active = user[2] == 1
    if(not is_active):
        await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
        await update.callback_query.answer("User is not active")
        return
    Repo.SetUserActiveState(id,False)
    await update.effective_chat.send_message("✅ User Deactivated")
    await context.bot.edit_message_reply_markup(update.effective_chat.id,update.callback_query.message.message_id,reply_markup=None)
    await update.callback_query.answer()


