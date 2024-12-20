# codenames-workshop
## Requirements for provided AI client (word2vec)
* Install requirements: `pip install -r requirements.txt`
  * Requires scipy **version 1.12** (included in requirements.txt)
* Download https://www.kaggle.com/datasets/leadbest/googlenewsvectorsnegative300
  * Extract .bin and place in client/ folder
 
# Running the server locally
* Install requirements (as above). Make sure you have `flask`, `flask-socketio`, and `flask-cors` installed.
* Add an environment variable `FLASK_ENV` and set the value to `development`.
  * `conda env config vars set FLASK_ENV="development"`
* The server code is in app.py, and you run it with the command `flask run`. The server should start up on 127.0.0.1:5000, which you can visit on your browser to reach the HTML client.
* client.py should read that same environment variable to point to the local server