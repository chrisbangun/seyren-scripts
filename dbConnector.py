#!/bin/python

import sqlite3

class DBConnector:

	_db = None
	_cursor = None

	def __init__(self):
		self._db = sqlite3.connect('checks-seyren.db')
		self._cursor = self._db.cursor()


	def create_table(self):
		self._cursor.execute('''
			CREATE TABLE checks(id INTEGER PRIMARY KEY, name TEXT)
			''')
		self._db.commit()

	def insert_data(self,checks_name):
		self._cursor.execute('''
			INSERT INTO checks(name)
			VALUES(?)''', (checks_name,))
		self._db.commit()

	def retrieve_data(self):
		return self._cursor.execute('''SELECT * FROM checks''')
		#return self._cursor.fetchall()

	def get_id_for_checks(self,checks_name):
		cursor = self._cursor.execute('''SELECT id from checks WHERE name = ? ''',(checks_name,))
		return cursor.fetchall()

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
	#dbConnector.create_table()
	cursor = dbConnector.retrieve_data()
	if cursor.fetchone():
		print "found"
	else:
		print "not found"

	#dbConnector.drop_table()
	#dbConnector.insert_data("TRIPOPS - Jetty status #HOTEL")
	#_ids = dbConnector.get_id_for_checks("HOPS - Jetty status #HOTEL")
	#for _id in _ids:
	#	print _id[0]
	#dbConnector.close_db()
