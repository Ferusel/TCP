from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class IngredientsForm(FlaskForm):

    def __init__(self, ing_amt):
        self.ing_amt = ing_amt
    
    ingredients = {}
    for ing in range(ing_amt):
        d["ing{0}".format(ing)] = StringField('Ingredient', validators=[DataRequired()])
    cuisineType = SelectField('cuisineType', choices=['Chinese', 'Indian', 'Mexican'])
    
    submit = SubmitField("Submit Ingredients")
