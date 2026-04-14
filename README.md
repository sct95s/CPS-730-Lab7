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

From PowerShell on Windows, locate to your Key.pem file location:

```powershell
ssh -i ":C\Your_file_location\Key.pem" ubuntu@YOUR_PUBLIC_IP
```
<br>

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

To verify that Redis caching was implemented correctly, open a second SSH session

Then SSH into the server again:
```powershell
ssh -i ":C\Your_file_location\Key.pem" ubuntu@YOUR_PUBLIC_IP
```

Now you have:
- Window 1: Flask running
- Window 2: Redis checking commands


## Inspect Redis keys
In the second SSH window, type:
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


--- 
---
# Bonus: Update the `/courses` Route to Support POST

This bonus extension adds **POST support** to the `/courses` route in the Flask application.

<br>

## Step 1: Stop the current running apps
```powershell
Ctrl + C
```


## Step 2: Change the code
On the first ssh
```powershell
cd ~/redis-lab
cat > app.py <<'PY'
from flask import Flask, jsonify, request
import redis
import os
import time

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

ROUTE_FILES = {
    "announcements": "announcements.txt",
    "courses": "courses.txt",
    "faq": "faq.txt"
}

def read_file_content(filename):
    time.sleep(2)

    if not os.path.exists(filename):
        return None

    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def get_content(route_name):
    cached_data = r.get(route_name)

    if cached_data:
        return {
            "route": route_name,
            "source": "cache",
            "content": cached_data
        }

    filename = ROUTE_FILES.get(route_name)
    if not filename:
        return None

    file_data = read_file_content(filename)
    if file_data is None:
        return None

    r.setex(route_name, 60, file_data)

    return {
        "route": route_name,
        "source": "file",
        "content": file_data
    }

@app.route("/")
def home():
    return """
    Redis File Cache Demo is running.
    Available routes:
    /announcements
    /courses
    /faq
    """

@app.route("/announcements")
def announcements():
    result = get_content("announcements")
    if result:
        return jsonify(result)
    return jsonify({"error": "Content not found"}), 404

@app.route("/courses", methods=["GET", "POST"])
def courses():
    if request.method == "POST":
        data = request.get_json(silent=True)

        if not data or "course" not in data:
            return jsonify({"error": "Please provide JSON with a 'course' field"}), 400

        new_course = data["course"].strip()

        if not new_course:
            return jsonify({"error": "Course entry cannot be empty"}), 400

        with open("courses.txt", "a", encoding="utf-8") as f:
            f.write("\n" + new_course)

        r.delete("courses")

        return jsonify({
            "message": "Course added successfully",
            "added": new_course,
            "cache": "courses cache cleared"
        }), 201

    result = get_content("courses")
    if result:
        return jsonify(result)
    return jsonify({"error": "Content not found"}), 404

@app.route("/faq")
def faq():
    result = get_content("faq")
    if result:
        return jsonify(result)
    return jsonify({"error": "Content not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
PY
```

## How to change `app.py` file manually
At the top of `app.py`, change:
```python
from flask import Flask, jsonify
```

to this:
```python
from flask import Flask, jsonify, request
```
<br>


Delete your current `/courses` route and replace it with this:
```python
@app.route("/courses", methods=["GET", "POST"])
def courses():
    if request.method == "POST":
        data = request.get_json(silent=True)

        if not data or "course" not in data:
            return jsonify({"error": "Please provide JSON with a 'course' field"}), 400

        new_course = data["course"].strip()

        if not new_course:
            return jsonify({"error": "Course entry cannot be empty"}), 400

        with open("courses.txt", "a", encoding="utf-8") as f:
            f.write("\n" + new_course)

        # Reset the cache for courses
        r.delete("courses")

        return jsonify({
            "message": "Course added successfully",
            "added": new_course,
            "cache": "courses cache cleared"
        }), 201

    result = get_content("courses")
    if result:
        return jsonify(result)
    return jsonify({"error": "Content not found"}), 404
```

## Your full updated `app.py`
In case the file is wrong, here is the whole `app.py` file:
```python
from flask import Flask, jsonify, request
import redis
import os
import time

app = Flask(__name__)

# Connect to local Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Each route maps to one text file
ROUTE_FILES = {
    "announcements": "announcements.txt",
    "courses": "courses.txt",
    "faq": "faq.txt"
}

def read_file_content(filename):
    # Artificial delay so the class can notice the benefit of caching
    time.sleep(2)

    if not os.path.exists(filename):
        return None

    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def get_content(route_name):
    # 1. Check Redis first
    cached_data = r.get(route_name)

    if cached_data:
        return {
            "route": route_name,
            "source": "cache",
            "content": cached_data
        }

    # 2. If not in Redis, look up the matching text file
    filename = ROUTE_FILES.get(route_name)
    if not filename:
        return None

    file_data = read_file_content(filename)
    if file_data is None:
        return None

    # 3. Save in Redis with a TTL of 60 seconds
    r.setex(route_name, 60, file_data)

    return {
        "route": route_name,
        "source": "file",
        "content": file_data
    }

@app.route("/")
def home():
    return """
    Redis File Cache Demo is running.
    Available routes:
    /announcements
    /courses
    /faq
    """

@app.route("/announcements")
def announcements():
    result = get_content("announcements")
    if result:
        return jsonify(result)
    return jsonify({"error": "Content not found"}), 404

@app.route("/courses", methods=["GET", "POST"])
def courses():
    if request.method == "POST":
        data = request.get_json(silent=True)

        if not data or "course" not in data:
            return jsonify({"error": "Please provide JSON with a 'course' field"}), 400

        new_course = data["course"].strip()

        if not new_course:
            return jsonify({"error": "Course entry cannot be empty"}), 400

        with open("courses.txt", "a", encoding="utf-8") as f:
            f.write("\n" + new_course)

        # Reset the cache for courses
        r.delete("courses")

        return jsonify({
            "message": "Course added successfully",
            "added": new_course,
            "cache": "courses cache cleared"
        }), 201

    result = get_content("courses")
    if result:
        return jsonify(result)
    return jsonify({"error": "Content not found"}), 404

@app.route("/faq")
def faq():
    result = get_content("faq")
    if result:
        return jsonify(result)
    return jsonify({"error": "Content not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

## Step 3: Test the POST request
Open a new PowerShell window on your computer and run this:
```powershell
Invoke-RestMethod -Method POST -Uri "YOUR_IP_ADDRESS/courses" -ContentType "application/json" -Body '{"course":"CS 999 - Cloud Systems Lab"}'
```

You should get back something like:
```powershell
{
  "message": "Course added successfully",
  "added": "CS 999 - Cloud Systems Lab",
  "cache": "courses cache cleared"
}
```

## Step 4: Verify it worked
### In the browser, open
```powershell
http://YOUR_IP_ADDRESS/courses
```


### In SSH, run: 
```powershell
cat courses.txt
```

You should see courses added to the `courses.txt` file:
- CS 301 - Software Engineering
- CS 211 - Software Testing
- CS 730 - Web Technology
- CS 999 - Cloud Systems Lab



## Goal
Allow users to send a POST request to add a new course entry into `courses.txt`.  
After the file is updated, the Redis cache for the `courses` route must also be cleared so that the next GET request returns the updated content.

## What Was Changed
The `/courses` route was updated to support both:

- **GET** — returns the list of courses, using Redis caching
- **POST** — accepts a new course entry and appends it to `courses.txt`

When a new course is added:
1. The server reads the JSON body from the POST request
2. The new course is appended to `courses.txt`
3. The Redis key for `courses` is deleted
4. The next GET request reloads the updated file content and stores it back in Redis















