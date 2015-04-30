
mobile-privacy-thesis
=====================

Introduction
---
This repository contains code I wrote for my senior thesis in mobile privacy. Here is the thesis abstract:

> This paper presents a dynamic analysis of user privacy in 2425 Android applications. While previous studies make tradeoffs in depth of privacy investigation and scale, this project studies thousands of apps while focusing specifically on privacy-related questions. As a dynamic analysis, the project runs apps on an Android device while recording the network requests leaving the device. The apps are run with a novel software monkey called Chimp, which performs "social login" in apps that offer it. The collected network data is processed through a privacy heuristic pipeline that flags incidents of personal information being shared. In the results, we first present high-level metrics like popular data-collecting entities and apps. Then, we investigate specific cases of misleading and alarming security practices that can potentially compromise user privacy.

Getting Oriented
---
Each of the folders contain a specific set of files:
- `apk-categorizer/` - categorize packages into their Google Play Store categories
- `apk-downloader/` - download top apps from the Google Play Store
- `data-accessories/` - scripts to clean data after it has been collected
- `data/` - MongoDB dump of `runs` collection, which contains the original network requests
- `entity-resolution/` - resolve hostnames to entity names
- `find-fb-login/` - identify which packages might offer social login
- `misc/` - some utility scripts
- `monkeys/` - each folder contains a different monkey implementation
- `osx/` - port forwarding configuration files for OS X
- `privacy-accessories/` - scripts for privacy-related operations
- `profiles/` - profile files I used to run Chimp. You will almost certainly need to change these
- `results/` - iPython Notebooks used to generate my results
- `virtualbox-accessories/` - some scripts useful for Virtualbox usage
- `webapp` - code for Extensive Privacy Incident Catalog (EPIC)

Installation (Debian)
---
- Install MongoDB
- Install Android SDK
- `pip install -r requirements.txt`
- On Android, disable Settings > Security > Verify apps. Enable Unknown sources
- Disable sleep time in System settings
- Install the mitmproxy certificate on the Android phone

Data Collection Usage
---
- Ensure phone is disconnected from proxy and google to find its ip address
- Log in to root on test machine
- Set the following iptables rules, with the phone's ip address: `iptables -A INPUT -p tcp -s xxx.xxx.xxx.xxx --dport 8080 -j ACCEPT && iptables -A INPUT -p tcp -s 0.0.0.0/0 --dport 8080 -j DROP`
- Connect the phone to the test machine's proxy. Test with mitmproxy
- Ensure that phone is logged into Facebook app
- Kill existing mongod processes
- Run `mongod --fork --syslog --port 27017 --dbpath mongodata`
- Run `nohup python privacy-accessories/request_queue_server.py &`
- Run `nohup mitmdump --host -s privacy-accessories/trace.py &`
- Run `nohup python chimp.py profiles/fb_dfs.yml &`
- Logs are written to `runs.log`
