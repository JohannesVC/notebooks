from datatools.analyser_classes import Exchange, Dashboard
from datatools.user_data import UserData
import openai
import logging
from fuzzywuzzy import fuzz
from datatools.google_cloud_storage import GoogleCloudStorage
import matplotlib.pyplot as plt
import json
import re

class ANALYSER:
    def __init__(self):
        
        self.analyser_system_message = """
        You have been provided with a dataframe called *'df'*. 
        Subset the columns relevant to the user and visualise the DataFrame in Seaborn.
        You are using Python version 3.9.6 and Pandas 1.3.3.
        ALWAYS include a variable 'json_output' that results from df.to_json(). 
        ALWAYS include an 'Axes' object 'ax'. 
        NEVER include 'plt.show()'.
        **NEVER add backticks, markdown or plain text.**"""
        
    def primer(self, df, docstring) -> tuple:
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
        
    def ai_coder(self, df, docstring) -> str:
        primer_code, primer_desc = self.primer(df, docstring)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"system","content": self.analyser_system_message},
                    {"role":"user","content": primer_desc}],
            temperature=0,
            stream=False)
        try: 
            # logging.info('run_requests response is: ', str(response["choices"][0]["message"]["content"]))
            content = response["choices"][0]["message"]["content"]
            if content:
                code = primer_code + content
                
                if "`" not in code:
                    print(code)
                    return code
                
                elif "```python" in code:
                    matched_content = re.search(r"```python(.*?)```", code, flags=re.DOTALL)
                    if matched_content:
                        code_within_backticks = matched_content.group(1)
                        print(code_within_backticks)
                        return code_within_backticks
                
                else: 
                    logging.error("ai_coder is adding markdown and I cannot parse it.")
            
        except Exception as e:
            logging.error('run_request broke on this error: ', str(e))
            # raise Exception(f"run_request broke on: {str(e)}") from e

    def format_result(self, code, json_output):
        return f"""
    You wrote the following code: 

    ```python
    {code}
    ```

    Which produced:

    ```json
    {json_output}
    ```
    """

    def analyse_dfs(self, docstring, portfolio_id):
        exchange_instance = Exchange(portfolio_id)
        dashboard = Dashboard(exchange_instance)
        df = dashboard.pivot_attr_values()
        df.reset_index(inplace=True)
        # df.drop_duplicates(subset=['index', 'Metric'], inplace=True)
        try:
            self.code = ''
            local_vars = {'df': df, 'ax': None, 'plt': plt}
            code = self.ai_coder(df, docstring)
            exec(code, {}, local_vars)
            json_output = local_vars.get('json_output')
            ax = local_vars.get('ax')
            if ax: 
                storage = GoogleCloudStorage()
                name = storage.save_png(ax)
                url = storage.generate_signed_url(name)
                self.image = url
                # logging.info("this is the url analyse_df created: ", str(url))
            else:
                self.image = "No image generated."
                
            if json_output:
                self.data = self.format_result(code, json.dumps(json_output))
            else: 
                self.data = json.dumps(df.to_json())
                
        except Exception as e:
            logging.error('The analyser broke on: ', str(e))
            # raise Exception("Note that the analyser is still in beta mode. Try using more specific names.") from e
        
    def analyse_portfolio(self, docstring="analyse the dataset", portfolio_name=None):
        portfolios = UserData()
        portfolios.pull_and_map_portfolios()
        if len(portfolios.map) == 1:
            portfolio_id = portfolios.map[0]['_id']
            self.analyse_dfs(docstring, portfolio_id)
        elif len(portfolios.map) > 1:
            ratio = 50
            while ratio <= 100:
                matches = []
                for portfolio in portfolios.map:
                    if fuzz.partial_ratio(portfolio_name, portfolio['title']) > ratio:
                        matches.append(portfolio)
                    if len(matches) == 1:
                        self.analyse_dfs(docstring, portfolio['_id']) 
                ratio += 5 
        else: 
            raise ValueError(f"""No matches for '{portfolio_name}'. Try using a specific fund name. Alternatively, reset the chat as that refreshes my memory on who you are and which funds you own.""")