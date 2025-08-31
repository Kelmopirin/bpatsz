import requests
import matchgetdata as mg
import tablegetdata as tg
import playergetdata as pg
import pandas as pd
import os

def download_season_data(bajnoksag,osztaly):
    src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag={bajnoksag["id"]}&osztaly={osztaly["id"]}&fordulo={1}"
    response=requests.get(src)
    data=tg.extract_competition_data(response.text)
    tg.export_table_to_csv(data,f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}")
    for fordulo in range(1,31):

            src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag={bajnoksag["name"]}&osztaly={osztaly}&fordulo={fordulo}"
            response=requests.get(src)
            data=tg.extract_competition_data(response.text)
            tg.export_matches_to_csv(data,f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}/rounds/{fordulo}")
            for match in data['matches']:
                src=f"http://www.bpatsz.hu/bpatszenyr/index.php?action=mecslap&id={match["match_id"]}"
                response=requests.get(src)
                data=mg.extract_match_data(response.text)
                mg.export_to_csv(data,f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}/rounds/{fordulo}/matches")
            print(f"Adatok kinyerve: {bajnoksag["name"]} {osztaly["name"]} {fordulo}. forduló")

def get_player_data(player_id):
    src=f"http://www.bpatsz.hu/bpatszenyr/egyeni-bajnokilista.php"
    response=requests.post(src,data={"bajnokiev":27,"engszam":21614})
    if response.status_code==200:
        return response.text
    else:
        return None
def get_all(years,classes):
    for bajnoksag in range(2014,2025):
        for osztaly in classes["id"].values:
            download_season_data(bajnoksag,
                                 years.loc[years["year"]==bajnoksag]["id"].values[0],osztaly,
                                 osztaly,
                                 )
def main():
    classes=pd.read_csv("src/classid.csv")
    years=pd.read_csv("src/yearid.csv")
    bajnoksag=2024
    osztaly="Bp1_B2"
    bajnoksag={"name":f"{bajnoksag}-{bajnoksag+1}","id":years.loc[years["year"]==bajnoksag]["id"].values[0]}
    osztaly={ "name":osztaly,"id":classes.loc[classes["name"]==osztaly]["id"].values[0]}
    download_season_data(bajnoksag,osztaly)
    #get_player_data(21614)
    #get_all()
    print(get_classes_from_file("src/classid.csv"))
if __name__=="__main__":
    main()