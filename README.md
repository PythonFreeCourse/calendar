virtualenv env
.\env\Scripts\activate.bat
pip install -r requirements.txt
# Copy configuration.py.example to configuration.py.
# Edit the variables' values.
uvicorn app.main:app --reload