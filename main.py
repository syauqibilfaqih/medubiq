import paho.mqtt.client as mqtt

# Define the callback function for when a message is received
def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")

# Create an MQTT client instance
client = mqtt.Client()

# Assign the callback function
client.on_message = on_message

# Connect to the MQTT broker
broker_address = "test.mosquitto.org"  # You can use any public MQTT broker or your own
client.connect(broker_address, 1883, 60)

# Subscribe to a topic
topic = "outTopic/message"
client.subscribe(topic)

# Start the loop to process received messages
client.loop_forever()