#!/bin/python
#ACB

import requests
import json
import csv
import sys

class Seyren:
   URL = "http://seyren.traveloka.com/api/checks"
   results = []
   
   def __init__(self):
     self.results = self.get_all_metrics()

   def get_all_metrics(self):
     metrics = requests.get(self.URL)
     result = metrics.json()
     return result['values']

   def show_checks(self):
    for data in self.results:
      print data['name']

   def prompt_for_user_input(self):
     while True:
      user_input = raw_input("(add | show | done): ")
      if user_input == "show":
        self.show_checks()
      elif user_input == "add":
        self.add_subscriber()
      else:
        break

   def add_subscriber(self):
     default_header = {'content-type' : 'application/json'}
     if len(sys.argv) == 1:
       target_subscriber = raw_input("target_subscriber (example: @beta): ")
       type_subscriber = raw_input("type (example: SLACK): ")
       check_name = raw_input("check's name: ")
     else:
        target_subscriber = sys.argv[1]
        type_subscriber = "SLACK"
        check_name = sys.argv[2]

     for data in self.results:
       if data['name'] == check_name:
        new_metrics = data
        d = {
              "target": target_subscriber,
              "type": type_subscriber,
              "ignoreWarn":"false",
              "ignoreError":"false",
              "ignoreOk":"false",
              "notifyOnWarn":"true",
              "notifyOnError":"true",
              "notifyOnOk":"true",
              "fromTime":"0000",
              "toTime":"2359",
              "su":"true",
              "mo":"true",
              "tu":"true",
              "we":"true",
              "th":"true",
              "fr":"true",
              "sa":"true",
              "enabled":"true"
          }
        new_metrics['subscriptions'] = d
        resp = requests.post(self.URL +"/"+ data['id']+"/subscriptions",json.dumps(new_metrics['subscriptions']), headers=default_header)
        if resp.status_code == 201:
          print "Successfully add new subscriber to ", check_name
        else:
          print resp
          print "Failed adding new subscriber to ",check_name
        json.dumps(new_metrics)


if __name__ == '__main__':
  seyren = Seyren()
  total_argument = len(sys.argv)
  if total_argument == 3:
    seyren.add_subscriber()
  else:
    seyren.prompt_for_user_input()