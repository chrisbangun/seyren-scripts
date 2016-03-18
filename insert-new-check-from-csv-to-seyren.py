#!/bin/python
#ACB
import requests
import json
import csv
class CSVMetrics:
    URL = "http://seyren.[empty].com/api/checks"
    file = ""
    def __init__(self,_file):
        self.file = _file
    def insert_new_check(self):
        f = open(self.file)
        csv_f = csv.reader(f)
        print "======================================================="
        self.insert_new_check_util(csv_f)
    def insert_new_check_util(self,csv_file):
        first_row_index = -1
        skipped_row = iter(csv_file)
        next(skipped_row)
        for row in csv_file:
            first_row_index = first_row_index + 1
            if first_row_index != 0 and first_row_index==1:
                data = {
                    "name":row[1],
                    "description":row[2],
                    "target":row[3],
                    "warn":row[4],
                    "error":row[5],
                    "enabled":"true"
                    }
                #print data

                resp = requests.post(self.URL, data=datas, headers={'content-type': 'application/json'})
                if resp.status_code == 201:
                    print "new check is successfully inserted"
                else:
                    print resp
                    print "Failed to insert a new check"
                    
if __name__ == "__main__":
    file_location = raw_input("Insert csv file with the absolute path: ")
    csvMetric = CSVMetrics(file_location)
    print file_location
    csvMetric.insert_new_check()
