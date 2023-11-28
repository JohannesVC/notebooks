import openai
from copilot.tools import functions
from copilot.function_call import function_call
from copilot.history import add_history, load_history
import os
import json
import time
import logging

openai.api_key = os.getenv('OPENAI_API_KEY')

def openai_stream(user_id):
    loaded_history = load_history(user_id)  
    print('this is the openai_stream input: ', loaded_history)  
    response = openai.ChatCompletion.create(
                                model="gpt-4",
                                messages=[{"role": m["role"], "content": m["content"]}
                                        for m in loaded_history], 
                                stream=True,
                                temperature=0.4,
                                max_tokens=1024,
                                functions=functions)
    return response
    
def stream_chunks(text):
    words = text.split(" ")
    for word in words:
        time.sleep(0.1)
        yield json.dumps({'message': word + ' '}).encode('utf-8')


def openai_call(user_id, prompt:str):
    full_response = ""
    arguments = ""
    name = ""

    try: 
        for res in openai_stream(user_id):
            delta = res.choices[0].delta
            
            if "function_call" not in delta:
                content_chunk = delta.get("content", "")
                full_response += content_chunk
                yield json.dumps({'message': content_chunk}).encode('utf-8')
                
            elif "name" in delta.function_call: 
                name += delta.function_call.name
                # yield from stream_chunks('Let me have a look in my database. Hang on, this can take a minute... \n')
                
            elif "arguments" in delta.function_call: 
                arguments += delta.function_call.arguments

            if res.choices[0].finish_reason:
                if "function_call" in res.choices[0].finish_reason:
                    logging.info("function call: %s %s", name, arguments)
                    yield from function_call(user_id, prompt, name, arguments)
                    
                elif "stop" in res.choices[0].finish_reason: 
                    message = {"role": "assistant", "content": full_response}        
                    add_history(user_id, message)
                    
    except Exception as e:
        yield from stream_chunks(f"Sorry, I'm having some trouble. I forwarded the error to our tech team. {e}")

# cd C:/Users/johan/Documents/GitHub/supernova-py/
# flask --app api_orion run --debug
