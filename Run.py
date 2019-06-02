from MyLists import app
import os
import sys

if __name__ == "__main__":
    if not os.path.isfile('./config.ini'):
        print("Config file not found. Exit.")
        sys.exit()

app.run(debug=False)
