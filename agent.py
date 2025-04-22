import speech_recognition as sr
from pydantic_ai import Agent
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import asyncio


load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')


class AgentOrder(BaseModel):
    product: str | None
    amount: int | None


# Define agent
transcript_agent = Agent(
    model='groq:llama-3.3-70b-versatile',
    result_type=AgentOrder,
    system_prompt="""
        You are an excellent grocery shopping list writer assistant.
        When provided with two possibilities for items to add to a shopping list, you will
        return the most appropriate of the two.

        If neither of the possibilities seem appropriate for a grocery shopping list, return 
        product as empty string.

        If the returned item includes an amount, you will split the item into product and amount.
        There should be no amount in the product string.
        If the returned item does not include an amount, leave the amount as None.
        You do not have to translate from hebrew to english but if the item is in hebrew it should
        adhere to the rules mentioned above with regard to no amount in product.

        Whether in english or in hebrew, the product should not include an amount!

    """
)


def transcript(message):
    """ This function returns english and hebrew transcript to feed to agent """
    # Speech recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(message) as source:
        audio_data = recognizer.record(source)

        try:
            text_en = recognizer.recognize_google(audio_data, language="en-US")
            text_he = recognizer.recognize_google(audio_data, language="he-IL")
            return text_en, text_he
        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError:
            print("Could not request results, please check your internet connection.")


def transcript_order(message):
    try:
        text_en, text_he = transcript(message)

        # Try if there is access to groq to run agent
        try:
            # Run transcript agent
            item_to_add = transcript_agent.run_sync(user_prompt=f'please return appropriate item: '
                                                                f'{text_en} or '
                                                                f'{text_he}')
            # If agent came to decision
            if item_to_add.output != '':
                result = item_to_add.output
                # Make dict from agent RunResult
                result_dict = result.model_dump()
                product = result_dict['product']
                amount = result_dict['amount']

                if product != '':
                    return [product, amount]
                else:
                    return "Could not understand your order. Please try again."

            # If agent could not make a decision
            else:
                return "Could not understand your order. Please try again."

        except:
            # # Run alternative manual process
            return text_en, text_he

    except TypeError:
        pass
