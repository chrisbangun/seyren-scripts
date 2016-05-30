#!/bin/python
#ACB
import requests
import json
import logging
import collections
import slacker
import logging
from dbConnector import DBConnector
import datetime
from datetime import timedelta

class UnknownState:
    URL = "http://seyren.traveloka.com/api/checks"
    results = []
    checksDict = {}
    API_TOKEN= 'xoxb-18174125041-fLDaQzlmFgp2TUke2HCJSs0o'

    unknown_checks = 0
    total_checks = 0
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
            self.total_checks = self.total_checks + 1
            if data['state'] == "UNKNOWN":
                print data['name']
                if data['subscriptions']:
                    self.unknown_checks = self.unknown_checks + 1
                    subscriptions = data['subscriptions']
                    list_of_target = []
                    for target in subscriptions:
                        list_of_target.append(target['target'])
                    self.checksDict[str(data['name'])] = list_of_target
        return self.checksDict

    def notify(self,target,key,target_type):
        slack = slacker.Slacker(self.API_TOKEN)
        message_to_send = "Hello, I've been asked by @release-eng to notify you that `"+str(key)+"` is currently in an *unkown* state"
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
        temp_subscriber = ["@kevin","@adi"]
        #for subscriber in list_of_subscriber:
        for subscriber in temp_subscriber:
            _subscriber = str(subscriber)
            if(_subscriber.startswith('@')):
                print "AAAAAAA"
                self.notify(_subscriber[1:],key,"user")
                #self.notify("kevin",key,"user")
            elif(_subscriber.startswith('#')):
                #print "BBBBB"
                self.notify(_subscriber,key,"channel")
                # self.notify("kevin",key,"channel")

    def notify_subscriber(self):
        self.logger.info("total checks: %s", self.total_checks)
        self.logger.info ("unknown checks: %s",self.unknown_checks)
        threshold_for_alert = self.total_checks/4
        self.logger.info ("threshold_for_alert: %s", threshold_for_alert)
        if self.unknown_checks < threshold_for_alert:
            print "YES"
            for key in self.checksDict.keys():
                self.identify_subscriber_type(self.checksDict[key],key)
        #else:
        #    self.notify("adichris","all checks","user")
class Main:
    unknownState = None
    dbConnector = None
    def __init__(self):
        self.unknownState = UnknownState()
        self.dbConnector = DBConnector()
    def validate_the_unknown_state(self):
        checkDictionary = self.unknownState.get_unknown_state_checks()
        delete_table = False
        for key in checkDictionary.keys():
            if self.dbConnector.if_exist_on_table(key):
                if self.worth_to_notify(key):
                    delete_table = True
                    self.unknownState.notify_subscriber()
            else:
                self.dbConnector.insert_data(key,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if delete_table:
            self.dbConnector.drop_table()
        self.dbConnector.close_db()

    def worth_to_notify(self,key):
        state_time = self.dbConnector.get_state_time_for_check(key)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time = datetime.datetime.now().strptime(str(current_time),"%Y-%m-%d %H:%M:%S")
        time_difference = current_time - state_time[0]
        time_difference_in_minutes = time_difference.total_seconds() / 60
        #self.logger.info(key, " has been in unknown state for: ", time_difference_in_minutes," minutes")
        if time_difference_in_minutes >= 30 :
            return True
        return False
if __name__ == '__main__':
    main = Main()
    main.validate_the_unknown_state()
