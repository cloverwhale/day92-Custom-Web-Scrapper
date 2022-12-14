from bs4 import BeautifulSoup as bs
import requests
import argparse

DEFAULT_SEARCH_KEYWORD = "scone"
SOURCE_URL = "https://www.allrecipes.com/search"
DATA_COUNT = 3
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win63; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br"
}
HTML_PASER = "html.parser"


class WebScrapper:

    def __init__(self, **kargs) -> None:
        self.search_phrase = kargs["search_phrase"]
        self.recipe_count = kargs["number"]
        self.default_count = DATA_COUNT

    def get_search_result(self):
        search_result = self.get_request(url=SOURCE_URL, params={"q": self.search_phrase})
        search_result_soup = bs(search_result.text, HTML_PASER)

        recipe_cards = search_result_soup.find_all("a", class_="mntl-card-list-items")
        return [item.get("href") for item in recipe_cards if "/recipe/" in item.get("href")]

    def get_recipe(self):

        links = self.get_search_result()
        number_of_output = self.recipe_count if self.recipe_count < len(links) else self.default_count

        for item in links[:number_of_output]:

            file_name=item.split("/")[-2]

            # get recepie data
            recipe_page = self.get_request(url=item, params={"print":""})
            recipe_page_soup = bs(recipe_page.text, HTML_PASER)
            article = recipe_page_soup.find("article", id="allrecipes-article_1-0")
            title = article.select("h1")[0]
            subtitle = article.select("p#article-subheading_2-0")[0]
            recipie = article.select("div#article-content_1-0")[0]

            # remove all buttons
            for button in recipie.select("button"):
                button.decompose()
    
            # reconstruct html page
            title_with_link=recipe_page_soup.new_tag("a")
            title_with_link["href"] = item
            title_with_link.append(title)
            new_soup = bs(str(title_with_link), HTML_PASER)
            new_soup.append(subtitle)
            new_soup.append(recipie)
        
            self.write_to_html(file_name=file_name, recipe_soup=new_soup)

    def write_to_html(self, file_name, recipe_soup):
        print(file_name)
        html = recipe_soup.prettify("utf-8")
        with open(f"{file_name}.html", "wb") as file:
            file.write(html)

    def get_request(self, **kargs):
        return requests.request("GET", kargs["url"], params=kargs["params"], headers=HEADERS)


if __name__ == "__main__":

    # get parameters from user
    parser = argparse.ArgumentParser(description="Search recipes by given a keyword")
    parser.add_argument("-s", "--search", type=str, help="search key word", default=DEFAULT_SEARCH_KEYWORD)
    parser.add_argument("-n", "--number", type=int, help="number of recipes to save", default=DATA_COUNT)
    args = parser.parse_args()

    ws = WebScrapper(search_phrase=args.search, number=args.number)
    links = ws.get_recipe()
