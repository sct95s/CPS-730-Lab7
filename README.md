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
