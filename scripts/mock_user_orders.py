import time
import random
from locust import HttpUser, task, between

API_PATH = "/"