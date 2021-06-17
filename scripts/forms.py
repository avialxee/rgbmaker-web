# -*- coding: utf-8 -*-

from wtforms import Form, StringField, validators, DecimalField, SelectField, BooleanField


class LoginForm(Form):
    username = StringField('Username:', validators=[validators.required(), validators.Length(min=1, max=30)])
    password = StringField('Password:', validators=[validators.required(), validators.Length(min=1, max=30)])
    email = StringField('Email:', validators=[validators.optional(), validators.Length(min=0, max=50)])

class QueryForm(Form) :
    name = StringField('Name',render_kw={"placeholder": "Name"}, validators=[validators.optional(), validators.Length(min=2, max=30)])
    position = StringField('Position',render_kw={"placeholder": "Position"}, validators=[validators.required(), validators.Length(min=2, max=30)])
    radius = DecimalField('Radius',render_kw={"placeholder": "Radius"},places=2, validators=[validators.required()],default=0.12)
    archives = SelectField(u'Archives ', choices=[(1, 'None'), (2, 'NVAS')])
    images = SelectField(u'Images ', choices=[(1, 'IOU ROR Optical'), (2, 'Composite contours on DSS2R'),(3,'None')])
    #submit = SubmitField('query')
