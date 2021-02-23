.
├── app
│   ├── __init__.py
│   ├── dependencies.py
│   ├── main.py
│   ├── database
│       ├── __init__.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│   ├── internal
│       ├── __init__.py
│       ├── admin.py
│       ├── agenda_events.py
│       ├── email.py
│   ├── media
│       ├── example.png
│       ├── fake_user.png
│       ├── profile.png
│   ├── routers
│       ├── __init__.py
│       ├── agenda.py
│       ├── categories.py
│       ├── email.py
│       ├── event.py
│       ├── profile.py
│   ├── static
│       ├── event
│           ├── eventedit.css
│           ├── eventview.css
│       ├── agenda_style.css
│       ├── popover.js
│       ├── style.css
│   ├── templates
│       ├── base.html
│       ├── home.html
│       ├── profile.html
├── LICENSE
├── requirements.txt
├── schema.md
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── test_agenda_internal.py
    ├── test_agenda_route.py
    ├── test_app.py
    ├── test_categories.py
    ├── test_email.py
    ├── test_event.py
    └── test_profile.py