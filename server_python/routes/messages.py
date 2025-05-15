import csv
from datetime import date, timedelta
from flask import current_app, Blueprint, request, jsonify
import logging
from db import db
from models import Message, TransactionView
from utils import sanitize_message
from openai_client import openai_client
import json
from sqlalchemy import func

bp = Blueprint("messages", __name__)
logger = logging.getLogger(__name__)

PLAID_CATEGORIES = set()
with open("./transactions-personal-finance-category-taxonomy.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        PLAID_CATEGORIES.add(row["PRIMARY"])
        PLAID_CATEGORIES.add(row["DETAILED"])

tools = [{
  "name": "financial_insights",
  "description": "Provides insights into personal financial data and spending habits",
  "strict": True,
  "type": "function",
  "parameters": {
    "type": "object",
    "required": [
      "date_range",
      "request_type",
      "amount",
      "category", 
      "vendor"
    ],
    "properties": {
      "amount": {
        "type": "number",
        "description": "Amount for filtering purchases in queries"
      },
      "category": {
        "type": "string",
        "enum": sorted(PLAID_CATEGORIES),
        "description": "Select the closest category from the list of categories. The category should be one of the following: {PLAID_CATEGORIES}"
      },
      "date_range": {
        "type": "object",
        "required": [
          "start_date",
          "end_date"
        ],
        "properties": {
          "end_date": {
            "type": "string",
            "description": "End date for the analysis period"
          },
          "start_date": {
            "type": "string",
            "description": "Start date for the analysis period"
          }
        },
        "description": "Optional date range for the financial analysis",
        "additionalProperties": False
      },
      "request_type": {
        "type": "string",
        "description": "Type of financial request (e.g. 'spending', 'budget_comparison', 'current_net_worth', 'active_subscriptions')"
      },
      "vendor": {
        "type": "string",
        "description": "Vendor name for filtering purchases in queries (e.g. 'Starbucks')"
      }
    },
    "additionalProperties": False
  }
}]

def get_spending(args, user_id):
    vendor = args.get("vendor")
    category = args.get("category")

    start_date = args.get("date_range", {}).get("start_date")
    end_date = args.get("date_range", {}).get("end_date")

    # 1) Base filters
    filters = [TransactionView.user_id == user_id]

    # 2) Only add date filter if both dates provided
    if start_date is not None and end_date is not None:
        filters.append(TransactionView.date.between(start_date, end_date))

    # 3) Build & execute query
    q = db.session.query(func.coalesce(func.sum(TransactionView.amount), 0).label("total_spent")).filter(*filters)

    if vendor:
        logger.info(f"Filtering by vendor: {vendor}")
        q = q.filter(
            TransactionView.name.ilike(f"%{vendor}%")
        )

    elif category:
        q = q.filter(
            TransactionView.personal_finance_category_detailed.ilike(f"%{category}%")
        )
        if not q.scalar():
            q = q.filter(
            TransactionView.personal_finance_category_primary.ilike(f"%{category}%")
        )

    else:
        return {
            "error": "Please specify at least a vendor or a category."
        }

    total = q.scalar()  # executes the query
    logger.info(f"Total spent: {total}")
    return {
        "user_id":     user_id,
        "vendor":      vendor,
        "category":    category,
        "total_spent": float(total)
    }

def get_budget_comparison(args, user_id):
    pass

def get_current_net_worth(args, user_id):
    pass

def get_active_subscriptions(args, user_id):
    pass

def tool_function_call(args, user_id):
    if args["request_type"] == "spending":
        # Call the function to get spending last month
        return get_spending(args, user_id)
    elif args.request_type == "budget_comparison":
        # Call the function to get budget comparison
        return get_budget_comparison(args, user_id)
    elif args.request_type == "current_net_worth":
        # Call the function to get current net worth
        return get_current_net_worth(args, user_id)
    elif args.request_type == "active_subscriptions":
        # Call the function to get active subscriptions
        return get_active_subscriptions(args, user_id)
    else:
        return "failed"
    

@bp.route("/messages", methods=["POST"])
def create_message():
    """Create a new message"""
    data = request.get_json()
    user_id = data.get("userId")
    text = data.get("text")
     
    if not all([user_id, text]):
        return jsonify({"error": "Missing required fields"}), 400

    # Create a new message
    user_message = Message(
        user_id=user_id,
        text=text,
        author="user"
    )

    db.session.add(user_message)
    db.session.commit()

    # Emit the new message to the client
    message = {
        "id": user_message.id,
        "user_id": user_message.user_id,
        "text": user_message.text,
        "author": "user"
    }
    io = current_app.config['socketio']
    io.emit('NEW_RESPONSE_MESSAGE', {'message': message})

    with open("./expenses_prompt.txt", "r", encoding="utf-8") as f:
        instructions = f.read()

    response = openai_client.client.responses.create(
        model="gpt-4.1",
        instructions=instructions,
        input=text,
        tools=tools,
        tool_choice="auto",
    )
    logger.info(f"OpenAI response: {response.output}")
    
    input_messages = []
    for tool_call in response.output:
        if tool_call.type != "function_call":
            continue

        args = json.loads(tool_call.arguments)

        result = tool_function_call(args, user_id)
        input_messages.append(tool_call)
        input_messages.append({
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": str(result)
        })

    response = openai_client.client.responses.create(
        model="gpt-4.1",
        input=input_messages,
        tools=tools,
    )
    response_text = response.output_text
    logger.info(f"Final OpenAI response: {response_text}")

    response_message_obj = Message(
        user_id=user_id,
        text=response_text,
        author="bot"
    )

    db.session.add(response_message_obj)
    db.session.commit()

    response_message = {
        "id": response_message_obj.id,
        "user_id": response_message_obj.user_id,
        "text": response_message_obj.text,
        "author": "bot"
    }

    io = current_app.config['socketio']
    io.emit('NEW_RESPONSE_MESSAGE', {'message': response_message})

    return "", 201

@bp.route("/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    """Delete a message"""
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return "", 204