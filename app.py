# -*- coding: utf-8 -*-

from scripts import forms,smv
from flask import Flask, redirect, url_for, render_template, request, jsonify
import os
from flask_cors import CORS
from flask_restful import reqparse, abort, Api, Resource
from celery import Celery
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.sql.expression import update
from sqlalchemy import create_engine
import psycopg2

def make_celery(app):
    celery = Celery(
        name='tasks',
        #backend=app.config["CELERY_BACKEND_URL"],
        backend='db+postgresql://jjsalsnwqgzzrj:67f90487c651655f3bee4e9ea0f80e7362bf0d370274178b76e1e035cf3a297d@ec2-34-193-112-164.compute-1.amazonaws.com:5432/dge1pebnv4tda',
        result_backend='db+postgresql://jjsalsnwqgzzrj:67f90487c651655f3bee4e9ea0f80e7362bf0d370274178b76e1e035cf3a297d@ec2-34-193-112-164.compute-1.amazonaws.com:5432/dge1pebnv4tda',
        #cache='db+sqlite:///db.sqlite3',
        #broker='amqp://guest:@localhost:5672//',
        broker='amqps://nxkkxiyy:PhMB6k2UJ_jqKHrslJTZn44TbyEPY3YK@hornet.rmq.cloudamqp.com/nxkkxiyy',
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

app = Flask(__name__)
#app.config['CELERY_RESULT_BACKEND']=""
api = Api(app)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only
CORS(app)
# Heroku
#from flask_heroku import Heroku
#heroku = Heroku(app)


# ======== Celery =========================================================== #

celery = make_celery(app)


@celery.task(bind=True)
def get_image(self, arg):
    info, uri, txt, otext = smv.query(name=arg['name'], position=arg['position'],
                                      radius=arg['radius'], imagesopt=arg['imagesopt'], archives=arg['archives'])
    self.update_state(state='PROGRESS' or info,
                      meta={'txt': txt, 'otext': otext,
                            'uri': uri})
    return {'info': info, 'message': txt, 'url': uri, 'brieftext': otext}

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    return redirect(url_for('query'))

# -------- Task Status output ------------------------------------------------------------- #
@app.route('/status/<idv>')
def taskstatus(idv):
    task = get_image.AsyncResult(task_id=idv)
    if task.state == 'PENDING':
        info = {'info': 'processing'}
        return info, 202
    elif task.state == 'SUCCESS':
        info = task.info
        try:
            print("success")
            deleteRecord(task.id)
        except:
            print("record not found for task")
    else:
        info = task.info
    return info

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
            info, uri, txt, otext = smv.query(name,position,radius,archives,images)
            try :
                return jsonify([info,txt,uri,otext]) 
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
        arg = parse.parse_args()
        task = get_image.delay(arg)
        return {'Location': url_for('taskstatus', idv=task.id)}, 202
    def get(self):
        return redirect(url_for('query'))
api.add_resource(RGBMaker, '/api')


# ------------========------------ SQL function ---------=========---------#
def deleteRecord(tid):
    """
    deleting record of each task created by celery.
    """
    try:
        engine = create_engine(
            'postgresql://jjsalsnwqgzzrj:67f90487c651655f3bee4e9ea0f80e7362bf0d370274178b76e1e035cf3a297d@ec2-34-193-112-164.compute-1.amazonaws.com:5432/dge1pebnv4tda')
        conn = engine.connect()

        meta = MetaData()

        celery_taskmeta = Table(
            'celery_taskmeta', meta,
            Column('task_id', Integer, primary_key=True),
            Column('status', String),
        )
        sql_exec = celery_taskmeta.delete().where(
            celery_taskmeta.c.task_id == tid, celery_taskmeta.c.status == 'SUCCESS')
        #sql = """DELETE from celery_taskmeta where task_id=?"""
        conn.execute(sql_exec)
        conn.commit()
        conn.close()
        print("status : deleted")
    except sqlite3.Error as error:
        print("Failed to delete record from sqlite table", error)

def checkRecord(tid):
    """
    checking record of each task created by celery.
    """
    try:
        engine = create_engine('sqlite:///db.sqlite3')
        conn = engine.connect()

        meta = MetaData()

        celery_taskmeta = Table(
            'celery_taskmeta', meta,
            Column('task_id', Integer, primary_key=True),
            Column('status', String),
        )
        sql_exec = celery_taskmeta.select().where(
            celery_taskmeta.c.task_id == tid, celery_taskmeta.c.status == 'SUCCESS')
        #sql = """DELETE from celery_taskmeta where task_id=?"""
        conn.execute(sql_exec)
        conn.commit()
        conn.close()
    except sqlite3.Error as error:
        print("Failed to delete record from sqlite table", error)
        
# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=False, use_reloader=True)
