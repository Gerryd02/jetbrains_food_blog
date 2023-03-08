import sqlite3
from sys import argv
import argparse

parser = argparse.ArgumentParser(description='Food Blog')
args = parser.parse_args()

parser.add_argument("--ingredients", help="look for recipes with ingredients")
parser.add_argument("--meals", help="look for recipes with meals")
parser.add_argument("", help="database name")

conn = sqlite3.connect('food_blog.db')
db = conn.cursor()

db.execute('PRAGMA foreign_keys = ON;')
db.execute('CREATE TABLE IF NOT EXISTS meals (meal_id INTEGER PRIMARY KEY, meal_name TEXT NOT NULL UNIQUE)')
db.execute('CREATE TABLE IF NOT EXISTS ingredients (ingredient_id INTEGER PRIMARY KEY, '
           'ingredient_name TEXT NOT NULL UNIQUE)')
db.execute('CREATE TABLE IF NOT EXISTS measures (measure_id INTEGER PRIMARY KEY, measure_name TEXT UNIQUE)')
db.execute('CREATE TABLE IF NOT EXISTS recipes (recipe_id INTEGER PRIMARY KEY, '
           'recipe_name TEXT NOT NULL, recipe_description)')
db.execute(''' CREATE TABLE IF NOT EXISTS serve (serve_id INTEGER PRIMARY KEY,
           meal_id INTEGER NOT NULL,
           recipe_id INTEGER NOT NULL, 
            FOREIGN KEY(meal_id) REFERENCES meals(meal_id) 
            FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id))''')
db.execute(''' CREATE TABLE IF NOT EXISTS quantity (quantity_id INTEGER PRIMARY KEY,
            measure_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id)
            FOREIGN KEY(measure_id) REFERENCES measures(measure_id)
            FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id))''')
conn.commit()
data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}


def load_meals(data):
    for meal in data.get("meals"):
        db.execute(f'INSERT INTO meals (meal_name) VALUES ("{meal}")')
        conn.commit()


def load_ingredients(data):
    for ingredient in data.get("ingredients"):
        db.execute(f'INSERT INTO ingredients (ingredient_name) VALUES ("{ingredient}")')
        conn.commit()


def load_measures(data):
    for measure in data.get("measures"):
        db.execute(f'INSERT INTO measures (measure_name) VALUES ("{measure}")')
        conn.commit()


def add_recipes():
    print('Pass the empty recipe name to exit')
    while True:
        recipe_name = input('Recipe name: ')
        if not recipe_name:
            conn.close()
            break
        recipe_description = input('Recipe description:')
        print('1) breakfast 2) brunch 3) lunch 4) supper')
        serve_at = input('When the dish can be served: ')
        recipe_id = db.execute(f'INSERT INTO recipes (recipe_name, recipe_description) VALUES ("{recipe_name}", "{recipe_description}")').lastrowid
        conn.commit()
        for _ in serve_at.split():
            print(_)
            print(recipe_id)
            db.execute(f'INSERT INTO serve(meal_id, recipe_id) VALUES ("{int(_)}", "{int(recipe_id)}")')
        conn.commit()
        get_ingredients(recipe_id)

def get_ingredients(recipe_id):
    while True:
        ingredient = input('Input quantity of ingredient <press enter to stop>: ')
        if not ingredient:
            break
        ingredient_list = ingredient.split()
        print(f'ingredient_list - {ingredient_list}')
        quantity = ingredient_list[0]
        print(f'quantity - {quantity}')
        if len(ingredient_list) == 3:
            measure = ingredient_list[1]
            ingredient = ingredient_list[2]
        else:
            measure = ""
            ingredient = ingredient_list[1]
        measure_id = query_for_id(measure, 'measures', recipe_id)
        ingredient_id= query_for_id(ingredient, 'ingredients', recipe_id)
        print(f'{measure} - {measure_id}')
        print(f'{ingredient} - {ingredient_id}')
        db.execute(f'INSERT INTO quantity(quantity, recipe_id, measure_id, ingredient_id) '
                   f'VALUES ("{int(quantity)}", "{int(recipe_id)}", "{int(measure_id)}", "{int(ingredient_id)}")')
        conn.commit()

def query_for_id(query_value, table_name, recipe_id):
    value = db.execute(f'SELECT {table_name[:-1]}_id FROM {table_name} WHERE {table_name[:-1]}_name LIKE "%{query_value}%"').fetchall()
    if len(value) == 1:
        return value[0][0]
    print(f'The {table_name[:-1]} is not conclusive')
    get_ingredients(recipe_id)


def main():
    try:
        load_meals(data)
        load_ingredients(data)
        load_measures(data)
    except sqlite3.IntegrityError:
        pass
    add_recipes()


if __name__ == "__main__":
    main()
    conn.close()
