#!/bin/python
#ACB

import requests
import json
import logging

class Seyren:

  list_of_mongos = [
     "mongodata",
     "mongofb",
     "mongohotel",
     "mongohnet"
  ]

  URL = "http://seyren.traveloka.com/api/checks"
  results = []
  metric_names = []

  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)

  handler = logging.FileHandler('update-seyren-if-primary-change.log')
  handler.setLevel(logging.INFO)

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)

  def __init__(self):
    self.results = self.__get_all_metrics()
    self.__get_metrics_name_from_seyren()

  def __get_all_metrics(self):
    self.logger.info("[2] getting all metrics from Syren...")
    metrics = requests.get(self.URL)
    result = metrics.json()
    return result['values']
  
  def __get_metrics_name_from_seyren(self):
    for mongo in self.list_of_mongos:
      for data in self.results:
        if mongo in data['name'] and "[OLD]" not in data['name']:
          self.metric_names.append(data['name'])

  def get_metric_names(self):
    return self.metric_names
  
  def get_json_seyren(self):
    return self.results
  


#if __name__ == '__main__':
#  seyren = Seyren()
#  seyren.get_metrics_name_from_seyren()
#  metric_names = seyren.get_metric_names()
  