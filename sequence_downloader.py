import mercantile, mapbox_vector_tile, requests, json, os
from vt2geojson.tools import vt_bytes_to_geojson
from PIL import Image
import piexif
from io import BytesIO
import time

def add_gps_info_to_image_data(latitude, longitude):
    def convert_to_degrees(value):
        d = int(value)
        m = int((value - d) * 60)
        s = (value - d - m/60) * 3600
        return d, m, s

    lat_deg = convert_to_degrees(latitude)
    lon_deg = convert_to_degrees(longitude)

    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: 'N' if latitude >= 0 else 'S',
        piexif.GPSIFD.GPSLatitude: [(lat_deg[0], 1), (lat_deg[1], 1), (int(lat_deg[2]*100), 100)],
        piexif.GPSIFD.GPSLongitudeRef: 'E' if longitude >= 0 else 'W',
        piexif.GPSIFD.GPSLongitude: [(lon_deg[0], 1), (lon_deg[1], 1), (int(lon_deg[2]*100), 100)],
    }

    exif_dict = {"GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    return exif_bytes
    
if not os.path.exists("downloads"):
    os.makedirs("downloads")
                            
access_token = ''

sequence_id = ''
url = "https://graph.mapillary.com/image_ids?sequence_id={}".format(sequence_id)
header = {'Authorization' : 'OAuth {}'.format(access_token)}
r = requests.get(url, headers=header)
data = r.json()
for img_id in data["data"]:
    image_url = 'https://graph.mapillary.com/{}?fields=thumb_original_url, geometry'.format(img_id["id"])
    img_r = requests.get(image_url, headers=header)
    img_data = img_r.json()
    image_get_url = img_data['thumb_original_url']
    print(img_data)
    if not os.path.exists("downloads/" + sequence_id):
        os.makedirs("downloads/" + sequence_id)
    with open('downloads/{}/{}.jpg'.format(sequence_id, img_id["id"]), 'wb') as handler:
        image_data = requests.get(image_get_url, stream=True).content
        exif_bytes = add_gps_info_to_image_data(img_data['geometry']['coordinates'][1], img_data['geometry']['coordinates'][0])
        image = Image.open(BytesIO(image_data))
        image.save('downloads/{}/{}.jpg'.format(sequence_id, img_id["id"]), exif=exif_bytes)

