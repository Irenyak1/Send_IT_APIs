import re
from flask import jsonify, flash, request, make_response
from app import app
from app.models.parcel_model import Parcel, parcels
from app.models.users_model import *
from app.models.item_model import Item

class Parcel_Controller:

    def index():
        """Index page"""
        return """parcels ==>
        <a href="https://send-it-api-app.herokuapp.com/api/v1/parcels">
        Navigate to this link to interact with the API</a><br><br>
        """

    def get_parcels():
        """Retrieve all parcels"""
        parcels_list = []
        for parcel in parcels:
            parcels_list.append(parcel.to_dict())
        if parcels_list:
            return jsonify({"number_of_parcel_delivery)orders":len(parcels_list)},{"parcels": parcels_list}), 200
        else:
            return jsonify({"message":"There are no parcel delivery orders"}), 200


    def get_parcels_by_user(user_id):
        """Retrieve all parcels by a specific user"""
        my_parcels = []
        for parcel in parcels:
            parcel_dict = parcel.to_dict()
            if parcel_dict['user_id'] == user_id:
                my_parcels.append(parcel_dict)
                return jsonify({'my_pacels':my_parcels}), 200
        return jsonify({'message':'There are no parcels delivery orders created by that user or the user does not exist'}), 200


    def get_parcel(parcel_id):
        """Retrieve a particular parcel"""

        for parcel in parcels:
            parcel_dict = parcel.to_dict()
            if parcel_dict['parcel_id'] == parcel_id:
                return jsonify({"parcel":parcel_dict}), 200
        return jsonify({'message': f"Parcel with ID {parcel_id} does not exist"}), 200


    def cancel_parcel(parcel_id):
        """Cancel a particular parcel delivery order"""
        for parcel in parcels:
            parcel_dict = parcel.to_dict()
            if parcel_dict['parcel_id'] == parcel_id: 
                if parcel_dict['status'] == 'pending':
                    parcel_dict["status"] = "cancelled"
                    return jsonify({"Parcel_delivery_order_cancelled":parcel_dict}), 200
                # else:
                #     return jsonify({'message':'The parcel delivery order is not pending! It cannot be cancelled'}), 200
        return jsonify({'message':'There is no parcel with that ID'}), 200


    def cancel_parcel_by_user(parcel_id, user_id):
        """Cancel a particular parcel delivery order by a user"""
        for parcel in parcels:
            parcel_dict = parcel.to_dict()
            if parcel_dict['parcel_id']:
                if parcel_dict['parcel_id'] == parcel_id and parcel_dict['user_id'] == user_id: 
                    if parcel_dict['status'] == 'pending':
                        parcel_dict["status"] = "cancelled"
                        return jsonify({"Parcel_delivery_order_cancelled":parcel_dict}), 200
                    # else:
                    #     return jsonify({'message':'The parcel delivery order is not pending! It cannot be cancelled'}), 200
                else:
                    return jsonify({'message':'You dont have rights to cancel this parcel delivery order'}), 200
        return jsonify({'message':'There is no parcel with that ID'}), 200


    def create_parcel():
        """Create a parcel function wrapped around the Post /parcels endpoint"""

        user_input = request.get_json(force=True)

        user_id = user_input.get("user_id")
        if not user_id:
            return jsonify({'message':'User ID is required'}), 400
        if not isinstance(user_id, int):
            return jsonify({'message':'Enter a valid user ID'}), 400

        destination = user_input.get("destination")
        if not destination or destination.isspace():
            return jsonify({'message':'Destination is required'}), 400
        charset = re.compile('[A-Za-z]')
        checkmatch = charset.match(destination)
        if not checkmatch:
            return jsonify({'message':'Destination must be letters'}), 400

        recipient_name = user_input.get("recipient_name")
        if not recipient_name or recipient_name.isspace():
            return jsonify({'message':'Recipient name is required'}), 400
        charset = re.compile('[A-Za-z]')
        checkmatch = charset.match(recipient_name)
        if not checkmatch:
            return jsonify({'message':'Recipient name must be letters'}), 400

        recipient_mobile = user_input.get("recipient_mobile")
        if not recipient_mobile:
            return jsonify({'message':'Recipient mobile contact is required'}), 400
        if not isinstance(recipient_mobile,int):
            return jsonify({'message':'Recipient mobile contact must be numbers'}), 400
        if len(str(recipient_mobile)) != 10:
            return jsonify({'message':'Please enter a valid mobile contact'})

        pickup_location = user_input.get("pickup_location")
        if not pickup_location or pickup_location.isspace():
            return jsonify({'message':'Pickup location is required'}), 400
        charset = re.compile('[A-Za-z]')
        checkmatch = charset.match(pickup_location)
        if not checkmatch:
            return jsonify({'message':'Pickup location must be letters'}), 400

        result_items = user_input.get("items")
        if not result_items:
            return jsonify({'message':'Enter at least one item'}), 400
        if not isinstance(result_items, list):
            return jsonify({'message':'Items must be a list of dictionaries'}), 400
        
                
        items = []
        for result_item in result_items:
            item_name = result_item["item_name"] 
            if not item_name or item_name.isspace():
                return jsonify({'message':'Parcel item name is required'}), 400
            charset = re.compile('[A-Za-z]')
            checkmatch = charset.match(item_name)
            if not checkmatch:
                return jsonify({'message':'Parcel item name must be letters'}), 400

            item_weight = result_item['item_weight'] 
            if not item_weight:
                return jsonify({'message':'Parcel item weight is required'}), 400
            if not isinstance(item_weight,int):
                return jsonify({'message':'Parcel item weight must be an integer'}), 400
                
            item = Item(item_name, item_weight)
            items.append(item)

        parcel = Parcel(user_id, pickup_location, destination, items, recipient_name, recipient_mobile)

        for user in users:
            user_dict = user.to_dict()
            if user_dict['user_id'] == user_id:
                parcels.append(parcel)
                return jsonify({"parcel_successfully_created":parcel.to_dict()}), 201
        return jsonify({'message':'You dont have rights to create a parcel delivery order'}), 200