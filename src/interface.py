# Import the necessary libraries
from src.recommender import cafe_recommender
import json

# Dash imports
import dash
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

def run_app() -> dash:
    """
    Runs the user interface
    and provides the recommendation
    """
    # Initialize the app
    app = dash.Dash(
        __name__, 
        external_stylesheets = [dbc.themes.BOOTSTRAP], 
        suppress_callback_exceptions = True
        )

    # Atmosphere and specials descriptors
    atmosphere_desc = json.dumps(["cozy", "bright", "modern", "funky", "airy", "hole in the wall", 
                       "chic", "bustling", "upscale", "modest", "local", "authentic", "cheap"])

    specials_desc = json.dumps(["fruity", "sweet", "earthy", "nutty", "chocolatey", "bitter",
                     "spicy", "floral", "rich", "strong", "creamy", "vanilla", "light"])

    # Create the questions
    questions = [
        {
            "id": "q1", 
            "text": "Do you want to study at this café?",
            "options": [
                {"label": "Yes", "value": "1"},
                {"label": "No", "value": "0"}
            ]
        },
        {
            "id": "q2",
            "text": "Are you willing to drive to this café?",
            "options": [
                {"label": "Yes", "value": "1"},
                {"label": "No", "value": "0"}
            ]
        },
        {
            "id": "q3",
            "text": "Do you typically order coffee with non-dairy milk?",
            "options": [
                {"label": "Yes", "value": "1"},
                {"label": "No", "value": "0"}
            ]
        },
        {
            "id": "q4",
            "text": "Are you gluten free?",
            "options": [
                {"label": "Yes", "value": "1"},
                {"label": "No", "value": "0"}
            ]
        },
        {
            "id": "q5",
            "text": "Do you want to eat a full meal at this café?",
            "options": [
                {"label": "Yes", "value": "1"},
                {"label": "No", "value": "0"}
            ]
        },
        {
            "id": "q6",
            "text": "What is your preferred price point?",
            "options" : [
                {"label": "Low", "value": "low"},
                {"label": "Mid", "value": "mid"},
                {"label": "High", "value": "high"}
            ]
        },
        {
            "id": "q7",
            "text": "Please select your top three ajectives for the ideal café atmosphere:",
            "options": [{"label": "bundle", "value": atmosphere_desc}]
        },
        {
            "id": "q8",
            "text": "Please select your top three flavors for a coffee drink:",
            "options": [{"label": "bundle", "value": specials_desc}]
        }
    ]

    # Create the app's layout
    app.layout = html.Div([
        # Header image
        html.Img(src = "/assets/got_coffee.png", style = {"height": "50%", "width": "50%"}),
        # Keep track of each question the user is on
        dcc.Store(id = "question-index", data = 0),
        # Keep track of user answers
        dcc.Store(id = "user-prefs-general", data = {}),
        dcc.Store(id = "user-prefs-atmosphere", data = []),
        dcc.Store(id = "user-prefs-specials", data = []),
        html.Div(id = "question-container"),
        html.Div(id = "user")], className = "container", style = {"textAlign": "center"})

    # Ask the first question
    @app.callback(
        Output("question-container", "children"),
        Input("question-index", "data")
    )

    # Run through each question
    def show_questions(index):
        # Message for finishing asking the questions
        if index >= len(questions):
            return html.Div()

        # Use this variable to reference the correct question
        question = questions[index]
        # Display the question's text
        question_text = [html.P(question["text"], style = {"fontSize": "30px"})]

        # Specifically use a dropdown for questions 6 and 6
        if question["id"] in ["q7", "q8"]:
            options = json.loads(question["options"][0]["value"])
            question_text.append(
                dcc.Dropdown(
                    id = "current-answer",
                    options = [{"label": i, "value": i} for i in options],
                    multi = True
                )
            )
        # For all previous questions, use radio items
        else:
            question_text.append(
                dcc.RadioItems(
                    id = "current-answer",
                    options = question["options"],
                    inline = True
                )
            )

        # Line break
        question_text.append(html.Br())
        # Next button to continue to next question
        question_text.append(
            html.Button(
                id = "next-button",
                n_clicks = 0,
                children = [html.Img(
                    src = "/assets/next_button.png", 
                    style = {
                            "height": "30%", 
                            "width": "30%", 
                            "backgroundColor": "transparent",
                            "border": "none"
                            }
                )],
                style = {
                        "border": "none",
                        "backgroundColor": "transparent"
                        }
            )
        )

        return html.Div(id = f"q{index + 1}", children = question_text)

    # Roll through the questions
    @app.callback(
        Output("question-index", "data"),
        Output("user-prefs-general", "data"),
        Output("user-prefs-atmosphere", "data"),
        Output("user-prefs-specials", "data"),
        Output("user", "children"),
        Input("next-button", "n_clicks"),  
        # Catch data from user's current question and inputs
        State("question-index", "data"),
        State("current-answer", "value"),
        State("user-prefs-general", "data"),
        State("user-prefs-atmosphere", "data"),
        State("user-prefs-specials", "data"),
        prevent_initial_call = True
    )


    def next_question(n_clicks: int, 
                      current_index: int, 
                      current_answer, 
                      user_prefs_general: dict, 
                      user_prefs_atmosphere: list, 
                      user_prefs_specials: list):
        """
        Function moves on to the next question
        and displays the final recommendation
        """
        # Keys for user answer dictionary
        question_keys = ["study_space", 
                         "car_req", 
                         "nondairy_charge", 
                         "gluten_free", 
                         "food_menu",
                         "price_point_mid",
                         "price_point_high"]
        # Create string to store recommendation message
        recommendation = ""

        # Do not continue until the user pushes the button
        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate
        
        # Don't continue until the user answers the question
        if current_answer is None:
            raise PreventUpdate

        # Store boolean values into the user general preferences dictionary
        if current_index < 5:
            working_pref_dict =user_prefs_general.copy()
            working_pref_dict[question_keys[current_index]] = int(current_answer)
            user_prefs_general = working_pref_dict
        # Store user price preferences in the dictionary
        elif current_index == 5:
            if current_answer == "low":
                user_prefs_general["price_point_mid"] = 0
                user_prefs_general["price_point_high"] = 0
            elif current_answer == "mid":
                user_prefs_general["price_point_mid"] = 1
                user_prefs_general["price_point_high"] = 0
            elif current_answer == "high":
                user_prefs_general["price_point_mid"] = 0
                user_prefs_general["price_point_high"] = 1
        # Store descriptors as two lists; Do not continue unless user picks three options
        elif current_index == 6:
            if len(current_answer) != 3:
                raise PreventUpdate
            user_prefs_atmosphere = current_answer
        elif current_index == 7:
            if len(current_answer) != 3:
                raise PreventUpdate
            user_prefs_specials = current_answer

        # Display the recommendation at the end!
        if current_index == len(questions) - 1:
            top_match = cafe_recommender(user_prefs_general, 
                                         user_prefs_atmosphere, 
                                         user_prefs_specials)
            recommendation = html.Div([
                html.P(f"Your café recommendation is {top_match['cafe_name'].iloc[0]}.", style = {"fontSize": "30px", "marginBottom": "5px"}),
                html.P(f"You should try their {top_match['specials'].iloc[0]}!", style = {"fontSize": "30px", "marginBottom": "5px"}),
                html.Img(src = f"/assets/{top_match['specials'].iloc[0]}.png", style = {"height": "50%", "width": "50%"})
            ])
            # Increment the index and return the recommendation
            return current_index + 1, user_prefs_general, user_prefs_atmosphere, user_prefs_specials, recommendation
        
        # Increment the index and return no message if end of questions is not reached
        return current_index + 1, user_prefs_general, user_prefs_atmosphere, user_prefs_specials, ""

    return app