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

## Usage

```sh
gunicorn Swim4LoveV2.wsgi -c gunicorn.conf.py
```