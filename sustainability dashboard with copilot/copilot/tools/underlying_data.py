from datatools.user_data import UserData
from fuzzywuzzy import fuzz
from utils.db import db
import json
import logging

def underlying_data(company_name, metric_name):
    user = UserData()
    user.pull_and_map_portfolios()
    
    ratio = 50
    while ratio <= 100:
        matches = []
        for exchange_instance in user.exchanges_in_fund():
            for dict in exchange_instance.to_list_of_dicts():
                if fuzz.partial_ratio(company_name, dict['Company']) > ratio:
                    if fuzz.partial_ratio(metric_name, dict['Metric']) > ratio:
                        matches.append(dict)
        if len(matches) == 1:
            logging.info("underlying_data found a match for company_name and metric_name")
            metricValue = db.metricValues.find_one({'metric_meta_link': matches[0]['MetricMeta_id'],
                                                    'company_link': matches[0]['Company_id']}, 
                                                   {'_id':0, 'company_link': 0, 'metric_meta_link': 0})
            if metricValue: 
                return json.dumps({"company_name": matches[0]['Company'], 
                                   "metricMeta_name": matches[0]['Metric'], 
                                   "metricValue": metricValue})
            else: 
                raise ValueError(f"No submission data was found for '{company_name}' and '{metric_name}'.")
        ratio += 5
    raise ValueError(f"No matches for company '{company_name}' and metric '{metric_name}'.")