#!/usr/bin/python
# -*- coding:utf-8 -*-

import tweepy
import urllib, urllib2
import BeautifulSoup
import random as rd
from datetime import datetime
import time
from daemon import Daemon
import config

access_key = ''
access_secret = ''

def find_auth_token(page):
	a=page.find('twttr.form_authenticity_token =')
	b=page.find('\'',a)
	c=page.find('\'',b+1)
	return page[b+1:c]
	
def find_oauth_verifier(page):
	a=page.find('oauth_verifier')
	b=page.find('=',a)
	c=page.find('"',b+1)
	return page[b+1:c]

def get_access_token(user_id, password):
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
	redirect_url = auth.get_authorization_url()
	page_temp=opener.open(redirect_url).read()
	auth_token=find_auth_token(page_temp)
	login_params = urllib.urlencode({'authenticity_token':auth_token,'session[username_or_email]':user_id, 'session[password]':password , 'Authorize app':'allow'})
	page_content=opener.open(redirect_url, login_params) 
	soup = BeautifulSoup.BeautifulSoup(page_content)
	tag=soup.findAll('meta')[3]
	verifier=find_oauth_verifier(str(tag))
	auth.get_access_token(verifier)
	print "Add below lines into config.py"
	print "access_key = %s\naccess_secret = %s" % (auth.access_token.key, auth.access_token.secret)

def read_voice():
	try:
		lalavoicefile = config.lalavoicefile
	except AttributeError:
		print "Add a lalavoicefile variable into config.py"
		exit(1)
	f=open(lalavoicefile, "r")
	data=[]
	for i in f.read().splitlines():
		data.append(i)

	voice=[]
	line=''
	for i in data:
		line=line+i+'\n'
		if i=='':
			voice.append(line)
			line=''
	return voice

class LalaBotDaemon(Daemon):
	def run(self):
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_key, access_secret)
		api = tweepy.API(auth)

		voice = read_voice()
		while True:
			tweet=rd.choice(voice)
			try:
				api.update_status(tweet)
			except:
				g.write("error occured !! \n")
				g.write(tweet)
			time.sleep(1800)
			

if __name__ == "__main__":
	import sys
	try:
		access_key = config.access_key
		access_secret = config.access_secret
	except AttributeError:
		access_key = ''
		access_secret = ''

	if access_key == '' or access_secret == '':
		get_access_token(config.user_id, config.password)
		exit(1)

	daemon = LalaBotDaemon('/tmp/lalasweetbot.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
