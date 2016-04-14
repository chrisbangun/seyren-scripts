#!/bin/python

import sqlite3
import datetime

class DBConnector:

	_db = None
	_cursor = None

	def __init__(self):
		self._db = sqlite3.connect('checks-seyren.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		self._cursor = self._db.cursor()
		self.create_table()


	def create_table(self):
		self._cursor.execute(''' SELECT COUNT(*) FROM sqlite_master WHERE type = "table" AND name = "checks"''')
		result = self._cursor.fetchone()
		if not bool(result[0]):
			print "creating a new table named checks..."
			self._cursor.execute('''
					CREATE TABLE checks(id INTEGER PRIMARY KEY, name TEXT, state_time timestamp)
				''')
			self._db.commit()
			print "table has been created."
		else:
			print "connected to: checks-seyren.db"
			print "at:",str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			print "table's name: checks"
			

	def insert_data(self,checks_name,date):
		self._cursor.execute('''
			INSERT INTO checks(name,state_time)
			VALUES(?, ?)''', (checks_name,date,))
		self._db.commit()

	def retrieve_data(self):
		return self._cursor.execute('''SELECT * FROM checks''')
		#return self._cursor.fetchall()

	def get_id_for_checks(self,checks_name):
		cursor = self._cursor.execute('''SELECT id from checks WHERE name = ? ''',(checks_name,))
		return cursor.fetchall()

	def if_exist_on_table(self,checks_name):
		cursor = self._cursor.execute('''SELECT * FROM checks WHERE name = ?''',(checks_name,))
		return cursor.fetchone()

	def get_state_time_for_check(self,checks_name):
		cursor = self._cursor.execute('''SELECT state_time as "ts [timestamp]" from checks WHERE name = ?''',(checks_name,))
		return cursor.fetchone()

	def update_data(self,_id,checks_name):
		self._cursor.execute('''UPDATE checks set name = ? WHERE id = ? ''', (checks_name,_id))
		self._db.commit()

	def drop_table(self):
		self._cursor.execute('''DROP TABLE checks''')
		self._db.commit()

	def close_db(self):
		self._db.close()

if __name__ == '__main__':
	dbConnector = DBConnector()
	dbConnector.close_db()


