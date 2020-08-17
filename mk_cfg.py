#这段程序用于根据链路状态信息的数据库，自动生成MIP运行所需配置文件
# coding:utf-8
import pymysql
import json
import re
import os,subprocess
from operator import itemgetter

import psutil
import collections
import os
import ConfigParser

p = os.popen("hostname")
line = p.readline()
hostname=line.strip()
hostname=hostname+'%'
print(hostname)

db = pymysql.connect("114.212.112.36", "root", "123456","communication")

if 'LEO' in hostname:
	c1 = db.cursor()
	c1.execute("select * from link_table1 where destport like '%s' AND sourcetype='GEO'"%hostname)
	leo_links = c1.fetchall()
	c2 = db.cursor()
	c2.execute("select * from link_table1 where sourceport like '%s' AND desttype='GEO'"%hostname)
	leo_links += c2.fetchall()

	print("-----------------leo_links------------------",leo_links)
	print(len(leo_links))

	#use id in link_table1 
	c3 = db.cursor()
	leo_flow0=[]
	for i in range(len(leo_links)):
	    c3.execute("select * from flow_table1 where link_id=%s and starttime=0"%leo_links[i][0])
	    leo_flow0+=c3.fetchall()

	print("---------------leo_flow0-------------------",leo_flow0)

	c4 = db.cursor()
	c4.execute("select * from link_table1 where id=%s"%leo_flow0[0][1])
	leo_link0=c4.fetchall()

	print("---------------leo_link0------------------",leo_link0)

	if leo_link0[0][5]=='GEO':
	    home_agent_ip=leo_link0[0][2]
	else:
	    home_agent_ip=leo_link0[0][7]

	print("------------home_agent------------",home_agent_ip)

	if leo_link0[0][5]=='GEO':
	    home_address_ip=leo_link0[0][7]
	else:
	    home_address_ip=leo_link0[0][2]

	print("------------home_address------------",home_address_ip)

	if_gw_table={}
	for i in range(len(leo_links)):
	    if leo_links[i][5]=='GEO':
		if_gw_table[leo_links[i][8]]=leo_links[i][2]
	    else:
		if_gw_table[leo_links[i][3]]=leo_links[i][7]

	print("----------------if_gw_table--------------",if_gw_table)

	CONFIG_FILE = "mn.cfg"

	spi = 256
	key = 1234567812345678
	home_agent = home_agent_ip
	home_address = home_address_ip
	if_gateways = if_gw_table


	conf = ConfigParser.ConfigParser()

	cfgfile = open(CONFIG_FILE,'w')

	conf.add_section("MobileNodeAgent")

	conf.set("MobileNodeAgent", "SPI", spi)
	conf.set("MobileNodeAgent", "KEY", key)
	conf.set("MobileNodeAgent", "HOME_AGENT", home_agent)
	conf.set("MobileNodeAgent", "HOME_ADDRESS", home_address)
	conf.set("MobileNodeAgent", "IF_GATEWAYS", if_gateways)

	conf.write(cfgfile)

	cfgfile.close()

else:
	c5 = db.cursor()
	c5.execute("select * from link_table1 where destport like '%s' AND sourcetype='LEO'"%hostname)
	geo_links = c5.fetchall()
	c6 = db.cursor()
	c6.execute("select * from link_table1 where sourceport like '%s' AND desttype='LEO'"%hostname)
	geo_links += c6.fetchall()

	print("-------------geo_links-------------",geo_links)

	for i in range(len(geo_links)):
		if geo_links[i][5] == 'GEO':
		    address_ip = geo_links[i][2]
		else:
		    address_ip = geo_links[i][7]

	print("------------------address_ip----------------",address_ip)

	#creat ha.cfg
	CONFIG_FILE = "ha.cfg"

	address = address_ip
	auth_table = {256:"1234567812345678"}


	conf = ConfigParser.ConfigParser()

	cfgfile = open(CONFIG_FILE,'w')

	conf.add_section("HomeAgent")

	conf.set("HomeAgent", "ADDRESS", address)
	conf.set("HomeAgent", "AUTH_TABLE", auth_table)

	conf.write(cfgfile)

	cfgfile.close()

db.close()
