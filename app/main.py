import asyncio
import aiohttp
import os
import os.path
import csv
import re

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .forbidden_words import FORBIDDEN_WORDS

app = FastAPI()

# Mount static directories
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/videos", StaticFiles(directory=os.getenv("VIDEO_DIR")), name="videos")

templates = Jinja2Templates(directory="app/templates")

VIDEO_DIRECTORY = os.getenv("VIDEO_DIR")
RATING_FILE = f"{os.getenv('VIDEO_DIR')}/ratings.csv"

# Define forbidden words
FORBIDDEN_WORDS_RE = re.compile(r'\b(' + '|'.join(map(re.escape, FORBIDDEN_WORDS)) + r')\b', re.IGNORECASE)


def get_video_list():
    return sorted([f for f in os.listdir(VIDEO_DIRECTORY) if f.endswith(".mp4")])


def read_ratings(with_ip=False):
    ratings = {}
    if os.path.exists(RATING_FILE):
        with open(RATING_FILE, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                video_name, rating, ip = row
                rating = int(rating)
                ratings[(video_name, ip)] = rating
    
    if with_ip: return ratings
    result = {}
    for (video_name, ip), rating in ratings.items():
        if video_name in result:
            result[video_name].append(rating)
        else:
            result[video_name] = [rating]
    return result


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, video_name: str = None):
    client_host_ip = str(request.client.host)
    videos = get_video_list()
    if not videos:
        return templates.TemplateResponse(
            "index.html", {"request": request, "video": None}
        )

    if video_name in videos:
        current_index = videos.index(video_name)
    else:
        current_index = 0

    video = videos[current_index]
    video_title = os.path.splitext(video)[0].replace("_", " ").title()
    prev_video = videos[current_index - 1] if current_index > 0 else videos[-1]
    next_video = (
        videos[current_index + 1] if current_index < len(videos) - 1 else videos[0]
    )

    # Get average rating
    ratings = read_ratings()
    ratings_w_ip = read_ratings(with_ip=True)
    video_ratings = ratings.get(video, [])
    number_of_ratings = len(video_ratings)
    if video_ratings:
        average_rating = round(sum(video_ratings) / len(video_ratings), 2)
    else:
        average_rating = "No ratings yet"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "video": video,
            "video_title": video_title,
            "prev_video": prev_video,
            "next_video": next_video,
            "videos": videos,
            "current_index": current_index,
            "average_rating": average_rating,
            "number_of_ratings": number_of_ratings,
            "existing_rating": ratings_w_ip.get((video, client_host_ip)),
        },
    )


def display_first_vid_w_error_message(request, prompt, error_msg):
    client_host_ip = str(request.client.host)
    videos = get_video_list()
    current_index = 0
    video = videos[current_index]
    video_title = os.path.splitext(video)[0].replace("_", " ").title()
    prev_video = videos[current_index - 1] if current_index > 0 else videos[-1]
    next_video = (
        videos[current_index + 1] if current_index < len(videos) - 1 else videos[0]
    )
    # Get average rating
    ratings = read_ratings()
    ratings_w_ip = read_ratings(with_ip=True)
    video_ratings = ratings.get(video, [])
    number_of_ratings = len(video_ratings)
    if video_ratings:
        average_rating = round(sum(video_ratings) / len(video_ratings), 2)
    else:
        average_rating = "No ratings yet"
    context = {
        "request": request,
        "error_message": error_msg,
        "prompt": prompt,
        "video": video,
        "video_title": video_title,
        "prev_video": prev_video,
        "next_video": next_video,
        "videos": videos,
        "current_index": current_index,
        "average_rating": average_rating,
        "number_of_ratings": number_of_ratings,
        "existing_rating": ratings_w_ip.get((video, client_host_ip)),
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/", response_class=HTMLResponse)
async def create_video(request: Request, prompt: str = Form(...)):
    # Check for offensive content
    if FORBIDDEN_WORDS_RE.search(prompt):
        error_message = "Your prompt contains inappropriate language. Please try again."
        return display_first_vid_w_error_message(request, prompt, error_message)

    video_name = await generate_video(prompt)
    if len(get_video_list()) < 200:
        if video_name:
            return RedirectResponse(url=f"/?video_name={video_name}", status_code=303)
        else:
            return display_first_vid_w_error_message(
                request, prompt, 'Something went wrong, displaying first video.'
            )
    else:
        return display_first_vid_w_error_message(
            request, prompt, 'More than 200 videos already exist, cannot generate more.'
        )


async def generate_video(prompt):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"http://{os.getenv('VIDEOGEN_SERVICE_HOST')}:8000/text2motion", json={"user_prompt": prompt}) as resp:
                if resp.status == 200:
                    response_json = await resp.json()
                    video_name = response_json.get("video_name")
                    return video_name
                else:
                    return None
        except Exception as e:
            print(f"Error: {e}")
            return None


@app.post("/rate")
async def rate_video(request: Request):
    data = await request.json()
    client_host_ip = request.client.host
    video_name = data.get('video_name')
    rating = data.get('rating')
    if not video_name or not rating:
        return {"status": "error", "message": "Invalid data"}

    # Validate rating
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return {"status": "error", "message": "Invalid rating value"}
    except ValueError:
        return {"status": "error", "message": "Invalid rating value"}

    # Record the rating in 'ratings.csv'
    with open(RATING_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([video_name, rating, client_host_ip])

    # Calculate new average rating
    ratings = read_ratings()
    video_ratings = ratings.get(video_name, [])
    number_of_ratings = len(video_ratings)
    if video_ratings:
        average_rating = sum(video_ratings) / len(video_ratings)
    else:
        average_rating = 0

    return {"status": "success", "average_rating": average_rating, "number_of_ratings": number_of_ratings}
