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
# Rendering JWT_KEY:
python -c "import secrets; from pathlib import Path; f = Path('app/config.py'); f.write_text(f.read_text().replace('JWT_KEY_PLACEHOLDER', secrets.token_hex(32), 1));"
```
### Running tests
```shell
python -m pytest --cov-report term-missing --cov=app tests
```

### Generating  personal JWT Secret Key
'''shell
python
import secrets
secrets.token_hex(32)
# copy generated string.
# in config.py file, replace JWT_KEY value with generated string
''' 

## Using security dependencies:
'''
from app.internal.security.dependencies:
use is_logged_in and current_user functions as a route dependencies.
an example for how to use can be found at tests.security_testing_routes file.
'''

## Contributing
View [contributing guidelines](https://github.com/PythonFreeCourse/calendar/blob/master/CONTRIBUTING.md).

