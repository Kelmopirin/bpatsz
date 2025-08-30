import requests

bajnoksag=27
osztaly=1
fordulo=1
src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag={bajnoksag}&osztaly={osztaly}&fordulo={fordulo}"
response=requests.get(src)
file=open("index.html","w",encoding="utf-8")
file.write(response.text)
file.close()
meccsid=23029
src=f"http://www.bpatsz.hu/bpatszenyr/index.php?action=mecslap&id={meccsid}"
response=requests.get(src)
file=open("mecslap.html","w",encoding="utf-8")
file.write(response.text)
file.close()