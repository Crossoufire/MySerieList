import os
from MyLists import app


if __name__ == "__main__":
    app.run(debug=bool(os.environ.get('FLASK_DEBUG')))
