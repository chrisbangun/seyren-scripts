#!/bin/python
#ACB

import requests
import json
import re
import logging
import sys
import fileinput
from graphite_get_mongoPrimary import Graphite
from seyren_get_mongo_checks import Seyren

class MongoAlert:
  
  URL = "http://seyren.traveloka.com/api/checks"
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

  old_primary_mongos = []
  
  def __init__(self):
    try:
      with open("old-mongos.txt",'r') as ins:
        for line in ins:
          self.old_primary_mongos.append(line)
    except:
      self.logger.error("Failed to open/read old-mongos.txt. The file may not exist")
      sys.exit(0)

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
      if mongo_machine.lower() in data['name'].lower():
        old_target = data['target']
        new_metric = data
        new_metric['target'] = self.change_metric_to_primary_mongo(old_target,complete_machine,mongo_machine)
        resp = requests.put(self.URL+"/"+data['id'], json.dumps(new_metric), headers=default_header)
        if resp.status_code != 201:
          self.logger.info("target metric has been succesfully updated: %s", new_metric['target'])
        else:
          self.logger.error("Failed to update target metric for: %s", data['name'])

  def check_for_primary_change(self):
    changed = False
    temp_mongos = []
    for old,current in zip(self.old_primary_mongos,self.current_primary_mongos):
      temp_mongos.append(current)
      old = old.replace("\n","")
      if old != current:
        changed = True
        mongo_machine,complete_machine = self.__get_mongo_machine(current)
        self.update_target_metrics_in_seyren(mongo_machine,complete_machine,current)

    self.update_mongo_primary_list(temp_mongos)
    if not changed:
      self.logger.info("All mongo primary machines haven't been changed")

  def update_mongo_primary_list(self,old_mongos_primary):
    file = None
    try:
      file = open("old-mongos.txt",'w')
    except:
      self.logger.error("Cannot create/write to file old-mongos.txt")
      sys.exit(0)
    counter = 1
    for mongos in old_mongos_primary:
      if counter == len(old_mongos_primary):
        file.write(mongos)
      else:
        file.write(mongos+"\n")
      counter = counter + 1
      file.truncate()
    file.close()


if __name__ == '__main__':
  mongoAlert = MongoAlert()
  graphite = Graphite()
  seyren = Seyren()
  
  current_primary_mongos = graphite.get_mongo_primary_metrics()
  json_data_from_seyren = seyren.get_json_seyren()
  
  mongoAlert.set_current_primary_mongos(current_primary_mongos)
  mongoAlert.set_seyren_json_data(json_data_from_seyren)
  mongoAlert.check_for_primary_change()
