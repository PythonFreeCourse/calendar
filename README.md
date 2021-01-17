Run on Windows:

virtualenv env
.\env\Scripts\activate.bat
pip install -r requirements.txt
cd app
uvicorn main:app --reload


Cypress:
Front end testing tool built for the modern web.

Every test created with testLevel configuration, the defualt level we run our test is 5.
Basic tests will spicified with lower testLevel than advanced tests.

To run Cypress:

1. Make sure you already installed npm (run npm --version to check).
2. Run the server
3. Nevigate to 'test-ui' folder: calendar/tests/test-ui
    - Run with Test Runner:
        1. Run on terminal: npx cypress open
        2. Test Runner will open: choose test and click it to execute
    - Run all test without watching:
        1. Run on terminal: npx cypress run
    - Run a specific test file without watching:
        1. Run on terminal: npx cypress run --spec "cypress/integration/path/to/file"
    - Run tests with change level env config to 10: npx cypress run --env level=10