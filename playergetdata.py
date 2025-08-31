from bs4 import BeautifulSoup
import pandas as pd
import re
import os
def extract_player_stats(html_content):
    """Játékos statisztikák kinyerése HTML tartalomból"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Játékos információk kinyerése
    player_info = {
        'name': extract_player_name(soup),
        'license_number': extract_license_number(soup),
        'stats': extract_statistics(soup),
        'matches': extract_matches(soup)
    }
    
    return player_info

def extract_player_name(soup):
    """Játékos nevének kinyerése"""
    try:
        # Megkeressük az első táblázatot, ahol a játékos neve szerepel
        first_row = soup.find('tr', bgcolor='white')
        if first_row:
            name_cell = first_row.find('td')
            if name_cell:
                return name_cell.text.strip()
    except:
        pass
    return "Ismeretlen"

def extract_license_number(soup):
    """Játékos engedély számának kinyerése"""
    try:
        # Megkeressük az input mezőt, ahol az engedély szám van
        input_field = soup.find('input', {'id': 'engszam'})
        if input_field and 'value' in input_field.attrs:
            return input_field['value']
    except:
        pass
    
    # Alternatív megoldás: az első sorból kinyerjük
    try:
        first_row = soup.find('tr', bgcolor='white')
        if first_row:
            cells = first_row.find_all('td')
            if len(cells) > 1:
                return cells[1].text.strip()
    except:
        pass
    
    return "Ismeretlen"

def extract_statistics(soup):
    """Statisztikák kinyerése"""
    stats = {}
    try:
        # Statisztikai táblázat megkeresése
        stats_table = soup.find('table', cellspacing="2", cellpadding="5")
        if stats_table:
            rows = stats_table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    stats[key] = value
    except Exception as e:
        print(f"Hiba a statisztikák kinyerésekor: {e}")
    
    return stats

def extract_matches(soup):
    """Mérkőzések kinyerése"""
    matches = []
    try:
        # Mérkőzések táblázatának megkeresése
        matches_table = soup.find('table', border="0", bgcolor="lightblue")
        if matches_table:
            rows = matches_table.find_all('tr')[1:]  # Az első sor a fejléc, kihagyjuk
            
            for row in rows:
                if 'bgcolor' in row.attrs and row['bgcolor'] == 'white':
                    cells = row.find_all('td')
                    if len(cells) >= 8:
                        match_data = {
                            'name': cells[0].text.strip(),
                            'license_number': cells[1].text.strip(),
                            'match_id': extract_match_id(cells[2]),
                            'opponent': cells[3].text.strip(),
                            'opponent_team': cells[4].text.strip(),
                            'result': cells[5].text.strip(),
                            'round': cells[6].text.strip(),
                            'date': cells[7].text.strip()
                        }
                        matches.append(match_data)
    except Exception as e:
        print(f"Hiba a mérkőzések kinyerésekor: {e}")
    
    return matches

def extract_match_id(cell):
    """Mérkőzés azonosító kinyerése"""
    try:
        link = cell.find('a')
        if link and 'href' in link.attrs:
            href = link['href']
            match = re.search(r'id=(\d+)', href)
            if match:
                return match.group(1)
        return cell.text.strip()
    except:
        return "Ismeretlen"

def print_player_stats(player_info):
    """Játékos statisztikák szép megjelenítése"""
    print("=" * 60)
    print("JÁTÉKOS STATISZTIKÁK")
    print("=" * 60)
    print(f"Név: {player_info['name']}")
    print(f"Engedély szám: {player_info['license_number']}")
    print()
    
    print("Összesített statisztikák:")
    print("-" * 60)
    for key, value in player_info['stats'].items():
        print(f"{key}: {value}")
    print()
    
    print(f"Mérkőzések (összesen: {len(player_info['matches'])}):")
    print("-" * 60)
    for i, match in enumerate(player_info['matches'], 1):
        print(f"{i}. {match['date']} - {match['opponent']} ({match['opponent_team']})")
        print(f"   Eredmény: {match['result']}, Forduló: {match['round']}, Meccs ID: {match['match_id']}")
    print()

def export_to_csv(player_info,path):
    """Adatok exportálása CSV fájlokba"""
    # Statisztikák exportálása
    stats_df = pd.DataFrame([{
        'Név': player_info['name'],
        'Engedély_szám': player_info['license_number'],
        **player_info['stats']
    }])
    directory = os.path.dirname(f"{path}/")
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    name=player_info["name"].lower().replace(" ","_")
    stats_df.to_csv(f'{path}/{name}_{player_info["license_number"]}_stat.csv', index=False, encoding='utf-8')
    
    # Mérkőzések exportálása
    matches_df = pd.DataFrame(player_info['matches'])
    matches_df.to_csv(f'{path}/{name}_{player_info["license_number"]}_matches.csv', index=False, encoding='utf-8')


def main():
    with open('test/jatekos.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
# Adatok kinyerése
    player_info = extract_player_stats(html_content)

    # Eredmények megjelenítése
    print_player_stats(player_info)

    # CSV exportálás
    export_to_csv(player_info,"test/player")

if __name__ == "__main__":
    main()