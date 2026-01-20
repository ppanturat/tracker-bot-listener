import requests
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("APP_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not APP_ID or not BOT_TOKEN:
    print("Error: Missing APP_ID or BOT_TOKEN in .env file.")
    exit()

url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"

json_commands = [
    # Add Stock
    {
        "name": "add_stock",
        "description": "Add a stock to the tracker",
        "options": [
            {"name": "symbol", "description": "Stock Symbol", "type": 3, "required": True},
            {"name": "target", "description": "Target Price", "type": 10, "required": True},
            {"name": "bucket", "description": "Bucket A or B", "type": 3, "required": True, "choices": [{"name": "A", "value": "A"}, {"name": "B", "value": "B"}]}
        ]
    },
    # List Stock
    {
        "name": "list_stock",
        "description": "Show current watchlist configuration"
    },
    # Delete Stock 
    {
        "name": "delete_stock",
        "description": "Remove a stock from the tracker",
        "options": [
            {
                "name": "symbol",
                "description": "Stock Symbol to delete",
                "type": 3, # String
                "required": True
            }
        ]
    },
    # Edit Stock
    {
        "name": "edit_stock",
        "description": "Update the target price of a stock",
        "options": [
            {
                "name": "symbol",
                "description": "Stock Symbol",
                "type": 3, # String
                "required": True
            },
            {
                "name": "new_target",
                "description": "New Target Price",
                "type": 10, # Number
                "required": True
            }
        ]
    },
    # Parcel Commands
    {
        "name": "track",
        "description": "Start tracking a parcel",
        "options": [
            {"name": "number", "description": "Tracking Number", "type": 3, "required": True}
        ]
    },
    {
        "name": "parcels",
        "description": "Show your active parcels"
    }
]

headers = {"Authorization": f"Bot {BOT_TOKEN}"}

r = requests.put(url, headers=headers, json=json_commands)
print(r.status_code)
print(r.text)