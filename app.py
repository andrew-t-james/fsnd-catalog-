from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Categories, Sports, User

# session imports for auth
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
import requests
import httplib2
import json

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Extreme Sports Application"

engine = create_engine('sqlite:///catalogue.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# api json endpoints
@app.route("/api/categories")
def categories_api():
    '''Returns a JSON Response for all categories in db'''
    category = session.query(Categories).all()
    return jsonify(Categories=[i.serialize for i in category])


@app.route("/api/sports")
def sports_api():
    '''Returns a JSON Response for all sports in db'''
    sports = session.query(Sports).all()
    return jsonify(Sports=[i.serialize for i in sports])


# routes for app
@app.route("/")
def index():
    '''Home Route returns a list of all Categories and Renders index page'''
    categories = session.query(Categories).all()
    return render_template("index.html", categories=categories)


@app.route("/sport/<int:sport_id>")
def sport_description(sport_id):
    '''Route for individual Winter Sports returns sportdescription page'''
    sport_id = session.query(Sports).filter_by(id=sport_id).first()
    return render_template("sportdescription.html", sport_id=sport_id)


@app.route("/<sport_season>")
def season(sport_season):
    '''Conditionally Render season page based on season'''
    if request.path == '/winter':
        sports = session.query(Sports).join(
            Categories).filter_by(id=1).all()
        return render_template("winter.html", sports=sports, season=sport_season)
    sports = session.query(Sports).join(
        Categories).filter_by(id=2).all()
    return render_template("summer.html", sports=sports, season=sport_season)


@app.route('/sport/new', methods=['GET', 'POST'])
def newMenuItem():
    '''Add new Sport Route using GET to render the form,
    POST to submit the new sport to the database'''
    if request.method == 'POST':
        new_sport = Sports(
            name=request.form['name'],
            description=request.form['description'],
            description_link=request.form['description_link'],
            image_link=request.form['image_link'],
            category_id=request.form['category_id'])

        session.add(new_sport)
        session.commit()
        # flash("new menu item created!")
        return redirect(url_for('index'))
    else:
        return render_template('newsport.html')


@app.route('/sport/<int:sport_id>/delete', methods=['GET', 'POST'])
def deleteSport(sport_id):
    '''Route search for and to Delete a specific sport from the database'''
    sport_to_delete = session.query(Sports).filter_by(id=sport_id).first()
    if request.method == 'POST':
        session.delete(sport_to_delete)
        session.commit()
        flash("Item deleted")
        return redirect(url_for('index', sport_id=sport_id))
    else:
        return render_template('deleteconfirm.html', sport=sport_to_delete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
