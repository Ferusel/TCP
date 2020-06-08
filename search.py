# Search() object allows you to:
# 1) Given a set of ingredients, cuisine and mealtype, return the link for allrecipes, seriouseats, or foodnetwork's search gallery
# 2) Given a search gallery link, return a list containing info for the recipes for a given search gallery link, including the:
# title, recipe link (absolute), image
# of the recipe
# allRecipes & foodnetwork returns 5 recipes, seriouseats returns 10
from requests_html import HTML, HTMLSession
from domain import *
from bs4 import BeautifulSoup
import requests
import random
from recipe_scrapers import scrape_me
import numpy as np
from fuzzywuzzy import fuzz

# because seriouseats and foodnetwork may not return 5 and 6 recipes respectively, I decided to make allrecipes the catch-all in-case there are additional slots to be filled up. As such, seriouseats and foodnetwork search will be run first, and any remaining recipes to be filled will be filled by allrecipes.
class Search():
    
    def __init__(self, ingredients, cuisine, mealtype, follow_strictly):
        self.ingredients = ingredients
        self.cuisine = cuisine
        self.mealtype = mealtype
        self.follow_strictly = follow_strictly
        self.search_id = ""
        self.link = ""
        self.recipe_count = 21
        self.PAGE_LIMIT = 20
    
    # address bug where if there is a space between ingredients (eg. "chicken thigh")
    # returns an array containing ingredients as each element
    def remove_whitespace(self, replacement):
        ingredients_for_link = []
        for ing in range(len(self.ingredients)):
            if ' ' in self.ingredients[ing]:
                ingredients_for_link.append(self.ingredients[ing].replace(' ', replacement))
            else:
                ingredients_for_link.append(self.ingredients[ing])
        return ingredients_for_link

    def allRecipes_link(self, page_num):
        ingredients_for_link = self.remove_whitespace('%20')
        self.search_id = "%20".join(ingredients_for_link + [self.cuisine, self.mealtype])
        self.link = f"https://www.allrecipes.com/search/results/?wt={self.search_id}&sort=re&page={page_num}"

        return self.link

    # improvement/bug: if only 1 ingredient, it's hard to return any recipes, eg. "asian dinner potato". more recipes are returned if you just search the ingredient and omit the "asian dinner", so for seriousEats_link, if len(ingredients) is only 1, then only include the ingredient in the search link.
    # if only 1 ingredient, a special URL is returned linking to the ingredient/topic for seriouseats. should return another type of URL in this case to allow for pagination (for infinite scroll, yet to be implemented).
    # grab the header, grab the link from there, then add pagination feature
    def seriousEats_link(self, page_num):
        ingredients_for_link = self.remove_whitespace('+')
        if len(self.ingredients) == 1:
            # pagination
            self.search_id = ingredients_for_link[0]
            tmp = f"https://www.seriouseats.com/search?term={self.search_id}&site=recipes"
            self.link = requests.head(tmp).headers['location']
            self.link = f"{self.link}?page={page_num}#recipes"
        else:
            self.search_id = "+".join(ingredients_for_link + [self.cuisine, self.mealtype])
            self.link = f"https://www.seriouseats.com/search?term={self.search_id}&site=recipes"
        
        return self.link

    def foodNetWork_link(self, page_num):
        ingredients_for_link = self.remove_whitespace('-')
        self.search_id = "-" + "-".join(ingredients_for_link + [self.cuisine, self.mealtype]) + "-"
        self.link = f"https://www.foodnetwork.com/search/{self.search_id}/p/{page_num}/CUSTOM_FACET:RECIPE_FACET"

        return self.link

    # returns 10 allrecipes recipes
    def search_allRecipes(self):
        info = []
        counter = 0
        page_num = 1

        while True:
            print(f'==== TRAWLING ALLRECIPES ====')
            print(f'now trawling page {page_num}')
            print(f'counter is now {counter}')
            
            # generate link, soup for that page number
            self.link = self.allRecipes_link(page_num)
            source = requests.get(self.link).text
            soup = BeautifulSoup(source, 'lxml')

            # search through each recipe
            for recipe in soup.find_all("article", class_="fixed-recipe-card"):
                recipe_link = recipe.find('a').get('href')
                print(recipe_link)
                # test for recipe strictness
                if (self.follow_strictly == True):
                    if (self.is_strict(recipe_link, self.ingredients) == True):
                        title = recipe.find("span", class_="fixed-recipe-card__title-link").text
                        image = recipe.find('img', attrs={"data-lazy-load": True} ).get('data-original-src')
                        info.append({'title': title, 'recipe_link': recipe_link, 'image': image})
                        counter += 1
                        self.recipe_count -= 1
                        print('recipe added!')

                # if recipe doesn't need to be strict
                else:
                    title = recipe.find("span", class_="fixed-recipe-card__title-link").text
                    image = recipe.find('img', attrs={"data-lazy-load": True} ).get('data-original-src')
                    info.append({'title': title, 'recipe_link': recipe_link, 'image': image})
                    counter += 1
                    self.recipe_count -= 1
                    print('recipe added!')

                # check if remaining recipe slots are filled up to 21
                if (not self.recipe_count):
                    print("==== ALLRECIPES COMPLETE ====")
                    return info
            page_num += 1

    
    # returns 6 foodnetwork recipes
    # manual pagination used!
    def search_foodNetWork(self):
        info = []
        counter = 0
        page_num = 1

        # automatically exits if page limit is too high
        while (page_num != self.PAGE_LIMIT):
            print(f'==== TRAWLING FOODNETWORK ====')
            print(f'now trawling page {page_num}')
            print(f'counter is now {counter}')

            # generate link, soup for that page number
            self.link = self.foodNetWork_link(page_num)
            source = requests.get(self.link).text
            soup = BeautifulSoup(source, 'lxml')

            # search through each recipe
            for recipe in soup.find_all('section', class_='o-RecipeResult o-ResultCard'):
                recipe_link = "https:" + recipe.find('h3', class_="m-MediaBlock__a-Headline").find('a').get('href')
                print(recipe_link)
                # test for recipe strictness
                if (self.follow_strictly == True):
                    if (self.is_strict(recipe_link, self.ingredients) == True):
                        title = recipe.find('span', class_='m-MediaBlock__a-HeadlineText').text
                        try:
                            image = "https:" + recipe.find('img').get('src')
                        except Exception as e:
                            image = "https://homepages.cae.wisc.edu/~ece533/images/fruits.png"
                        info.append({'title': title, 'recipe_link': recipe_link, 'image': image})
                        counter += 1
                        self.recipe_count -= 1
                        print("recipe found!")

                # if recipe doesn't need to be strict        
                else:
                    title = recipe.find('span', class_='m-MediaBlock__a-HeadlineText').text
                    try:
                        image = "https:" + recipe.find('img').get('src')
                    except Exception as e:
                        image = "https://homepages.cae.wisc.edu/~ece533/images/fruits.png"
                    info.append({'title': title, 'recipe_link': recipe_link, 'image': image})
                    counter += 1
                    self.recipe_count -= 1
                    print("recipe found!")

                # check if counter is at 6
                if (counter == 6):
                    print("==== FOODNETWORK COMPLETE ====")
                    return info
            page_num += 1
        print("==== EXIT FOODNETWORK, PAGE_NUM EXCEEDED ====")
        return info
    # returns 5 seriouseats recipes
    # seriouseats will return another kind of URL if it's just 1 ingredient being searched. in this case, should reprocess url to allow for pagination.
    def search_seriousEats(self):
        info = []
        counter = 0
        page_num = 1

        # automatically exits if page limit is too high
        while (page_num != self.PAGE_LIMIT):
            print(f'==== TRAWLING SERIOUSEATS ====')
            print(f'now trawling page {page_num}')
            print(f'counter is now {counter}')

            # generate link, soup for that page number
            self.link = self.seriousEats_link(page_num)
            source = requests.get(self.link).text
            soup = BeautifulSoup(source, 'html.parser')
            
            # search through each recipe if ingredients > 1
            if len(self.ingredients) > 1:
                for recipe in soup.find_all('div', class_='module'):
                    recipe_link = recipe.find('a', class_='module__link').get('href')
                    if (recipe_link[36:42] == 'topics'):
                        continue
                    else:
                        print(recipe_link)
                        # test for strictness
                        if (self.follow_strictly == True):
                            if (self.is_strict(recipe_link, self.ingredients) == True):
                                scraper = scrape_me(recipe_link)
                                title = scraper.title()
                                image = scraper.image()
                                info.append({'title': title, 'recipe_link': recipe_link, 'image': image})
                                counter += 1
                                self.recipe_count -= 1
                                print("recipe found!")

                        # if recipe doesn't need to be strict
                        else:
                            scraper = scrape_me(recipe_link)
                            title = scraper.title()
                            image = scraper.image()
                            info.append({'title': title, 'recipe_link': recipe_link, 'image': image})
                            counter += 1
                            self.recipe_count -= 1
                            print("recipe found!")
                        
                        # test if counter is at 5
                        if (counter == 5):
                            print("==== SERIOUSEATS COMPLETE ====")
                            return info

            elif len(self.ingredients) == 1:
                for recipe in soup.find_all('h4', class_='c-card__title'):
                    recipe_link = recipe.find('a', class_='o-link-wrapper').get('href')
                    if (recipe_link[36:42] == 'topics'):
                        continue
                    else:
                        print(recipe_link)
                        # test for strictness
                        if (self.follow_strictly == True):
                            if (self.is_strict(recipe_link, self.ingredients) == True):
                                scraper = scrape_me(recipe_link)
                                title = scraper.title()
                                image = scraper.image()
                                info.append({'title': title, 'recipe_link': recipe_link, 'image': image})
                                counter += 1
                                self.recipe_count -= 1
                                print("recipe found!")

                        # if recipe doesn't need to be strict
                        else:
                            scraper = scrape_me(recipe_link)
                            title = scraper.title()
                            image = scraper.image()
                            info.append({'title': title, 'recipe_link': recipe_link, 'image': image})
                            counter += 1
                            self.recipe_count -= 1
                            print("recipe found!")
                        
                        # test if counter is at 5
                        if (counter == 5):
                            print("==== SERIOUSEATS COMPLETE ====")
                            return info
        print("==== EXIT FOODNETWORK, PAGE_NUM EXCEEDED ====")
        return info


    # returns a list of 21 dictionaries shaped 3x7, each containing info from different websites, recipes from websites randomly shuffled
    # remember the use of recipe_count!
    # to check if this works, input only 1 ingredient (Chicken)
    def search_all(self):
        tmp = []
        tmp.append(self.search_seriousEats())
        tmp.append(self.search_foodNetWork())
        tmp.append(self.search_allRecipes())
        
        info = [j for sub in tmp for j in sub]
        random.shuffle(info)
        return info

    # returns true if all specified ingredients is in the ingredients list for a given recipe, else returns false
    def is_strict(self, link, specified_ing):
        counter = 0
        recipe = scrape_me(link)
        recipe_ing = recipe.ingredients()
        for i in range(len(specified_ing)):
            for j in range(len(recipe_ing)):
                score = fuzz.token_set_ratio(specified_ing[i], recipe_ing[j])
                if (score > 50) or (specified_ing[i] in recipe_ing[j]):
                    counter += 1
                    break
        if (counter == len(specified_ing)):
            return True
        return False
        
ingredients = ['chicken']
cuisine = 'asian'
mealtype = 'breakfast'
follow_strictly = True

a = Search(ingredients, cuisine, mealtype, follow_strictly)
# info = a.search_allRecipes()
# print(info)
# print(len(info))

link = a.allRecipes_link(1)
print(link)