'''
    This file purpose is for developers to add their features to the database
    in one convenient place, every time the system loads up it's adding and
    updating the features in the features table in the database.

    To update a feature, The developer needs to change the name or the route
    and let the system load, but not change both at the same time otherwise
    it will create junk and unnecessary duplicates.

    *   IMPORTANT - To enable features panel functionlity the developer must  *
    *   add the feature_access_filter decorator to ALL the feature routs      *
    *   Please see the example below.                                         *

    Enjoy and good luck :)
'''

'''
Example to feature stracture:

{
    "name": '<feature name>',
    "route": '/<the route like: /features >',
    "description": '<description>',
    "creator": '<creator name or nickname>'
}
'''

'''
*   IMPORTANT   *

Example to decorator placement:

    @router.get("/<my-route>")
    @feature_access_filter     <---- just above def keyword!
    def my_cool_feature_route():
        ....
        ...
            some code.
        ..
        .

'''

features = [
    {
        "name": 'Google Sync',
        "route": '/google/sync',
        "description": 'Sync Google Calendar events with Pylender',
        "creator": 'Liran Caduri'
    },
]
