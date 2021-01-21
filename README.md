# PyLander

## Open Source Calendar built with Python

### Run on Windows:

```shell
virtualenv env
.\env\Scripts\activate.bat
pip install -r requirements.txt
# Copy configuration.py.example to configuration.py.
# Edit the variables' values.
uvicorn app.main:app --reload
```
