import json
from flask import Flask,jsonify,request

app = Flask(__name__)

@app.route('/',methods=['POST'])
def update_ip():
    ip_data = str(json.loads(request.data))
    with open('Data/ip.txt', 'w') as f:
        try:
            f.write(ip_data)
        except Exception as e:
            print(ip_data)
            return jsonify({'error': 'Invalid IP Provided'}), 400
    return '',201
    
@app.route('/',methods=['GET'])
def get_ip():
    with open('Data/ip.txt','r') as f:
        ip = f.read()
    print(f'Sent: {ip}')
    if ip == '' or ip is None:
        return 'IP not set', 400
    return ip

if __name__ == '__main__':
   app.run(port=5000)