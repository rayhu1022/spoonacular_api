from spoonacular_api.spoonacular_api import GroceryList
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_Key = os.getenv('API_Key')

test = GroceryList('username', 'firstname', 'lastname', 'user@email.com', API_Key)

def test_searchRecipe():
    data = {'Recipe': ['Spinach Soup With Wontons', 'The Best Quinoa Minestrone', 'Pomegranate Soup (Ash-E Anar)'], 
            'Servings': [4, 8, 6], 
            'Price Per Serving': [2.43, 2.92, 2.05],
            'Recipe ID': [661351, 663227, 656635]}
    df = pd.DataFrame(data)
    df2 = test.searchRecipe('soup', 'chicken', 'spinach', 'pepper')
    assert df.equals(df2)

def test_getIngredient():
    data = {'Ingredient': ['mushrooms', 'baby spinach', 'shallot', 'parmesan cheese', 'eggs', 'olive oil', 'butter', 'salt and pepper'], 
            'Amount': [96, 60, 2.00, 25.00, 3.00, 0.50, 0.50, 0.25], 
            'Unit': ['ml', 'g', 'Tbsps', 'g', 'large', 'Tbsps', 'Tbsps', 'tsps']}
    df = pd.DataFrame(data)
    df2 = test.getIngredients(1697687)
    assert df.equals(df2)
