#!/bin/python
#ACB

import requests
import json
import csv

class Seyren:
	URL = "http://seyren.traveloka.com/api/checks"
	

	def insert_new_check(self):
		name= raw_input("name: ")
		target = raw_input("target: ")
		description = raw_input("description: ")
		enabled = raw_input("enabled: ")
		warn = raw_input("warn: ")
		error = raw_input("error: ")
		
		self.__insert_new_check_util(name,target,description,enabled,warn,error)

	def __insert_new_check_util(self,name,target,description,enabled,warn,error):

		data = {
		   "name":name,
		   "description":description,
		   "target":target,
		   "warn":warn,
		   "error":error,
		   "enabled":enabled
		}

		resp = requests.post(self.URL, data=json.dumps(data), headers={'content-type': 'application/json'})
		#print resp
		#print data

		if resp.status_code == 201:
			print "new check was successfully inserted"
		else:
			print "Failed to insert new check"


	


if __name__ == "__main__":
	seyren = Seyren()
	input = raw_input("insert new check? (yes | no): ")
	while input == "yes":
		seyren.insert_new_check()
		input = raw_input("insert new check? (yes | no): ")