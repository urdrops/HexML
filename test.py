import json
str = "{ 'hello': 13}"
js = json.loads(str)

print(js['hello'])