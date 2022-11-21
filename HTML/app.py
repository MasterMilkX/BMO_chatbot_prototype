# import
from flask import Flask, jsonify, request, render_template
import json
import sys
sys.path.append("..")

from Python import bmo


app = Flask(__name__,static_url_path='/static')
BMO = bmo.BMO()

# run home page
@app.route('/', methods=['GET', 'POST'])
def home_page():
    return render_template('index.html')

# get a response from the chatbot
@app.route('/bot_chat', methods=['POST'])
def get_bot_response():
    return "hello football!"
    # userText = request.data.msg
    # bmo_response = BMO.talk_html(userText)
    # return json.stringify(bmo_response)



# this goes last
app.run(debug=True)