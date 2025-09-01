import requests
import matchgetdata as mg
import tablegetdata as tg
import playergetdata as pg
import pandas as pd
import datetime
import os

def update_season_data(bajnoksag,osztaly,logfile):
    changed_data=False
    try:
        src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag={bajnoksag["id"]}&osztaly={osztaly["id"]}&fordulo={1}"
        response=requests.get(src)
        data=tg.extract_competition_data(response.text)
        tg.export_table_to_csv(data,f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}")
        for fordulo in range(1,31):
            src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag={bajnoksag["id"]}&osztaly={osztaly}&fordulo={fordulo}"
            response=requests.get(src)
            data=tg.extract_competition_data(response.text)
            tg.export_matches_to_csv(data,f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}/rounds/{fordulo}")
            for match in data['matches']:
                src=f"http://www.bpatsz.hu/bpatszenyr/index.php?action=mecslap&id={match["match_id"]}"
                response=requests.get(src)
                data=mg.extract_match_data(response.text)
                mg.export_to_csv(data,f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}/rounds/{fordulo}/matches/{match["match_id"]}")
            changed_data=True
            print(f"Adatok kinyerve: {bajnoksag["name"]} {osztaly["name"]} {fordulo}. forduló")
    except Exception as e:
        logfile.write(f"{datetime.datetime.now()}\tHiba a kinyervéssel: {e}\n")
        print(f"Hiba a kinyervéssel: {e}")
        logfile.write(f"{datetime.datetime.now()} {bajnoksag['name']} {osztaly['name']} {e}\n")
        print(f"Bajnokság: {bajnoksag['name']}, Osztály: {osztaly['name']}")
    logfile.flush()
    return True
def download_season_data(bajnoksag,osztaly,logfile):
    try:
        changed_data=False
        src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag={bajnoksag["id"]}&osztaly={osztaly["id"]}&fordulo={1}"
        print(f"Bajnokság: {bajnoksag['name']}, Osztály: {osztaly['id']}")
        response=requests.get(src)
        data=tg.extract_competition_data(response.text)
        tg.export_table_to_csv(data,f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}")
        for fordulo in range(1,31):
            src=f"http://www.bpatsz.hu/bpatszenyr/index.php?bajnoksag={bajnoksag["id"]}&osztaly={osztaly["id"]}&fordulo={fordulo}"
            response=requests.get(src)
            data=tg.extract_competition_data(response.text)
            tg.export_matches_to_csv(data,f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}/rounds/{fordulo}")
            for match in data['matches']:
                src=f"http://www.bpatsz.hu/bpatszenyr/index.php?action=mecslap&id={match["match_id"]}"
                response=requests.get(src)
                data=mg.extract_match_data(response.text)
                mg.export_to_csv(data,f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}/rounds/{fordulo}/matches/{match["match_id"]}")
            print(f"Adatok kinyerve: {bajnoksag["name"]} {osztaly["name"]} {fordulo}. forduló")
            changed_data=True
    except Exception as e:
        logfile.write(f"{datetime.datetime.now()}\tHiba a kinyervéssel: {e}\n")
        print(f"Hiba a kinyervéssel: {e}")
        logfile.write(f"{datetime.datetime.now()} {bajnoksag['name']} {osztaly['name']} {e}\n")
        print(f"Bajnokság: {bajnoksag['name']}, Osztály: {osztaly['name']}")
    logfile.flush()
    return changed_data
def get_player_data(player_id):
    src="http://www.bpatsz.hu/bpatszenyr/egyeni-bajnokilista.php"
    response=requests.post(src,data={"bajnokiev":27,"engszam":player_id})
    if response.status_code==200:
        return response.text
    else:
        return None
def get_all(years,classes,logfile):
    for year in range(2014,2025):
        for osztaly in classes["name"].values:
            bajnoksag={"name":f"{year}-{year+1}","id":years.loc[years["year"]==year]["id"].values[0]}
            osztaly={ "name":osztaly,"id":classes.loc[classes["name"]==osztaly]["id"].values[0]}
            if os.path.exists(f"bajnoksagok/{bajnoksag["name"]}/{osztaly["name"]}/rounds/30"):
                logfile.write(f"{datetime.datetime.now()}\t{bajnoksag["name"]}/{osztaly["name"]} Alredy downloaded\n")
                print(f"{bajnoksag['name']}/{osztaly["name"]} Alredy downloaded")
                continue
            changed_data=download_season_data(bajnoksag,osztaly,logfile)
            if changed_data:
                os.system("git add .")
                os.system(f"git commit -m \"{bajnoksag['name']}/{osztaly['name']} done\"")
                os.system("git push")
def main():
    classes=pd.read_csv("src/classid.csv")
    years=pd.read_csv("src/yearid.csv")
    bajnoksag=2024
    osztaly="Bp1_B2"
    bajnoksag={"name":f"{bajnoksag}-{bajnoksag+1}","id":years.loc[years["year"]==bajnoksag]["id"].values[0]}
    osztaly={ "name":osztaly,"id":classes.loc[classes["name"]==osztaly]["id"].values[0]}
    #with open("log.txt","a",encoding="utf-8") as logfile:
    #    logfile.write(f"{datetime.datetime.now()}\tLog start\n")
    #    download_season_data(bajnoksag,osztaly,logfile)
    #get_player_data(21614)
    with open("log.txt","a",encoding="utf-8") as logfile:
        logfile.write(f"{datetime.datetime.now()}\tLog start\n")
        try:
            get_all(years,classes,logfile)
        except Exception as e:
            print(e)
            logfile.write(f"{datetime.datetime.now()} {e}\n")
        finally:
            logfile.write(f"{datetime.datetime.now()}\tLog end\n")
            logfile.close()
            os.system("git add .")
            os.system(f"git commit -m \"Log end\"")
            os.system("git push")
            os.system("shutdown now -h")
if __name__=="__main__":
    main()