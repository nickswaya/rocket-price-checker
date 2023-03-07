import pandas as pd
import requests
from bs4 import BeautifulSoup


PLATFORM = {
    "pc": 1,
    "psn": 2,
    "xbox": 3,
    "switch": 4
}

SLOT = {
    "Topper": "toppers",
    "Player Banner": "banners",
    "Decal": "decals",
    "Engine Audio": "engine_sounds",
    "Antenna": "antennas",
    "Rocket Boost": "boosts",
    "Animated Decal": "decals",
    "Avatar Border": "avatar_borders",
    "Trail": "trails",
    "Goal Explosion": "goal_explosions",
    "Body": "cars",
    "Paint Finish": "paint_finishes",
    "Wheels": "wheels"
}

COLORS = {
    "Lime": "lime",
    "Saffron": "saffron",
    "Crimson": "crimson",
    "Cobalt": "cobalt",
    "Purple": "purple",
    "Titanium White": "white",
    "Black": "black",
    "Sky Blue": "sblue",
    "Burnt Sienna": "sienna",
    "Forest Green": "fgreen",
    "Grey": "grey",
    "Pink": "pink",
    "Orange": "orange"
}

SPECIAL_EDITION = {
    "Edition_Holographic": "holographic",
    "Edition_Inverted": "inverted",
    "Edition_Remixed": "remixed",
    "Edition_Infinite": "infinite"
}

platform = PLATFORM['pc']


def read_filter_df(csv_path='inventory.csv'):
    inventory = pd.read_csv(csv_path, on_bad_lines='skip')
    tradeable = inventory[inventory["tradeable"]].reset_index(drop=True)
    non_blueprints = tradeable[tradeable[" blueprint cost"] == 0]
    return non_blueprints


def create_url(row, platform='pc'):
    base_url = f'https://rl.insider.gg/en/{platform}/'
    if row['slot'] == 'Decal':
        try:
            url = base_url + 'decals/' + row['name'].split(':')[0].lower() + '/' + row['name'].split(':')[1].lower().replace(' ', '_').replace('-', '_')[1:]
            if row['specialedition'] != 'none':
                url += f'/{SPECIAL_EDITION[row["specialedition"]]}'
            if row['paint'] != 'none':
                url += f'/{COLORS[row["paint"]]}'
            return url
        except:
            print(row)

    url = base_url + SLOT[row['slot']] + '/'
    if ':' in row['name']:
        url += row['name'].split(':')[0].lower().replace('-', '_').replace(' ', '_') + '/' + row['name'].split(':')[1].lower().replace(' ', '_').replace('-', '_').replace('_', '')
    else:
        url += row['name'].lower().replace('-', '_').replace(' ', '_')

    if row['specialedition'] != 'none':
        url += f'/{SPECIAL_EDITION[row["specialedition"]]}'
    if row['paint'] != 'none':
        url += f'/{COLORS[row["paint"]]}'
    return url


def get_price(url):
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')
    try:
        price_matrix = soup.find('table', {"class": "priceVariantsMatrix"})
        matrix_row = price_matrix.find('tr', {"id": "matrixRow0"}).find_all('td')
        return matrix_row[platform].text
    except:
        print(url)
    

def transform_price(price):
    try:
        avg = (int(price.split('-')[0]) + int(price.split('-')[1])) / 2
    except:
        avg = 0
    return avg


def transform_df(df, test=True):
    df['url'] = df.apply(lambda x: create_url(x), axis=1)
    if test:
        df = df.head(200)
    df['price'] = df['url'].apply(lambda x: get_price(x))
    df['price_avg'] = df['price'].apply(lambda x: transform_price(x))
    df = df.sort_values(by='price_avg', ascending=False)
    df.to_csv('output_df.csv')


if __name__ == "__main__":
    transform_df(read_filter_df(), test=False)

