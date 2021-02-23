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
# Rendering JWT_KEY:
python -c "import secrets; from pathlib import Path; f = Path('app/config.py'); f.write_text(f.read_text().replace('JWT_KEY_PLACEHOLDER', secrets.token_hex(32), 1));"
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

### Cypress:
Front end testing tool.

Every test created with testLevel configuration, the defualt level we run our test is 5.
Basic tests will spicified with lower testLevel than advanced tests.

#To run Cypress:

1. Make sure you already installed npm (run npm --version to check).
2. Run the server
3. Nevigate to 'test-ui' folder: calendar/tests/test-ui
    - Run with Test Runner:
        1. Run on terminal: ```npx cypress open```
        2. Test Runner will open: choose test and click it to execute
    - Run all test without watching:
        1. Run on terminal: ```npx cypress run```
    - Run a specific test file without watching:
        1. Run on terminal: ```npx cypress run --spec cypress/integration/path/to/file```
    - Run tests with change level env config to 10: ```npx cypress run --env level=10```
### Running tests
# Rendering JWT_KEY:
python -c "import secrets; from pathlib import Path; f = Path('app/config.py'); f.write_text(f.read_text().replace('JWT_KEY_PLACEHOLDER', secrets.token_hex(32), 1));"

### Running tox
```shell
# Standard tests: 'coverage' and 'flake8'
tox
# Only flake8 tests
tox -e flake8
# Coverage with html reports
tox -e rep
```

## Contributing
View [contributing guidelines](https://github.com/PythonFreeCourse/calendar/blob/master/CONTRIBUTING.md).
