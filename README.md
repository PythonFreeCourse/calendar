# PyLander

<p style="text-align:center">
  <img title="Apache-2.0" alt="License Apache-2.0 icon" src="https://img.shields.io/github/license/PythonFreeCourse/calendar.svg">
</p>

👋 Welcome to Open Source Calendar built with Python. 🐍

* [Project's objectives](#Project's-objectives)
* [Creating development environment](#creating-development-environment)
* [Contributing](#contributing)
### Project's objectives
1. Develop open source calendar tool using new technics while trying new things.
2. Using Python as main programming language and plain HTML/JS for GUI.
3. Create bonding in our community.

## Creating development environment
### Prerequisites
1. Windows or Linux based system - either [WSL on windows](https://docs.microsoft.com/en-us/windows/wsl/install-win10) or full blown linux.
2. [Python](https://www.python.org/downloads/release/python-385/)
3. Install python's requirements:
```shell
pip install -r requirements.txt
```
4. Install pre-commit hooks:
```shell
pre-commit install
```

### Running on Windows

```shell
virtualenv env
.\env\Scripts\activate.bat
pip install -r requirements.txt
# Copy app\config.py.example to app\config.py.
# Edit the variables' values.
uvicorn app.main:app --reload
```

### Running on Linux
```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp app/config.py.example app/config.py
# Edit the variables' values.
uvicorn app.main:app --reload
```
### Running tests
```shell
python -m pytest --cov-report term-missing --cov=app tests
```

## Contributing
View [contributing guidelines](https://github.com/PythonFreeCourse/calendar/blob/master/CONTRIBUTING.md).
