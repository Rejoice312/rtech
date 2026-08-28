from logic.google.gemini import Gemini, GEMINI_MODELS
from config import GEMINI_API_KEY
from time import sleep
import json
import config


def ai_reply(prompt, as_dict:bool = True):
    for index, model in enumerate(GEMINI_MODELS):
        try:
            gemini = Gemini(model=model, api_key= GEMINI_API_KEY)
        except Exception as e:
            if config.DEBUG:
                print(e)
                return
            else:
                raise e
        try: 
            reply = gemini.reply(prompt)
        except Exception as e:
            print(e)
            if model == GEMINI_MODELS[-1]: 
                return
            sleep(3**(index + 2))

        # validate reply
        if as_dict:
            reply = (
                reply.replace('`', '')
                .replace('json', '')
                .replace('\r', '')
                .replace('**', '')
            )
            try:
                reply = json.loads(reply)
            except:
                return
        return reply
