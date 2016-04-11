#!/bin/python
#ACB

import requests
import json
import logging
import collections
import slacker
import logging

class UnknownState:
	URL = "http://seyrendotcom/api/checks"
	results = []
	checksDict = {}
	API_TOKEN= 'xxxxxx'

	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)
	handler = logging.FileHandler('seyren-unknown-check.log')
	handler.setLevel(logging.INFO)

	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  	handler.setFormatter(formatter)
  	logger.addHandler(handler)

	def __init__(self):
		self.checksDict = collections.defaultdict(list)
		self.results = self.__get_all_metrics()


	def __get_all_metrics(self):
		metrics = requests.get(self.URL)
		result = metrics.json()
		return result['values']

	def get_results(self):
		return self.results

	def get_unknown_state_checks(self):
		self.logger.info("getting all checks with unknown state")
		for data in self.results:
			if data['state'] == "UNKNOWN":
				if data['subscriptions']:
					subscriptions = data['subscriptions']
					list_of_target = []
					for target in subscriptions:
						list_of_target.append(target['target'])
					self.checksDict[str(data['name'])] = list_of_target
	
	def notify(self,target,key,target_type):
		slack = slacker.Slacker(self.API_TOKEN)
		print target
		message_to_send = "Hello, I've been asked by @release-eng to notify you that "+str(key)+" is currently in an *unkown* state"
		continue_text = "Please kindly check your metrics, machine or anything related to this. Thanks :bow: :bow:"
		user_id = ""
		try:
			user_id = slack.users.get_user_id(target)
		except:
			self.logger.error("cannot get user_id for target: %s", target)
		try:
			if target_type == "channel":
				slack.chat.post_message(target,message_to_send+" "+continue_text,"release-eng-bot",None,None,None)
			else:
				slack.chat.post_message(user_id,message_to_send+" "+continue_text,"release-eng-bot",None,None,None)
		except:
			self.logger.error("cannot send message to user/channel")


	def identify_subscriber_type(self,list_of_subscriber,key):
		for subscriber in list_of_subscriber:
			_subscriber = str(subscriber)
			if(_subscriber.startswith('@')):
				self.notify(_subscriber[1:],key,"user")
			elif(_subscriber.startswith('#')):
				self.notify(_subscriber,key,"channel")

	def notify_subscriber(self):
		for key in self.checksDict.keys():
			self.identify_subscriber_type(self.checksDict[key],key)


if __name__ == '__main__':
	unknownState = UnknownState()
	unknownState.get_unknown_state_checks()
	unknownState.notify_subscriber()
