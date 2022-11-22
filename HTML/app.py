# import
from flask import Flask, jsonify, request, render_template
import json
import sys
sys.path.append("..")

from Python import bmo
BMO = bmo.BMO()


app = Flask(__name__,static_url_path='/static')
# BMO = bmo.BMO()

# run home page
@app.route('/', methods=['GET', 'POST'])
def home_page():
    return render_template('index.html')

# get a response from the chatbot
@app.route('/bot_chat', methods=['POST'])
def get_bot_response():
    # return jsonify({"txt":"hello football!","face":"sus"})
    if request.method == "POST":    
        userText = request.form['msg']
        bmo_response = BMO.talk_html(userText)
        return jsonify(bmo_response)



# this goes last
app.run(debug=True)