# -*- coding: utf-8 -*-

#from wtforms.fields.simple import TextAreaField
from scripts import forms,smv
#,helpers,tabledef
from flask import Flask, redirect, url_for, render_template, request, jsonify
#,session,flash,
#import json
#import sys
import os
from flask_restful import reqparse, abort, Api, Resource


app = Flask(__name__)
api = Api(app)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only

# Heroku
#from flask_heroku import Heroku
#heroku = Heroku(app)

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    return redirect(url_for('query'))


# -------- Query ---------------------------------------------------------- #
@app.route('/query', methods=['GET', 'POST'])
def query():
    qform = forms.QueryForm(request.form)
    if request.method == 'POST':
        name=request.form['name']
        position=request.form['position']
        radius=request.form['radius']
        archives=request.form['archives']
        images=request.form['images']

        
        if qform.validate():
            info, uri, txt = smv.query(name,position,radius,archives,images)
            try :
                return jsonify([info,txt,uri]) 
            except Exception as e :
                return jsonify(success=0, error_msg=str(e))
        else :
            info = jsonify(['error','validation failed','#'])
            
    else:
        info = jsonify(['info','Please enter coordinates','#'])

    return render_template('query.html', form=qform)



##-----------==============         API for accessing RGBMaker       ========-----------##

@app.route('/home/<string:num>', methods = ['GET'])
def disp(num):
    info, uri, txt = smv.query(position=num)
    return jsonify({'info': info, 'message': txt, 'url':uri})

parse = reqparse.RequestParser()
parse.add_argument('position')
parse.add_argument('radius')
parse.add_argument('imagesopt')
parse.add_argument('archives')
parse.add_argument('name')



class RGBMaker(Resource):
    def post(self):
        arg= parse.parse_args()
        info, uri, txt = smv.query(name=arg['name'],position=arg['position'], radius=arg['radius'], imagesopt=arg['imagesopt'], archives=arg['archives'])
        return {'info': info, 'message': txt, 'url':uri}, 200
    def get(self):
        return redirect(url_for('query'))
api.add_resource(RGBMaker, '/api')



# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=False, use_reloader=True)
