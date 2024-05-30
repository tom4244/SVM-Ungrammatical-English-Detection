#!/usr/bin/python3
""" This method to find commonality of trigrams is DEPRECATED
    The Yahoo BOSS service on which this was based has been discontinued
    Replace the Yahoo query in this file with a similar web query such as python Scrapy
    or use a corpus such as the Project Gutenberg corpus described at
    https://github.com/openzim/gutenberg
   
    Retrieves the number of times an exact sequence of words
    has been used in documents on the web according to Yahoo
    Based on the Boss search API from the Yahoo "BOSS Team"
    Requires 'config.json' file with Yahoo Boss authorizations.
    Usage: yahoo-query.get_web_uses("words to search")
"""
# from urllib2 import quote_plus
from urllib3 import quote_plus
# import oauth2 as oauth
import oauth2client as oauth
import time, sys, re
# import urllib, urllib2
import simplejson
from yos.crawl import rest

CONFIG = simplejson.load(open("config.json", "r"))
SEARCH_API_URL_V1 = CONFIG["uri_v1"].rstrip("/") + 
     "/%s/v%d/%s?start=%d&count=%d&lang=%s&region=%s" + 
     "&appid=" + CONFIG["appid"]
SEARCH_API_URL_V2 = CONFIG["uri_v2"]
CC_KEY = CONFIG['cc_key']
CC_SECRET = CONFIG['cc_secret']
SOURCE_TAG = CONFIG['source_tag']

def params(d):
    """ Takes a dictionary of key, value pairs and generates 
        a cgi parameter/argument string
    """
    p = ""
    for k, v in d.iteritems():
        p += "&%s=%s" % (quote_plus(k), quote_plus(v))
    return p

search_type = "limitedweb"  # "web"
def search(command,bucket=search_type,count=1,start=0,more={}):
    """ Perform search of words on web pages known to Yahoo """
    params = {
         'oauth_version': "1.0",
         'oauth_nonce': oauth.generate_nonce(),
         'oauth_timestamp': int(time.time()),
         'q': quote_plus(command),
         'count': count,
         'start': start,
         'format': 'json',
         'ads.recentSource': SOURCE_TAG 
    }
    params.update(more)
    url =  SEARCH_API_URL_V2 + bucket
    consumer = oauth.Consumer(CC_KEY,CC_SECRET)
    req = oauth.Request(method="GET", url=url, parameters=params)
    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, None)
    return rest.load_json(req.to_url()) 

def get_web_uses(search_words):
    """ Get usage of search words using Yahoo """
    yahoo_response = search(search_words)
    return yahoo_response['bossresponse'][search_type]['totalresults']

