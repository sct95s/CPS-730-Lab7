# CPS 730 Lab 7 - Redis + Flask on AWS EC2

## Overview
This lab deploys a Flask application and Redis cache on an Ubuntu-based Amazon EC2 instance. The application reads content from text files and caches the results in Redis for 60 seconds.

The API behavior is:

- Check Redis for the requested content
- If found, return the cached content
- If not found, read from the corresponding text file
- Store the content in Redis with a TTL of 60 seconds
- Return the result

---

## AWS EC2 Setup

### AMI used
- Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
- 64-bit (x86)

### Instance settings
- Public subnet
- Auto-assign public IP enabled
- Security group created for the lab

### Security group inbound rules
- SSH, port 22, source = My IP
- Custom TCP, port 8000, source = Anywhere (`0.0.0.0/0`)

---

## Connecting to the EC2 instance

From PowerShell on Windows:

```powershell
ssh -i "D:\TMU_CLASSES\FOURTH_YEAR\2nd_Semester\CPS730\Lab7\Lab7.pem" ubuntu@YOUR_PUBLIC_IP
```

For Ubuntu EC2 instances, the username is:
```powershell
ubuntu
```

---
## Server setup commands

### Update package list
```powershell
sudo apt update
```

### Install Redis, Python, pip, and venv
```powershell
sudo apt install -y redis-server python3 python3-pip python3-venv
```

### Start and enable Redis
```powershell
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Test Redis
```powershell
redis-cli ping
```

### Expectec Output
```powershell
PONG
```

---

# Project folder setup

## Create project folder
```powershell
mkdir -p ~/redis-lab
cd ~/redis-lab
```


## Create and activate virtual environment
```powershell
python3 -m venv venv
source venv/bin/activate
```

## Install Python packages
```powershell
pip install flask redis
```


---

## Project files

The following files are used in this lab:

- `announcements.txt`
- `courses.txt`
- `faq.txt`
- `app.py`

These files should be created inside the `redis-lab` folder.

Example commands:
```powershell
nano announcements.txt
nano courses.txt
nano faq.txt
nano app.py
```

---
# Running the Flask app

 ## Make sure you are in the project folder and the virtual environment is active.
```powershell
cd ~/redis-lab
source venv/bin/activate
python3 app.py
```

## Expected output includes something like:
```powershell
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:8000
* Running on http://172.31.x.x:8000
```

---

# Testing the web application

## Open the following endpoints in a browser:
```powershell
http://YOUR_PUBLIC_IP:8000/announcements
http://YOUR_PUBLIC_IP:8000/courses
http://YOUR_PUBLIC_IP:8000/faq
```

## Expected cache behavior

- First request: ` "source":"file" `
- Immediate second request: ` "source":"cache" `
- After waiting 60 seconds: ` "source":"file" ` again

This shows that:
- The application first reads from the file
- Then serves cached data from Redis
- Then re-reads from the file after the Redis key expires

---
# Redis cache verification

To verify that Redis caching was implemented correctly, open a second SSH session and run these commands.

## Inspect Redis keys

```powershell
redis-cli KEYS "*"
```

## Read a cached value
```powershell
redis-cli GET announcements
```

You can also test other routes:
```powershell
redis-cli GET courses
redis-cli GET faq
```

## Check remaining TTL
```powershell
redis-cli TTL announcements
```

## Update TTL to 10 seconds
```powershell
redis-cli EXPIRE announcements 10
```

## Check TTL again
```powershell
redis-cli TTL announcements
```

## What these commands prove
- `KEYS "*"` shows which cache keys exist
- `GET announcements` shows the cached content
- `TTL announcements` shows how many seconds remain before expiration
- `EXPIRE announcements 10` changes the remaining TTL to 10 seconds

---
#Demonstration flow used in the lab

## Step 1: Run the application:
```powershell
python3 app.py
```

## Step 2: 
Open
```powershell
[python3 app.py](http://YOUR_PUBLIC_IP:8000/announcements)
```

The first response should show:
```powershell
"source":"file"
```

## Step 3:
Refresh the same endpoint immediately.

The second response should show:
```powershell
"source":"cache"
```

## Step 4:
Wait about 60 seconds and refresh again.

The response should return to:
```powershell
"source":"file"
```

## Step 5: 
Open a second SSH session and verify Redis using:
```powershell
redis-cli KEYS "*"
redis-cli GET announcements
redis-cli TTL announcements
redis-cli EXPIRE announcements 10
redis-cli TTL announcements
```

---
# Notes

## Stopping the Flask app
Use:
```powershell
Ctrl + C
```


---
# Summary

This lab successfully demonstrated:

launching an Ubuntu EC2 instance in AWS
configuring a public subnet and security group
installing Redis and Python dependencies
running a Flask application on port 8000
serving content from text files
caching content in Redis
verifying Redis keys, values, TTL, and expiration behavior



















