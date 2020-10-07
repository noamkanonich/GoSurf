from flask import Flask, render_template, request, jsonify
#import pandas as pd
import requests
import arrow
from datetime import datetime
import pycountry
#from StyleFrame import StyleFrame

app = Flask(__name__)

API_key = '379a56aac502394eae6dcdef5335cab7'
API_surf_key = 'd37556ee-14e9-11ea-8553-0242ac130002-d3755928-14e9-11ea-8553-0242ac130002'

weather_dic = {
                'Country':[],
                'City':[],
                'Weather': [],
                'Clouds': [],
                'Temperature': [],
                'Wind': [],
                'Humidity': [],
                'Sunrise': [],
                'Sunset': [],
                'Time': [],
                'Water Temperature': [],
                'Wave Height': [],
                'Wind Speed': [],
                'Best Time To Surf':[],
                'Highest Wave':[],
                'Surfer Level Stars':[],
                'Surfer Level':[],
                'Best Water Temp':[],
                'Best Air Temp':[],
                'Best Wind Speed':[]

                }

weather_dic_24hours = {
                'Date':[],
                'Time': [],
                'Water Temperature': [],
                'Air Temperature': [],
                'Humidity': [],
                'Visibility': [],
                'Wave Height': [],
                'Wind Speed': [],
                'Wave Direction': [],
                'Wave Period': [],
                'Sea Level': [],
                'Swell Direction': [],
                'Swell Height': [],
                'Swell Period': []
            }

def per_hour_forecast(json):
    i = 0
    while i < 24:
        data_time = json['hours'][i]['time']
        date = data_time[8:10]+'/'+data_time[5:7]
        time = data_time[11:16]
        weather_dic_24hours['Date'].insert(i, date)
        weather_dic_24hours['Time'].insert(i, time)
        weather_dic_24hours['Water Temperature'].insert(i, str(json['hours'][i]['waterTemperature'][1]['value'])+'°')
        weather_dic_24hours['Air Temperature'].insert(i, str(json['hours'][i]['airTemperature'][0]['value'])+'°')
        weather_dic_24hours['Wave Height'].insert(i, json['hours'][i]['waveHeight'][2]['value'])
        weather_dic_24hours['Wind Speed'].insert(i, str(json['hours'][i]['windSpeed'][0]['value'])[0:4]+' km/h')
        weather_dic_24hours['Humidity'].insert(i, str(json['hours'][i]['humidity'][0]['value']) + '%')
        weather_dic_24hours['Visibility'].insert(i, str(json['hours'][i]['visibility'][0]['value'])+' km')
        weather_dic_24hours['Sea Level'].insert(i, str(json['hours'][i]['seaLevel'][0]['value'])+' m')
        weather_dic_24hours['Wave Direction'].insert(i, str(json['hours'][i]['waveDirection'][0]['value'])+'°')
        weather_dic_24hours['Wave Period'].insert(i, str(json['hours'][i]['wavePeriod'][0]['value'])+'s')
        weather_dic_24hours['Swell Direction'].insert(i, str(json['hours'][i]['swellDirection'][0]['value'])+'°')
        weather_dic_24hours['Swell Period'].insert(i, str(json['hours'][i]['swellPeriod'][0]['value'])+'s')
        weather_dic_24hours['Swell Height'].insert(i, str(json['hours'][i]['swellHeight'][0]['value'])+' m')

        i = i + 1

def best_surfing_time(data):
    max_wave_height = data['hours'][0]['waveHeight'][2]['value']
    best_time = data['hours'][0]['time']
    best_water_temp = data['hours'][0]['waterTemperature'][1]['value']
    best_air_temp = data['hours'][0]['airTemperature'][0]['value']
    best_wind_speed = data['hours'][0]['windSpeed'][0]['value']
    i = 1
    while i < len(data['hours']):
        if i + 1 == len(data['hours']):
            if max_wave_height < data['hours'][i]['waveHeight'][2]['value']:
                max_wave_height = data['hours'][i]['waveHeight'][2]['value']
                best_time = data['hours'][i]['time']
                best_water_temp = data['hours'][i]['waterTemperature'][1]['value']
                best_air_temp = data['hours'][i]['airTemperature'][0]['value']
                best_wind_speed = data['hours'][i]['windSpeed'][0]['value']
                i = len(data['hours'])
                break
        else:
            if max_wave_height < data['hours'][i]['waveHeight'][2]['value']:
                max_wave_height = data['hours'][i]['waveHeight'][2]['value']
                best_time = data['hours'][i]['time']
                best_water_temp = data['hours'][i]['waterTemperature'][1]['value']
                best_air_temp = data['hours'][i]['airTemperature'][0]['value']
                best_wind_speed = data['hours'][i]['windSpeed'][0]['value']

        i = i + 1

    stars = ''
    level = ''
    if max_wave_height <= 1:
        stars = "3"
        level = "Beginner"
    elif max_wave_height > 1 and max_wave_height < 3:
        stars = "4"
        level = "Average"
    elif max_wave_height > 3:
        stars = "5"
        level = "Expert"

    return [max_wave_height, best_time, stars, level, best_water_temp, best_air_temp, best_wind_speed]

#run the main function
def the_weather(thecity):
        city = str(thecity)
        while True:
            url = 'http://api.openweathermap.org/data/2.5/weather?appid=' + '23ba5a3dca250d8bea422d026c3ce427' + '&q=' + city + '&units=metric'
            json_data = requests.get(url).json()

            if json_data['cod'] == '401':
                print('Invalid API key')
                break

            if city == '':
                break

            if json_data['cod'] == '404':
                print('City not found!')
                return '404'

            lat_coordinate = json_data['coord']['lat']
            lng_coordinate = json_data['coord']['lon']

            # Get first hour of today
            start = arrow.now().shift(hours=2)
            # Get last hour of today
            end = start.shift(hours=24)
            surf_response = requests.get(
                    'https://api.stormglass.io/v1/weather/point',
                    params={
                        'lat': lat_coordinate,
                        'lng': lng_coordinate,
                        'params': ','.join(['waveHeight', 'airTemperature', 'waterTemperature', 'windSpeed', 'windDirection', 'humidity', 'visibility',
                                            'seaLevel', 'waveDirection', 'wavePeriod', 'swellDirection', 'swellPeriod', 'swellHeight']),
                        'start': start.to('UTC').timestamp,  # Convert to UTC timestamp
                        'end': end.to('UTC').timestamp  # Convert to UTC timestamp
                    },
                    headers={
                        'Authorization': API_surf_key
                    }
                )

            json_data_surf = surf_response.json()
            country = pycountry.countries.get(alpha_2=json_data['sys']['country'])
            sunrise_time = str(datetime.utcfromtimestamp(json_data['sys']['sunrise']))
            sunset_time = str(datetime.utcfromtimestamp(json_data['sys']['sunset']))

            weather_dic['Country'].insert(0, country.name)
            weather_dic['City'].insert(0, json_data['name'])
            weather_dic['Weather'].insert(0, str(json_data['weather'][0]['main']))
            weather_dic['Clouds'].insert(0, json_data['weather'][0]['description'])
            weather_dic['Temperature'].insert(0, str(json_data['main']['temp'])+'°')
            weather_dic['Wind'].insert(0, str(json_data['wind']['speed']*3.6)[0:4]+' km/h')
            weather_dic['Humidity'].insert(0, str(json_data['main']['humidity'])+'%')
            weather_dic['Sunrise'].insert(0, sunrise_time)
            weather_dic['Sunset'].insert(0, sunset_time)

            data_time = json_data_surf['hours'][0]['time']
            weather_dic_24hours['Date'].append(data_time[8:10]+'/'+data_time[5:7])
            weather_dic_24hours['Time'].append(data_time[11:16])
            weather_dic_24hours['Water Temperature'].append(str(json_data_surf['hours'][0]['waterTemperature'][1]['value']) + '°')
            weather_dic_24hours['Wave Height'].append(str(json_data_surf['hours'][0]['waveHeight'][2]['value']))
            weather_dic_24hours['Wind Speed'].append(str(json_data_surf['hours'][0]['windSpeed'][0]['value'])[0:4] + ' km/h')
            weather_dic_24hours['Humidity'].append(str(json_data_surf['hours'][0]['humidity'][0]['value'])+'%')
            weather_dic_24hours['Visibility'].append(str(json_data_surf['hours'][0]['visibility'][0]['value'])+' km')
            weather_dic_24hours['Sea Level'].append(str(json_data_surf['hours'][0]['seaLevel'][0]['value'])+' m')
            weather_dic_24hours['Wave Direction'].append(str(json_data_surf['hours'][0]['waveDirection'][0]['value'])+'°')
            weather_dic_24hours['Wave Period'].append(str(json_data_surf['hours'][0]['wavePeriod'][0]['value'])+'s')
            weather_dic_24hours['Swell Direction'].append(str(json_data_surf['hours'][0]['swellDirection'][0]['value'])+'°')
            weather_dic_24hours['Swell Period'].append(str(json_data_surf['hours'][0]['swellPeriod'][0]['value'])+'s')
            weather_dic_24hours['Swell Height'].append(str(json_data_surf['hours'][0]['swellHeight'][0]['value'])+' m')

            date = best_surfing_time(json_data_surf)[1]
            weather_dic['Best Time To Surf'].insert(0, date[8:10]+'/'+date[5:7] + ', ' + date[11:16])
            weather_dic['Highest Wave'].insert(0, best_surfing_time(json_data_surf)[0])
            weather_dic['Surfer Level Stars'].insert(0, str(best_surfing_time(json_data_surf)[2])+'x')
            weather_dic['Surfer Level'].insert(0, str(best_surfing_time(json_data_surf)[3]))
            weather_dic['Best Water Temp'].insert(0, str(best_surfing_time(json_data_surf)[4])+'°')
            weather_dic['Best Air Temp'].insert(0, str(best_surfing_time(json_data_surf)[5])+'°')
            weather_dic['Best Wind Speed'].insert(0, str(best_surfing_time(json_data_surf)[6])[0:4]+' km/h')

            per_hour_forecast(json_data_surf)
            return

#the home page of the app
@app.route('/')
def welcome():
     return render_template("welcome.html")

@app.route('/back' ,methods=['POST'])
def back():
    if request.method == 'POST':
            the_weather(weather_dic['City'])
            weather = {
                'Country': weather_dic['Country'],
                'City': weather_dic['City'],
                'Weather': weather_dic['Weather'],
                'Clouds': weather_dic['Clouds'],
                'Temperature': weather_dic['Temperature'],
                'Wind': weather_dic['Wind'],
                'Humidity': weather_dic['Humidity'],
                'Sunrise': weather_dic['Sunrise'],
                'Sunset': weather_dic['Sunset'],
                'Best Time To Surf': weather_dic['Best Time To Surf'],
                'Highest Wave': weather_dic['Highest Wave'],
                'Best Water Temp': weather_dic['Best Water Temp'],
                'Best Air Temp': weather_dic['Best Air Temp'],
                'Best Wind Speed': weather_dic['Best Wind Speed'],
                'Surfer Level Stars': weather_dic['Surfer Level Stars'],
                'Surfer Level': weather_dic['Surfer Level']
            }

            weather_table = {
                'Date': weather_dic_24hours['Date'],
                'Time': weather_dic_24hours['Time'],
                'Water Temperature': weather_dic_24hours['Water Temperature'],
                'Air Temperature': weather_dic_24hours['Air Temperature'],
                'Wave Height': weather_dic_24hours['Wave Height'],
                'Wind Speed': weather_dic_24hours['Wind Speed']
            }
            return render_template("home.html", weather=weather, weather_table=weather_table)

    else:
        return render_template("city.html")

    return render_template("home.html", weather=weather, weather_table=weather_table)

@app.route('/forecast', methods=['POST'])
def forcast():
    weather = {
        'Country': weather_dic['Country'],
        'City': weather_dic['City'],
        'Humidity': weather_dic_24hours['Humidity'],
    }

    weather_table = {
                'Date': weather_dic_24hours['Date'],
                'Time': weather_dic_24hours['Time'],
                'Water Temperature': weather_dic_24hours['Water Temperature'],
                'Air Temperature': weather_dic_24hours['Air Temperature'],
                'Wave Height': weather_dic_24hours['Wave Height'],
                'Wave Direction': weather_dic_24hours['Wave Direction'],
                'Wave Period' : weather_dic_24hours['Wave Period'],
                'Wind Speed': weather_dic_24hours['Wind Speed'],
                'Visibility' : weather_dic_24hours['Visibility'],
                'Sea Level': weather_dic_24hours['Sea Level'],
                'Swell Direction': weather_dic_24hours['Swell Direction'],
                'Swell Height': weather_dic_24hours['Swell Height'],
                'Swell Period': weather_dic_24hours['Swell Period']
    }
    return render_template("forcast.html", weather=weather, weather_table=weather_table)


@app.route('/city', methods=['GET','POST'])
def home():
    if request.method == 'POST':
            new_city = request.form['new_city']
            if new_city == '':
                return render_template("welcome.html")
            cod = the_weather(new_city)
            if cod == '404':
                return render_template("welcome.html")

            weather = {
                'Country': weather_dic['Country'],
                'City': weather_dic['City'],
                'Weather': weather_dic['Weather'],
                'Clouds': weather_dic['Clouds'],
                'Temperature': weather_dic['Temperature'],
                'Wind': weather_dic['Wind'],
                'Humidity': weather_dic['Humidity'],
                'Sunrise': weather_dic['Sunrise'],
                'Sunset': weather_dic['Sunset'],
                'Best Time To Surf': weather_dic['Best Time To Surf'],
                'Highest Wave': weather_dic['Highest Wave'],
                'Best Water Temp': weather_dic['Best Water Temp'],
                'Best Air Temp': weather_dic['Best Air Temp'],
                'Best Wind Speed': weather_dic['Best Wind Speed'],
                'Surfer Level Stars': weather_dic['Surfer Level Stars'],
                'Surfer Level': weather_dic['Surfer Level']
            }

            weather_table = {
                'Date': weather_dic_24hours['Date'],
                'Time': weather_dic_24hours['Time'],
                'Water Temperature': weather_dic_24hours['Water Temperature'],
                'Air Temperature': weather_dic_24hours['Air Temperature'],
                'Wave Height': weather_dic_24hours['Wave Height'],
                'Wind Speed': weather_dic_24hours['Wind Speed']
            }
            return render_template("home.html", weather=weather, weather_table=weather_table)

    else:
        return render_template("city.html")

    return render_template("home.html", weather=weather, weather_table=weather_table)


if __name__ == "__main__":
    app.run(debug=True)
