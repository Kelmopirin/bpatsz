import requests
import matchgetdata as mg
import tablegetdata as tg
import pandas as pd
import os

bajnoksag=27
osztaly=1
fordulo=30
src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag={bajnoksag}&osztaly={osztaly}&fordulo={fordulo}"
response=requests.get(src)
data=tg.extract_competition_data(response.text)
directory = os.path.dirname("bajnoksagok/2024-2025/")
if directory and not os.path.exists(directory):
    os.makedirs(directory, exist_ok=True)
tg.export_to_csv(data,"bajnoksagok/2024-2025")
exit(0)
meccsid=23743
src=f"http://www.bpatsz.hu/bpatszenyr/index.php?action=mecslap&id={meccsid}"
response=requests.get(src)
file=open("mecslap.html","w",encoding="utf-8")
file.write(response.text)
file.close()