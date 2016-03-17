#!/bin/python
#ACB

import json
import requests
import logging


class Graphite:
  mongo_isPrimary_metrics = [
   "collectd.mongodata*_traveloka_com.mongostat.counter.mongo_primary",
   "collectd.mongofb*_traveloka_com.mongostat.counter.mongo_primary",
   "collectd.mongohotel*_traveloka_com.mongostat.counter.mongo_primary",
   "collectd.mongohnet*_traveloka_com.mongostat.counter.mongo_primary"
   ]
  
  mongo_primary_metrics = []
  URL = "http://graphiteweb.traveloka.com/render?target=#&format=json"

  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)

  handler = logging.FileHandler('update-seyren-if-primary-change.log')
  handler.setLevel(logging.INFO)

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  
  def __init__(self):
    self.__get_json_data()

  def __get_json_data(self):
    self.logger.info("[1]retrieving all primary mongo...")
    for metric in self.mongo_isPrimary_metrics:
      mongo_url = self.URL.replace('#',metric)
      response = requests.get(mongo_url)
      data = response.json()
      if not data:
        self.logger.error("No Json object has been retrieved. The metrics might not exist")
        return
      self.mongo_primary_metrics.append(self.__find_mongo_primary(data))
    self.logger.info("Done...")

  def __find_mongo_primary(self,data):
    for d in data:

      if abs(d['datapoints'][0][0] - 1.0) < 0.0000001:
        return d['target']

  def get_mongo_primary_metrics(self):
    return self.mongo_primary_metrics

#if __name__ == '__main__':
#  graphite = GRAPHITE() 
#  graphite.get_json_data()
#  mongo_primary_metrics = graphite.get_mongo_primary_metrics()
#  for metric in mongo_primary_metrics:
#    print metric