from bs4 import BeautifulSoup
import pandas as pd
import re
import os

def extract_match_data(html_content):
    """Mérkőzés adatok kinyerése HTML tartalomból"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Alap információk kinyerése
    teams=soup.find_all(style=re.compile(r'font-size:11pt;'))[:2]
    match_info = {
        'home_team': teams[0].text.strip(),
        'away_team': teams[1].text.strip(),
        'score': extract_score(soup),
        'round_info': extract_round_info(soup),
        'matches': extract_individual_matches(soup),
        'referees': extract_referees(soup),
        'substitutes': extract_substitutes(soup),
        'notes': extract_notes(soup)
    }
    
    return match_info

def extract_score(soup):
    """Eredmény kinyerése"""
    try:
        score_row = soup.find('td', style=re.compile(r'font-size:15pt'))
        score = score_row.text.strip()
        return score
    except:
        return "Nem sikerült kinyerni"

def extract_round_info(soup):
    """Forduló információk kinyerése"""
    try:
        round_info = soup.find('span', class_='kiir').text.strip()
        return round_info
    except:
        return "Nem sikerült kinyerni"

def extract_individual_matches(soup):
    """Egyéni mérkőzések kinyerése"""
    matches = []
    try:
        # Játékosok neveinek kinyerése
        players_row = soup.find('tr', class_='tablerow2')
        away_players = [td.text.strip() for td in players_row.find_all('td')[1:5]]
        # Hazai játékosok kinyerése
        home_players_rows = soup.find_all('tr', style=re.compile(r'height:64px;'))
        
        for i, row in enumerate(home_players_rows[1:]):
            home_player = row.find('td', class_='tablerow2').text.strip()
            # Eredmények kinyerése minden egyes mérkőzéshez
            match_cells = [cell for cell in row.find_all('td')[1:] if len(cell.find_all('tr')) >7]
            for j, cell in enumerate(match_cells):
                if j < len(away_players):
                    match_data = extract_match_details(cell, home_player, away_players[j])
                    matches.append(match_data)
                    
    except Exception as e:
        print(f"Hiba az egyéni mérkőzések kinyerésekor: {e}")
    
    return matches

def extract_match_details(cell, home_player, away_player):
    """Egyéni mérkőzés részletek kinyerése"""
    try:
        # Szettek kinyerése
        sets = []
        set_rows = cell.find_all('tr')[:5]  # Maximum 5 szett
        
        for set_row in set_rows:
            set_cells = set_row.find_all('td')
            if len(set_cells) == 2:
                home_score = set_cells[0].text.strip()
                away_score = set_cells[1].text.strip()
                if home_score and away_score:
                    sets.append(f"{home_score}-{away_score}")
        # Eredmény kinyerése (pl. 3/0)
        result_span = cell.find_all('span', style=re.compile(r'font-weight: bold'))
        resulthome = result_span[0].text.strip() if result_span else "N/A"
        resultaway = result_span[1].text.strip() if len(result_span) > 1 else "N/A"
        # Mérkőzés száma
        match_num_span = cell.find('td', style=re.compile(r'color:gray;font-size:70%'))
        match_num = match_num_span.text.strip() if match_num_span else "N/A"
        
        return {
            'home_player': home_player,
            'away_player': away_player,
            'sets': sets,
            'resulthome': resulthome,
            'resultaway': resultaway,
            'match_number': match_num
        }
    except Exception as e:
        print(f"Hiba a mérkőzés részletek kinyerésekor: {e}")
        return {
            'home_player': home_player,
            'away_player': away_player,
            'sets': [],
            'result': "N/A",
            'match_number': "N/A"
        }

def extract_referees(soup):
    """Játékvezetők kinyerése"""
    referees = {}
    try:
        ref_table = soup.find('td', string='Főbíró-játékvezető:').find_parent('table')
        rows = ref_table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                role = cells[0].text.strip().replace(':', '')
                name = cells[1].text.strip()
                if name:
                    referees[role] = name
    except:
        pass
    
    return referees

def extract_substitutes(soup):
    """Cserejátékosok kinyerése"""
    substitutes = {}
    try:
        sub_table = soup.find('td', string='Hazai cserejátékos:').find_parent('table')
        rows = sub_table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                role = cells[0].text.strip().replace(':', '')
                name = cells[1].text.strip()
                if name:
                    substitutes[role] = name
    except:
        pass
    
    return substitutes

def extract_notes(soup):
    """Megjegyzések és büntetések kinyerése"""
    notes = {}
    try:
        notes_table = soup.find('td', string='Megjegyzés:').find_parent('table')
        rows = notes_table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].text.strip().replace(':', '').replace('�', '')
                value = cells[1].text.strip()
                if value:
                    notes[key] = value
    except:
        pass
    
    return notes

def print_match_data(match_data):
    """Mérkőzés adatok szép megjelenítése"""
    print("=" * 60)
    print("MÉRKŐZÉS ADATAI")
    print("=" * 60)
    print(f"Hazai csapat: {match_data['home_team']}")
    print(f"Vendég csapat: {match_data['away_team']}")
    print(f"Eredmény: {match_data['score']}")
    print(f"Forduló: {match_data['round_info']}")
    print()
    
    print("Egyéni mérkőzések:")
    print("-" * 60)
    for i, match in enumerate(match_data['matches'], 1):
        print(f"{i}. {match['home_player']} - {match['away_player']}")
        print(f"   Eredmény: {match['resulthome']} - {match['resultaway']}")
        if match['sets']:
            print(f"   Szettek: {', '.join(match['sets'])}")
        print()
    
    if match_data['referees']:
        print("Játékvezetők:")
        print("-" * 60)
        for role, name in match_data['referees'].items():
            print(f"{role}: {name}")
        print()
    
    if match_data['substitutes']:
        print("Cserejátékosok:")
        print("-" * 60)
        for role, name in match_data['substitutes'].items():
            print(f"{role}: {name}")
        print()
    
    if match_data['notes']:
        print("Megjegyzések és büntetések:")
        print("-" * 60)
        for key, value in match_data['notes'].items():
            print(f"{key}: {value}")

# HTML fájl beolvasása
# Opcionális: adatok exportálása CSV fájlba
def export_to_csv(match_data, path):
    """Adatok exportálása CSV fájlba"""
    # Egyéni mérkőzések exportálása
    directory = os.path.dirname(path+"/")
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    matches_df = pd.DataFrame(match_data['matches'])
    matches_df.to_csv(f"{path}/egyeni_merkozesek.csv", index=False, encoding='utf-8')
    
    # Egyéb információk exportálása
    other_data = {
        'Hazai csapat': [match_data['home_team']],
        'Vendég csapat': [match_data['away_team']],
        'Eredmény': [match_data['score']],
        'Forduló': [match_data['round_info']]
    }
    
    # Játékvezetők hozzáadása
    for role, name in match_data['referees'].items():
        other_data[role] = [name]
    
    other_df = pd.DataFrame(other_data)
    other_df.to_csv(f"{path}/merkozes_adatok.csv", index=False, encoding='utf-8')


def main():
    with open('test/mecslap.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Adatok kinyerése
    match_data = extract_match_data(html_content)

    # Eredmények megjelenítése  
    print_match_data(match_data)

    # CSV exportálás (megjegyzésbe téve, ha nem szeretnéd)
    if not os.path.exists("test/meccslapok/"):
        os.makedirs("test/meccslapok/")
    export_to_csv(match_data,"test/meccslapok")

if __name__ == "__main__":
    main()