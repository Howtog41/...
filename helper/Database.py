import motor.motor_asyncio

from datetime import datetime, timedelta

from config import Config

class Database:

    def __init__(self):

        # Initialize MongoDB client and collection

        self.client = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI)

        self.db = self.client[Config.DB_NAME]

        self.users_collection = self.db[Config.USERS_COLLECTION]

    # Fetch a user from the database

    async def get_user(self, user_id):

        user = await self.users_collection.find_one({'user_id': user_id})

        return user

    # Add a new user to the database

    async def add_user(self, user_id):

        user = await self.get_user(user_id)

        if not user:

            new_user = {

                "user_id": user_id,

                "channels": []  # Default empty channels list

            }

            await self.users_collection.insert_one(new_user)

            return new_user

        return user  # Return existing user

    # Update user's channels

    async def add_channel(self, user_id, channel_id):

        await self.users_collection.update_one(

            {'user_id': user_id},

            {'$addToSet': {'channels': channel_id}}

        )

    # Remove a channel from the user's list

    async def remove_channel(self, user_id, channel_id):

        await self.users_collection.update_one(

            {'user_id': user_id},

            {'$pull': {'channels': channel_id}}

        )

    # Get all the user's channels

    async def get_channels(self, user_id):

        user = await self.get_user(user_id)

        if user:

            return user.get('channels', [])

        return []

    # Method to add a user with the trial period

    async def add_user_with_trial(self, user_id, join_date):

        await self.users_collection.update_one(

            {'user_id': user_id},

            {'$set': {'join_date': join_date, 'authorized': False}},

            upsert=True

        )

    # Method to check if trial period has expired

    async def is_trial_expired(self, user_id):

        user = await self.users_collection.find_one({'user_id': user_id})

        if not user:

            return True

        join_date = user.get('join_date')

        if not join_date:

            return True

        trial_period_end = join_date + timedelta(minutes=5)

        return datetime.utcnow() > trial_period_end

    # Unauthorize a user

    async def unauthorize_user(self, user_id):

        await self.users_collection.update_one(

            {'user_id': user_id},

            {'$set': {'authorized': False, 'expiration_date': None}}

        )

    # Check if user is authorized and their access is still valid

    async def is_authorized(self, user_id):

        user = await self.get_user(user_id)

        if not user or not user.get('authorized', False):

            return False

        expiration_date = user.get('expiration_date')

        if expiration_date and datetime.utcnow() > expiration_date:

            return False

        return True

    # Authorize a user and set expiration date

    async def authorize_user(self, user_id, expiration_date):

        await self.users_collection.update_one(

            {'user_id': user_id},  # Find the user by their Telegram ID

            {

                '$set': {

                    'authorized': True,  # Set authorized to True

                    'expiration_date': expiration_date  # Save the expiration date

                }

            },

            upsert=True  # If the user doesn't exist, insert a new document

        )

    ### NEW METHODS FOR AUTO-FORWARD PLUGIN ###

    # Set the private channel ID

    async def set_private_channel(self, user_id, private_channel_id):

        await self.users_collection.update_one(

            {'user_id': user_id},

            {'$set': {'private_channel_id': private_channel_id}},

            upsert=True

        )

    # Set the public channel ID

    async def set_public_channel(self, user_id, public_channel_id):

        await self.users_collection.update_one(

            {'user_id': user_id},

            {'$set': {'public_channel_id': public_channel_id}},

            upsert=True

        )

    # Set the time for auto-forwarding

    async def set_forward_time(self, user_id, forward_time):

        await self.users_collection.update_one(

            {'user_id': user_id},

            {'$set': {'forward_time': forward_time}},

            upsert=True

        )

    # Set the number of messages to forward daily

    async def set_num_messages(self, user_id, num_messages):

        await self.users_collection.update_one(

            {'user_id': user_id},

            {'$set': {'num_messages': num_messages}},

            upsert=True

        )

    # Get the private channel ID

    async def get_private_channel(self, user_id):

        user = await self.get_user(user_id)

        return user.get('private_channel_id')

    # Get the public channel ID

    async def get_public_channel(self, user_id):

        user = await self.get_user(user_id)

        return user.get('public_channel_id')

    # Get the time for auto-forwarding

    async def get_forward_time(self, user_id):

        user = await self.get_user(user_id)

        return user.get('forward_time')

    # Get the number of messages to forward daily

    async def get_num_messages(self, user_id):

        user = await self.get_user(user_id)

        return user.get('num_messages')

# Initialize the Database object

db = Database()