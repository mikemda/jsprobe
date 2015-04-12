#!/bin/python
"""Usage: 
	jsprobe.py  <url> [--cookie=<cookie> --cookiedomain=<cookiedomain>] [--proxyhost=<proxyhost> --proxyport=<proxyport>] [--debug]
	jsprobe.py -h | --help
	jsprobe.py --version

Arguments:
	<url>    web url to use for testing
	
Options:
	-h --help            show this
	--debug              shows browser window
	--version            shows the current version
"""
from docopt import docopt
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
import time
from pyvirtualdisplay import Display
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def runapp(url, driver):
	try:
		print '+++trying '+url
		driver.get(url)
		wait = ui.WebDriverWait(driver, 10) # timeout after 10 seconds
		
		settledurl = driver.current_url
		print '+++settled on '+settledurl
		probe_window(driver)
	except:
		print "error in runapp"
		print "Unexpected error:", sys.exc_info()[0]
		raise


def probe_all(driver):
	probe_window(driver)
	probe_jqueryv1(driver)
	probe_jqueryv2(driver)
	probe_drupal(driver)
	probe_wordpress(driver)
	probe_generator(driver)
	probe_DARLA(driver)
	probe_DARLA_CONFIG(driver)
	probe_backbone(driver)
	probe_modernizr(driver)
	probe_microsoft_dynamics_crm(driver)
	

def probe_modernizr(webdriver):
	try:
		modenizer = webdriver.execute_script("return Modernizr._version")
		print "Modernizr: "+modenizer
	except:
		pass


def probe_microsoft_dynamics_crm(webdriver):
	try:
		serverurl = webdriver.execute_script("return SERVER_URL")
		userlangcode = webdriver.execute_script("return USER_LANGUAGE_CODE")
		orglangcode = webdriver.execute_script("return ORG_LANGUAGE_CODE")
		orgname = webdriver.execute_script("return ORG_UNIQUE_NAME")
		appversion = webdriver.execute_script("return APPLICATION_FULL_VERSION")
		
		# if we got this far without an error then we must be crm
		print "Microsoft Dynamics CRM found:"
		print "\tSERVER_URL: "+serverurl
		print "\tUSER_LANGUAGE_CODE: "+str(userlangcode)
		print "\tORG_LANGUAGE_CODE: "+str(orglangcode)
		print "\tORG_UNIQUE_NAME: "+orgname
		print "\tAPPLICATION_FULL_VERSION: "+appversion
		#bonus
		print "\tIS_PATHBASEDURLS: "+str(webdriver.execute_script("return IS_PATHBASEDURLS"))
		print "\tIS_OUTLOOK_CLIENT: "+str(webdriver.execute_script("return IS_OUTLOOK_CLIENT"))
		print "\tIS_ONLINE: "+str(webdriver.execute_script("return IS_ONLINE"))
		print "\tIS_LIVE: "+str(webdriver.execute_script("return IS_LIVE"))
		print "\tIS_ONPREMISE: "+str(webdriver.execute_script("return IS_ONPREMISE"))
		print "\tCURRENT_WEB_THEME: "+str(webdriver.execute_script("return CURRENT_WEB_THEME"))
		print ""
	except:
		pass


	
def probe_window(webdriver):
	print "getting global window object"
	globalitems=[]
	noargfunctions=[]
	properrors=0
	try:
		javascript="jsproberesults=[];for (name in this) {  try{jsproberesults.push( {'name':''+name, 'value': ''+this[name]})}catch(err){var anyerror='ignore'};}"
		webdriver.execute_script(javascript)
		javascript="return jsproberesults"
		jsresults = webdriver.execute_script(javascript)
		for logline in jsresults:
			if '[native code]' not in logline['value'] and 'jsproberesults' not in logline['name']:
				globalitems.append(logline)
		
		print str(len(globalitems))+' global items found'
		for record in globalitems:
			if record['value'].startswith('function '+record['name']+'()') or record['value'].startswith('function ()'):
				noargfunctions.append(record['name'])
			print '\t'+record['name']+': '+record['value']
		print ""
		print "found "+str(len(noargfunctions))+" lone functions"
		for record in noargfunctions:
			print "\t"+record
			
	except WebDriverException as e:
		print "Selenium Exception: Message: "+str(e)
	except:
		print 'probe_window FAILED'
		print "Unexpected error:", sys.exc_info()[0]
		pass


def probe_DARLA(webdriver):
	try:
		darla = webdriver.execute_script("return DARLA.version")
		print "DARLA: "+darla
	except:
		pass

def probe_DARLA_CONFIG(webdriver):
	try:
		darla = webdriver.execute_script("return DARLA_CONFIG.version")
		print "DARLA_CONFIG: "+darla
	except:
		pass
		
def probe_backbone(webdriver):
	try:
		backbone = webdriver.execute_script("return Backbone.VERSION")
		print "Backbone: "+backbone
	except:
		pass


def probe_jqueryv1(webdriver):
	try:
		jquery = webdriver.execute_script("return $.fn.jquery")
		print "jquery: "+jquery
	except:
		#print 'probe_window FAILED'
		pass

def probe_jqueryv2(webdriver):
	try:
		jquery = webdriver.execute_script("return jQuery.fn.jquery")
		print "jquery: "+jquery
	except:
		#print 'probe_window FAILED'
		pass

def probe_drupal(webdriver):
	try:
		data = webdriver.execute_script("return Drupal")
		print "Drupal CMS detected"
	except:
		pass

def probe_wordpress(webdriver):
	# <meta name="generator" content="WordPress 4.1.1" />
	try:
		metatag = webdriver.find_element_by_xpath("//meta[@name='generator']")
		data = metatag.get_attribute("content")
		if 'WordPress' in data:
			print "WordPress CMS detected"
	except:
		pass


def probe_generator(webdriver):
	# <meta name="generator" content="WordPress 4.1.1" />
	try:
		metatag = webdriver.find_element_by_xpath("//meta[@name='generator']")
		data = metatag.get_attribute("content")
		print "Generator: "+data
	except:
		pass





if __name__ == '__main__':
    arguments = docopt(__doc__, version='jsprobe 0.1')
    url = arguments['<url>']
    debug = arguments['--debug']
    proxyhost = arguments['--proxyhost']
    proxyport = arguments['--proxyport']
    cookie = arguments['--cookie']
    cookiedomain = arguments['--cookiedomain']
    display=''
    if debug == False:
		# hide the window unless in debug mode
		display = Display(visible=0, size=(1920, 1080))
		display.start()
	
    closewindow=debug==False
    profile = webdriver.FirefoxProfile()
    if proxyhost  and proxyport:
		print "+++using proxy "+proxyhost
		profile.set_preference("network.proxy.type", 1)
		profile.set_preference("network.proxy.http", proxyhost)
		profile.set_preference("network.proxy.http_port", int(proxyport))
		profile.set_preference("network.proxy.ssl", proxyhost)
		profile.set_preference("network.proxy.ssl_port", int(proxyport))
		profile.update_preferences()
    driver = webdriver.Firefox(firefox_profile=profile)
    
    # setup any cookies we may have.
    if cookie:
		driver.get('http://'+cookiedomain+"/web.config")
		
		cookies = cookie.split('; ')
		for cookietoadd in cookies:
			splitter = cookietoadd.index('=')
			mykey = cookietoadd[:splitter]
			myvalue=cookietoadd[splitter+1:]
			print "+++adding cookie "+mykey+":"+str(myvalue)
			driver.add_cookie({'name' : mykey, 'value' : myvalue})    
    
    runapp(url, driver)
    
    if debug == False:
		driver.quit()
		display.stop()





