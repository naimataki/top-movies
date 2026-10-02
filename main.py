from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv

load_dotenv()

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

API_KEY = os.environ["API_KEY"]
AUTHORIZATION = os.environ["API_KEY"]
url = 'https://api.themoviedb.org/3/search/movie'

headers = {
    "accept": "application/json",
    "Authorization": AUTHORIZATION
}

response = requests.get(url, headers=headers)

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB

class Base(DeclarativeBase):
    pass
 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String)
    rating: Mapped[float] = mapped_column(Float)
    ranking: Mapped[int] = mapped_column(Integer)
    review: Mapped[str] = mapped_column(String)
    img_url: Mapped[str] = mapped_column(String)
 
with app.app_context():
    db.create_all()

class RateMovieForm(FlaskForm):
    rating = FloatField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddMovieForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

# create record
#with app.app_context():
#    new_movie = Movie(
#    title="Phone Booth",
#    year=2002,
#    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#    rating=7.3,
#    ranking=10,
#    review="My favourite character was the caller.",
#    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#)
#    db.session.add(new_movie)
#    db.session.commit()

#with app.app_context():
#    second_movie = Movie(
#        title="Avatar The Way of Water",
#        year=2022,
#        description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#        rating=7.3,
#        ranking=9,
#        review="I liked the water.",
#        img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
#    )
#    db.session.add(second_movie)
#    db.session.commit()

@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.title))
    all_movies = result.scalars().all()
    return render_template('index.html', movies=all_movies)

@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        headers = {
            "accept": "application/json",
            "Authorization": AUTHORIZATION
        }
        body = {
            'query': movie_title,
        }
        response = requests.get(url, headers=headers, data=body)
        results = response.json()["results"]
        #new_movie = Movie(title=request.title.data)
        #db.session.add(new_movie)
        #db.session.commit()
        return render_template('select.html', results=results)
    return render_template('add.html', form=form)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = RateMovieForm()
    if form.validate_on_submit():
        movie_id = request.args.get('id')
        movie_to_update = db.get_or_404(Movie, movie_id)
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    movie_id = request.args.get('id')
    movie_selected = db.get_or_404(Movie, movie_id)
    return render_template('edit.html', form=form, movie=movie_selected)

@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    # DELETE A RECORD BY ID
    movie_to_delete = db.get_or_404(Movie, movie_id)
    # Alternative way to select the movie to delete.
    # movie_to_delete = db.session.execute(db.select(movie).where(movie.id == movie_id)).scalar()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
