#!/bin/python
#ACB

import requests
import json
import re
import logging
from graphite_get_mongoPrimary import Graphite
from seyren_get_mongo_checks import Seyren

class MongoAlert:
  
  URL = "http://seyren.[empty].com/api/checks"
  metric_names = []
  seyren_json_data = []
  current_primary_mongos = []

  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)
  handler = logging.FileHandler('update-seyren-if-primary-change.log')
  handler.setLevel(logging.INFO)

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)


  old_primary_mongos = [
    "[empty]",
    "[empty]",
    "[empty]",
    "[empty]"
  ]
  
  def __get_mongo_machine(self,primary_mongos):
    mongo_complete_machine = primary_mongos.split(".")[1]
    return mongo_complete_machine.split("0")[0],mongo_complete_machine

  def set_metric_names(self,_metric_names):
    self.metric_names = _metric_names

  def set_seyren_json_data(self,_json_data):
    self.seyren_json_data = _json_data
  
  def set_current_primary_mongos(self,_current_primary_mongos):
    self.current_primary_mongos = _current_primary_mongos
  
  
  def change_metric_to_primary_mongo(self,old_target,primary_machine,mongo_machine):
    pattern = "("+mongo_machine+"(?:\d*\.|\*)?\d*[_|A-Za-z]*)"
    matchTarget = re.sub(pattern,primary_machine,old_target,False)
    return matchTarget
    

  def update_target_metrics_in_seyren(self,mongo_machine,complete_machine,current):
    default_header = {'content-type' : 'application/json'}
    for data in self.seyren_json_data:
      if mongo_machine in data['name'] and "[OLD]" not in data['name']:
        old_target = data['target']
        new_metric = data
        new_metric['target'] = self.change_metric_to_primary_mongo(old_target,complete_machine,mongo_machine)
        resp = requests.put(self.URL+"/"+data['id'], json.dumps(new_metric), headers=default_header)
        if resp.status_code != 201:
          self.logger.info("target metric has been succesfully updated")
        else:
          self.logger.error("Failed to update target metric for: ", data['name'])

  def check_for_primary_change(self):
    changed = False
    for old,current in zip(self.old_primary_mongos,self.current_primary_mongos):
      if old != current:
        changed = True
        mongo_machine,complete_machine = self.__get_mongo_machine(current)
        self.update_target_metrics_in_seyren(mongo_machine,complete_machine,current)
        self.old_primary_mongos = old

    if not changed:
      self.logger.info("All mongo primary machines haven't been changed")



if __name__ == '__main__':
  mongoAlert = MongoAlert()
  graphite = Graphite()
  seyren = Seyren()
  
  current_primary_mongos = graphite.get_mongo_primary_metrics()
  json_data_from_seyren = seyren.get_json_seyren()
  
  mongoAlert.set_current_primary_mongos(current_primary_mongos)
  mongoAlert.set_seyren_json_data(json_data_from_seyren)
  mongoAlert.check_for_primary_change()
