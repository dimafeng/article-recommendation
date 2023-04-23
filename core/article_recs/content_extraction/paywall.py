
import json
import os

UNPAYWALL = [
    "https://archive.is/",
    "https://12ft.io/",
    "https://web.archive.org/web/"
]

def loadpaywall():
    """Load paywall list from file"""
    with open(os.path.join(os.path.dirname(__file__), 'paywalls.json'), 'r') as f:
        paywall = f.read()
    return json.loads(paywall)

def ispaywall(url):
    """Check if url is paywall"""
    paywall = loadpaywall()
    for i in paywall:
        if i in url:
            return True
    return False

def getUnpaywalledUrls(url):
    """Get unpaywalled urls"""
    urls = []
    for i in UNPAYWALL:
        urls.append(i + url)
    return urls
