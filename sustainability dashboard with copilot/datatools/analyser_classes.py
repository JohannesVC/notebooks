from utils.db import db
from bson.objectid import ObjectId
import pandas as pd
import json
import numpy as np
from flask import abort
import logging

class Company:
    def __init__(self, company_id):
        self.document = db.companies.find_one({'_id': ObjectId(company_id)})
        if self.document is None: 
            logging.error("company_id not found")
            abort(404, description="company_id not found")
        self.title = self.document['title'] if self.document else None
        self.id = self.document['_id']
        
class MetricMeta:
    def __init__(self, metric_id):
        self.document = db.metricMeta.find_one({'_id': ObjectId(metric_id)}, {'embeddings': 0})
        if self.document is None: 
            logging.error("metricMeta not found")
            abort(404, description="metricMeta not found")
        self.title = self.document['title'] if self.document else None
        self.id = self.document['_id']
        self.aggregation_type = self.document.get('aggregation_type', '') if self.document else None

class MetricValue:
    def __init__(self, metric_id, company_link):
        self.document = db.metricValues.find_one({'metric_meta_link': metric_id, 'company_link': company_link})
        if self.document and self.document['value']:
            self.value = float(self.document['value']) 
        else: 
            self.value = np.nan
        self.aggregation_type = self.document.get('aggregation_type', '') if self.document else None
        self.submitted = self.document.get('is_public', False) if self.document else False
        self.id = self.document.get('_id', '') if self.document else ''

    def get_attributed_value(self, weight):
        if self.aggregation_type == 'sum':
            return self.value * weight
        else:
            return self.value

class Exchange:
    def __init__(self, portfolio_link):
        exchanges = db.exchange.find({"portfolio_link": str(portfolio_link)})
        self.exchange = [e for e in exchanges if e][0]
        # self.exchange = db.exchange.find_one({"_id": ObjectId(exchange_id)})
        if self.exchange is None: 
            logging.error("exchange not found")
            abort(404, description="exchange not found")
        
        self.id = str(self.exchange['_id'])
        
        self.portfolio = db.portfolios.find_one({'_id': ObjectId(str(portfolio_link))})
        if self.portfolio is None: 
            logging.error("portfolio_id not found")
            # abort(404, description="portfolio_id not found")
        self.companies = {}
        self.metric_meta = {}
        self.metric_values = {}
        self.pull_and_map()

    def pull_and_map(self):
        for comp in self.exchange['companies']:
            self.company_id = comp['company_link']
            self.companies[self.company_id] = Company(self.company_id)
            for metric_id in comp['requested_metrics']:
                self.metric_values[f"{metric_id}/{self.company_id}"] = MetricValue(metric_id, self.company_id)
                if metric_id not in self.metric_meta:
                    self.metric_meta[metric_id] = MetricMeta(metric_id)

    def get_row_data(self, weight, company_doc, metric_meta_doc, metric_value_doc):
        return {
            'Company': str(company_doc.title),
            'Metric': str(metric_meta_doc.title),
            'Value': float(metric_value_doc.value),
            'Weight': float(weight),
            'Attributed_Value': float(metric_value_doc.get_attributed_value(weight)),
            'Aggregation_Type': str(metric_value_doc.aggregation_type),
            'Submitted': bool(metric_value_doc.submitted),
            'Company_id': str(company_doc.id),
            'MetricMeta_id': str(metric_meta_doc.id),
            'MetricValue_id': str(metric_value_doc.id)}
        
    def to_list_of_dicts(self):
        all_row_data = []
        for comp in self.exchange['companies']:
            self.company_id = comp['company_link']
            company_doc = self.companies[self.company_id]
            if self.portfolio:
                weight = float(next((item["weight"] for item in self.portfolio['companies'] if item["company_link"] == self.company_id), np.nan))/float(100)
            else: weight = 1
            for metric_id in comp['requested_metrics']:
                metric_meta_doc = self.metric_meta[metric_id]
                metric_value_doc = self.metric_values[f"{metric_id}/{self.company_id}"]
                if metric_meta_doc and metric_value_doc:
                    row_data = self.get_row_data(weight, company_doc, metric_meta_doc, metric_value_doc)
                    all_row_data.append(row_data)
        return all_row_data
    
       
def custom_aggregation(group):
    aggregation_type = group.iloc[0].get('Aggregation_Type', 'sum') 
    if aggregation_type == 'percentage':
        return np.average(group['Attributed_Value'], weights=group['Weight'])
    else:
        return group['Attributed_Value'].sum()
                
class Dashboard:
    def __init__(self, exchange):
        self.exchange = exchange
        list_of_dicts = self.exchange.to_list_of_dicts()
        self.df = pd.DataFrame(list_of_dicts)
        self.df['Company'] = self.df['Company'].astype('str')
        # self.df.set_index('Metric', inplace=True)
    
    def pivot_values(self):
        attr_df = self.df.copy()
        return attr_df.pivot(index='Company', columns='Metric', values='Value')
    
    def pivot_attr_values(self):
        attr_df = self.df.copy()
        # attr_df.reset_index(inplace=True)
        attr_df.drop_duplicates(subset=['Company', 'Metric'], inplace=True)
        return attr_df.pivot(index='Company', columns='Metric', values='Attributed_Value')
        
    def get_aggregated_dataframe(self):
        aggregated_df = self.df.groupby(['Metric']).apply(custom_aggregation).reset_index(name='aggregated_value')
        aggregated_df.set_index('Metric', inplace=True)
        aggregated_df['coverage'] = self.df.groupby('Metric')['Submitted'].mean() * 100
        aggregated_df['MetricMeta_id'] = self.df.groupby('Metric')['MetricMeta_id'].first()
        return aggregated_df

class Export:
    def __init__(self, exchange, dashboard):
        self.exchange = exchange
        self.dashboard = dashboard
    
    def to_restructured_json(self):
        df = self.dashboard.df
        aggregated_df = self.dashboard.get_aggregated_dataframe()
        restructured_json = []
        parent = None
        for idx, agg_row in aggregated_df.iterrows():
            df_dict = agg_row.to_dict()
            metricMeta_id = df_dict['MetricMeta_id']
            aggregate_pdf = {"metricMeta_id": str(metricMeta_id), "exchange_id": str(self.exchange.id)}
            parent = {'data': {'metric': idx,
                               'value': df_dict['aggregated_value'] if not pd.isna(df_dict['aggregated_value']) else None,
                               'coverage': df_dict['coverage'],
                               'download': aggregate_pdf}, 
                      'children': []}
            restructured_json.append(parent)

            for _, row in df.iterrows():
                df2_dict = row.to_dict()
                MetricValue_id = df2_dict['MetricValue_id']
                metric = df2_dict['Metric']
                if metric == idx:
                    child = {'data': {'metric': idx,
                                      'companies': df2_dict['Company'],
                                      'value': df2_dict['Value'] if not pd.isna(df2_dict['Value']) else None,
                                      'attributed_value': df2_dict['Attributed_Value'] if not pd.isna(df2_dict['Attributed_Value']) else None,
                                      'coverage': df2_dict['Submitted'],
                                      'download': {"MetricValue_id": str(MetricValue_id)}}, 
                             }          
                    parent['children'].append(child)

        return restructured_json