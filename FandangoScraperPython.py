import os
import requests
from bs4 import BeautifulSoup
import datetime
import time
import re


#List of all urls to every theater in America that is on Fandango.com
theaterLinks=[]

    
def soupLink(url, baseURL='', headers={}):
    """ Takes in a URL and proceeds to return a BeautifulSoup HTML parsed object. BASEURL is required when the URL does not have HTTPS://
    """
    r = requests.get(baseURL + url, data={})
    c = r.content
    return BeautifulSoup(c,'html.parser')

#We don't want to have to run the script to generate the theater links every time, so we check if the file exists
if (not os.path.isfile('TheaterLinks.txt')):
    #The starting URL. It has Fandango's list of states which are links to the theaters in the states
    startURL = 'https://www.fandango.com/site-index/movietheaters.html'
    
    soup = soupLink(startURL)
    
    #List of all links to the state webpages
    #We only want the states in USA, not Canada, and other islands
    stateLinks = soup.find_all("a")
    stateLinks = stateLinks[0:52]
    
    with open('TheaterLinks.txt', 'a') as the_file:
        #To traverse each of the states, we need this base url
        baseURL = 'https://www.fandango.com/site-index/'
        for astate in stateLinks:
            soupstate = soupLink(astate['href'], baseURL)
            stateTheaterLinks = soupstate.find_all("a")
            for aStateTheater in stateTheaterLinks:
                theaterLinks.append(aStateTheater['href'])
                the_file.write(aStateTheater['href'] + '\n')                
else:
    with open('TheaterLinks.txt', "r") as myfile:
        theaterLinks = myfile.readlines()


#For formatting when doing the requests
sTomorrow = str(datetime.date.today() + datetime.timedelta(1))

#Since we need a header to make it look like we are visiting on a desktop
userAgentHeader = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
userAgentHeader={'User-agent': 'Mozilla/5.0'}

itest=0

rMovieTimes=False
rUnlocker=False

#Now go through every Theater in America
for theaterLink in theaterLinks:
    itest = itest+1
    if itest == 2:
        break;
    #Strip is necessary because there is a /n at the end
    theaterLink=theaterLink.strip()
    #Need to find the code in the theater url. In TheaterLinks.txt, it follows underscore, but underscores become hyphens after the URL redirects
    m = re.search('.*_(.*)\/theaterpage', theaterLink)
    theaterCode = m.group(1)
    theaterLink = requests.get(theaterLink).url
    theaterSoup = soupLink(theaterLink)
    theaterLinkReqMovieTime='https://www.fandango.com/napi/theaterMovieShowtimes/'+theaterCode+'?startDate='+sTomorrow+'&isdesktop=true'
    theaterLinkReqMovieTimeValue=theaterLink+'?date='+sTomorrow
    
    data={'referer':theaterLinkReqMovieTimeValue}
    headers = {**data, **userAgentHeader}
    
    #For some reason, we need to REQUEST.GET this url below with key/value so that our IP will be unlocked or something
    #r = requests.get('https://www.fandango.com/napi/nearbyTheaters?limit=7&zipCode=99515', data = {'referer':'https://www.fandango.com/regal-dimond-center-9-cinemas-aacwx/theater-page?date=2018-03-16'},headers=headers)
    #So, we basically need the zipcode of the theater
    zipElement=theaterSoup.find_all("div", {"class": "js-closestTheaters-lazy"})
    sZipCode=zipElement[0].get('data-theater-zip')
    theaterUnlockerLink = 'https://www.fandango.com/napi/nearbyTheaters?limit=7&zipCode=' + sZipCode
    rUnlocker = requests.get(theaterUnlockerLink, headers=headers)
    while(True):
        if ('Not Authorized' in rUnlocker.text):
            print('Not Authorized when requesting the zipcode link')
            time.sleep(0.5)
            rUnlocker = requests.get(theaterUnlockerLink, headers=headers)
        else:
            break
    rMovieTimes = requests.get(theaterLinkReqMovieTime, headers=headers)
    while(True):
        if ('Not Authorized' in rUnlocker.text):
            print('Not Authorized when getting the Movie times')
            time.sleep(0.5)
            rMovieTimes = requests.get(theaterLinkReqMovieTime, headers=headers)
        else:
            break
    
