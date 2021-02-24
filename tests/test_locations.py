from app.internal import locations


def test_create_location_object():
    location_fields = {
        'country': "AD",
        'city': "Andorra La Vella",
        'zip_number': "3041563",
        'end_month': 4,
        'end_day_in_month': 19,
    }
    result = locations.create_location_object(location_fields)
    assert result.city == 'Andorra La Vella'
    assert result.zip_number == "3041563"
