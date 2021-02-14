'''
    This file purpose is for developers to add their features to the database
    in one convenient place, every time the system loads up it's adding and
    updating the features in the features table in the database.

    To update a feature, The developer needs to change the name or the route
    and let the system load, but not change both at the same time otherwise
    it will create junk and unnecessary duplicates.

    Enjoy and good luck :)
'''

'''
All icons come from https://ionicons.com/.

If you want your feature to have an icon Go To: https://ionicons.com/
and follow the next steps:

1. pick an icon and press on it, copy the name.
2. create dict in the icons list below.
3. copy and paste your feature name and your
    icon name you copied earlier (follow the example).

4. And You Are Done. the icon will show automaticly.

If you dont pick an icon your feature will have a default icon.

Example to feature icon stracture:

{
    .
    .
    .
    "<feature name>": '<icon name>',
    .
    .
    .
}
'''

# Add to last!
icons = {
    'feature-panel': 'albums-outline'
    }


'''
Example to feature stracture:

{
    "name": '<feature name>',
    "route": '/<the route like: /features >',
    "description": '<description>',
    "creator": '<creator name or nickname>'
}
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
