import requests

BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "test"
CITY = "Vienna"

url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY


def kelvinToCelsius(kelvin):
    celsius = kelvin - 273.15
    return celsius


def hPAToBar(hPA):
    bar = hPA/1000
    return bar


response = requests.get(url).json()

temp_curr_kelvin = response["main"]["temp"]
temp_max_kelvin = response["main"]["temp_max"]
temp_min_kelvin = response["main"]["temp_min"]

humi = response["main"]["humidity"]
press_hPA = response["main"]["pressure"]

temp_curr_celsius = round(kelvinToCelsius(temp_curr_kelvin), 2)
temp_max_celsius = round(kelvinToCelsius(temp_max_kelvin), 2)
temp_min_celsius = round(kelvinToCelsius(temp_min_kelvin), 2)

press_bar = hPAToBar(press_hPA)

print("Current Temperature:", temp_curr_celsius)
print("Max Temperature:", temp_max_celsius)
print("Min Temperature:", temp_min_celsius)
print("Humidity:", humi)
print("Pressure:", press_bar)
