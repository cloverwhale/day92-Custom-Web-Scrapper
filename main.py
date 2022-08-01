from bs4 import BeautifulSoup as bs
import pandas as pd
import requests

SEARCH_PHRASE = 'Egg Tarts'
SOURCE_URL = 'https://www.allrecipes.com/search/results/'
DATA_COUNT = 3
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win63; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'accept-encoding': 'gzip, deflate, br'
}
HTML_PASER = 'html.parser'
CSV_FILE_NAME = SEARCH_PHRASE.replace(' ', '') + "-recipes.csv"


def join_list_data(input_list):
    numbered_list = []
    for i in range(len(input_list)):
        numbered_list.append(f"{i + 1}. {input_list[i]}")
    return '\n'.join(numbered_list)


if __name__ == '__main__':

    search_result = requests.request('GET', SOURCE_URL, params={'search': SEARCH_PHRASE}, headers=HEADERS)
    search_result_soup = bs(search_result.text, HTML_PASER)
    recipe_cards = search_result_soup.find_all('div', class_='card__detailsContainer-left')[:DATA_COUNT]
    recipe_links = [item.a['href'] for item in recipe_cards]

    output_title = []
    output_ingredients = []
    output_steps = []

    for link in recipe_links:
        recipe_details = requests.request('GET', link, headers=HEADERS)
        recipe_details_soup = bs(recipe_details.text, HTML_PASER)

        recipe_title = recipe_details_soup.find('h1', class_='headline').get_text()
        output_title.append(recipe_title)

        ingredients_span = recipe_details_soup.find_all('span', class_='ingredients-item-name')
        ingredients = [item.get_text() for item in ingredients_span]
        ingredients_str = join_list_data(ingredients)
        output_ingredients.append(ingredients_str)

        directions_li = recipe_details_soup.find_all('li', class_='instructions-section-item')
        steps = [item.contents[3].contents[0].get_text() for item in directions_li]
        steps_str = join_list_data(steps)
        output_steps.append(steps_str)

    output_json = {
        'title': output_title,
        'ingredients': output_ingredients,
        'steps': output_steps
    }

    df = pd.DataFrame(output_json)
    df.to_csv(CSV_FILE_NAME)
