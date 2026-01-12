import logging
import os
import requests
import time
import json
import asyncio
import aiohttp
import aiofiles
from datetime import datetime, timedelta
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from config import CHANNEL_ID, THUMB_URL,BOT_TEXT
import zipfile
from Extractor.core.utils import forward_to_log
from io import BytesIO

# Constants
MAX_WORKERS = 5000
MAX_RETRIES = 15
TIMEOUT = 90
UPDATE_INTERVAL = 15
SESSION_TIMEOUT = 200

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def khan_login(app: Client, message: Message):
    """Start the KGS extraction process."""
    try:
        start_time = time.time()
        
        
def get_auth_token(username, password):
    login_url = "https://admin2.khanglobalstudies.com/api/login-with-password"
    login_payload = {
        "phone": username,
        "password": password,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }

    login_response = requests.post(login_url, headers=headers, json=login_payload)

    if login_response.status_code == 200:
        return login_response.json().get('token', '')
    else:
        print("Login failed. Status code:", login_response.status_code)
        print("Response:", login_response.text)
        return None

def fetch_courses(token):
    headers = {
        "Host": "admin2.khanglobalstudies.com",
        "authorization": f"Bearer {token}",
        "client-id": "5f439b64d553cc02d283e1b4",
        "client-version": "21.0",
        "user-agent": "Android",
        "randomid": "385bc0ce778e8d0b",
        "client-type": "MOBILE",
        "device-meta": "{APP_VERSION:19.0,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.khansirofficial}",
        "content-type": "application/json; charset=UTF-8",
    }
    params = {
        "mode": "2",
        "filter": "false",
        "exam": "",
        "amount": "",
        "organisationId": "5f439b64d553cc02d283e1b4",
        "classes": "",
        "limit": "20",
        "page": "1",
        "programId": "5f476e70a64b4a00ddd81379",
        "ut": "1652675230446",
    }
    response = requests.get(
        "https://admin2.khanglobalstudies.com/api/user/v2/courses?medium=0",
        params=params,
        headers=headers,
    ).json()

    if not response:
        print("Failed to fetch courses.")
        return None

    courses_info = ""
    course_dict = {}
    for course in response:
        course_id = course["id"]
        course_title = course["title"]
        price = course.get("price", "N/A")
        start_at = course.get("start_at", "N/A")
        end_at = course.get("end_at", "N/A")
        
        courses_info += f"{course_id} ☆ {course_title} ☆ {price}\n"
        courses_info += f"Start At: {start_at}\n"
        courses_info += f"End At: {end_at}\n\n"

        course_dict[course_id] = course_title

    print(courses_info)
    return course_dict

def fetch_and_save_lessons(token, course_id, course_title):
    headers = {
        "Host": "admin2.khanglobalstudies.com",
        "authorization": f"Bearer {token}",
        "client-id": "5f439b64d553cc02d283e1b4",
        "client-version": "21.0",
        "user-agent": "Android",
        "randomid": "385bc0ce778e8d0b",
        "client-type": "MOBILE",
        "device-meta": "{APP_VERSION:19.0,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.khansirofficial}",
        "content-type": "application/json; charset=UTF-8",
    }

    response2 = requests.get(
        f"https://admin2.khanglobalstudies.com/api/user/courses/{course_id}/lessons?medium=0",
        headers=headers,
    ).json().get("lessons", [])

    if not response2:
        print("Failed to fetch lessons.")
        return

    lessons = []
    for lesson in response2:
        lesson_name = lesson["name"]
        
        for video in lesson.get("videos", []):
            video_name = video["name"]
            video_url = video["video_url"]
            lessons.append(f"({lesson_name}) {video_name} [🧊 Sunny Ji 🧊]:{video_url}\n")
    # Reverse the order of lessons
    lessons.reverse()

    file_name = f"{course_id}_{course_title}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.writelines(lessons)
    print(f"Links saved to {file_name}")

def main():
    while True:
        username = input("Enter your Number: ")
        password = input("Enter your password: ")

        token = get_auth_token(username, password)
        if not token:
            continue

        while True:
            course_dict = fetch_courses(token)
            if not course_dict:
                break

            course_id = input("Enter the Course ID to Download: ")
            course_title = course_dict.get(course_id, "title")

            fetch_and_save_lessons(token, course_id, course_title)

            option = input("Enter '1' to download another course for this ID, '2' to log in with another ID, or '3' to exit: ")
            if option == '1':
                continue
            elif option == '2':
                break
            elif option == '3':
                return
            else:
                print("Invalid option. Exiting.")
                return

