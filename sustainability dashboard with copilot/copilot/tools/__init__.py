functions = [{
            "name": "search_climatiq",
            "description": "Get the emission factor",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "The search term. Eg. hybrid car. NEVER include 'emission', 'carbon emissions' or 'emission factor'."
                        }, 
                    "region": {
                        "type": "string", 
                        "description": "UN/LOCODE for the region, e.g. GB for the UK, or US NYC for New York."
                        }, 
                    "year": {
                        "type": "number", 
                        "description": "the year that is searched"
                        },                   
                    },
                "required": ["query"]
                }},
             {
            "name": "climatiq_estimate",
            "description": "Estimate the emissions of the grid",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "The search term. Eg. energy mix. NEVER include 'emission', 'carbon emissions' or 'emission factor'."
                        }, 
                    "region": {
                        "type": "string", 
                        "description": "UN/LOCODE for the region. Two letters, e.g. GB."
                        }, 
                    "year": {
                        "type": "number", 
                        "description": "the year that is searched"
                        }, 
                    "energy": {
                        "type": "number", 
                        "description": "The energy in kWh for which the emissions are estimated."
                        },                
                    },
                "required": ["query", "energy"]
                }},
            {
            "name": "filtered_semantic_metricMeta",
            "description": "Use this to search a metric's metadata, including User Guidance, Calculation method and Frameworks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "The description or keywords for the search. Eg. 'scope 1 carbon emissions', 'water reuse in cities', 'gender balance in the board of directors'."
                        },
                    },
                "required": ["query"]
            }},
            {
            "name": "analyse_portfolio",
            "description": "Use this to answer any questions about the data in the database, including 'analyse my data', 'tell me the main takeaways', 'give me the key insights from my data', as well as prompts containing 'show me', 'visualise', or 'plot a graph'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "docstring": {
                        "type": "string", 
                        "description": "The user's query: transform this into a well-formed docstring with capital letters and punctuation."
                        },
                    "portfolio_name": {
                        "type": "string", 
                        "description": "The name of the user's fund."
                        },
                    },
                "required": ["query", "portfolio_name"]
                }
            },
            {
            "name": "underlying_data",
            "description": "Use this to answer any questions the underlying data on a company's performance on any given metric, including calculation methods, descriptions and policies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string", 
                        "description": "Pass a company's name."
                        },
                    "metric_name": {
                        "type": "string", 
                        "description": "Pass a metric's name."
                        },
                    },
                "required": ["query"]
                }
            }
]