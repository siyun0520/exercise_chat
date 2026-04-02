from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# This will hold our messages
messages = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_message():
    # Get the message from the request
    message = request.json['message']
    # Store the message in the list
    messages.append(message)
    return jsonify(success=True)

@app.route('/messages', methods=['GET'])
def get_messages():
    # Return the list of messages as JSON
    return jsonify(messages)

if __name__ == '__main__':
    app.run(debug=True)
