from pyrogram import Client
from pyrogram.errors import BadRequest

async def send_all_polls(chat_id, client: Client, questions, custom_description=None):
    answer_mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}  # Maps the correct answer to quiz option index
    max_question_length = 255
    max_option_length = 100
    max_description_length = 200

    for question in questions:
        try:
            text = question.get('Question')
            options = [
                question.get('Option A', ''), 
                question.get('Option B', ''), 
                question.get('Option C', ''), 
                question.get('Option D', '')
            ]
            correct_option = question.get('Answer')  # Extract the correct option from the CSV

            # Map correct option (A, B, C, D) to an index for quiz (0, 1, 2, 3)
            correct_option_id = answer_mapping.get(correct_option.upper(), None) if correct_option else None
            
            description = question.get('Description', '')

            # Check for missing data in the question or options
            if not text or any(not option for option in options) or correct_option_id is None:
                await client.send_message(chat_id=chat_id, text="Some data is missing or incorrect in the MCQ. Please check and upload again.")
                continue

            # Ensure description contains "@SecondCoaching"
            if '@SecondCoaching' not in description:
                description += ' @SecondCoaching'

            # Append custom description if provided
            if custom_description:
                description += f' {custom_description}'

            # Send quiz if a correct option is available
            if correct_option_id is not None:
                await client.send_poll(
                    chat_id=chat_id,
                    question=text,
                    options=options,
                    type='quiz',  # Ensures the poll is sent as a quiz
                    correct_option_id=correct_option_id,  # Correct answer index (0, 1, 2, 3)
                    explanation=description,
                    is_anonymous=True  # Anonymous quiz
                )
            else:
                # Send as an anonymous poll if no correct answer is provided
                await client.send_poll(
                    chat_id=chat_id,
                    question=text,
                    options=options,
                    is_anonymous=True
                )

        except BadRequest as e:
            error_message = "Aapne jo CSV file upload ki hai usme kuch gadbadi hai. Kripya use shi karke punh upload kre."
            await client.send_message(chat_id=chat_id, text=error_message)
            continue
