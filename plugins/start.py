from datetime import datetime, timedelta

from pyrogram import Client, filters

from config import Config  # For MongoDB and bot configuration

from helper.Database import db  # Import the db object for database operations

@Client.on_message(filters.command("start") & filters.private)

async def start(client, message):

    user_id = message.from_user.id  # Get the user ID from the message

    # Fetch user information from the database

    user_info = await db.get_user(user_id)

    if user_info:

        # Check if trial period has expired

        join_date = user_info.get('join_date')

        trial_period_end = join_date + timedelta(minutes=5) if join_date else None

        trial_expired = datetime.utcnow() > trial_period_end if trial_period_end else True

        if trial_expired and not user_info.get('authorized', False):

            await message.reply_text(

                "Your 3-day trial period has expired. Please contact the admin to purchase full access to the bot."

            )

            return

        # If user is still within trial or authorized, send a welcome back message

        await message.reply_text(

            "Welcome back! ʜɪ ᴛʜᴇʀᴇ!  \n"

            "➻ɪ'ᴍ ʏᴏᴜʀ ᴍᴄQ ʙᴏᴛ. 🤖 \n"

            "➻ᴜᴘʟᴏᴀᴅ ʏᴏᴜʀ ᴄꜱᴠ 📄ꜰɪʟᴇ ᴡɪᴛʜ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏʟᴜᴍɴꜱ: \n"

            "👉Qᴜᴇꜱᴛɪᴏɴ, ᴏᴘᴛɪᴏɴ ᴀ, ᴏᴘᴛɪᴏɴ ʙ, ᴏᴘᴛɪᴏɴ ᴄ, ᴏᴘᴛɪᴏɴ ᴅ, ᴀɴꜱᴡᴇʀ, ᴅᴇꜱᴄʀɪᴘᴛɪᴏɴ.\n"

            "Use Command: -🔰 /uploadcsv.\n"

            "➻ ɪ'ʟʟ ᴄᴏɴᴠᴇʀᴛ ɪᴛ ɪɴᴛᴏ ᴍᴜʟᴛɪᴘʟᴇ-ᴄʜᴏɪᴄᴇ Qᴜᴇꜱᴛɪᴏɴꜱ ꜰᴏʀ ʏᴏᴜ! \n"

            "• Mᴀɪɴᴛᴀɪɴᴇʀ: @How_to_Google \n"

        )

    else:

        # If user is not found in the database, add them with the join date for trial period tracking

        join_date = datetime.utcnow()

        await db.add_user_with_trial(user_id, join_date)

        # Send a welcome message with trial period notification

        await message.reply_text(

            "Welcome! You have a 3-day trial period to use the bot's features.\n"

            "➻ɪ'ᴍ ʏᴏᴜʀ ᴍᴄQ ʙᴏᴛ. 🤖 \n"

            "➻ᴜᴘʟᴏᴀᴅ ʏᴏᴜʀ ᴄꜱᴠ 📄ꜰɪʟᴇ ᴡɪᴛʜ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏʟᴜᴍɴꜱ: \n"

            "👉Qᴜᴇꜱᴛɪᴏɴ, ᴏᴘᴛɪᴏɴ ᴀ, ᴏᴘᴛɪᴏɴ ʙ, ᴏᴘᴛɪᴏɴ ᴄ, ᴏᴘᴛɪᴏɴ ᴅ, ᴀɴꜱᴡᴇʀ, ᴅᴇꜱᴄʀɪᴘᴛɪᴏɴ.\n"

            "Use Command: -🔰 /uploadcsv.\n"

            "➻ ɪ'ʟʟ ᴄᴏɴᴠᴇʀᴛ ɪᴛ ɪɴᴛᴏ ᴍᴜʟᴛɪᴘʟᴇ-ᴄʜᴏɪᴄᴇ Qᴜᴇꜱᴛɪᴏɴꜱ ꜰᴏʀ ʏᴏᴜ! \n"

            "• Mᴀɪɴᴛᴀɪɴᴇʀ: @How_to_Google \n"

        )