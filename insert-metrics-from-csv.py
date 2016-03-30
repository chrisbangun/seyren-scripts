#!/bin/python
#ACB
import requests
import json
import csv
class CSVMetrics:
    URL = "http://seyren.traveloka.com/api/checks"
    file = ""
    def __init__(self,_file):
        self.file = _file
    def insert_new_check(self):
        f = open(self.file)
        csv_f = csv.reader(f)
        print "======================================================="
        self.insert_new_check_util(csv_f)

    def insert_subscriber(self,check,target_subscriber):
            subscribers = target_subscriber.split(',')
            print check
            for user in subscribers:
                d = {
                    "target": user,
                    "type": "SLACK",
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
                check['subscriptions'] = d
                resp = requests.post(self.URL +"/"+ check['id']+"/subscriptions",json.dumps(check['subscriptions']), headers={'content-type': 'application/json'})
                if resp.status_code == 201:
                    print "Successfully add new subscriber to ", check['name']
                else:
                    print resp
                    print "Failed adding new subscriber to ",check['name']
        
    def insert_new_check_util(self,csv_file):
        first_row_index = -1
        skipped_row = iter(csv_file)
        next(skipped_row)
        for row in csv_file:
            first_row_index = first_row_index + 1
            if first_row_index != 0:
                data = {
                    "name":row[1]+" "+row[3],
                    "description":row[4],
                    "target":row[5],
                    "warn":row[6],
                    "error":row[7],
                    "enabled":"true"
                    }

                _results = []
                resp = requests.post(self.URL, data=json.dumps(data), headers={'content-type': 'application/json'})
                if resp.status_code == 201:
                    print "new check is successfully inserted"
                    _metrics = requests.get(self.URL)
                    _result = _metrics.json()
                    _results = _result['values']
                    target_subscriber = row[8]
                    for d in _results:
                        if data['name'] == d['name']:
                            self.insert_subscriber(d,target_subscriber)
                else:
                    print resp
                    print "Failed to insert a new check"
                


                    
if __name__ == "__main__":
    file_location = raw_input("Insert csv file with the absolute path: ")
    csvMetric = CSVMetrics(file_location)
    print file_location
    csvMetric.insert_new_check()