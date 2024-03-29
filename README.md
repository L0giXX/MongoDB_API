# DIPLOMA THESIS 2022/23

## Smart Monitoring Dashboard

My part of the diploma thesis is the development of an API, which is using MongoDB as the database. The code is written in Python and I am using the popular Web-Framework FastAPI.

### Functions

- Saving sensor data from ESP32 into database
- Getting data from database to visiualize it 
- Register/Login user
- Requesting current weather from https://home.openweathermap.org/
  
  

### Using the API

Activate your Python virtual environment and change the MongoDB URL with your MongoDB connection string. It is highly recommended to use a .env file for security reasons.

```python
# Install the requirements:
pip install -r requirements.txt

# Configure the location of your MongoDB database:
# If you are using a .env file (recommended):
client = pymongo.MongoClient(config["MONGODB_URL"])
# If you have the MongoDB URL hardcoded:
client = pymongo.MongoClient("MONGODB_URL")

# Configure the openweathermap URL:
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"

# If you are using a .env file (recommended):
API_KEY = config["API_KEY"]
# If you have the openweather API KEY hardcoded:
API_KEY = "API_KEY"
# Choose your city:
CITY = "Vienna"
url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY

# Start the service:
uvicorn src.main:app --reload
```

Now you can start testing the different requests via Postman or Thunderclient.



### Deploying the API

First of all if you want to use the API you need to deploy it on a server. Therefore you need to configure a dockerfile. This is used to isolate the files and build an image.  The dockerfile code can be seen at /docker/dockerfile. 

- Install Docker Desktop

- 2 new folders /docker/app

- Copy the Python files from src into /docker/app

- Make a new dockerfile in /docker

- Copy requirements.txt into /docker

```python
# Create a docker account 
# Login at https://hub.docker.com/ and create a new repository
# Paste the commands into a terminal, while docker desktop is being used
# Change username and repository with your data and press ENTER
# This will start building the image and commit it to your repository

docker build -t {username/repository} docker
docker push {username/repository}
```

If the build was successful you will find the image in your docker repository. Then you can deploy the image on your server and start using the API.
