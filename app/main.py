import asyncio
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
    # Start the video generation process
    video_name = await generate_video(prompt)
    # Redirect to the new video
    return RedirectResponse(url=f"/?video_name={video_name}", status_code=303)


async def generate_video(prompt):
    # Simulate external API call
    await asyncio.sleep(5)  # Simulate processing time

    # Generate a dummy video file (copying an existing one)
    source_video = os.path.join(VIDEO_DIRECTORY, get_video_list()[0])
    new_video_name = f"{prompt.replace(' ', '_')}.mp4"
    new_video_path = os.path.join(VIDEO_DIRECTORY, new_video_name)

    with open(source_video, "rb") as src, open(new_video_path, "wb") as dst:
        dst.write(src.read())

    return new_video_name
