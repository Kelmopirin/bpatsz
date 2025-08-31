import requests
import matchgetdata as mg
import tablegetdata as tg
import pandas as pd
import os

bajnoksag=27
osztaly=1
for fordulo in range(1,31):
    src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag={bajnoksag}&osztaly={osztaly}&fordulo={fordulo}"
    response=requests.get(src)
    data=tg.extract_competition_data(response.text)
    if fordulo==1:
        tg.export_table_to_csv(data,"bajnoksagok/2024-2025")
    tg.export_matches_to_csv(data,"bajnoksagok/2024-2025",fordulo)
    for match in data['matches']:
        src=f"http://www.bpatsz.hu/bpatszenyr/index.php?action=mecslap&id={match["match_id"]}"
        response=requests.get(src)
        data=mg.extract_match_data(response.text)
        mg.export_to_csv(data,"bajnoksagok/2024-2025",fordulo,match["match_id"])
