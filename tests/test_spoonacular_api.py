from spoonacular_api.spoonacular_api import GroceryList
import pandas as pd

API_Key = '98d4afc5d8f34efbbea6ccda53a7f965'

test = GroceryList('username', 'firstname', 'lastname', 'user@email.com', API_Key)

def test_searchRecipe():
    data = {'Recipe': ['Spinach Soup With Wontons', 'The Best Quinoa Minsetrone', 'Pomegranate Soup (Ash-E Anar)'], 
            'Servings': [4, 8, 6], 
            'Price Per Serving': [2.43, 2.92, 2.05],
            'Recipe ID': [661351, 663227, 656635]}
    df = pd.DataFrame(data)
    df2 = test.searchRecipe('soup', 'chicken', 'spinach', 'pepper')
    assert df.equals(df2)
