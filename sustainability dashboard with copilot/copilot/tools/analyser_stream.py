from datatools.analyser_classes import Exchange, Dashboard
from datatools.user_data import UserData
import openai
import logging
from fuzzywuzzy import fuzz
from datatools.google_cloud_storage import GoogleCloudStorage
import matplotlib.pyplot as plt
import json
from typing import Generator
import re

analyser_system_message = """
You have been provided with a dataframe called *'df'*. 
Your job is analyse and visualise it.
You are using Python version 3.9.6 and Pandas 1.3.3.
ALWAYS include a variable 'json_output' that results from df.to_json(). 
ALWAYS include an 'Axes' object 'ax'. 
NEVER include 'plt.show()'.
**NEVER add backticks, markdown or plain text.**"""
      
def primer(df, docstring) -> tuple:
    primer_desc = '"""\nUse the dataframe called df to plot: \n' + docstring \
        + ". \nThe dataframe called 'df' has the following columns: '" \
        + "','".join(str(x) for x in df.columns) + "'. "
    for i in df.columns:        
        if df.dtypes[i]=="O":
            primer_desc += "\nThe column '" + i + "' has categorical values '" + "','".join({str(x) for x in df[i]}) + "'. "
        elif df.dtypes[i]=="int64" or df.dtypes[i]=="float64":
            primer_desc += "\nThe column '" + i + "' is type " + str(df.dtypes[i]) + " and contains numerical values. "
    primer_desc += "\nLabel the x and y axes appropriately. Add a title." + '\n"""\n' # Set the fig subtitle as empty.
    primer_code = "import pandas as pd" \
                + "\nimport matplotlib.pyplot as plt \nimport seaborn as sns\n" \
                + "fig,ax = plt.subplots(1,1,figsize=(10,4))" \
                + "\nax.spines['top'].set_visible(False)" \
                + "\nax.spines['right'].set_visible(False)" \
                + "\ndf = df.copy()\n"
                
    return primer_code, primer_desc
    
def ai_coder(df, docstring):
    primer_code, primer_desc = primer(df, docstring)
    response = openai.ChatCompletion.create(
        model="gpt-4",  
        messages=[{"role":"system","content": analyser_system_message},
                  {"role":"user","content": primer_desc}],
        temperature=0, stream=True)
    try: 
        full_response = primer_code
        flag = 0
        for res in response:
            content_chunk = res.choices[0].delta.get("content", "")
            full_response += content_chunk
            if "`" in content_chunk:
                flag = 1
                continue
            if flag == 0:
                print(content_chunk, end='')
                yield content_chunk
            
        if "```" in full_response:
            matched_content = re.search(r"```python(.*?)```", full_response, flags=re.DOTALL)
            if matched_content:
                code_within_backticks = matched_content.group(1)
                yield code_within_backticks
            else: raise ValueError("ai_coder is adding markdown and can't parse it.")
            
    except Exception as e:
        # logging.error('run_request broke on this error: ', str(e))
        raise Exception(f"run_request broke on: {str(e)}") from e

def format_result(code, json_output):
    
    yield f"""
You wrote the following code: 

```python
{code}
```

Which produced a graph and the following result:

```json
{json_output}
```
"""

def analyse_df(docstring, portfolio_id) -> Generator[dict[str, str], None, None]: 
    exchange_instance = Exchange(portfolio_id)
    dashboard = Dashboard(exchange_instance)
    df = dashboard.pivot_attr_values()
    df.reset_index(inplace=True)
    try:
        local_vars = {'df': df, 'ax': None, 'plt': plt}
        code = ''
        for chunk in ai_coder(df, docstring):
            code += chunk
            yield {'code': chunk}
            
        exec(code, {}, local_vars)
        json_output = local_vars.get('json_output')
        ax = local_vars.get('ax')
        if ax: 
            storage = GoogleCloudStorage()
            name = storage.save_png(ax)
            url = storage.generate_signed_url(name)
            yield {'image_url': url}
            logging.info("this is the url analyse_df created: ", str(url))
        else:
            yield {'image_url':"No image generated."}
        
        for data_ in format_result(code, json.dumps(json_output)):
            yield {'data': data_}
    
    except Exception as e:
        logging.error('The analyser broke on: ', str(e))
        raise Exception("Note that the analyser is still in beta mode.") from e
     

def analyse_portfolio(docstring, portfolio_name=None):
    user_data = UserData()
    user_data.pull_and_map_portfolios()
    if len(user_data.map) == 1:
        portfolio_id = user_data.map[0]['_id']
        yield from analyse_df(docstring, portfolio_id)
    
    elif len(user_data.map) > 1:
        ratio = 50
        while ratio <= 100:
            matches = []
            for portfolio in user_data.map:
                if fuzz.partial_ratio(portfolio_name, portfolio['title']) > ratio:
                    matches.append(portfolio)
                if len(matches) == 1:
                    yield from analyse_df(docstring, portfolio['_id']) 
            ratio += 5 
            
    else: 
        raise ValueError(f"""No matches for '{portfolio_name}'. Try using a specific fund name. Alternatively, reset the chat as that refreshes my memory on who you are and which funds you own.""")
    
