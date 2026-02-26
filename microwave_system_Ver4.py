# ==================== SMART MICROWAVE OVEN SYSTEM ====================
# Team Members and Roles:
# - Lead Developer: Oladipo Towobola
# - Testing & Quality Assurance Lead: Arturo Menchaca
# - Documentation Lead: Oliver Michael Wilderman
# - Team Lead: Harrison Scgalski
# ======================================================================

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import random
import sys
import time
import threading
from datetime import datetime
from enum import Enum

# Recipes file path: same directory as this script
RECIPES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recipes.json")

# ==================== ENUM CLASSES ====================
class PowerLevel(Enum):
    LOW = 30
    MEDIUM = 60
    HIGH = 100

class CookingStage(Enum):
    DEFROST = "defrost"
    COOK = "cook"
    WARM = "warm"
    REHEAT = "reheat"

# ==================== CORE CLASSES ====================

class MicrowaveEngine:
    """Handles cooking logic, timing, and power management"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.is_running = False
        self.remaining_time = 0
        self.current_power = PowerLevel.HIGH.value
        self.current_stage = None
        self.timer_thread = None
        self.sensor_data = [0.0] * 10  # List for sensor readings (replaces numpy)
        self.cooking_history = []  # List of cooking sessions
        self.defrost_table = {  # Dictionary for defrost times
            "chicken": {"thin": 3, "thick": 6},
            "beef": {"thin": 4, "thick": 8},
            "fish": {"thin": 2, "thick": 4},
            "vegetables": {"thin": 2, "thick": 3}
        }
        self.power_settings = {
            "Low (30%)": 30,
            "Medium (60%)": 60,
            "High (100%)": 100
        }
    
    def start_cooking(self, time_seconds, power_level=100, stage=CookingStage.COOK):
        """Start or resume cooking with specified parameters"""
        with self._lock:
            if self.is_running:
                return False
            if self.remaining_time > 0:
                self.is_running = True
                self.timer_thread = threading.Thread(target=self._cooking_timer, daemon=True)
                self.timer_thread.start()
                return True
            self.is_running = True
            self.remaining_time = time_seconds
            self.current_power = power_level
            self.current_stage = stage
            session = {
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "duration": time_seconds,
                "power": power_level,
                "stage": stage.value
            }
            self.cooking_history.append(session)
        self.timer_thread = threading.Thread(target=self._cooking_timer, daemon=True)
        self.timer_thread.start()
        return True
    
    def _cooking_timer(self):
        """Internal timer method"""
        while True:
            with self._lock:
                if self.remaining_time <= 0 or not self.is_running:
                    self.is_running = False
                    break
                self.remaining_time -= 1
                # Simulate sensor data collection (roll left, append new reading)
                self.sensor_data = self.sensor_data[1:] + [random.uniform(20, 100)]
            time.sleep(1)
        
    def stop_cooking(self):
        """Stop cooking immediately"""
        with self._lock:
            self.is_running = False
            self.remaining_time = 0

    def pause_cooking(self):
        """Pause cooking"""
        with self._lock:
            self.is_running = False

    def resume_cooking(self):
        """Resume cooking"""
        with self._lock:
            if self.remaining_time <= 0:
                return
            self.is_running = True
        self.timer_thread = threading.Thread(target=self._cooking_timer, daemon=True)
        self.timer_thread.start()
    
    def calculate_defrost_time(self, food_type, thickness, weight_grams):
        """Calculate defrost time based on food type and weight"""
        base_time = self.defrost_table.get(food_type, {}).get(thickness, 3)
        time_minutes = base_time * (weight_grams / 500)  # Scale based on weight
        return int(time_minutes * 60)  # Convert to seconds
    
    def get_cooking_history(self):
        """Return cooking history"""
        with self._lock:
            return list(self.cooking_history)

    def get_status(self):
        """Get current microwave status"""
        with self._lock:
            status = {
                "running": self.is_running,
                "remaining_time": self.remaining_time,
                "current_power": self.current_power,
                "current_stage": self.current_stage.value if self.current_stage else None,
                "sensor_reading": self.sensor_data[-1] if self.sensor_data else 0
            }
        return status


class RecipeManager:
    """Manages recipe storage, retrieval, and organization"""
    
    def __init__(self):
        self.recipes = []  # List of recipes
        self.categories = ["Breakfast", "Lunch", "Dinner", "Dessert", "Snacks"]
        self.favorites = []  # List of favorite recipe indices
        self.load_recipes()
        
        # Sample recipes if none exist
        if not self.recipes:
            self._create_sample_recipes()
    
    def _create_sample_recipes(self):
        """Create sample recipes for demonstration"""
        sample_recipes = [
            {
                "name": "Microwave Omelette",
                "category": "Breakfast",
                "ingredients": ["2 eggs", "2 tbsp milk", "salt", "pepper", "cheese"],
                "steps": ["Whisk eggs and milk", "Microwave for 2 minutes", "Add cheese", "Microwave 30 seconds"],
                "cooking_stages": [
                    {"time": 120, "power": 100, "action": "Cook eggs"},
                    {"time": 30, "power": 50, "action": "Melt cheese"}
                ],
                "rating": 4.5
            },
            {
                "name": "Mug Cake",
                "category": "Dessert",
                "ingredients": ["4 tbsp flour", "2 tbsp sugar", "2 tbsp cocoa", "3 tbsp milk", "1 tbsp oil"],
                "steps": ["Mix dry ingredients", "Add wet ingredients", "Microwave for 90 seconds"],
                "cooking_stages": [
                    {"time": 90, "power": 100, "action": "Bake cake"}
                ],
                "rating": 4.8
            },
            {
                "name": "Steamed Vegetables",
                "category": "Lunch",
                "ingredients": ["2 cups mixed vegetables", "2 tbsp water", "1 tsp butter", "salt"],
                "steps": ["Place vegetables in bowl", "Add water", "Cover and microwave for 5 minutes"],
                "cooking_stages": [
                    {"time": 300, "power": 100, "action": "Steam vegetables"}
                ],
                "rating": 4.2
            }
        ]
        
        self.recipes.extend(sample_recipes)
        self.save_recipes()
    
    def add_recipe(self, name, category, ingredients, steps, cooking_stages):
        """Add a new recipe"""
        recipe = {
            "name": name,
            "category": category,
            "ingredients": ingredients,
            "steps": steps,
            "cooking_stages": cooking_stages,
            "rating": 0.0
        }
        self.recipes.append(recipe)
        self.save_recipes()
        return len(self.recipes) - 1
    
    def get_recipes_by_category(self, category):
        """Get recipes filtered by category"""
        return [recipe for recipe in self.recipes if recipe["category"] == category]
    
    def get_all_recipes(self):
        """Get all recipes"""
        return self.recipes
    
    def search_recipes(self, query):
        """Search recipes by name or ingredient"""
        results = []
        query = query.lower()
        for recipe in self.recipes:
            if (query in recipe["name"].lower() or 
                any(query in ing.lower() for ing in recipe["ingredients"])):
                results.append(recipe)
        return results
    
    def add_to_favorites(self, recipe_index):
        """Add recipe to favorites"""
        if recipe_index not in self.favorites:
            self.favorites.append(recipe_index)
            self.save_recipes()
    
    def remove_from_favorites(self, recipe_index):
        """Remove recipe from favorites"""
        if recipe_index in self.favorites:
            self.favorites.remove(recipe_index)
            self.save_recipes()
    
    def get_favorites(self):
        """Get favorite recipes"""
        return [self.recipes[i] for i in self.favorites if i < len(self.recipes)]
    
    def load_recipes(self):
        """Load recipes from file"""
        try:
            with open(RECIPES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.recipes = data.get("recipes", [])
                self.favorites = data.get("favorites", [])
        except FileNotFoundError:
            self.recipes = []
            self.favorites = []
        except (json.JSONDecodeError, OSError):
            self.recipes = []
            self.favorites = []

    def save_recipes(self):
        """Save recipes to file"""
        data = {
            "recipes": self.recipes,
            "favorites": self.favorites
        }
        try:
            with open(RECIPES_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"Could not save recipes: {e}", file=sys.stderr)


class UserInterface:
    """Main GUI controller and display manager"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Microwave Oven System")
        self.root.geometry("1200x700")
        
        # Initialize core components
        self.engine = MicrowaveEngine()
        self.recipe_manager = RecipeManager()
        # Map listbox index -> recipe index (fixes Cook/Favorite after search)
        self.displayed_recipe_indices = []

        # Create containers
        self.create_widgets()
        self.setup_layout()
        
        # Start status update thread
        self.update_status()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        
        # ========== CONTROL PANEL TAB ==========
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Control Panel")
        
        # Display
        self.display_var = tk.StringVar(value="READY")
        self.display = tk.Label(self.control_frame, textvariable=self.display_var, 
                               font=("Arial", 24), bg="black", fg="green", 
                               width=30, height=2)
        
        # Timer controls
        self.time_var = tk.StringVar(value="1:00")
        self.time_entry = ttk.Entry(self.control_frame, textvariable=self.time_var, 
                                   font=("Arial", 14), width=10, justify="center")
        
        # Power level selector
        self.power_var = tk.StringVar(value="High (100%)")
        self.power_combo = ttk.Combobox(self.control_frame, textvariable=self.power_var,
                                       values=list(self.engine.power_settings.keys()),
                                       state="readonly", width=20)
        
        # Cooking mode selector
        self.mode_var = tk.StringVar(value="Cook")
        self.mode_combo = ttk.Combobox(self.control_frame, textvariable=self.mode_var,
                                      values=[stage.value.title() for stage in CookingStage],
                                      state="readonly", width=20)

        # Control buttons (in a frame so layout groups them)
        self.btn_frame = ttk.Frame(self.control_frame)
        self.start_btn = ttk.Button(self.btn_frame, text="START",
                                    command=self.start_cooking, width=15)
        self.stop_btn = ttk.Button(self.btn_frame, text="STOP/RESET",
                                  command=self.stop_cooking, width=15)
        self.pause_btn = ttk.Button(self.btn_frame, text="PAUSE/RESUME",
                                    command=self.pause_cooking, width=15)
        self.quick_btn = ttk.Button(self.btn_frame, text="QUICK 30s",
                                   command=lambda: self.quick_start(30), width=15)
        
        # Quick time buttons
        self.quick_buttons_frame = ttk.Frame(self.control_frame)
        for seconds in [30, 60, 90, 120]:
            btn = ttk.Button(self.quick_buttons_frame, text=f"{seconds}s",
                           command=lambda s=seconds: self.quick_start(s))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Status display
        self.status_text = scrolledtext.ScrolledText(self.control_frame, 
                                                    width=50, height=10,
                                                    font=("Courier", 10))
        
        # ========== RECIPE TAB ==========
        self.recipe_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recipe_frame, text="Recipes")
        
        # Recipe list
        self.recipe_listbox = tk.Listbox(self.recipe_frame, width=40, height=15,
                                        font=("Arial", 11))
        self.load_recipe_list()
        
        # Recipe details
        self.recipe_details = scrolledtext.ScrolledText(self.recipe_frame,
                                                       width=60, height=15,
                                                       font=("Arial", 10))
        
        # Recipe controls
        self.cook_recipe_btn = ttk.Button(self.recipe_frame, text="Cook This Recipe",
                                         command=self.cook_selected_recipe)
        self.favorite_btn = ttk.Button(self.recipe_frame, text="Add to Favorites",
                                      command=self.add_to_favorites)
        
        # Recipe search
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.recipe_frame, textvariable=self.search_var)
        self.search_btn = ttk.Button(self.recipe_frame, text="Search",
                                    command=self.search_recipes)
        
        # ========== DEFROST TAB ==========
        self.defrost_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.defrost_frame, text="Auto Defrost")
        
        # Defrost controls
        self.food_type_var = tk.StringVar(value="chicken")
        self.thickness_var = tk.StringVar(value="thin")
        self.weight_var = tk.IntVar(value=500)
        
        ttk.Label(self.defrost_frame, text="Food Type:").grid(row=0, column=0, padx=5, pady=5)
        self.food_combo = ttk.Combobox(self.defrost_frame, textvariable=self.food_type_var,
                                      values=list(self.engine.defrost_table.keys()),
                                      state="readonly")
        self.food_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.defrost_frame, text="Thickness:").grid(row=1, column=0, padx=5, pady=5)
        self.thickness_combo = ttk.Combobox(self.defrost_frame, textvariable=self.thickness_var,
                                           values=["thin", "thick"], state="readonly")
        self.thickness_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.defrost_frame, text="Weight (grams):").grid(row=2, column=0, padx=5, pady=5)
        self.weight_scale = ttk.Scale(self.defrost_frame, from_=100, to=2000,
                                     variable=self.weight_var, orient=tk.HORIZONTAL)
        self.weight_scale.grid(row=2, column=1, padx=5, pady=5)
        
        self.weight_label = ttk.Label(self.defrost_frame, text="500g")
        self.weight_label.grid(row=2, column=2, padx=5, pady=5)
        
        self.calc_defrost_btn = ttk.Button(self.defrost_frame, text="Calculate Time",
                                          command=self.calculate_defrost)
        self.calc_defrost_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.defrost_result = ttk.Label(self.defrost_frame, text="", font=("Arial", 12))
        self.defrost_result.grid(row=4, column=0, columnspan=3, pady=10)
        
        # ========== HISTORY TAB ==========
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Cooking History")
        
        # History display
        self.history_text = scrolledtext.ScrolledText(self.history_frame,
                                                     width=80, height=20,
                                                     font=("Courier", 10))
        self.history_text.pack(padx=10, pady=10)
        
        self.refresh_history_btn = ttk.Button(self.history_frame, text="Refresh History",
                                            command=self.load_history)
        self.refresh_history_btn.pack(pady=5)
    
    def setup_layout(self):
        """Setup widget layout"""
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control Panel Layout
        self.display.pack(pady=10)
        
        ttk.Label(self.control_frame, text="Time (MM:SS):").pack(pady=5)
        self.time_entry.pack(pady=5)
        
        ttk.Label(self.control_frame, text="Power Level:").pack(pady=5)
        self.power_combo.pack(pady=5)
        
        ttk.Label(self.control_frame, text="Cooking Mode:").pack(pady=5)
        self.mode_combo.pack(pady=5)
        
        self.quick_buttons_frame.pack(pady=10)

        self.start_btn.pack(side=tk.LEFT, padx=5, pady=10)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=10)
        self.pause_btn.pack(side=tk.LEFT, padx=5, pady=10)
        self.quick_btn.pack(side=tk.LEFT, padx=5, pady=10)
        self.btn_frame.pack(pady=10)
        
        ttk.Label(self.control_frame, text="System Status:").pack(pady=5)
        self.status_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Recipe Tab Layout
        recipe_left = ttk.Frame(self.recipe_frame)
        recipe_right = ttk.Frame(self.recipe_frame)
        
        recipe_left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        recipe_right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Recipe list on left
        ttk.Label(recipe_left, text="Recipes", font=("Arial", 14, "bold")).pack()
        self.recipe_listbox.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Search on left
        search_frame = ttk.Frame(recipe_left)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_btn.pack(side=tk.RIGHT, padx=5)
        search_frame.pack(pady=5, fill=tk.X)
        
        # Recipe details on right
        ttk.Label(recipe_right, text="Recipe Details", font=("Arial", 14, "bold")).pack()
        self.recipe_details.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Recipe buttons
        self.cook_recipe_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.favorite_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Bind recipe selection
        self.recipe_listbox.bind('<<ListboxSelect>>', self.on_recipe_select)
    
    def update_status(self):
        """Update display and status panel"""
        status = self.engine.get_status()
        
        # Update display
        if status["running"]:
            mins = status["remaining_time"] // 60
            secs = status["remaining_time"] % 60
            self.display_var.set(f"COOKING {mins:02d}:{secs:02d}")
            self.display.config(fg="red")
        else:
            if status["remaining_time"] == 0:
                self.display_var.set("READY")
                self.display.config(fg="green")
            else:
                mins = status["remaining_time"] // 60
                secs = status["remaining_time"] % 60
                self.display_var.set(f"PAUSED {mins:02d}:{secs:02d}")
                self.display.config(fg="orange")
        
        # Update status text
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, 
            f"Microwave Status:\n"
            f"{'='*40}\n"
            f"Running: {status['running']}\n"
            f"Remaining Time: {status['remaining_time']}s\n"
            f"Current Power: {status['current_power']}%\n"
            f"Cooking Stage: {status['current_stage']}\n"
            f"Sensor Reading: {status['sensor_reading']:.1f}°C\n"
            f"{'='*40}\n"
            f"Recipes Loaded: {len(self.recipe_manager.recipes)}\n"
            f"Favorites: {len(self.recipe_manager.favorites)}\n"
            f"Cooking Sessions: {len(self.engine.get_cooking_history())}"
        )
        
        # Update weight label
        self.weight_label.config(text=f"{self.weight_var.get()}g")
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def _is_paused(self):
        """True if cooking is paused (remaining time but not running)."""
        s = self.engine.get_status()
        return not s["running"] and s["remaining_time"] > 0

    def start_cooking(self):
        """Start cooking with entered parameters"""
        if self._is_paused():
            messagebox.showwarning(
                "Cooking Paused",
                "Cooking is paused. Use PAUSE/RESUME to resume or STOP/RESET to cancel."
            )
            return
        try:
            time_str = self.time_var.get().strip()
            if ":" in time_str:
                parts = time_str.split(":")
                if len(parts) != 2:
                    raise ValueError("Use MM:SS or seconds")
                mins, secs = int(parts[0]), int(parts[1])
                if secs < 0 or secs >= 60 or mins < 0:
                    raise ValueError("Minutes must be >= 0; seconds must be 0-59")
                time_seconds = mins * 60 + secs
            else:
                time_seconds = int(time_str)
                if time_seconds < 0:
                    raise ValueError("Time must be non-negative")
            
            # Get power level
            power_str = self.power_var.get()
            power_level = self.engine.power_settings.get(power_str, 100)
            
            # Get cooking stage
            mode_str = self.mode_var.get().lower()
            stage = CookingStage(mode_str)
            
            # Start cooking
            success = self.engine.start_cooking(time_seconds, power_level, stage)
            
            if success:
                messagebox.showinfo("Cooking Started", 
                                  f"Cooking started for {time_seconds} seconds at {power_level}% power")
            else:
                messagebox.showwarning("Already Cooking", "Microwave is already running!")
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid time (MM:SS or seconds)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start cooking: {str(e)}")
    
    def stop_cooking(self):
        """Stop cooking"""
        self.engine.stop_cooking()
        messagebox.showinfo("Stopped", "Cooking stopped")
    
    def pause_cooking(self):
        """Pause cooking"""
        if self.engine.get_status()["running"]:
            self.engine.pause_cooking()
            messagebox.showinfo("Paused", "Cooking paused")
        else:
            messagebox.showinfo("Resumed", "Cooking resumed")
            self.engine.resume_cooking()
    
    def quick_start(self, seconds):
        """Quick start with preset time (displays as MM:SS when >= 60). Disabled when paused."""
        if self._is_paused():
            messagebox.showwarning(
                "Cooking Paused",
                "Cooking is paused. Use PAUSE/RESUME to resume or STOP/RESET to cancel."
            )
            return
        if seconds >= 60:
            self.time_var.set(f"{seconds // 60}:{seconds % 60:02d}")
        else:
            self.time_var.set(str(seconds))
        self.start_cooking()
    
    def load_recipe_list(self):
        """Load recipes into listbox"""
        self.recipe_listbox.delete(0, tk.END)
        self.displayed_recipe_indices = list(range(len(self.recipe_manager.recipes)))
        for i, recipe in enumerate(self.recipe_manager.recipes):
            star = "★ " if i in self.recipe_manager.favorites else ""
            self.recipe_listbox.insert(tk.END, f"{star}{recipe['name']} ({recipe['category']})")
    
    def on_recipe_select(self, event):
        """Handle recipe selection"""
        selection = self.recipe_listbox.curselection()
        if selection and selection[0] < len(self.displayed_recipe_indices):
            real_index = self.displayed_recipe_indices[selection[0]]
            recipe = self.recipe_manager.recipes[real_index]
            
            # Display recipe details
            self.recipe_details.delete(1.0, tk.END)
            self.recipe_details.insert(1.0,
                f"Recipe: {recipe['name']}\n"
                f"{'='*40}\n"
                f"Category: {recipe['category']}\n"
                f"Rating: {recipe['rating']}/5.0\n\n"
                f"Ingredients:\n"
                f"{'-'*20}\n"
            )
            
            for ingredient in recipe['ingredients']:
                self.recipe_details.insert(tk.END, f"• {ingredient}\n")
            
            self.recipe_details.insert(tk.END,
                f"\nSteps:\n"
                f"{'-'*20}\n"
            )
            
            for i, step in enumerate(recipe['steps'], 1):
                self.recipe_details.insert(tk.END, f"{i}. {step}\n")
            
            self.recipe_details.insert(tk.END,
                f"\nCooking Instructions:\n"
                f"{'-'*20}\n"
            )
            
            for stage in recipe['cooking_stages']:
                self.recipe_details.insert(tk.END,
                    f"• {stage['action']}: {stage['time']}s at {stage['power']}% power\n")
    
    def cook_selected_recipe(self):
        """Start cooking selected recipe (first stage only)."""
        selection = self.recipe_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a recipe first")
            return
        if selection[0] >= len(self.displayed_recipe_indices):
            return
        real_index = self.displayed_recipe_indices[selection[0]]
        recipe = self.recipe_manager.recipes[real_index]
        
        # Start with first cooking stage
        if recipe['cooking_stages']:
            stage = recipe['cooking_stages'][0]
            self.time_var.set(str(stage['time']))
            power_key = [k for k, v in self.engine.power_settings.items() 
                        if v == stage['power']]
            if power_key:
                self.power_var.set(power_key[0])
            self.start_cooking()
    
    def add_to_favorites(self):
        """Add current recipe to favorites"""
        selection = self.recipe_listbox.curselection()
        if selection and selection[0] < len(self.displayed_recipe_indices):
            real_index = self.displayed_recipe_indices[selection[0]]
            self.recipe_manager.add_to_favorites(real_index)
            self.load_recipe_list()
            messagebox.showinfo("Added", "Recipe added to favorites!")
    
    def search_recipes(self):
        """Search for recipes"""
        query = self.search_var.get()
        if not query:
            self.load_recipe_list()
            return
        results = self.recipe_manager.search_recipes(query)
        self.recipe_listbox.delete(0, tk.END)
        self.displayed_recipe_indices = [self.recipe_manager.recipes.index(r) for r in results]
        for recipe in results:
            original_index = self.recipe_manager.recipes.index(recipe)
            star = "★ " if original_index in self.recipe_manager.favorites else ""
            self.recipe_listbox.insert(tk.END, f"{star}{recipe['name']} ({recipe['category']})")
    
    def calculate_defrost(self):
        """Calculate defrost time"""
        food_type = self.food_type_var.get()
        thickness = self.thickness_var.get()
        weight = int(round(self.weight_var.get()))
        
        try:
            time_seconds = self.engine.calculate_defrost_time(food_type, thickness, weight)
            mins = time_seconds // 60
            secs = time_seconds % 60
            
            self.defrost_result.config(
                text=f"Defrost Time: {mins} minutes {secs} seconds\n"
                     f"for {weight}g of {food_type} ({thickness} cut)"
            )
            
            # Set the calculated time
            self.time_var.set(f"{mins}:{secs:02d}")
            self.mode_var.set("Defrost")
            
        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))
    
    def load_history(self):
        """Load cooking history"""
        history = self.engine.get_cooking_history()
        self.history_text.delete(1.0, tk.END)
        
        if not history:
            self.history_text.insert(1.0, "No cooking history available.")
            return
        
        self.history_text.insert(1.0, "COOKING HISTORY\n")
        self.history_text.insert(tk.END, "="*60 + "\n\n")
        
        for i, session in enumerate(reversed(history), 1):
            self.history_text.insert(tk.END,
                f"Session {i}:\n"
                f"  Start Time: {session['start_time']}\n"
                f"  Duration: {session['duration']} seconds\n"
                f"  Power: {session['power']}%\n"
                f"  Mode: {session['stage']}\n"
                f"{'-'*40}\n"
            )


# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = UserInterface(root)
    
    # Set window icon and title
    root.title("Smart Microwave Oven System - Team Project")
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()