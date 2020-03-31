import json5
from urllib.parse import quote

with open('config.json', 'r', encoding="utf-8") as f:
    data = json5.load(f)
dataEncodingArr = ['sF21648_2', 'sF21648_4', 'sF21648_6', 'sF21649_2',
                   'sF21650_2', 'sF21650_3', 'sF21650_4', 'sF21650_10']
print(data)
for dataIdx in dataEncodingArr:
    data[dataIdx] = quote(data[dataIdx].encode("gb2312"))
print(data)
