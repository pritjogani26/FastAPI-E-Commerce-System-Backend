# redis_file/redis_client.py
import redis
import json
from datetime import timedelta

# Connect to Redis server (running on localhost and port 6379)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
