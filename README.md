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

3. Collect static files:
```sh
python3 manage.py collectstatic
```
4. Migrate the database:
```sh
python3 manage.py makemigrations
python3 manage.py migrate
```

## Usage

```sh
gunicorn Swim4LoveV2.wsgi -c gunicorn.conf.py
```