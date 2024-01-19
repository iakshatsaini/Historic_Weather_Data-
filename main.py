import json
from flask import Flask, jsonify, request
from passlib.hash import pbkdf2_sha256
from db_helper import register_user, user_authentication
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import requests

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'secretKey' 
jwt = JWTManager(app)


@app.route('/')
def index():
    return {"message":"API is Working", "status":200}

@app.route('/user', methods = ['POST'])
def user_registration():
    if request.method == 'POST':
        response_dict = {}
        try:
            username = request.json['username']
            password = request.json['password']
            
            if username and password: 
                hashed_password = pbkdf2_sha256.hash(password)
                response_dict = register_user(username, hashed_password)  
            else:
                response_dict = {"message":"username or password is missing, Please check", "status":400}
            return response_dict, response_dict["status"]
        except Exception as e:
            print(e)
            return {"message":"Internal Server Error", "status":500}, 500
        
@app.route('/authentication', methods = ['POST'])
def authentication():
    if request.method == 'POST':
        response_dict = {}
        try:
            username = request.json['username']
            password = request.json['password']
            
            if username and password:
                response_dict = user_authentication(username, password)
                if 'error' not in response_dict:
                    access_token = create_access_token(identity={'username': response_dict.get('userName')})
                    return jsonify(access_token=access_token), 200
            else:
                response_dict = {"message":"username or password is missing, Please check", "status":400}
            return response_dict, response_dict["status"]
        except Exception as e:
            return {"message":"Internal Server Error", "status":500}, 500


@app.route('/secure/endpoint', methods=['GET'])
@jwt_required()
def secure_endpoint():
    try:
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200
    except Exception as e:
        return {"message":"Internal Server Error", "status":500}, 500


@app.route('/historic-weather', methods=['GET'])
def get_historic_weather():
    try:
        # Get parameters from the request
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        num_days = int(request.args.get('num_days'))

        # Prepare parameters for Open Meteo API
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m',
            'past_days': num_days,
        }
        
        response = requests.get(url = f"https://api.open-meteo.com/v1/forecast", params=params)
        raw_data = json.loads(response.text)
        print(raw_data)
        if 'error' not in raw_data:
            time_list = raw_data['hourly']['time']
            temperature_list = raw_data['hourly']['temperature_2m']
            humidity_list = raw_data['hourly']['relative_humidity_2m']
            wind_speed_list = raw_data['hourly']['wind_speed_10m']

            # Creating a list of dictionaries
            weather_data_list = []

            for i in range(len(time_list)):
                weather_data_list.append({
                    'time': time_list[i],
                    'temperature': temperature_list[i],
                    'humidity': humidity_list[i],
                    'wind_speed': wind_speed_list[i]
                })
            return {"historicData":weather_data_list,"status":200}
        else:
            return {"message":"No data found on these input", "status":404}
    except Exception as e:
        return {"message":"Internal Server Error", "status":500}, 500


if __name__ == '__main__':
    app.run(debug = True)