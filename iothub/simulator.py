import random
import time
import threading
import sys
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

CONNECTION_STRING = "{Your IoT hub device connection string}"
CPU_USAGE = 0.0
MEMORY_USAGE = 0.0
INTERVAL = 1
DEVICE_STATUS = 0 # 0: OK, 1: Warn , 2: Alert

def init_client():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

def event_listener(client):
    global DEVICE_STATUS

    while True:
        req = client.receive_method_request()
        print(f'Received event => Method = {req.name}, Payload = {req.payload}')

        if req.name == 'SetDeviceStatus':
            try:
                DEVICE_STATUS = int(req.payload)
            except ValueError:
                res_payload = {'Response': 'Invalid payload'}
                res_status = 400
            else:
                res_payload = {'Response': f'Method "{req.name}" is excuted'}
                res_status = 200
        else:
            res_payload = {'Response': f'Method "{req.name}" is not defined'}
            res_status = 404

        res = MethodResponse(req.request_id, res_status, payload=res_payload)
        client.send_method_response(res)

def run_device():
    try:
        client = init_client()
        print("This device is sending messages periodically, press Ctrl-C to exit.")
        
        event_listener_thread = threading.Thread(target=event_listener, args=(client,))
        event_listener_thread.daemon = True
        event_listener_thread.start()

        while True:
            if DEVICE_STATUS == 1:
                print('[Warn] Device is overloaded.')
            elif DEVICE_STATUS == 2:
                print('[Alert] Device will be stopped in 10 sec cause of overload.')
                break

            cpu = CPU_USAGE + random.randrange(1, 100)
            memory = MEMORY_USAGE + random.randrange(1, 100)
            msg = Message(f'{{"cpu": {cpu}, "memory": {memory}}}')

            client.send_message(msg)
            print(f'Message sent: {msg}')
            time.sleep(INTERVAL)

        time_wait = 10
        while time_wait > 0:
            print(f'Count: {time_wait}')
            time_wait = time_wait - 1
            time.sleep(1)

        sys.exit(0)

    except KeyboardInterrupt:
        print('Device is stopped cause of keyboard interrupt.')

if __name__ == '__main__':
    run_device()
