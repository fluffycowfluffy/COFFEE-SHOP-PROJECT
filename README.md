# Got Coffee?
## The Williamsburg Coffee Recommender System
### Greta Lin Risgin
### Automation & Workflows
### 12 May 2025

---
The Williamsburg Coffee Recommender System takes user preferences on cafés and returns a local coffee shop recommendation. The data for this project was collected from 15 different coffee shops in the Williamsburg area.
---
Note: This project is also being publically hosted on my [website](http://risgin.com/). However, the publically hosted version is running on select outdated Python libraries and may be flagged as an unsecure website on certain devices. Cloning this GitHub will produce a faster and more accurate version of the recommendation system.

---
Quick Start
---
After cloning this repository, sync the virtual environment:
```
uv sync
```
Then run the main function from the correct directory:
```
uv run main.py
```
About the Project
---
This repository includes the following folders and files:
- `main.py` runs the following Python scripts found in `src`.
- `src` contains the following material required to run the program.
  - `recommender.py` is the Python file calculating user scores that matches their preferences to the cafés.
    - `cafe_recommender` is this file's main function. It uses one-hot encoding for most of the dataframe, which converts the data to binary for more manageable handling during data matching. Price point is assigned weighted values. For example,  if a user selects the `High` price point, `Mid` ranked cafés are wighted more heavily than `Low` ranked cafés. Multi label binary classification is used for variables `atmosphere_desc` and `specials_desc`, which contain lists of descriptor data for each café. The program compares the user preferences against cafés using binary vectors to produce matching scores for each café and return the top match. 
  - `interface.py` creates a Plotly Dash interface for the program.
    - `run_app` is the function that runs the entire Dash app.
    - `show_questions` runs through each question based on the current index. It pulls from pre-set questions created previously in the Python script.
    - `next_question` takes the created variables for user preferences and fills them with the asnwer provided at each question. It disallows continuation of the survey without providing answers and displays the top match found by runnning `cafe_recommender` with a corresponding custom vizualization.
  - `assets` contains the vizualization artwork for the program, including a header image, next button icon, and custom images for each café's signature drink. It also contains a `style.css` file that provides some basic styling applied to the entire Dash interface.
- `data` contains CSV files for the collected café data.
  - `coffeeshop_df` is a dataframe containing each café's ID, binary T/F variables, and the ordinal price point variable.
  - `descriptor_df` is a dataframe containing the descriptors, assigned using each café's unique ID, for atmosphere and signature drink.
  - `reference_df` is a dataframe containing the corresponding establishment name, signature drink, and address for each unique café ID.
- `pyproject.toml` and `uv.lock` are necessary for syncing virtual environments with the correct requirements.
- `writeup` contains more in-depth information on this project.
---
