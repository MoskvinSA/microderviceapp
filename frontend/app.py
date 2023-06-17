import dash
from dash import html, dcc
import pika
import json
import os

userName = 'user'
userPassword = 'password'
hostToConnect = os.environ.get('RABBITMQ_ADDRES')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div(dcc.Input(id='input-box-1', type='text')),
    html.Button('service_word', id='button-example-1'),
    html.Div(id='output-container-button-1',
             children='Enter a value and press submit'),
    
    html.Div(dcc.Input(id='input-box-2', type='number')),
    html.Button('service_number', id='button-example-2'),
    html.Div(id='output-container-button-2',
             children='Enter a value and press submit')
])

def connect_rabbitmq():
    credentials = pika.PlainCredentials(userName, userPassword)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            hostToConnect, 
            5672,
            '/',
            credentials
        )
    )
    return connection

def producer(_body, queueName):
    connection = connect_rabbitmq()
    channel = connection.channel()    
    if (_body):
        channel.queue_declare(queue=queueName, durable=True)
        channel.basic_publish(exchange='',
                                routing_key=queueName,
                                body= json.dumps(_body),
                                properties=pika.BasicProperties(
                                    content_type='application/json'
                                ))
    channel.close()
    connection.close()

@app.callback(
    dash.dependencies.Output('output-container-button-1', 'children'),
    [dash.dependencies.Input('button-example-1', 'n_clicks')],
    [dash.dependencies.State('input-box-1', 'value')])
def update_output_word(n_clicks, value):
    if (n_clicks and value):
        producer({n_clicks : value}, "word")
        return 'The input value was "{}" and the button has been clicked {} times'.format(
            value,
            n_clicks
        )

@app.callback(
    dash.dependencies.Output('output-container-button-2', 'children'),
    [dash.dependencies.Input('button-example-2', 'n_clicks')],
    [dash.dependencies.State('input-box-2', 'value')])
def update_output(n_clicks, value):
    if (n_clicks and value):
        producer({n_clicks : value}, "number")
        return 'The input value was "{}" and the button has been clicked {} times'.format(
            value,
            n_clicks
        )

if __name__ == '__main__':
    app.run_server(host=os.environ.get('FRONT_ADDR'),  port=8050)