import requests

osztaly=1
fordulo=1
src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag=28&osztaly={osztaly}&fordulo={fordulo}"
response=requests.get(src)
file=open("index.html","w",encoding="utf-8")
file.write(response.text)
file.close()
