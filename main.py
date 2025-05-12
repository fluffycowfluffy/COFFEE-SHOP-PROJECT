#import dash
from src.interface import run_app
#from src.recommender import cafe_recommender

# Pull the app from interface.py
app = run_app()

# Run the app
if __name__ == "__main__":
   app = app.run(debug = False)
