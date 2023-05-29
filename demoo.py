from flask import Flask
from jaeger_client import Config
from opentracing.propagation import Format
from threading import Thread
import subprocess
import time

app = Flask(__name__)
task = None

# Configure the Jaeger client
config = Config(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
        'local_agent': {
            'reporting_host': '20.75.152.153',
            'reporting_port': 16686,
        },
    },
    service_name='my-flask-app',
    validate=True,
)
tracer = config.initialize_tracer()

# Define a route to generate some trace data
@app.route('/hello')
def hello():
    with tracer.start_active_span('hello') as scope:
        scope.span.log_kv({'event': 'hello'})
        return 'Hello, World!'
    
@app.route('/test1')
def test1():
    with tracer.start_active_span('test1') as scope:
        scope.span.log_kv({'event': 'test1'})
        return 'Hello, World!'

@app.route('/test2')
def test2():
    with tracer.start_active_span('test2') as scope:
        scope.span.log_kv({'event': 'test2'})
        return 'Hello, World!'

def send_curl_request():
    # Execute the cURL command
    subprocess.call(["curl", "http://localhost:8081/hello"]);
    subprocess.call(["curl", "http://localhost:8081/test1"]);
    subprocess.call(["curl", "http://localhost:8081/test2"]);

def background_task():
    # Run the loop indefinitely
    while True:
        send_curl_request()
        # Sleep for 60 seconds (1 minute)
        # time.sleep(60)

# Define a route for triggering the background task
@app.route('/start_task')
def start_task():
    global task
    # Check if the task is already running
    if task is None or not task.is_alive():
        # Start the background task
        task = Thread(target=background_task)
        task.start()
        return 'Task started'
    else:
        return 'Task is already running'
    
# Define a route for stopping the background task
@app.route('/stop_task', methods=['POST'])
def stop_task():
    global task  # Declare task as global
    # Check if the task is running
    if task is not None and task.is_alive():
        # Stop the background task
        task.stop()
        return 'Task stopped'
    else:
        return 'No task is running'


if __name__ == '__main__':
    app.run(port=8081,debug=True)