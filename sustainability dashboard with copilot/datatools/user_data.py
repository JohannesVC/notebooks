from utils.db import db
from utils.jwt_config import fund_link_in_token
from datatools.analyser_classes import Exchange
from flask import abort
import logging 

class UserData:
    """Unlike the others, is this calling on the token.
    It finds a list of portfolios to then help connecting their titles to requests."""
    def __init__(self):
        self.fund_id = fund_link_in_token()
        self.map = []
        
   
    def pull_and_map_portfolios(self):
        portfolios = db.portfolios.find({'fund_link': str(self.fund_id)})
        if portfolios is None: 
            logging.error("portfolio_id not found")
            # abort(404, "portfolio not found")
        for port in portfolios:
            doc = {'_id': str(port['_id']),
                   'title': port['title'],
                   'description': port['description']}
            self.map.append(doc) 
        return self.map
            
    def portfolio_names(self):
        return [port['title'] for port in self.map]

    def exchanges_in_fund(self):
        for exchange in db.exchange.find({"fund_link": self.fund_id}):
            portfolio_link = str(exchange['portfolio_link'])
            yield Exchange(portfolio_link)

    def string_of_companies(self):
        """for system message"""
        exchange_list = []
        for portfolio, exchange_instance in zip(self.portfolio_names(), self.exchanges_in_fund()):
            list_of_dicts = exchange_instance.to_list_of_dicts()
            companies = [d['Company'] for d in list_of_dicts]
            companies_string = f"\nIn {portfolio} you have the following companies: '" + "', '".join(set(companies)) + "'. "
            exchange_list.append(companies_string)
        return ', '.join(exchange_list)

    def string_of_metric_names(self):
        """for system message"""
        exchange_list = []
        for portfolio, exchange_instance in zip(self.portfolio_names(), self.exchanges_in_fund()):
            list_of_dicts = exchange_instance.to_list_of_dicts()
            metrics = [d['Metric'] for d in list_of_dicts]
            metrics_string = f"\nIn {portfolio} you have the following metrics: " + ", ".join(set(metrics)) + ". "
            exchange_list.append(metrics_string)
        return ', '.join(exchange_list)