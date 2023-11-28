import requests
import os
import logging

MY_API_KEY = os.getenv('CLIMATIQ_API_KEY')


def search_climatiq(year: int = 2021, **args) -> list[dict]:
    logging.info('Searching climatiq')
    url = "https://beta4.api.climatiq.io/search"
    authorization_headers = {"Authorization": f"Bearer: {MY_API_KEY}"}
    params = {**args, "year": year, "data_version": "^1"}
    result = requests.get(url, params=params, headers=authorization_headers).json()
    keys_to_keep = ["name", "source", "year", "region_name", "description", "unit", "factor", "constituent_gases", "activity_id"]
    first_results = result["results"][0:4]
    list_of_results = []
    for result_ in first_results:
        keep = {key: result_[key] for key in keys_to_keep if key in result_}
        list_of_results.append(keep)
        print("search_climatiq list:", list_of_results)
    if not list_of_results:
        logging.error("search_climatiq is returning an empty list of results")
        raise ValueError("The list is empty.")
    else: 
        return list_of_results

def climatiq_estimate(year: int = 2021, energy = 100, **args):
    result = search_climatiq(**args)
    activity_id = result[0]["activity_id"] 
    parameters = {
            "energy": energy,
            "energy_unit": "kWh"
        }
    json_body = {
            "emission_factor": {
            "activity_id": activity_id,
            "region": args['region'],
            "data_version": "^1"},
            "parameters": parameters}
    authorization_headers = {"Authorization": f"Bearer: {MY_API_KEY}"}
    response = requests.post("https://beta4.api.climatiq.io/estimate", json=json_body, headers=authorization_headers)
    return response.json()