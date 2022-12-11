import pymongo
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
from dotenv import dotenv_values

config = dotenv_values("src/.env")

# Connect to the MongoDB database
client = pymongo.MongoClient(config["MONGODB_URL"])
db = client["ESP32DB"]
dataC = db["data"]

# Get the temperature data from the "temperature" collection
tmp = []
temp = []
for x in dataC.find({"sensor": "BME680"}):
    tmp.append(x)
temp = tmp[-1]

# Create a SkillBuilder object
sb = SkillBuilder()


class GetTemperatureIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # return true if the intent name is "GetTemperatureIntent"
        return is_intent_name("GetTemperatureIntent")(handler_input)

    def handle(self, handler_input):
        # Loop through the temperature data and get the most recent record
        tmp = []
        for x in dataC.find({"sensor": "BME680"}):
            tmp.append(x)
        current_temp = tmp[-1]["temp"]

        # Create a response that includes the temperature data
        speech_text = f"The current temperature is {current_temp} degrees."
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Temperature", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response


# Register the intent handler
sb.add_request_handler(GetTemperatureIntentHandler())

# Create an AWS Lambda function
lambda_handler = sb.lambda_handler()
