from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import reg_exp

app = FastAPI()

inprogress_session = {}

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()


    intent = payload['queryResult']['intent']['displayName']
    parameter = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    sessionId = reg_exp.extraction_sessionID(output_contexts[0]['name'])

    intent_handler = {
        "track.order-context:ongoing-tracking": track_order,
        "order.complete-context:ongoing-order": complete_order,
        "order.remove-context:ongoing-order": remove_order,
        "order.add-context:ongoing-order": add_to_order
    }
    return intent_handler[intent](parameter, sessionId)

def add_to_order(parameter: dict, session_ID: str):
    food_items = parameter['food-item']
    quantity = parameter['number']

    if len(food_items) != len(quantity):
        fulfillmentText = "Please specify the correct quantity of food items"
    else:

        new_food_dict = dict(zip(food_items, quantity))

        if session_ID in inprogress_session:
            current_food_dict = inprogress_session[session_ID]
            current_food_dict.update(new_food_dict)
            inprogress_session[session_ID] = current_food_dict
        else:
            inprogress_session[session_ID] = new_food_dict

        order_string = reg_exp.get_str_from_dic(inprogress_session[session_ID])
        fulfillmentText = f"So far you have {order_string}. Do you need anything else?"

    return JSONResponse(
        content={"fulfillmentText": fulfillmentText}
    )

def track_order(parameter: dict, session_id):
    order_id = int(parameter['number'])
    status = db_helper.get_order_status(order_id)
    if status:
        fulfillmentText = f"The order status for the {order_id} is: {status}"
    else:
        fulfillmentText = "Cannot find the order status"
    return JSONResponse(
        content={"fulfillmentText": fulfillmentText}
    )


def complete_order(parameter: dict, session_ID: str):
    if session_ID in inprogress_session:
        order = inprogress_session[session_ID]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillmentText = "Cannot place the order"
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillmentText = f"Order is placed successfully"\
                              f'Here is your order id {order_id}, order total is {order_total}'
        del inprogress_session[session_ID]

    else:
        fulfillmentText = "I  am having trouble in processing your order"


    return JSONResponse(content={
        "fulfillmentText": fulfillmentText
    }
    )

def save_to_db(order: dict):
    next_order_id = db_helper.next_order_id()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(str(food_item), quantity, next_order_id)
    if rcode == -1:
        return -1
    db_helper.insert_order_tracking(next_order_id, "in progress")

    return next_order_id

def remove_order(parameter: dict, session_ID: str):

    current_order = inprogress_session[session_ID]
    if session_ID not in inprogress_session:
        return JSONResponse(content={
            "fulfillmentText": "There is no such order in the backend. Try again"
        })
    else:
        food_items = parameter['food-item']
        removed_items = []
        no_such_items = []

        for food in food_items:
            if food not in current_order:
                no_such_items.append(food)
            else:
                removed_items.append(food)
                del current_order[food]
        if len(removed_items) > 0:
            fulfillmentText = f"There are {', '.join(removed_items)} items removed"
        if no_such_items:
            fulfillmentText = f"Order specified {', '.join(no_such_items)} not available"
        if len(current_order.keys()) == 0:
            fulfillmentText = "There is no such order in the backend. Try again"

        else:
            order_str = reg_exp.get_str_from_dic(current_order)
            fulfillmentText = f"Here is what you are left with {order_str}"

        return JSONResponse(content={
            "fulfillmentText": fulfillmentText
        })





