from copilot.tools.climatiq import search_climatiq, climatiq_estimate
from copilot.tools import functions
from copilot.tools.semantic_search import filtered_semantic_metricMeta
from copilot.tools.analyser_v2 import ANALYSER
from copilot.tools.underlying_data import underlying_data
from copilot.history import add_history
import json
import logging
import openai

def interpreting_data(user_id, prompt:str, name:str, args:str, prefix, data:str): # generator
    full_response = ''
    completion_res = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo-0613",
                            temperature=0,
                            messages=[
                                {"role": "user", "content": prompt},
                                {"role": "assistant", "content": 'null', "function_call": {"name": name, "arguments": args}},
                                {"role": "function", "name": name, "content": data}],
                            stream=True,
                            functions=functions)
    try:
        for res in completion_res:
            content_chunk = res.choices[0].delta.get("content", "")
            if content_chunk:
                full_response += content_chunk
                yield json.dumps({'message': content_chunk}).encode('utf-8')
        
        data_log = {"role": "system", "content": f"{prefix} + {data}"}        
        add_history(user_id, data_log)
        interpretation_log = {"role": "assistant", "content": full_response}        
        add_history(user_id, interpretation_log)
    except TypeError:
        raise TypeError(f"The interpreting_data's input is None.")
    except Exception as e:
        raise Exception(f"interpreting_data returned an unexpected error: {e}") from e

def function_call(user_id, prompt:str, name:str, arguments:str):
    args = json.loads(arguments) 
    data = None
    logging.info(f"Searching {name} with: {str(args)}") 
    try: 
        if 'search_climatiq' in name:
            logging.info('Accessing climatiq')
            # yield json.dumps({'loading': 'Accessing Climatiq... \n'}).encode('utf-8')
            data = search_climatiq(**args)
                
        elif 'climatiq_estimate' in name:
            logging.info('accessing climatiq for estimates')
            # yield json.dumps({'loading': 'Accessing Climatiq for estimates... \n'}).encode('utf-8')
            data = climatiq_estimate(**args)
                                                        
        elif 'filtered_semantic_metricMeta' in name:
            logging.info('accessing filtered_semantic_metricMeta')
            # yield json.dumps({'loading': 'Accessing our semantic search engine for metrics... \n'}).encode('utf-8')
            data = filtered_semantic_metricMeta(**args)
        
        elif 'analyse_portfolio' in name:
            logging.info('accessing analyse_portfolio')
            yield json.dumps({'loading': 'Accessing our analytics function... \n'}).encode('utf-8')
            analyser = ANALYSER()
            analyser.analyse_portfolio(**args)
            data = analyser.data
            yield json.dumps({'image_url': analyser.image + ' '}).encode('utf-8')
            
            
        elif 'underlying_data' in name:
            logging.info('Accessing underlying_data')
            # yield json.dumps({'loading': "Accessing the company's underlying data... \n"}).encode('utf-8')
            data = underlying_data(**args)
        
        if data:
            logging.warning(f"The data returned from the function call has a length of {str(len(str(data).split(' ')))}.")
            logging.info(f'Successfully got {name} results.') 
            logging.info(f'Interpreting data from function call: {str(data)}')
            prefix = f"You have returned this data from our dataset: " if 'analyse_portfolio' not in name else ''
            yield from interpreting_data(user_id, prompt, name, str(args), prefix, str(data)) 
            
    except NameError:
        logging.error(f"Unfortunately, {name} isn't assigned to a function.")
    except Exception as e:
        logging.error("function_call ran into this error: ", exc_info=True)
        raise e
         