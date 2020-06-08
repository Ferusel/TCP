from requests_html import HTML, HTMLSession
from recipe_scrapers import scrape_me
from domain import *

class Scrape():

    def __init__(self, link):
        self.link = link
    
    def scrape_info(self):
        session = HTMLSession()
        r = session.get(self.link)
        scraper = scrape_me(self.link)
        
        # scrape information
        domain_name = get_domain_name(self.link)
        if domain_name == "allrecipes.com":
            try:
                author = r.html.find('a.author-name', first=True).text
            except AttributeError:
                author = r.html.find('div.submitter', first=True).text
        elif domain_name == "seriouseats.com":
            author = r.html.find('span.author-name', first=True).text
        elif domain_name == "foodnetwork.com":
            author = r.html.find('span.o-Attribution__a-Name', first=True).text
        title = scraper.title()
        ingredients = scraper.ingredients()
        steps = scraper.instructions().split('\n') 
        image = scraper.image()
        if (image == ''):
            image = "https://homepages.cae.wisc.edu/~ece533/images/fruits.png"

        return [title, author, ingredients, steps, image]

a = Scrape('https://www.allrecipes.com/recipe/230663/bombay-chicken-wings/').scrape_info()
b = Scrape('https://www.allrecipes.com/recipe/280246/chef-johns-tuna-noodle-casserole/?internalSource=previously%20viewed&referringContentType=Homepage').scrape_info()