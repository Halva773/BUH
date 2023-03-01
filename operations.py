from dadata import Dadata

DaDatatoken = "38cd715009142d4508117d5293e2cbec136496ac"
dadata = Dadata(DaDatatoken)
def checkLocation(location):
    for loc in location:
        if "4-й Вешняковский проезд, д 4" in loc['value']:
            return True
    return False

# lat=55.717903, lon=37.795361
if __name__ == "__main__":
    location = dadata.geolocate(name="address", lat=55.717903, lon=37.795361, radius_meters=50)
    print(checkLocation(location))