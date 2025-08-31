from bs4 import BeautifulSoup
import pandas as pd
import re
import os


def is_empty_html(html_content):
    keresztabla_első = soup.find('legend', string=re.compile("Kereszttábla.*első félév"))
    if keresztabla_első:
        keresztabla_első = keresztabla_első.find_parent('fieldset')
        if keresztabla_első:
            # Nézzük meg, van-e valódi adat a táblázatban
            tabla = keresztabla_első.find('table')
            if tabla:
                # Üres táblázat esetén csak egy sor van fejléccel
                sorok = tabla.find_all('tr')
                if len(sorok) > 1:  # Több sor van, van adat
                    return False
                elif len(sorok) == 1:
                    # Egy sor, de nézzük meg, van-e benne cella adat
                    cellak = sorok[0].find_all('td')
                    for cella in cellak:
                        if cella.text.strip() and cella.text.strip() != '&nbsp;':
                            return False
    return True
def extract_competition_data(html_content):
    """Verseny adatok kinyerése HTML tartalomból"""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Alap információk kinyerése
    competition_info = {
        'season': extract_season(soup),
        'class': extract_class(soup),
        'round': extract_round(soup),
        'matches': extract_matches(soup),
        'cross_table_first': extract_cross_table(soup, "Kereszttábla (első félév)"),
        'cross_table_second': extract_cross_table(soup, "Kereszttábla (második félév)"),
        'team_standings': extract_team_standings(soup),
        'player_rankings': extract_player_rankings(soup)
    }
    
    return competition_info

def extract_season(soup):
    """Bajnokság szezonjának kinyerése"""
    select = soup.find('select', {'name': 'bajnoksag'})
    if select:
        selected_option = select.find('option', selected=True)
        if selected_option:
            return selected_option.text.strip()
    return None

def extract_class(soup):
    """Osztály kinyerése"""
    select = soup.find('select', {'name': 'osztaly'})
    if select:
        selected_option = select.find('option', selected=True)
        if selected_option:
            return selected_option.text.strip()
    return None

def extract_round(soup):
    """Forduló kinyerése"""
    select = soup.find('select', {'name': 'fordulo'})
    if select:
        selected_option = select.find('option', selected=True)
        if selected_option:
            return selected_option.text.strip()
    return None

def extract_matches(soup):
    """Mérkőzések kinyerése"""
    matches = []
    fieldset = soup.find('legend', string=re.compile("forduló csapatmérkőzései"))
    if fieldset:
        fieldset = fieldset.find_parent('fieldset')
        if fieldset:
            match_links = fieldset.find_all('a', class_='meccslapramutat')
            for match in match_links:
                teams = match.find_all('span', style=re.compile("font-size : 10pt"))
                if len(teams) >= 2:
                    home_team = teams[0].text.strip()
                    away_team = teams[1].text.strip()
                    
                    # Eredmény kinyerése
                    score_span = match.find('span', style=re.compile("float:right;.*font-size:16pt"))
                    score = score_span.text.strip() if score_span else "N/A"
                    match_id = extract_match_id(match['href'])
                    matches.append({
                        'match_id': match_id,
                        'home_team': home_team,
                        'away_team': away_team,
                        'score': score
                    })
    return matches
def extract_match_id(html_content):
    """Mérkőzés számának kinyerése a HTML tartalomból"""
    try:
        # Keresés a action=mecslap&id= számára
        match = re.search(r'action=mecslap&id=(\d+)', html_content)
        if match:
            return match.group(1)
    except:
        pass
    
    # Alternatív keresés, ha az első nem működik
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        back_link = soup.find('a', href=re.compile(r'javascript:history\.go\(-1\)'))
        if back_link:
            # Megpróbáljuk kinyerni az előző oldal URL-jéből
            match = re.search(r'id=(\d+)', str(back_link))
            if match:
                return match.group(1)
    except:
        pass
    
    return "Ismeretlen"

def extract_cross_table(soup, table_name):
    """Kereszttábla kinyerése"""
    cross_table = {}
    legend = soup.find('legend', string=table_name)
    if legend:
        fieldset = legend.find_parent('fieldset')
        if fieldset:
            table = fieldset.find('table')
            if table:
                rows = table.find_all('tr')
                if rows:
                    # Csapatnevek kinyerése
                    teams = []
                    header_cells = rows[0].find_all('td')[1:]  # Az első cella üres
                    teams = [cell.text.strip() for cell in header_cells]
                    
                    # Eredmények kinyerése
                    for row in rows[1:]:
                        cells = row.find_all('td')
                        if cells:
                            team_name = cells[0].text.strip()
                            results = {}
                            for i, cell in enumerate(cells[1:len(teams)+1]):
                                if i < len(teams):
                                    cell_text = cell.text.strip()
                                    # Színkódok eltávolítása
                                    if cell_text and cell_text != 'X':
                                        results[teams[i]] = re.sub(r'[^\d:-]', '', cell_text)
                            cross_table[team_name] = results
    return cross_table

def extract_team_standings(soup):
    """Csapat tabella kinyerése"""
    standings = []
    legend = soup.find('legend', string="Tabella:")
    if legend:
        fieldset = legend.find_parent('fieldset')
        if fieldset:
            table = fieldset.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Fejléc kihagyása
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 7:
                        standings.append({
                            'position': cells[0].text.strip(),
                            'team': cells[1].text.strip(),
                            'matches': cells[2].text.strip(),
                            'wins': cells[3].text.strip(),
                            'draws': cells[4].text.strip(),
                            'losses': cells[5].text.strip(),
                            'points': cells[6].text.strip()
                        })
    return standings

def extract_player_rankings(soup):
    """Játékos ranglista kinyerése"""
    rankings = []
    legend = soup.find('legend', string="Jatékosranglista:")
    if legend:
        fieldset = legend.find_parent('fieldset')
        if fieldset:
            table = fieldset.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Fejléc kihagyása
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 7:
                        rankings.append({
                            'position': cells[0].text.strip(),
                            'name': cells[1].text.strip(),
                            'license': cells[2].text.strip(),
                            'team': cells[3].text.strip(),
                            'matches': cells[4].text.strip(),
                            'wins': cells[5].text.strip(),
                            'win_percentage': cells[6].text.strip()
                        })
    return rankings

# Adatok exportálása CSV fájlba (opcionális)
def export_table_to_csv(competition_data,src):
    """Adatok exportálása CSV fájlokba"""
    # Csapat tabella
    directory = os.path.dirname(f"{src}/")
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    standings_df = pd.DataFrame(competition_data['team_standings'])
    standings_df.to_csv(f'{src}/csapat_tabella.csv', index=False, encoding='utf-8')
    
    # Játékos ranglista
    players_df = pd.DataFrame(competition_data['player_rankings'])
    players_df.to_csv(f'{src}/jatekos_ranglista.csv', index=False, encoding='utf-8')

def export_matches_to_csv(competition_data,path):
    # Mérkőzések
    directory = os.path.dirname(path+"/")
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    matches_df = pd.DataFrame(competition_data['matches'])
    matches_df.to_csv(f'{path}/merkozesek.csv', index=False, encoding='utf-8')
    
def main():
    # HTML fájl beolvasása
    with open('test/index.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Adatok kinyerése
    competition_data = extract_competition_data(html_content)

    # Eredmények megjelenítése
    print("=== VERSENY ADATAI ===")
    print(f"Szezon: {competition_data['season']}")
    print(f"Osztály: {competition_data['class']}")
    print(f"Forduló: {competition_data['round']}")

    print("\n=== MÉRKŐZÉSEK ===")
    for i, match in enumerate(competition_data['matches'], 1):
        print(f"{i}. {match['home_team']} - {match['away_team']}: {match['score']}")

    print("\n=== CSAPAT TABELLA ===")
    for team in competition_data['team_standings']:
        print(f"{team['position']}. {team['team']} - Pont: {team['points']}")

    print("\n=== JÁTÉKOS RANGLISTA (első 5) ===")
    for player in competition_data['player_rankings'][:5]:
        print(f"{player['position']}. {player['name']} - Győzelmi arány: {player['win_percentage']}")



    # CSV exportálás (megjegyzésbe téve, ha nem szeretnéd)
    export_table_to_csv(competition_data,"test/table")
    export_matches_to_csv(competition_data,"test/table")
if __name__ == "__main__":
    main()