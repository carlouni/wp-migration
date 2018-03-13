###########################################################
#
# This python script is used for taking a WP site's DB and
# loading it in a different host with a different URL.
#
# Written by : Gonzalo Cardenas
# Created date: March 13, 2018
# Tested with : Python 3.6.4
# Script Revision: 0.1
#
##########################################################

from dotenv import load_dotenv
load_dotenv()

import os
import pipes
import re
from datetime import datetime

from pathlib import Path
#app_path = os.fspath(Path('.'))
app_path = os.path.dirname(os.path.abspath(__file__))
print(app_path)
env_path = app_path + '/.env'

# loads cionfig parameters
load_dotenv(dotenv_path=env_path)

proc_date = datetime.now().strftime('%Y%m%d%H%M%S')
data_path = app_path + '/../data/tmp_' + proc_date + '.sql'
data_bkp = app_path + '/../data/bkp_' + proc_date + '.sql'

# generate origin db backup
print('Downloading DB origin...')

result = os.system('mysqldump -h ' + os.getenv('ORIGIN_DB_HOST') + ' -u ' +
	os.getenv('ORIGIN_DB_USER') + ' -p' + pipes.quote(os.getenv('ORIGIN_DB_PASS')) + ' ' +
	os.getenv('ORIGIN_DB_NAME') + ' >> ' + data_path)

print('DB origin downloaded.')

# generate destination db backup
print('Downloading DB destination for backup...')

result = os.system('mysqldump -h ' + os.getenv('DESTINATION_DB_HOST') + ' -u ' +
	os.getenv('DESTINATION_DB_USER') + ' -p' + pipes.quote(os.getenv('DESTINATION_DB_PASS')) + ' ' +
	os.getenv('DESTINATION_DB_NAME') + ' >> ' + data_bkp)

print('DB destination downloaded and backed up.')

# replace URLs inside the .sql file
print('Replacing URLs on the DB...')

result = os.system('sed -i \'s/' + re.escape(os.getenv('ORIGIN_SITE_URL')) + '/' +
	re.escape(os.getenv('DESTINATION_SITE_URL')) + '/g\' ' + data_path)

print('URLs replaced.')

# Connecting to mysql
import mysql.connector

# Drop and create destination database
cnx = mysql.connector.connect(user=os.getenv('DESTINATION_DB_USER'), 
							  password=os.getenv('DESTINATION_DB_PASS'),
							  host=os.getenv('DESTINATION_DB_HOST'))
cursor = cnx.cursor()

query = ('DROP DATABASE ' +  os.getenv('DESTINATION_DB_NAME'))
cursor.execute(query)
print(cursor)

query = ('CREATE DATABASE ' +  os.getenv('DESTINATION_DB_NAME'))
cursor.execute(query)
print(cursor)

cursor.close()
cnx.close()

# Load new database
from subprocess import Popen, PIPE

command = ['mysql', '-h' + os.getenv('DESTINATION_DB_HOST'), '-u' + os.getenv('DESTINATION_DB_USER'),
			'-p' + os.getenv('DESTINATION_DB_PASS'), os.getenv('DESTINATION_DB_NAME'), '--database=' +
			os.getenv('DESTINATION_DB_NAME')]

with open(data_path) as input_file:
	proc = Popen(command, stdin = input_file, stderr=PIPE, stdout=PIPE )
	try:
		print('Loading new DB...')
		output,error = proc.communicate()
		print('New DB loaded')
	except TimeoutExpired:
	    proc.kill()
	    output,error = proc.communicate()