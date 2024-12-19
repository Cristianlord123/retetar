import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
from pathlib import Path

class RecipeFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Finder")
        self.root.geometry("800x600")
        
        # Initialize database
        self.setup_database()
        
        # Current ingredients list
        self.current_ingredients = []
        
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Left panel - Ingredients
        left_panel = ttk.LabelFrame(main_frame, text="Ingredients", padding="5")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=5)
        
        # Ingredient input
        self.ingredient_var = tk.StringVar()
        ingredient_entry = ttk.Entry(left_panel, textvariable=self.ingredient_var)
        ingredient_entry.grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(left_panel, text="Add", command=self.add_ingredient).grid(row=0, column=1, padx=5)
        
        # Ingredients listbox
        self.ingredients_listbox = tk.Listbox(left_panel, height=15)
        self.ingredients_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        ttk.Button(left_panel, text="Remove Selected", command=self.remove_ingredient).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Right panel - Recipes
        right_panel = ttk.LabelFrame(main_frame, text="Recipes", padding="5")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=5)
        
        # Search button
        ttk.Button(right_panel, text="Find Recipes", command=self.search_recipes).grid(row=0, column=0, pady=5)
        
        # Recipe results
        self.recipe_text = tk.Text(right_panel, wrap=tk.WORD, width=40, height=20)
        self.recipe_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
    def setup_database(self):
        #   Create database connection
        self.conn = sqlite3.connect(':memory:')  # Using in-memory database for this example
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY,
                name TEXT,
                instructions TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY,
                recipe_id INTEGER,
                ingredient TEXT,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        
        # Add sample recipes
        sample_recipes = [
            {
                "name": "Pasta",
                "ingredients": ["pasta", "tomato sauce", "cheese"],
                "instructions": "1. Cook pasta according to package\n2. Heat tomato sauce\n3. Combine and top with cheese"
            },
            {
                "name": "Basic Omelette",
                "ingredients": ["eggs", "milk", "cheese"],
                "instructions": "1. Beat eggs with milk\n2. Cook in pan\n3. Add cheese and fold"
            },
            {
                "name": "Grilled Cheese",
                "ingredients": ["bread", "cheese", "butter"],
                "instructions": "1. Butter bread slices\n2. Add cheese between slices\n3. Grill until golden"
            },
            {
                "name":"Pizza",
                "ingredients": ["pizza dought", "tomato sauce", "cheese", "toppings"],
                "instructions": "1. Make pizza dought\n2. Add tomato sauce\n3. Add cheese \n4. Add toppings\n5. bake in oven"
            },
            {
                "name": "fries",
                "ingredients": ["potatoes","oil","salt"],
                "instructions": "1.cut potatoes\n2.fry in oil\n3.add salt"
            },
            {
                "name": "rice",
                "ingredients": ["rice","water","salt"],
                "instructions": "1.cook rice\n2.add water\n3.add salt"
            },
            {
                "name": "burrito",
                "ingredients": ["tortilla","cheese","ham","lettuce","tomato","mayonnaise"],
                "instructions": "1.cook rice\n2.add water\n3.add salt"
            },
            {
                "name": "shaorma",
                "ingredients": ["chicken","lettuce","tomato","mayonnaise","ketchup","cucumber","wrap","fries"],
                "instructions": "1.cook chicken\n2.add wrap\n3.add fries\n4.add cooked chicken\n5.add lettuce\n5.add ketchup/mayonnaise\n6.add tomato\n7.add cucumber"
            },
            {
                "name": "burger",
                "ingredients": ["bun","lettuce","tomato","mayonnaise","ketchup","cheese","beef"],
                "instructions": "1.cook beef\n2.add bun\n3.add lettuce\n4.add beef\n5.add cheese\n6.add ketchup/mayonnaise\n7.add tomato"
            },
            {  
                "name": "pie",
                "ingredients": ["dought","fruit","sugar","water"],
                "instructions": "1.make dought\n2.add fruit\n3.add sugar\n4.add water\n5.bake in oven"
            },
            { 
                "name": "lasagna",
                "ingredients": ["mozzarella","tomato sauce","spices","cheese","onion","garlic","beef"],
                "instructions": "1.cook beef\n2.add spices\n3.add tomato sauce\n4.add cheese\n5.add onion\n6.add garlic\n7.add mozzarella"
            },            
        ]
        
        for recipe in sample_recipes:
            self.cursor.execute('INSERT INTO recipes (name, instructions) VALUES (?, ?)',
                              (recipe['name'], recipe['instructions']))
            recipe_id = self.cursor.lastrowid
            
            for ingredient in recipe['ingredients']:
                self.cursor.execute('INSERT INTO ingredients (recipe_id, ingredient) VALUES (?, ?)',
                                  (recipe_id, ingredient.lower()))
        
        self.conn.commit()
    
    def add_ingredient(self):
        ingredient = self.ingredient_var.get().strip().lower()
        if ingredient and ingredient not in self.current_ingredients:
            self.current_ingredients.append(ingredient)
            self.ingredients_listbox.insert(tk.END, ingredient)
            self.ingredient_var.set("")  # Clear input
    
    def remove_ingredient(self):
        selection = self.ingredients_listbox.curselection()
        if selection:
            ingredient = self.ingredients_listbox.get(selection)
            self.ingredients_listbox.delete(selection)
            self.current_ingredients.remove(ingredient)
    
    def search_recipes(self):
        if not self.current_ingredients:
            messagebox.showwarning("Warning", "Please add some ingredients first!")
            return
        
        # Find recipes that can be made with current ingredients
        placeholders = ','.join('?' * len(self.current_ingredients))
        query = f'''
        SELECT r.name, r.instructions, GROUP_CONCAT(i.ingredient) as ingredients
        FROM recipes r
        JOIN ingredients i ON r.id = i.recipe_id
        GROUP BY r.id
        HAVING COUNT(CASE WHEN i.ingredient IN ({placeholders}) THEN 1 END) = 
               COUNT(i.ingredient)
        '''
        
        self.cursor.execute(query, self.current_ingredients)
        results = self.cursor.fetchall()
        
        # Display results
        self.recipe_text.delete(1.0, tk.END)
        if not results:
            self.recipe_text.insert(tk.END, "No recipes found with these ingredients.")
            return
        
        for name, instructions, ingredients in results:
            self.recipe_text.insert(tk.END, f"\n{'='*40}\n")
            self.recipe_text.insert(tk.END, f"Recipe: {name}\n\n")
            self.recipe_text.insert(tk.END, f"Ingredients:\n{ingredients}\n\n")
            self.recipe_text.insert(tk.END, f"Instructions:\n{instructions}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeFinderApp(root)
    root.mainloop()