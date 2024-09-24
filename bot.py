from pyrogram import Client

from config import Config

class Bot(Client):

    def __init__(self):

        super().__init__(

            name="channel_bot",

            api_id=Config.API_ID,

            api_hash=Config.API_HASH,

            bot_token=Config.BOT_TOKEN,

            plugins={"root": "plugins"},  # Automatically loads the plugins from the 'plugins/' folder

            workers=200,  # Number of workers for handling updates

            sleep_threshold=15,  # Threshold for connection issues

        )

    async def start(self):

        await super().start()

        me = await self.get_me()

        self.mention = me.mention

        self.username = me.username

        print(f"{me.first_name} has started.")

    async def stop(self, *args):

        await super().stop()

        print("Bot stopped.")

# Run the bot

if __name__ == "__main__":

    Bot().run()