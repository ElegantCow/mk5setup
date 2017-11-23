#!/usr/bin/env python
# -*- coding: utf-8 -*-

import  paramiko
import datetime
import argparse
import os
import getpass

def buffer_text(inBuff):
	lineBuffer =""
	while not inBuff.channel.exit_status_ready():
		lineBuffer += inBuff.read(1)
       		if lineBuffer.endswith('\n'):
            		yield lineBuffer
            		lineBuffer = ''

def format_print(stdout, command, station, exp):
	if command == "ntpq -np":
	 for num, line in enumerate(stdout):
		if num >1 and num <3:
			print station+ " offset: "+ line.split()[-2]
	elif command == "./dim "+exp+station:
		for l in buffer_text(stdout):
			if "End with Enddim" in l:
				print l
				break 
	else:
		print stdout.read()

def ssh_connect(station, commands, exp):
	hostname = "mk5"+station
	print "Conectiong to "+hostname
	password = ""
	#password = getpass.getpass("Please enter the password for oper@mk5"+station+". '\n'")
	username = "oper"
	port = 22

	try:
    		client = paramiko.SSHClient()
		client.load_system_host_keys()
    		client.set_missing_host_key_policy(paramiko.WarningPolicy)
    
    		client.connect(hostname, port=port, username=username, password=password)
		for command in commands:
    			stdin, stdout, stderr = client.exec_command(command,get_pty=True)
    		
    		
			if not stdout:
				print stderr.read()
			else:
				format_print(stdout, command,station, exp)

	finally:
    		client.close()
	

def main():
 	parser = argparse.ArgumentParser()
	parser.add_argument("Exp", help="Experiment name. E.g. r4765")
	parser.add_argument("Stns", help="Stations participating, format hb-ke-yg-ho")
	args = parser.parse_args()
	exp =args.Exp
	stations = []
	
	for stn in range(len(args.Stns.split('-'))):
		stations.append(args.Stns.split('-')[stn])
	for stn, station in enumerate(stations):
		dimino = "./dim "+ exp+station
		commandsmk5 = ["ps -ef | grep -i dim", "/usr/local/bin/mark5/EndDIM", dimino, "ntpq -np" ]
		ssh_connect(station, commandsmk5, exp)
			
			
main()
