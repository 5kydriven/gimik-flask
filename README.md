gimik-flask Project

This is a Flask web application. Follow the steps below to set up and run the project.

Installation

1. Clone the Repository

git clone https://github.com/5kydriven/gimik-flask.git
cd gimik-flask

2. Create and Activate a Virtual Environment

Windows (CMD or PowerShell)

python -m venv .venv
.venv\Scripts\activate

macOS/Linux (Bash)

python3 -m venv .venv
source .venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

4. Set Environment Variables

Create a .env file in the project root and add the necessary environment variables:

FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1

Running the Application

1. Start the Flask Server

flask run

The app should now be running at http://127.0.0.1:5000.

Additional Notes

Ensure you have Python 3.8+ installed.

If flask run does not start in debug mode, try setting environment variables manually.

For production, use a WSGI server like Gunicorn.

License

This project is licensed under the MIT License.