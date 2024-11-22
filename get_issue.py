# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://proyectosan.atlassian.net/rest/api/3/issue/KAN-118"

auth = HTTPBasicAuth("carlo.bernucci@aguasnuevas.cl", "ATATT3xFfGF0QJMW2deqscfBig7PLfDPNjNk-aGVpF9FZgAHilK7wTQaCTHQldVXqTtBZqb25aA9u8WQHJJlTJ76AOMIa_o4X88YfAC5j9s2IJ27NWg4bYfcr3BijwDMEnmuP3CwuULAthmvsjGE70DTukWTZWzdxLpDl7jaHp4-vE5HtV2PJVQ=BD4752CB")

headers = {
  "Accept": "application/json"
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   auth=auth
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))