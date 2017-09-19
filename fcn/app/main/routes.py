import os
from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user
from ..models import User
from . import main
from .forms import LoginForm
from .upload_csv import UploadForm
from .modelingform import NewModelForm, SelectModelForm
from .select_create_model import Createnewmodel, Selectmodel
from random import choice
from bokeh.plotting import figure
from bokeh.resources import CDN, INLINE
from bokeh.embed import file_html, components
from bokeh.models import HoverTool #for enabling tools
import os



@main.route('/login', methods=['GET', 'POST'])
@main.route('/login/<int:exists>', methods=['GET','POST'])
def login(exists=True):
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            return redirect(url_for('main.login',exists=False))
        login_user(user, form.remember_me.data)
       
        return redirect(request.args.get('next') or url_for('main.index'))
    print exists
    return render_template('login.html', form=form,exists=exists)


@main.route('/register',methods=['GET','POST'])
@main.route('/register/<int:exists>', methods=['GET','POST'])
def register(exists=False):
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is not None:
            return redirect(url_for('main.register',exists=True))
        user=form.username.data
        password=form.password.data
        User.register(user,password)
        return redirect(url_for('main.login'))
    print exists
    return render_template('register.html',form=form,exists=exists)

tables=" "
pagination=" "
loans=" "
predict_data=" "
predict_tables=" "
predict_pagination=" "
selected_file_data=" "
probability_data=" "
@main.route('/preprocess', methods=['GET','POST'])
@main.route('/preprocess/<int:page>', methods=['GET','POST'])
@login_required
def preprocess(page=1):
    global tables,pagination,loans
    form = UploadForm()
    if request.method=='POST' and request.files['csv_file']:
        f=form.csv_file.data.stream
        tables,pagination,loans=form.show_tables(f,form)
        print "first data captured"

    elif tables!=" ":
        tables,pagination=UploadForm().csv_paginate(page)
    return render_template('preprocess.html',tables=tables,pagination=pagination,form=form)         

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/modeling')
@login_required
def modeling():
    return render_template('modeling.html')

@main.route('/createmodel', methods=['GET','POST'])
@login_required
def createmodel():
    accuracy=None

    form=NewModelForm()
    if request.method == 'POST' and loans is not " ":
        return redirect(url_for('main.results',modelname=form.modelname.data,target=form.identifier.data))
    message=request.args.get('')
    return render_template('createmodel.html',form=form,accuracy=accuracy)

@main.route('/selectmodel',methods=['GET','POST'])
@main.route('/selectmodel/<int:page>', methods=['GET','POST'])
@login_required
def selectmodel(page=1):
    global predict_data,predict_tables,predict_pagination,selected_file_data,probability_data
    form = SelectModelForm()
    select_model=Selectmodel()
    if request.method=="POST":
        model_name=form.modelName.data
        probability_value=form.probability_value.data
        
        if request.files['csv_file'] and model_name and probability_value:
            f=form.csv_file.data.stream
            print "with_POST_if"
            predict_tables,predict_pagination,predict_data,probability_data,selected_file_data=select_model.predicted_data(f,model_name,probability_value)

        elif selected_file_data is not " " and model_name and probability_value:
            print "with_post_elif"
            predict_tables,predict_pagination,predict_data,selected_file_data=select_model.predicted_prob_change_data(selected_file_data,probability_data,model_name,probability_value)

    elif predict_tables!=" ":
        predict_tables,predict_pagination=select_model.csv_paginate(predict_data,page)
        print "just_elif_selectmodel"
    #print saved_models_dict
    saved_models= os.listdir(os.path.join('static','models'))
    form.modelName.choices=[(j,j) for i ,j in enumerate(saved_models) ]
    return render_template("selectmodels.html", tables=predict_tables,pagination=predict_pagination,form=form)


@main.route('/results')
@login_required
def results():
    global loans
    modelname=request.args.get('modelname')
    target=request.args.get('target')
    accuracy=None
    precision=None
    recall=None
    model=Createnewmodel()
    js_resources = None
    css_resources = None
    script=None
    div = None
    if loans is not " ":
        precision,recall,accuracy=model.data_prepare(loans,modelname,target)
        hover=HoverTool(tooltips=[("index","$index"),("(precision,recall)","($x,$y)"),
        ])
        fig = figure(plot_width=400, plot_height=400,tools=[hover],title="Precision_Recall_curve")
        fig.line(precision, recall, color='blue', line_width=2)
        fig.xaxis.axis_label=" precision"
        fig.yaxis.axis_label=" recall"
        # Configure resources to include BokehJS inline in the document.
        # For more details see:
        #   http://bokeh.pydata.org/en/latest/docs/reference/resources_embedding.html#bokeh-embed
        print "ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
        # For more details see:
        #   http://bokeh.pydata.org/en/latest/docs/user_guide/embedding.html#components
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()
        script, div = components(fig, INLINE)
    return render_template('createmodel.html',form=None,
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        accuracy=accuracy)

@main.route('/visualize')
@login_required
def visualize():
    return redirect(url_for('main.index'))