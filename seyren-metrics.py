#!/bin/python
#ACB

import requests
import json
import csv

class Seyren:
   URL = "http://seyren.traveloka.com/api/checks"
   results = []
   
   def __init__(self):
     self.results = self.get_all_metrics()

   def get_all_metrics(self):
     metrics = requests.get(self.URL)
     result = metrics.json()
     return result['values']

   def get_name(self):
     for data in self.results:
       print data['id']
       print data['name']
       print data['description']
       print data['target']
       print data['warn']
       print data['error']
       print "============================================================================================="
   
   def create_csv_file(self):
     with open("seyren-metrics.csv","w") as file:
       csv_file = csv.writer(file)
       for item in self.results:
         csv_file.writerow([item['name'], item['description'], item['target'], item['warn'], item['error']])

   def named_all_current_metrics_to_OLD(self):
     default_header = {'content-type' : 'application/json'}
     for data in self.results:
       new_metrics = data
       new_metrics['name'] = new_metrics['name']+" - [OLD]"
       resp = requests.put(self.URL+"/"+data['id'], json.dumps(new_metrics), headers=default_header)
       if resp.status_code != 201:
         print "Successfully update metrics name"
       else:
         print "Failed to update metrics name"
       json.dumps(new_metrics)


if __name__ == '__main__':
  seyren = Seyren()
  #seyren.get_name()
  #seyren.create_csv_file()
  seyren.named_all_current_metrics_to_OLD()