# Text To (Stickman) Motion Generation App
Try out the capabilities of the text2motion motion MotionCLIP with just a few easy commands!
</br>

## Prepare your environemnt

1. Install [Docker](https://docs.docker.com/engine/install/)
2. Clone this repository
</br>


## Build Docker image
Position your shell in the root of this repository, and execute (be patient, some heavy packages are required :)
```
$ docker build -t text2motion .
```
</br>


## Run Docker container
```
$ docker run --rm -it -p 8111:8000 -v /Users/klabs/Downloads/app_vids:/src/app/videos text2motion
```
replace /Users/klabs/Downloads/app_vids with whatever directory on your machine you want the generated .mp4 videos to be saved.


## Development
Install python3.8</br>
```
conda create --name webapp_text2motion python=3.8
```

Activate conda env
```
conda activate webapp_text2motion
```

Install other dependencies
```
pip install -r requirements.txt
```

### Format and check code
```
pip install -r requirements-dev.txt
```
Format and check code
```
$ isort . && black . && ruff --ignore E501 . --fix && bandit -c bandit.yaml -rq . && mypy .
```