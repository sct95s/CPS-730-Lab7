
# CPS 730 Lab 7 - Redis + Flask on AWS EC2

## Overview
This project deploys a Flask application and Redis cache on an Ubuntu-based Amazon EC2 instance. The application serves content from text files and caches the results in Redis for 60 seconds.

The API behavior is:

- Check Redis for the requested content
- If found, return the cached content
- If not found, read from the corresponding text file
- Store the content in Redis with a TTL of 60 seconds
- Return the result

---

## Files

- `app.py` - Flask application
- `announcements.txt` - announcements content
- `courses.txt` - course list
- `faq.txt` - FAQ content

---

## EC2 Setup

### 1. Launch EC2 instance
Use an **Ubuntu Server 22.04 LTS (x86)** AMI.

Recommended settings:
- Ubuntu Server 22.04 LTS
- t2.micro or t3.micro
- Public subnet
- Auto-assign public IP = Enable

### 2. Security group rules
Inbound rules:
- SSH, port 22, source = My IP
- Custom TCP, port 8000, source = Anywhere (`0.0.0.0/0`)

---

## Connect to EC2

Use SSH from PowerShell:

```powershell
ssh -i "D:\TMU_CLASSES\FOURTH_YEAR\2nd_Semester\CPS730\Lab7\Lab7.pem" ubuntu@YOUR_PUBLIC_IP
