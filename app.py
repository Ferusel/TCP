from flask import Flask, flash
from flask import render_template, url_for, redirect, request
from scrape import *
from search import *
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

@app.route("/")
@app.route("/homepage")
def homepage():
    return render_template('homepage.html')

@app.route("/generalRecipes")
def generalRecipes():
    inglist = []
    cuisineType = ''
    mealtype = ''
    follow_strictly = False
    a = Search(inglist, cuisineType, mealtype, follow_strictly)
    recipes = np.array(a.search_all())
    recipes = recipes.reshape(7, 3).tolist()
    return render_template('recipes_list.html', recipes=recipes)

@app.route("/specificRecipes", methods=['GET', 'POST'])
def specificRecipes():
    if request.method == "POST":
        cuisineType = request.form.get('cuisineType')
        inglist = request.form.getlist('inglist')
        mealType = request.form.get('mealType')
        follow_strictly = bool(request.form.get('follow-strictly'))

        # test if inglist is empty
        for ing in inglist:
            if not ing:
                ing_amt = 3
                error = "Don't leave the ingredients field empty. Update if needed!"
                return render_template('ingredientSelection.html', error=error, ing_amt=ing_amt)
        # test if cuisineType or mealType is empty
        if (not cuisineType):
            ing_amt = 3
            error = "Please choose a cuisine!"
            return render_template('ingredientSelection.html', error=error, ing_amt=ing_amt)
        elif (not cuisineType):
            ing_amt = 3
            error = "Please choose a meal type!"
            return render_template('ingredientSelection.html', error=error, ing_amt=ing_amt)

        a = Search(inglist, cuisineType, mealType, follow_strictly)
        recipes = np.array(a.search_all())
        recipes = recipes.reshape(7, 3).tolist()
        return render_template('recipes_list.html', recipes=recipes)
    return redirect(url_for('ingredientSelection'))

@app.route("/ingredientSelection", methods=['GET', 'POST'])
def ingredientSelection():
    error = None
    ing_amt = 3
    if (request.method == 'POST'):
        try:
            ing_amt = (int)(request.form['ing_amt'])
        except ValueError:
            error = "Please enter an integer value!"
        else:
            if not (ing_amt < 6):
                error = "You can only choose a maximum of 5 ingredients!"
                ing_amt = 3
            elif not (ing_amt > 0):
                error = "Please enter at least 1 ingredient!"
                ing_amt = 3
            else:
                flash('Ingredient amount updated!')
                return render_template('ingredientSelection.html', ing_amt=ing_amt)
    return render_template('ingredientSelection.html', error=error, ing_amt=ing_amt)

@app.route("/recipePage", methods=['GET', 'POST'])
def recipePage():
    if (request.method == 'POST'):
        link = request.form['link']
        info = Scrape(link).scrape_info()
        title, author, ingredients, steps, image = info[0], info[1], info[2], info[3], info[4]
        return render_template('recipePage.html', title=title, author=author, ingredients=ingredients, steps=steps, image=image, link=link)
    return redirect(url_for('homepage'))

@app.route("/about")
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)