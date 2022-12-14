import requests
import json
import pandas as pd

class GroceryList():
    """
    This class takes in the user's credentials, generates a username and hash that allows the user to perform recipe searches, finds ingredients, and 
    creates shopping lists.

    Parameters
    ----------
    username : str
            The username of the user.
    firstName : str
            The first name of the user.
    lastName : str
            The last name of the user.
    email : str
            The email address of the user.
    API_Key : str
            The API Key the user obtained from spoonacular.com/food-api
    """

    def __init__(self, username, firstName, lastName, email, API_Key):
        assert isinstance(username, str), f'username must a string but username = {username}'
        assert isinstance(firstName, str), f'firstNname must a string but firstName = {firstName}'
        assert isinstance(lastName, str), f'lastName must a string but lastName = {lastName}'
        assert isinstance(email, str), f'email must a string but email = {email}'
        assert isinstance(API_Key, str), f'API_Key must a string but API_Key = {API_Key}'
        endpoint = 'https://api.spoonacular.com/users/connect'
        headers = {'Content-Type': 'application/json'}
        user_cred = requests.post(f'{endpoint}?apiKey={API_Key}', headers = headers, data = json.dumps({
            "username": username,
            "firstName": firstName,
            "lastName": lastName,
            "email": email
        }))
        if user_cred.status_code == 401:
                raise Exception('Not authorized, please check API Key')
        user_cred_json = user_cred.json()
        self.username = user_cred_json['username']
        self.hash = user_cred_json['hash']
        self.API_Key = API_Key
        
    def searchRecipe(self, query, *includeIngreds):
        """Search for recipes. 

        It searches for recipes depending on the user's input of query and includeIngreds parameters and returns the top 5 recipes sorted by 
        popularity in the form of a dataframe. 

        Parameters
        ----------
        query : str
                The type of recipe the user wants to search for.
        *includeIngreds : str or tuple of str, optional
                Any specific ingredients the user wants to include in the recipe, separated by comma.

        Returns
        -------
        pandas.core.frame.DataFrame
                The dataframe that contains the recipe names, servings, price per serving, and recipe IDs.

        Examples
        --------
        >>> recipe.searchRecipe('soup', 'chicken', 'carrot')
                Recipe	                                        Servings	Price Per Serving       Recipe ID
        0	Red Lentil Soup with Chicken and Turnips        8	        2.77	                715415
        1	Chipotle Black Bean Soup with Avocado Cream	8	        1.43	                638741
        2	Chicken Mulligatawny Soup		        6	        2.48	                638199
        3	Classic Matzo Ball Soup		                6	        2.07	                639616
        4	Light Greek Lemon Chicken Orzo Soup		8	        2.37	                1098350
        """
        assert isinstance(query, str), f'query must a string but query = {query}'
        if not all(isinstance(v, str) for v in includeIngreds):
                raise Exception('Ingredients must be in strings')
        headers = {'Content-Type': 'application/json'}
        API_Key = self.API_Key
        endpoint = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_Key}&query={query}&includeIngredients={includeIngreds}&addRecipeInformation=true&sort=popularity&number=5'
        search = requests.get(endpoint, headers = headers).json()
        df = pd.DataFrame(columns = ['Recipe', 'Servings', 'Price Per Serving', 'Recipe ID'])
        for recipe in search['results']:
            name = recipe['title']
            servings = recipe['servings']
            PPS = recipe['pricePerServing']
            id = recipe['id']
            df.loc[len(df.index)] = [name, servings, round(PPS/100,2), id]
        return df
    
    def getIngredients(self, recipeID):
        """Search for ingredients of a recipe. 

        It searchs for the ingredients of a recipe of the user's choosing. The user needs to input the recipe ID which can be obtained from the
        searchRecipe method. 

        Parameters
        ----------
        recipeID : int
                The recipe ID for which the user wants to get the ingredients for.

        Returns
        -------
        pandas.core.frame.DataFrame
                The dataframe that contains the ingredients and the amounts needed.

        Examples
        --------
        >>> recipe.getIngredients(638741)
                Ingredient	                        Amount	    Unit
        0	avocado	                                1.000	    small
        1	canned black beans	                1.276	    kgs
        2	diced carrots	                        256.000	    g
        3	chicken broth	                        940.000	    ml
        4	canned chipotle peppers in adobo	198.447	    g
        5	fresh cilantro leaves	                2.000	    Tbsps
        6	lemon juice	                        1.000	    Tbsp
        7	olive oil	                        2.000	    Tbsps
        8	diced onions	                        320.000	    g
        9	sour cream	                        57.500	    ml
        """
        assert isinstance(recipeID, int), f'recipeID must be an integer but recipeID is a string'
        headers = {'Content-Type': 'application/json'}
        API_Key = self.API_Key
        endpoint = f'https://api.spoonacular.com/recipes/{recipeID}/ingredientWidget.json?apiKey={API_Key}'
        get_ingred = requests.get(endpoint, headers=headers).json()
        ingred_df = pd.DataFrame(columns = ['Ingredient', 'Amount', 'Unit'])
        for ingredient in get_ingred['ingredients']:
            name = ingredient['name']
            value = ingredient['amount']['metric']['value']
            unit = ingredient['amount']['metric']['unit']
            ingred_df.loc[len(ingred_df.index)] = [name, value, unit]
        return ingred_df
    
    def addIngredient(self, ingred, amount, unit):
        """Add individual ingredients. 

        It lets the user add specific ingredients to the shopping list by the user's input of ingredient name, amount, and the unit of the amount. 

        Parameters
        ----------
        ingred : str
                The ingredient the user wants to add to the shopping list.
        amount : int or float
                The amount of the ingredient needed.
        unit : str
                The unit of the amount (g, ml, oz, tbs, etc).

        Returns
        -------
        pandas.core.frame.DataFrame
                The shopping list dataframe that contains the ingredients, amounts needed, the cost, and the item IDs.

        Examples
        --------
        >>> recipe.addIngredient('chicken broth', 940, 'ml')
        Shopping list
                Item	        Amount      Unit        Cost (USD)      Item ID
        0	chicken broth	940.0	    ml	        3.0	        1400323
        1	Total cost		                3.0	

        >>> recipe.addIngredient('diced carrots', 256, 'g')
        Shopping list
                Item	        Amount	    Unit	Cost (USD)      Item ID
        0	chicken broth	940.0	    ml	        3.00	        1400323
        1	diced carrots	256.0	    g	        0.45	        1400325
        2	Total cost			        3.45	

        """
        assert isinstance(ingred, str), f'ingred must a string but ingred = {ingred}'
        assert isinstance(amount, (int,float)), f'amount must an int or float but amount is a string'
        assert isinstance(unit, str), f'unit must a string of the unit (g, kg, oz, tbs, etc) but unit = {unit}'
        headers = {'Content-Type': 'application/json'}
        API_Key = self.API_Key
        username = self.username
        hash = self.hash
        endpoint = f'https://api.spoonacular.com/mealplanner/{username}/shopping-list/items?apiKey={API_Key}&hash={hash}'
        add_ingred = requests.post(endpoint, headers=headers, data=json.dumps({
            'item': f'{amount} {unit} {ingred}',
            'parse': True
        }))
        return self.getShoppingList()
        
    def addAllIngredients(self, recipeID):
        """Add all ingredients. 

        It lets the user add all the ingredients of a recipe to the shopping list. 

        Parameters
        ----------
        recipeID : int
                The recipe ID for which the user wants to add the ingredients to the shopping list for.

        Returns
        -------
        pandas.core.frame.DataFrame
                The shopping list dataframe that contains the ingredients, amounts needed, the cost, and the item IDs.

        Examples
        --------
        >>> recipe.addAllIngredients(638741)
        Shopping list
                Item	                                Amount          Unit            Cost (USD)	Item ID
        0	canned black beans	                1.276	        kg	        2.28	        1400329
        1	chicken broth	                        940.0	        ml	        3.00	        1400333
        2	canned chipotle peppers in adobo        198.447	        g	        1.98	        1400335
        3	sour cream	                        57.5	        ml	        0.38	        1400345
        4	olive oil	                        2.0	        Tbsps	        0.33	        1400341
        5	avocado	                                1.0	        small	        1.50	        1400327
        6	diced carrots	                        256.0	        g	        0.45	        1400331
        7	fresh cilantro leaves	                2.0	        bsps	        0.03	        1400337
        8	lemon juice	                        1.0	        Tbsp	        0.10	        1400339
        9	diced onions	                        320.0	        g	        0.70	        1400343
        10	Total cost			                                        10.76	
        """
        assert isinstance(recipeID, int), f'recipeID must an integer but recipeID is a string'
        headers = {'Content-Type': 'application/json'}
        API_Key = self.API_Key
        hash = self.hash
        username = self.username
        getIngred_endpoint = f'https://api.spoonacular.com/recipes/{recipeID}/ingredientWidget.json?apiKey={API_Key}'
        addIngred_endpoint = f'https://api.spoonacular.com/mealplanner/{username}/shopping-list/items?apiKey={API_Key}&hash={hash}'
        get_ingred = requests.get(getIngred_endpoint, headers = headers).json()
        for ingredient in get_ingred['ingredients']:
            name = ingredient['name']
            value = ingredient['amount']['metric']['value']
            unit = ingredient['amount']['metric']['unit']
            requests.post(addIngred_endpoint, headers=headers, data=json.dumps({
                'item': f'{value} {unit} {name}',
                'parse': True 
            }))
        return self.getShoppingList()
    
    def getShoppingList(self):
        """Get the shopping list. 

        It returns the user's shopping list in the form of a dataframe.

        Returns
        -------
        pandas.core.frame.DataFrame
                The shopping list dataframe that contains the ingredients, amounts needed, the cost, and the item IDs.

        Examples
        --------
        >>> recipe.getShoppingList()
        Shopping list
                Item	                                Amount          Unit            Cost (USD)      Item ID
        0	canned black beans	                1.276	        kg	        2.28	        1400329
        1	chicken broth	                        940.0	        ml	        3.00	        1400333
        2	canned chipotle peppers in adobo        198.447	        g	        1.98	        1400335
        3	sour cream	                        57.5	        ml	        0.38	        1400345
        4	olive oil	                        2.0	        Tbsps	        0.33	        1400341
        5	avocado	                                1.0	        small	        1.50	        1400327
        6	diced carrots	                        256.0	        g	        0.45	        1400331
        7	fresh cilantro leaves	                2.0	        bsps	        0.03	        1400337
        8	lemon juice	                        1.0	        Tbsp	        0.10	        1400339
        9	diced onions	                        320.0	        g	        0.70	        1400343
        10	Total cost			                                        10.76	
        """
        headers = {'Content-Type': 'application/json'}
        API_Key = self.API_Key
        username = self.username
        hash = self.hash
        endpoint = f'https://api.spoonacular.com/mealplanner/{username}/shopping-list?apiKey={API_Key}&hash={hash}'
        shopping_list = requests.get(endpoint, headers = headers).json()
        shopping_df = pd.DataFrame(columns = ['Item', 'Amount', 'Unit', 'Cost (USD)', 'Item ID'])
        for aisle in shopping_list['aisles']:
            for item in aisle['items']:
                name = item['name']
                amount = item['measures']['metric']['amount']
                unit = item['measures']['metric']['unit']
                cost = round(item['cost']/100,2)
                id = item['id']
                shopping_df.loc[len(shopping_df.index)] = [name, amount, unit, cost, id] 
        shopping_df.loc[len(shopping_df.index), 'Item'] = "Total cost"
        shopping_df.loc[shopping_df['Item'] == 'Total cost', 'Cost (USD)'] = round(shopping_list['cost']/100,2)
        shopping_df = shopping_df.fillna('')
        shopping_df.iloc[0:-1, 4] = shopping_df.iloc[0:-1, 4].astype(int)
        print('Shopping list')
        return shopping_df

    def deleteItem(self, *item_IDs):
        if not all(isinstance(v, int) for v in item_IDs):
                raise Exception('Item IDs must all be integers')
        """Delete items from the shopping list. 

        It lets the user delete specific ingredients from the shopping list by their item IDs. The item IDs can be obtained from the getShoppingLift method.

        Parameters
        ----------
        *item_IDs : int or tuple of int
                The item_ID(s) for the ingredients the user wants to delete from the shopping list.

        Returns
        -------
        pandas.core.frame.DataFrame
                The shopping listdataframe that contains the ingredients, amounts needed, the cost, and the item IDs without the deleted items.

        >>> recipe.deleteItem(1400329, 1400333, 1400335)
        Shopping list
                Item                            Amount          Unit            Cost (USD)      Item ID
        0	sour cream	                57.5	        ml	        0.38	        1400345
        1	olive oil	                2.0	        Tbsps	        0.33	        1400341
        2	avocado	                        1.0	        small	        1.50	        1400327
        3	diced carrots	                256.0	        g	        0.45	        1400331
        4	fresh cilantro leaves	        2.0	        bsps	        0.03	        1400337
        5	lemon juice	                1.0	        Tbsp	        0.10	        1400339
        6	diced onions	                320.0	        g	        0.70	        1400343
        7	Total cost			                                3.49	
        """
        headers = {'Content-Type': 'application/json'}
        API_Key = self.API_Key
        username = self.username
        hash = self.hash
        for item_ID in item_IDs:
            endpoint = f'https://api.spoonacular.com/mealplanner/{username}/shopping-list/items/{item_ID}?apiKey={API_Key}&hash={hash}'
            requests.delete(endpoint, headers = headers)
        return self.getShoppingList()