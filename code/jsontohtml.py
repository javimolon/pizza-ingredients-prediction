import json
from json2html import *

f = open('code/resources_created/dtypes.json')
infoFromJson = json.loads(f.read())
f.close()
f1 = open('code/resources_created/dtypes.html', 'w')
f1.write(json2html.convert(json = infoFromJson))