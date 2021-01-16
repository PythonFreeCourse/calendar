Run on Windows:

virtualenv env
.\env\Scripts\activate.bat
pip install -r requirements.txt
cd app
uvicorn main:app --reload