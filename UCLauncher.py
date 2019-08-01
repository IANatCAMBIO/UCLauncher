#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import plistlib
import ssl
import requests
import bs4
from distutils.version import LooseVersion
import re
import os
import sys

def Get_Local_Ver():
    with open('/Applications/Chromium.app/Contents/Info.plist','rb') as Local_PLIST_File:	
        Plist_Dict = plistlib.load(Local_PLIST_File)
    LocalVer = Plist_Dict["CFBundleShortVersionString"]
    return LocalVer

def Get_Latest_Ver(Level):
    #Don't worry about SSL certificates
    sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    sslcontext.verify_mode = ssl.CERT_NONE
    
    #Poll Releases Page for MACOS 
    Binaries_Page_HTML = requests.get("https://ungoogled-software.github.io/ungoogled-chromium-binaries/").text
    soup=bs4.BeautifulSoup(Binaries_Page_HTML, features='lxml')
    
    MacString = soup.find(string="macOS")
    MacRow = MacString.parent.parent.parent.parent
    RelTD=MacRow.contents[3]
    DevTD=MacRow.contents[5]
    
    RelURL = ("https://ungoogled-software.github.io" + RelTD.a['href'])
    DevURL = ("https://ungoogled-software.github.io" + DevTD.a['href'])
    
    if Level is "Release":
        return(RelTD.string, RelURL)
    if Level is "Development":
        return(DevTD.string, DevURL)

def Download_File(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename

###


Local_Version = Get_Local_Ver()
if len(sys.argv) > 1:
    if sys.argv[1] == '--Dev':
        Latest_Version = Get_Latest_Ver("Development")
    if sys.argv[1] == '--Rel':
        Latest_Version = Get_Latest_Ver("Release")
else:
    Latest_Version = Get_Latest_Ver("Release")
    
if LooseVersion(Local_Version) < LooseVersion(Latest_Version[0]):
    print("Remote Version: " + Latest_Version[0])
    print("Local Version: " + Local_Version)
    print("\nSearching for Update Link ...")


    HTML = requests.get(Latest_Version[1]).text
    soup = bs4.BeautifulSoup(HTML, features='lxml')
    
    DL_Link = soup.find(string=re.compile(".*dmg.*"))
    DL_Link = DL_Link.parent['href']
    
    print("\nDownloading File: " + DL_Link)
    Download_File(DL_Link)

    DL_Filename = DL_Link.split('/')[-1]
    os.system("open " + DL_Filename)
else:
    print("Your local version is already up-to-date!")
    print("Local Version: " + Local_Version[0])
    os.system("open /Applications/Chromium.app")




