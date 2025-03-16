# Swim4Love

This is a project for the Swim4Love event. It is a web application that allows users to track the swimmers.

## Installation

### Prerequisites

- Python 3.x
- pip

### Steps

1. Clone the repository:

```sh
git clone https://github.com/HenryXiaoYang/Swim4LoveV2.git
cd Swim4LoveV2
```

2. Install Python dependencies:

```sh
pip install -r requirements.txt
```

3. Edit the .env file to set your secret key:

```dotenv
DJANGO_SECRET_KEY=your_secret_key
```

Make sure to keep your keys safe!

5. Edit the Swim4LoveV2/settings.py file if you need to change some Django settings.


6. Collect static files:

```sh
python3 manage.py collectstatic
```

7. Migrate the database:

```sh
python3 manage.py makemigrations
python3 manage.py migrate
```

8. Create a superuser

```shell
python3 manage.py createsuperuser
```

## Usage

1. Run the server:

```sh
gunicorn DjangoConfigs.wsgi -c gunicorn.conf.py
```

2. Open your browser and go to `http://127.0.0.1:8000/` to view the website.
3. Use your superuser credentials to log in.

## Deploy with Docker

1. Build the image:

```sh
sudo docker build -t henryxiaoyang/swim4lovev2 .
```

2. Run the image:

```sh
sudo docker run -d \
  --name swim4lovev2 \
  --restart always \
  -v swim4lovev2:/app \
  -e DJANGO_SECRET_KEY=Your-Secret-Key \
  -p 8000:8000 \
  henryxiaoyang/swim4lovev2
```

or use docker-compose:

```docker-compose
version: "3"

services:
  swim4lovev2:
    image: henryxiaoyang/swim4lovev2
    container_name: swim4lovev2
    restart: always
    volumes:
        - swim4lovev2:/app
    environment:
      DJANGO_SECRET_KEY: Your-Secret-Key
    ports:
      - "8000:8000"

volumes:
    swim4lovev2:
```

```sh
docker-compose up -d
```