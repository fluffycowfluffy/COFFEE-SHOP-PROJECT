from src.interface import run_app

# Pull the app from interface.py
app = run_app()

# Run the app
if __name__ == "__main__":
   app = app.run(debug = False)
