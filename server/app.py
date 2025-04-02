from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    messages = []
    if request.method == 'GET':
        records = Message.query.order_by(Message.created_at.desc()).all()
        for message in records:
            message_dict = message.to_dict()
            messages.append(message_dict)
            response = make_response(
                messages,
                200
            )

        return response

    elif request.method == 'POST':

        data = request.get_json()  

        if not data or "body" not in data or "username" not in data:
            return jsonify({"error": "Missing body or username"}), 400

        new_message = Message(body=data["body"], username=data["username"])
        db.session.add(new_message)
        db.session.commit()

        return jsonify({
            "id": new_message.id,
            "body": new_message.body,
            "username": new_message.username,
            "created_at": new_message.created_at.isoformat()
        }), 201  
    


    

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    if request.method == 'PATCH':
        data = request.get_json()

        if not data or "body" not in data:
            return jsonify({'error': 'Missing body'}), 400
        
        message.body = data["body"]
        
        db.session.commit()

        return jsonify({
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "updated_at": message.updated_at.isoformat()
        }), 200  

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return jsonify({'message': 'Message deleted successfully'}), 200
if __name__ == '__main__':
    app.run(port=5555)
