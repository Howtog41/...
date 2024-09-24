from datetime import datetime, timedelta

from pyrogram import Client, filters

from helper.Database import db  # Import the database object

@Client.on_message(filters.command("myplan"))

async def myplan(client, message):

    user_id = message.from_user.id

    # Fetch user information from the database

    user_info = await db.get_user(user_id)

    if not user_info:

        await message.reply_text("You are not registered in the system. Please contact the admin.")

        return

    # Check if the user is authorized (premium) or on a trial

    authorized = user_info.get('authorized', False)

    join_date = user_info.get('join_date')

    expiration_date = user_info.get('expiration_date')

    if not join_date:

        await message.reply_text("You are not on a trial or authorized plan.")

        return

    if authorized:

        # If the user is authorized (premium), calculate remaining time

        if expiration_date:

            remaining_time = expiration_date - datetime.utcnow()

            remaining_days = remaining_time.days

            remaining_hours = remaining_time.seconds // 3600

            if remaining_days > 0:

                await message.reply_text(

                    f"Your plan: Premium\nRemaining days: {remaining_days} days, {remaining_hours} hours\n"

                    "Thank you for being a premium member!"

                )

            else:

                await message.reply_text("Your premium plan has expired. Please contact the admin to renew.")

        else:

            await message.reply_text("Your premium plan has no expiration.")

    else:

        # Calculate remaining trial time (5 minutes)

        trial_period_end = join_date + timedelta(minutes=5)

        remaining_time = trial_period_end - datetime.utcnow()

        remaining_minutes = remaining_time.seconds // 60

        if remaining_time.total_seconds() > 0:

            await message.reply_text(

                f"Your plan: Trial\nRemaining time: {remaining_minutes} minutes\n"

                "Enjoy your trial period!"

            )

        else:

            await message.reply_text("Your trial period has expired. Please contact the admin to upgrade to premium.")