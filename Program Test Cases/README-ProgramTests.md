# Smart Microwave Oven System — Test Cases

This repository contains a Tkinter-based “Smart Microwave Oven System” (`microwave_system_Ver4.py`).  
This README documents the **recommended test cases** (automated + manual GUI) to verify core behavior.

---

### Scope under test

- **Core logic**: `MicrowaveEngine`
- **Data/persistence**: `RecipeManager` (reads/writes `recipes.json` in the current working directory)
- **GUI**: `UserInterface` (manual functional verification)

---

### How to run the app

From this folder:

```bash
python microwave_system_Ver4.py
```

---

### Automated test execution (if you implement the tests)

If you implement the automated tests using either framework:

- **unittest**:

```bash
python -m unittest
```

- **pytest**:

```bash
pytest
```

Notes:

- **RecipeManager writes `recipes.json`**. Automated tests should run in a temporary directory (isolated CWD) to avoid overwriting a real `recipes.json`.
- The timer uses a background thread; timer tests typically use **very short durations** (2–5 seconds) and `sleep` to allow the countdown to complete.

---

## Recommended Test Cases

### MicrowaveEngine — logic test cases

| ID | Title | Preconditions | Input / Steps | Expected Result |
|----|--------|---------------|---------------|-----------------|
| **TC-ENG-01** | Start cooking with valid time | `MicrowaveEngine` idle (`is_running == False`) | Call `start_cooking(90, 100, CookingStage.COOK)` | Returns `True`; `is_running == True`; `remaining_time == 90`; `current_power == 100`; `current_stage == COOK`; new entry appended to `cooking_history`. |
| **TC-ENG-02** | Prevent second start while running | Engine already running | Immediately call `start_cooking(60, 60, CookingStage.WARM)` | Returns `False`; original session continues unchanged; no new history entry created. |
| **TC-ENG-03** | Timer countdown behavior | None | Call `start_cooking(3, 100, COOK)`; wait ~4 seconds | `is_running == False`; `remaining_time == 0`; `sensor_data` updated from initial zeros. |
| **TC-ENG-04** | Stop cooking mid-cycle | Cooking in progress | Call `stop_cooking()` | `is_running == False`; `remaining_time == 0`; countdown stops. |
| **TC-ENG-05** | Pause cooking mid-cycle | Cooking in progress | Call `pause_cooking()`; record `remaining_time`; wait ~2 seconds | `is_running == False`; `remaining_time` does **not** decrease during pause. |
| **TC-ENG-06** | Resume after pause | Paused with `remaining_time > 0` | Call `resume_cooking()`; wait until completion | Timer resumes; eventually `is_running == False` and `remaining_time == 0`. |
| **TC-ENG-07** | Resume when time is 0 | `remaining_time == 0` | Call `resume_cooking()` | No effect; `is_running` remains `False`. |
| **TC-ENG-08** | Defrost calculation — known table entry | None | Call `calculate_defrost_time("chicken", "thin", 500)` | Returns `180` seconds. |
| **TC-ENG-09** | Defrost calculation — scaled by weight | None | Call `calculate_defrost_time("beef", "thick", 1000)` | Returns `960` seconds. |
| **TC-ENG-10** | Defrost calculation — unknown defaults | None | Call `calculate_defrost_time("pork", "medium", 500)` | Defaults to 3 minutes; returns `180` seconds. |
| **TC-ENG-11** | Status snapshot while running | Cooking started | Call `get_status()` | Dict contains `running == True`; `current_power` matches; `current_stage` string matches; `sensor_reading` is a float. |
| **TC-ENG-12** | Status snapshot when idle | Ensure engine stopped | Call `get_status()` | `running == False`; `remaining_time == 0`; `current_stage == None`; `sensor_reading` is a float. |
| **TC-ENG-13** | Cooking history logging | From clean engine | Run one session; call `get_cooking_history()` | Contains entry with correct `duration`, `power`, `stage`, and a valid `start_time` string. |

---

### RecipeManager — data & search test cases

| ID | Title | Preconditions | Input / Steps | Expected Result |
|----|--------|---------------|---------------|-----------------|
| **TC-REC-01** | Load sample recipes when file missing | Ensure `recipes.json` does **not** exist in CWD | Instantiate `RecipeManager()` | `recipes` contains the 3 sample recipes defined in code; `favorites` empty; `recipes.json` created. |
| **TC-REC-02** | Add new recipe | Manager instantiated | Call `add_recipe(...)` with valid fields | Returns new index; `recipes` length increases; `rating` initialized to `0.0`; `recipes.json` updated. |
| **TC-REC-03** | Get recipes by category | Recipes exist | Call `get_recipes_by_category("Dessert")` | All returned recipes have `"category" == "Dessert"`. |
| **TC-REC-04** | Search by name (case-insensitive) | Recipe named “Mug Cake” exists | Call `search_recipes("mug")` | Results include the Mug Cake recipe. |
| **TC-REC-05** | Search by ingredient substring | Recipe has ingredient “eggs” | Call `search_recipes("eggs")` | Results include that recipe. |
| **TC-REC-06** | Search with no matches | None | Call `search_recipes("nonexistentingredient")` | Returns empty list. |
| **TC-REC-07** | Add to favorites (no duplicates) | Valid recipe index `i` | Call `add_to_favorites(i)` twice | `favorites` contains `i` only once; `recipes.json` persists the single favorite. |
| **TC-REC-08** | Remove from favorites | `favorites` contains index `i` | Call `remove_from_favorites(i)` | `i` removed; `get_favorites()` omits that recipe. |
| **TC-REC-09** | Favorites list bounds checking | `favorites` contains an index ≥ `len(recipes)` | Call `get_favorites()` | Out-of-range indices ignored; no exception thrown. |
| **TC-REC-10** | Persistence across runs | Add recipe + favorite | Create a new `RecipeManager()` instance | New instance loads added recipe and favorites from `recipes.json`. |

---

### UserInterface — GUI / integration test cases (manual functional)

| ID | Title | Preconditions | Steps | Expected Result |
|----|--------|---------------|--------|-----------------|
| **TC-UI-01** | Start cooking via control panel | App running; engine idle | Enter `1:30`, power `High (100%)`, mode `Cook`, click `START` | Info dialog; display shows `COOKING 01:30` (red); status shows `Running: True`. |
| **TC-UI-02** | Invalid time input error | App running | Enter `abc`, click `START` | Error dialog about invalid time; engine remains idle. |
| **TC-UI-03** | Quick 30s button | Engine idle | Click `QUICK 30s` | Time set to `30`; cooking starts; display shows `COOKING 00:30`. |
| **TC-UI-04** | Quick time shortcut buttons | Engine idle | Click `30s`, `60s`, `90s`, `120s` | Time updates and cooking starts (or warns if already running). |
| **TC-UI-05** | Pause and resume via button | Cooking in progress | Click `PAUSE`; wait; click `PAUSE` again | First click pauses (orange `PAUSED`); time stops decreasing. Second click resumes; countdown continues. |
| **TC-UI-06** | Stop button behavior | Cooking in progress | Click `STOP` | Info dialog; display returns to `READY` (green); remaining time becomes 0. |
| **TC-UI-07** | Defrost time calculation | Auto Defrost tab | Select food/thickness, set weight, click `Calculate Time` | Defrost label updates; main time field set; mode set to `Defrost`. |
| **TC-UI-08** | Recipe list initial load | Launch app first time | Open `Recipes` tab | Listbox shows sample recipes formatted as `Name (Category)`. |
| **TC-UI-09** | Recipe details display | Recipes tab | Select a recipe | Details pane shows category, rating, ingredients, steps, and cooking stages. |
| **TC-UI-10** | Cook selected recipe uses first stage | Recipes tab; recipe selected | Click `Cook This Recipe` | Control panel time/power set to first stage; cooking starts. |
| **TC-UI-11** | Add recipe to favorites | Recipes tab; recipe selected | Click `Add to Favorites` | Info dialog; list item shows `★` prefix. |
| **TC-UI-12** | Search recipes — reset on empty | Recipes tab | Search with query; then clear query and search again | Results filtered with query; full list restored when query empty. |
| **TC-UI-13** | Cooking history display | At least 2 sessions completed | Open `Cooking History`; click `Refresh History` | Sessions listed with start time, duration, power, and mode. |
| **TC-UI-14** | Status panel periodic refresh | Start a 10s cook | Observe status for >10 seconds | Remaining time decrements each second; sensor reading changes; returns to READY at end. |


