from twilio.rest import Client
from urllib2 import urlopen
import json
import time

#data for authorization for twilio
account_sid = "ACb2a7534e1d84c28169f5b13bb7764745"
auth_token = "787b63f2b13c95adf4fb70c5f247931a"
my_no="+91 9077174834"#your phone no

#data for authorization for rail api
mykey="4r4xgurbs4" #api key for railway api #100 requests per day


#sends the message=content to your phone
def sendmsg(content):
	try:	
	    client =  Client(account_sid, auth_token)
            message = client.messages.create(to=my_no, from_="+16194040245",body="Your status is "+content)
	except Exception as e:
		print "Sorry could not send message due to %s"%((type(e).__name__))


#returns json data for a particular pnr no
def getdata(pnr_no):
    url="https://api.railwayapi.com/v2/pnr-status/pnr/"+str(pnr_no)+"/apikey/"+mykey+"/"
    response = urlopen(url).read()
    obj = json.loads(response) 
    return obj
 
#processes json data #here interval is the period  in seconds after which you want to check pnr status again

def process(pnr_no,interval):
	try:
		data=getdata(pnrno)
                if (len(str(pnrno))!=10):
			print "Enter a valid 10 Digit PNR no"		
		elif data["response_code"]!=200:#There's something wrong
			if data["response_code"]==204:
				print "Empty response. Not able to fetch required data."
			elif data["response_code"]==401:
				print "Authentication Error. You passed an unknown API Key."
			elif data["response_code"]==403:
				print "Quota for the day exhausted. Applicable only for FREE users."
			elif data["response_code"]==405:
				print "Account Expired. Renewal was not completed on time."
			elif data["response_code"]==410:
				print "Flushed PNR / PNR not yet generated"			
			elif data["response_code"]==404:
				print "Service Down / Source not responding"
		else:
			i=1
			totalpassengers=data["total_passengers"]
			pstatus={} #stores present status of each passenger
			print "Current status at time "+str(time.ctime(time.time()))
			for passenger in data["passengers"]:#passenger is a dictionary
				pstatus[i]=passenger["current_status"]
				print "Passenger %s %s"%(i,pstatus[i])
				i+=1
			print "\n"
			#Check after period of one interval 
			while 1:
				cstatus={} #stores current status
				time.sleep(interval)
				data=getdata(pnrno)
				i=1
				for passenger in data["passengers"]:#passenger is a dictionary
					cstatus[i]=passenger["current_status"]
					i+=1	
				#checks whether current status is same after one inteval
				content=""
				for i in range(1,totalpassengers+1):
					if cstatus[i]!=pstatus[i]:
						content+="PNR status changed for passenger %s from %s to %s.\n"%(i,pstatus[i],cstatus[i])
				print "Checking status at "+(str(time.ctime(time.time())))
				time.sleep(2)			
				if len(content)==0:
					print "Sorry no change"
				else:
					print content
					sendmsg(content)
				print "\n"
	except:
		print "Sorry something went wrong.Retrying after 30 seconds....Please check your internet connection."
		time.sleep(30)
		process(pnrno,interval)			
								
pnrno=int(raw_input("Enter your pnr no\n"))#Ex:	2438994730
process(pnr_no,300)#Checks after interval of 5 minutes(300 s)	
'''
			
							
