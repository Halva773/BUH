print("[START] Файл operations.py запущен")


def checkLocation(location):
    for loc in location:
        if "4-й Вешняковский проезд, д 4" in loc['value']:
            return True
    return False



def generateID():
    i = 0
    while True:
        i += 1
        yield i

# lat=55.717903, lon=37.795361
    # location = dadata.geolocate(name="address", lat=55.717903, lon=37.795361, radius_meters=50)
    # print(checkLocation(location))
