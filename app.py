from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
# from dotenv import load_dotenv
import requests
import os
import json
import datetime
# load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'secretkey'
api_key = os.environ.get("WEATHER_API_KEY")
from_local = os.environ.get('WEATHER_API_KEY')
print('from_local:', from_local)

now = datetime.datetime.now()
current = now.strftime("%d-%m-%Y | %H:%M")
print('time', current)


db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID=13a432c7ce08aac8c299c70328d711f8'
    r = requests.get(url).json()
    return r


@app.route('/')
def show_weather():
    cities = City.query.all()

    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)

        weather = {
            'id': city.id,
            'city': city.name,
            'temp': str(int(round(r['main']['temp']))),
            'min': str(int(round(r['main']['temp_min']))),
            'max': str(int(round(r['main']['temp_max']))),
            'desc': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }

        weather_data.append(weather)

    return render_template('index.html', weather_data=weather_data[::-1], current=current)


@app.route('/', methods=['POST'])
def add_city():
    user_input = request.form.get('city')
    if user_input:
        check_city = City.query.filter_by(name=user_input).first()

    if not check_city:
        new_city_data = get_weather_data(user_input)
        if new_city_data['cod'] != '404':
            new_city = City(name=user_input)
            db.session.add(new_city)
            db.session.commit()
            return redirect(url_for('show_weather'))
        flash(
            f'{user_input} is not a valid city. Please enter valid city', category='danger')
        return redirect(url_for('show_weather'))
    flash('City already exists!', category='info')
    return redirect(url_for('show_weather'))


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    city_to_delete = City.query.get(id)
    db.session.delete(city_to_delete)
    db.session.commit()
    flash(f'{city_to_delete.name} deleted!', category='success')
    return redirect(url_for('show_weather'))


if __name__ == '__main__':
    app.run(debug=True)
