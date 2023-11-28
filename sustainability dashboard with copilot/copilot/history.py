from utils.db import db
from flask_pymongo import DESCENDING
from datetime import datetime
from utils.jwt_config import username_in_token, user_type_in_token
import logging

template = """
- You the Impact Investing Tech assistant. You are an expert in all things sustainability and impact. 
- You are positive, helpful and talkative. 
- You have a thorough understanding of SFDR and EU taxonomy regulations and are helpful at explaining it.
- You are a co-pilot and assist with compiling data requests, accessing databases and summarising data-heavy texts and tables.
- You explain what we do here at Impact Investing Tech, i.e. we facilitate the exchange of sustainability data between funds and companies.
- You can access the user's dataset. It contains both percentages and weighted values proportional to the ownership. You can analyse and visualise it with your functions.

- NEVER say to seek the assistance of experts. ALWAYS say Impact Investing Tech provides the necessary expertise and tools.
"""

def init_history(user_id):
    """this needs to have a button to reset the history, ie. start a new log. """
    username = username_in_token()
    user_type = user_type_in_token()
    
    if 'fund-investor' in user_type:
        
        from datatools.user_data import UserData
        user_data = UserData()
        user_data.pull_and_map_portfolios()
        
        custom = f"\n- You assist '{username}' with fund-level advice as an investor. "
        custom += f"\n\nYou have {len(user_data.portfolio_names())} portfolio(s). The names are the following: '" + "', '".join(user_data.portfolio_names()) + "'. "
        custom += user_data.string_of_companies() + user_data.string_of_metric_names()
        
    elif 'company-manager' in user_type:
        custom = f"\n- You assist {username} with company-level advice."
    else: 
        custom = f"\n- You assist {username} with advice with regards to building SAAS platforms in python, nest.js and angular, using a mongodb database."
 
    copilot_log = db.copilot_log
    chat_document = {
        "user_id": str(user_id),
        "username": username,
        "user-type": user_type_in_token(),
        "start_time": datetime.utcnow(),
        "messages": [{"role": "system", "content": template + custom}]}
    log = copilot_log.insert_one(chat_document)
    chat_id = log.inserted_id
    logging.info('copilot log %s is intialised, for user %s', str(chat_id), str(username))
    
    print(chat_document['messages'])
    return chat_document['messages']

def add_history(user_id, message):
    logging.info('copilot message is logged with add_history')
    try: 
        db.copilot_log.find_one_and_update(
        {"user_id": str(user_id)},
        {"$push": {"messages": message}},
        sort=[('_id', DESCENDING)])
    except Exception as e:
        logging.error("Add history raised this error:", e)
        init_history(user_id)        
    
def load_history(user_id) -> list[dict]:
    length = 10
    loaded_history = db.copilot_log.find_one({"user_id": str(user_id)}, 
                                             sort=[('_id', DESCENDING)]) 

    if loaded_history:
        # logging.info(f"There are {len(loaded_history['messages'])} messages in this conversation - but conversational memory size is set to {length}")
        
        if len(loaded_history['messages']) > length:
            return loaded_history['messages'][-length:]
        
        else: 
            return loaded_history['messages']
    else: 
        return init_history(user_id) 