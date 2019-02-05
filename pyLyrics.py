#!/usr/bin/env python3

import sys
import getopt
import hashlib
import time
import urllib.parse
import urllib.request
import requests
import os
from bs4 import BeautifulSoup

pyLyricsVer = "v1.0"
pyLyricsRel = "(beta)"

writeToFile = False
silent = False
raw = False

def main(argv):
    global pyLyricsVer
    global pyLyricsRel

    global writeToFile
    global silent
    global raw

    artist = ""
    title = ""
    output = ""
    outputHandle = None
    date = ""
    computerName = str(hashlib.md5(str(hashlib.md5(str(time.time()).split(".", 1)[0].encode()).hexdigest()[8:24]).encode()).hexdigest())
    sid = ""
    pid = ""
    timeNow = ""
    lyrics = {}
    try:
        opts, args = getopt.getopt(argv,"hva:t:o:sr",["help","version","artist=","title=","output=","silent","raw"])
    except getopt.GetoptError:
        printUsage()
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printUsage()
            sys.exit(0)
        elif opt in ("-v", "--version"):
            printVersion()
            sys.exit(0)
        elif opt in ("-a", "--artist"):
            artist = arg.strip()
        elif opt in ("-t", "--title"):
            title = arg.strip()
        elif opt in ("-o", "--output"):
            output = arg.strip()
            writeToFile = True
        elif opt in ("-s","--silent"):
            silent = True
        elif opt in ("-r","--raw"):
            raw = True

    if (len(args) <= 0) and (len(opts) <= 0):
        if not silent:
            printVersion()
            print("", sep="")
            printUsage()
        sys.exit(0)
    elif len(artist) == 0:
        if not silent:
            printError("artist_missing")
            printUsage()
        sys.exit(2)
    elif len(title) == 0:
        if not silent:
            printError("title_missing")
            printUsage()
        sys.exit(3)

    timeNow = str(time.time()).split(".", 1)[0]
    sid = genSid(computerName, timeNow)
    pid = genPid(artist, title, sid, getPidSeed(sid), timeNow)
    lyrics = getLyrics(artist, title, timeNow, pid, sid)

    if lyrics["lyrics"] != "":
        if writeToFile:
            if output == "default" : output = lyrics["artist"] + " - " + lyrics["title"] + ".txt"
            if not prepareOutputFile(output):
                try:
                    outputHandle = open(output, "a")
                    if not raw : outputHandle.write(str(lyrics["artist"] + " - " + lyrics["title"] + "\n\n\n"))
                    outputHandle.write(str(lyrics["lyrics"]))
                    outputHandle.close()
                except:
                    if not silent : printError("cant_write_file")
                    sys.exit(5)
            else:
                if not silent : printError("cant_write_file")
                sys.exit(5)
        else:
            if not silent:
                if not raw : print(lyrics["artist"]," - ",lyrics["title"],"\n\n", sep="")
                print(lyrics["lyrics"], sep="")
    else:
        if not silent : printError("no_result")
        sys.exit(4)

    return 0

def genSid(computerName, timestamp):
    sid = hashlib.md5((computerName + "|" + timestamp).encode()).hexdigest()

    return sid

def getPidSeed(sid):
    httpSessionAddress = "http://www.lyricsplugin.com/plugin/session.php"
    httpSessionHeaders = {"Accept":         "application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, application/x-shockwave-flash, application/vnd.ms-excel, application/msword, */*",
                         "User-Agent":      "Lyrics Plugin/0.4 (Winamp build)",
                         "Content-Type":    "application/x-www-form-urlencoded",
                         "Accept-Encoding": "gzip, deflate",
                         "Host":            "www.lyricsplugin.com",
                         "Connection":      "Keep-Alive",
                         "Cache-Control":   "no-cache"}
    httpSessionData = ""
    httpSessionResponse = ""
    httpSessionArg1 = "wa"
    httpSessionArg2 = "5062"
    httpSessionArg3 = "0"
    pidSeed = ""
    pidSeedHash = ""
    soupSession = None
    httpSessionData = urllib.parse.quote(str("sid=" + sid               + "&" +
                                             "i="   + httpSessionArg1   + "&" +
                                             "v="   + httpSessionArg2   + "&" +
                                             "m="   + httpSessionArg3), "/=&")
    httpSessionResponse = requests.post(httpSessionAddress, data=httpSessionData, headers=httpSessionHeaders)
    soupSession = BeautifulSoup(httpSessionResponse.text, "html.parser")
    pidSeed = soupSession.get_text().strip()
    if len(pidSeed) != 32 : pidSeed = "0123456789abcdef0123456789abcdef"
    pidSeedHash = str(hashlib.md5(str(hashlib.md5(pidSeed.encode()).hexdigest()).encode()).hexdigest())

    return pidSeedHash

def genPid(artist, title, sid, pidSeed, timestamp):
    timestampHash = str(hashlib.md5(timestamp.encode()).hexdigest())
    pid = str(timestampHash[0:4]     + "|" +
              pidSeed[0:16]          + "|" +
              timestampHash[8:12]    + "|" +
              artist                 + "|" +
              timestampHash[16:20]   + "|" +
              title                  + "|" +
              timestampHash[20:24]   + "|" +
              sid                    + "|" +
              timestampHash[12:16]   + "|" +
              pidSeed[16:32]         + "|" +
              timestampHash[4:8])
    pid = hashlib.md5(pid.encode()).hexdigest()

    return pid

def getLyrics(artist, title, timestamp, pid, sid):
    lyrics = {}
    httpPluginAddress = "http://www.lyricsplugin.com/plugin/0.4/winamp/plugin.php"
    httpPluginHeaders = {"Accept":          "application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, application/x-shockwave-flash, application/vnd.ms-excel, application/msword, */*",
                         "User-Agent":      "Lyrics Plugin/0.4 (Winamp build)",
                         "Content-Type":    "application/x-www-form-urlencoded",
                         "Accept-Encoding": "gzip, deflate",
                         "Host":            "www.lyricsplugin.com",
                         "Connection":      "Keep-Alive",
                         "Cache-Control":   "no-cache"}
    httpPluginData = ""
    httpPluginResponse = ""
    bgColor = str(int("0x000000", 0))
    fgColor = str(int("0xffffff", 0))
    soupPlugin = None
    httpPluginData = urllib.parse.quote(str("a="   + artist    + "&" +
                                            "t="   + title     + "&" +
                                            "i="   + timestamp + "&" +
                                            "pid=" + pid       + "&" +
                                            "sid=" + sid       + "&" +
                                            "bc="  + bgColor   + "&" +
                                            "tc="  + fgColor), "/=&")
    httpPluginResponse = requests.post(httpPluginAddress, data=httpPluginData, headers=httpPluginHeaders)
    soupPlugin = BeautifulSoup(httpPluginResponse.text, "html.parser")
    lyrics = {"artist": soupPlugin.find_all(["div"])[2].get_text().strip(),
              "title":  soupPlugin.find_all(["div"])[1].get_text().strip(),
              "lyrics": soupPlugin.find_all(["div"])[3].get_text().strip()}

    return lyrics

def prepareOutputFile(filepath):
    try:
        filepathHandle = open(filepath, "w")
        filepathHandle.write("")
        filepathHandle.close()
    except:
        if not silent : printError("cant_write_file")
        sys.exit(5)

    return 0

def printVersion():
    print(getModuleName()," ",pyLyricsVer," ",pyLyricsRel," - written by Alastor", sep="")
    print("lyricsplugin.com interface", sep="")

    return 0

def printError(error):
    if error == "" :
        return 0
    elif error == "artist_missing":
        print("Artist must be specified!")
    elif error == "title_missing":
        print("Title must be specified!")
    elif error == "cant_write_file":
        print("Can't write to file!")
    elif error == "no_result":
        print("No result!")

    return 0

def printUsage():
    print("Usage: ",getModuleName()," -a <artist> -t <title> [-o file] [-s] [-r] [-v]", sep="")
    print("",                                                                           sep="")
    print(" -h,  --help          Show this message",                                    sep="")
    print(" -a,  --artist        Song artist (required)",                               sep="")
    print(" -t,  --title         Song title (required)",                                sep="")
    print(" -o,  --output        Write output to file",                                 sep="")
    print(" -s,  --silent        Disable print output to stdout",                       sep="")
    print(" -r,  --raw           Print lyrics only",                                    sep="")
    print(" -v,  --version       Print version information",                            sep="")
    print("",                                                                           sep="")
    print(" example:",                                                                  sep="")
    print("  ",getModuleName()," -a \"ABBA\" -t \"Money\"",                             sep="")

    return 0

def getModuleName():
    moduleName = sys.argv[0]

    if os.sep in moduleName : moduleName = moduleName.split(os.sep)[-1]

    return moduleName

# Call main()
if __name__ == "__main__":
    main(sys.argv[1:])
