'''
    This file purpose is for developers to add their features to the database
    in one convenient place, every time the system loads up it's adding and
    updating the features table database.

    To update the developer needs to change the name or the route and let
    the system load, but not change both at the same time otherwise it will
    create junk and unnecessary duplicates.

    Enjoy and good luck :)
'''

features = [
    {
        "name": 'agenda',
        "route": '/agenda',
        "description": 'description',
        "creator": 'creator'
    },
    {
        "name": 'feature-panel',
        "route": '/features/',
        "description": 'description',
        "creator": 'liran caduri'
    },
    {
        "name": 'invitations',
        "route": '/invitations/',
        "description": 'description',
        "creator": 'creator2'
    },
    {
        "name": 'association',
        "route": '/features/test-association',
        "description": 'description',
        "creator": 'creator2'
    }
]
