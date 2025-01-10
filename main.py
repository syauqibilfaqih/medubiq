import paho.mqtt.client as mqtt
import dash 
from dash import dcc, html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import deque
from datetime import datetime
import re 

# Data Buffer 
MAX_LENGTH = 500

#rolling data in double ended queue -> pop left when 500 reached 
time_data = deque(maxlen=MAX_LENGTH)
force_data = deque(maxlen=MAX_LENGTH)
ax_data = deque(maxlen=MAX_LENGTH)
ay_data = deque(maxlen=MAX_LENGTH)
az_data = deque(maxlen=MAX_LENGTH)

#MQTT - fixed vars
broker_address = "test.mosquitto.org"
topic = "outTopic/message"


# Define the callback function for when a message is received
def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")

    payload_str = message.payload.decode()

    if payload_str.startswith("s;") and payload_str.endswith(";e"):
        trimmed = payload_str[2:-2]
        parts = trimmed.split(';')
        if len(parts) == 4:
            try: 
                force_val = float(parts[0])
                ax_val = float(parts[1])
                ay_val = float(parts[2])
                az_val = float(parts[3])
                now = datetime.now()

                time_data.append(now)
                force_data.append(force_val)
                ax_data.append(ax_val)
                ay_data.append(ay_val)
                az_data.append(az_val)
            except ValueError:
                print("payload not converted to float", parts) 
    else:
        print("Received not our message format", payload_str)


# Create an MQTT client instance
mqtt_client = mqtt.Client()

# Assign the callback function
mqtt_client.on_message = on_message

mqtt_client.connect(broker_address, 1883, 60)

# Subscribe 
mqtt_client.subscribe(topic)

# Start the loop to process received messages
# mqtt_client.loop_forever() # loop forever is blocking behaviour, lets use loop_start (starts new thread) 

# Now Dash setup idfk if this works 
app= dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Particle Acc and Force Sensor Data"),
    dcc.Graph(id='live-graph'), # animate=True),

    dcc.Interval(
        id='graph-update',
        interval=500, # 500 ms per update -> increase when we increase fireing rate of particle 
        n_intervals=0
    )
])

@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)


def update_graph_live(n):
    """
    trigger this callback periodicall by dcc Inteval
    contruct plotly fig using latest sensor data from global deques
    """

    t= list(time_data) # time data to list

    trace_force = go.Scatter(
        x=t,
        y=list(force_data),
        name='Force',
        mode='lines+markers'
    )

    trace_ax = go.Scatter(
        x=t,
        y=list(ax_data),
        name='Ax',
        mode='lines+markers' # markers maybe unnecessary
    )
    trace_ay = go.Scatter(
        x=t,
        y=list(ay_data),
        name='Ay',
        mode='lines+markers'
    )
    trace_az = go.Scatter(
        x=t,
        y=list(az_data),
        name='Az',
        mode='lines+markers'
    )

    layout = go.Layout(
        title="real time",
        xaxis=dict(title='Time'),
        yaxis=dict(title='Force/Acc'),
        hovermode='x unified'
    )
    
    fig = go.Figure(data=[trace_force, trace_ax, trace_ay, trace_az], 
                    layout=layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

# run by python .\main.py as usual then copy paste the url to browser
# got the warning that we should use latest Callback API version cause this one is depreceted -> had no time to look into TODO !