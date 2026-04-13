from flask import Flask, jsonify
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

@app.route("/courses")
def courses():
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