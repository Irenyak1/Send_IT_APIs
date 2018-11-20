import re
import json
from flask import jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt_identity)
from app import app
from app.models.parcel_model import Parcel, parcels
from app.models.users_model import *
from app.models.item_model import Item
from app.validator import Validator
from app.controllers.db import DatabaseConnection

db = DatabaseConnection()

class Parcel_Controller:

    def index():
        """Index page"""
        return """parcels ==>
        <a href="https://send-it-api-app.herokuapp.com/api/v1/parcels">
        Navigate to this link to interact with the API</a><br><br>
        """

    def get_parcels():
        """Retrieve all parcels"""     
        current_user = get_jwt_identity()
        if current_user == 'admin':
            parcels = db.get_all_parcels()
            if len(parcels) >= 1 :
                return jsonify({"parcels": parcels}), 200
            return jsonify({'message':'There are no parcel delivery orders'}), 200
        return jsonify({'message':'Invalid request! login or use the right access token'})


    def get_parcels_by_user(user_id):
        """Retrieve all parcels by a specific user"""
        current_user = get_jwt_identity()
        parcels = db.get_all_parcels()
        if current_user == 'admin' or current_user == parcels[2]:
            char_set = re.compile('[A-Za-z]')
            if not char_set.match(user_id):
                return jsonify({'message':'Enter a valid user name'}), 400
            parcels_by_user = db.get_parcels_by_user(user_id)
            if parcels_by_user is not None:
                return jsonify({"parcel(s)":parcels}), 200
            return jsonify({'message':f"There are no parcels delivery orders created by {user_id}"}), 200
        return jsonify({'message':'Invalid request! login or use the right access token'}), 400


    def get_parcel(parcel_id):
        """Retrieve a particular parcel"""
        current_user = get_jwt_identity()
        parcel = db.get_a_parcel(parcel_id)
        if current_user == 'admin' or current_user == parcel[1]:
            if parcel is not None:
                return jsonify({"parcel":parcel}), 200
            return jsonify({'message': f"Parcel with ID {parcel_id} does not exist"}), 200
        return jsonify({'message': f"You do not have access to parcel delivery order {parcel_id}"}), 400

    def change_present_location(parcel_id):
        """Change the present location of a parcel delivery order"""
        current_user = get_jwt_identity()
        user_input = request.get_json(force=True) 

        parcel = db.get_a_parcel(parcel_id)
        if parcel is not None:
            if current_user == 'admin':
                present_location = user_input.get('present_location')
                validate = Validator.validate_str_to_change(present_location)
                if validate is not None:
                    return validate   
                location_change = db.change_location(parcel_id, present_location)
                if location_change is not None:
                    return jsonify({"message":f"Present location changed to {present_location}"}), 200
            return jsonify({'message':'Invalid request! login or use the right access token'}), 400
        return jsonify({'message':'There is no parcel with that ID'}), 200

    def change_parcel_destination(parcel_id):
        """Change the destination of a parcel delivery order"""
        current_user = get_jwt_identity()
        user_input = request.get_json(force=True) 
        parcel = db.get_a_parcel(parcel_id)

        if parcel is not None:
            if current_user == parcel[1]:
                destination = user_input.get('destination')
                validate = Validator.validate_str_to_change(destination)
                if validate is not None:
                    return validate   
                destination_change = db.change_destination(parcel_id, destination)
                if destination_change is not None:
                    return jsonify({"message":f"Destination changed to {destination}"}), 200  
            return jsonify({'message':f"Invalid request! You do not have rights to change the destination of parcel {parcel_id}"}), 400 
        return jsonify({'message':'There is no parcel with that ID'}), 200

    def change_parcel_status(parcel_id):
        """Change the status of a parcel delivery order"""
        statuses = ['pending','in-transit','cancelled', 'delivered']
        current_user = get_jwt_identity()

        user_input = request.get_json(force=True) 

        parcel = db.get_a_parcel(parcel_id)
    
        status = user_input.get('status')
        validate = Validator.validate_str_to_change(status)
        if validate is not None:
            return validate
        if status not in statuses:
            return jsonify({"message":f"Status can only be {statuses}"})   

        if parcel is not None:
            if parcel[0] == parcel_id and current_user == 'admin': 
                status_change = db.change_status(parcel_id, status)
                return jsonify({"message":f"Status changed to {status}"}), 200  
            return jsonify({'message':f"Invalid request! You do not have rights to change the status of parcel {parcel_id}"}), 400 
        return jsonify({'message':'There is no parcel with that ID'}), 200
        

    def create_parcel():
        """Create a parcel delivery order"""
        user_input = request.get_json(force=True)

        current_user = get_jwt_identity()
        user_id = current_user
        recipient_name = user_input.get("recipient_name")
        recipient_mobile = user_input.get("recipient_mobile")
        pickup_location = user_input.get("pickup_location")
        destination = user_input.get("destination")
        weight = user_input.get("weight")
        total_price = user_input.get("total_price")

        parcel_dict = {
            "recipient_name": recipient_name,
            "recipient_mobile": recipient_mobile,
            "pickup_location" : pickup_location,
            "destination": destination,
            "weight": weight,
            "total_price": total_price
        }
        validate_parcel = Validator.validate_parcel(parcel_dict)
        msgs_list = validate_parcel['message(s)']
        if len(msgs_list) > 0:
            return jsonify({'errors':validate_parcel}), 200
        parcel = Parcel(user_id, parcel_dict)
        
        if current_user == 'admin':
            return jsonify({'message':'You cannot create parcel delivery orders'}), 200
        else:
            db.add_parcel(parcel.user_id, parcel.recipient_name, parcel.recipient_mobile, pickup_location, parcel.destination, parcel.weight, parcel.total_price)
            return jsonify({"parcel_successfully_created":parcel.to_dict()}), 201
