# config.py

class Config:

    # Telegram Bot Token

    BOT_TOKEN = '5645711998:AAE8oAHzKi07iqcydKPnuFjzknlVa2MxxUQ'

    # Admin user ID

    ADMIN_ID = [5018200809]  # You can have a list of admin IDs if needed

    # API credentials for Pyrogram

    API_ID = '15502786'  # Get this from https://my.telegram.org/apps

    API_HASH = 'bb32e00647b1bfe66e6cd298a2c66a5a'  # Get this from https://my.telegram.org/apps

    # MongoDB setup

    MONGO_URI = 'mongodb+srv://terabox255:Cja5vPiEqfJXvBq7@cluster0.nakwhlt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

    

    # Database and collection names

    DB_NAME = 'quiz_bot'

    USERS_COLLECTION = 'users'

    # Log Channel for Bot

    LOG_CHANNEL = -1002155664087  # Replace with your log channel ID

    # Webhook settings (if you're using webhook)

    WEBHOOK = False  # Set this to True if you're using webhook

    # Bot Uptime tracking

    BOT_UPTIME = 'YOUR_BOT_UPTIME_START_TIME'  # This can be a timestamp or time value

    # Other configurations as needed