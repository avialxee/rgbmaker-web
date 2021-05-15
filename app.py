# -*- coding: utf-8 -*-

from wtforms.fields.simple import TextAreaField
from scripts import tabledef,forms,helpers,smv
from flask import Flask, redirect, url_for, render_template, request, session,flash, jsonify
import json
import sys
import os

DEBUG = True
app = Flask(__name__)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only

# Heroku
#from flask_heroku import Heroku
#heroku = Heroku(app)

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if helpers.credentials_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both fields required'})
        return render_template('login.html', form=form)
    user = helpers.get_user()
    return render_template('home.html', user=user)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


# -------- Signup ---------------------------------------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'User/Pass required'})
        return render_template('login.html', form=form)
    return redirect(url_for('login'))


# -------- Settings ---------------------------------------------------------- #
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.change_user(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))

# -------- Query ---------------------------------------------------------- #
@app.route('/query', methods=['GET', 'POST'])
def query():
    
    #if session.get('logged_in'):
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
    #return redirect(url_for('login'))

@app.route('/get-flashes')
def get_flashes():
    return render_template('_flashes.html')


# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host="0.0.0.0")
