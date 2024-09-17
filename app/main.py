import asyncio
import aiohttp

import os
import os.path  # Import os.path for path manipulations

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount static directories
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/videos", StaticFiles(directory=os.getenv("VIDEO_DIR")), name="videos")

templates = Jinja2Templates(directory="app/templates")

VIDEO_DIRECTORY = os.getenv("VIDEO_DIR")


def get_video_list():
    return sorted([f for f in os.listdir(VIDEO_DIRECTORY) if f.endswith(".mp4")])


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, video_name: str = None):
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

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "video": video,
            "video_title": video_title,
            "prev_video": prev_video,
            "next_video": next_video,
            "videos": videos,  # Pass the list of videos
            "current_index": current_index,  # Pass the current index
        },
    )

@app.post("/", response_class=HTMLResponse)
async def create_video(request: Request, prompt: str = Form(...)):
    video_name = await generate_video(prompt)
    if video_name:
        return RedirectResponse(url=f"/?video_name={video_name}", status_code=303)
    else:
        videos = get_video_list()
        current_index = 0
        video = videos[current_index]
        video_title = os.path.splitext(video)[0].replace("_", " ").title()
        prev_video = videos[current_index - 1] if current_index > 0 else videos[-1]
        next_video = (
            videos[current_index + 1] if current_index < len(videos) - 1 else videos[0]
        )
        context = {
            "request": request,
            "error_message": "Something went wrong, displaying first video",
            "prompt": prompt,
            "video": video,
            "video_title": video_title,
            "prev_video": prev_video,
            "next_video": next_video,
            "videos": videos,  # Pass the list of videos
            "current_index": current_index,  # Pass the current index
        }
        return templates.TemplateResponse("index.html", context)


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
