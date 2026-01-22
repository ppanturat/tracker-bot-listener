from flask import Flask, jsonify, request
from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType
from supabase import create_client
import os
import requests
import json

app = Flask(__name__)

# --- CONFIGURATION ---
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
public_key = os.environ.get("DISCORD_PUBLIC_KEY")
track17_key = os.environ.get("TRACK17_KEY")

@app.route('/api/interactions', methods=['POST'])
@verify_key_decorator(public_key)
def interactions():
    data = request.json

    # 1. Handle Ping (Discord checks if bot is alive)
    if data["type"] == InteractionType.PING:
        return jsonify({"type": InteractionResponseType.PONG})

    # 2. Handle Commands
    if data["type"] == InteractionType.APPLICATION_COMMAND:
        command_name = data["data"]["name"]
        
        # Get User ID (works for both server and DM)
        user_id = data["member"]["user"]["id"] if "member" in data else data["user"]["id"]

        # ==============================
        #      STOCK TRACKER LOGIC
        # ==============================
        
        # Command: /add_stock
        if command_name == "add_stock":
            options = {opt["name"]: opt["value"] for opt in data["data"].get("options", [])}
            symbol = options.get("symbol").strip().upper()
            target = options.get("target")
            bucket = options.get("bucket").upper()

            if bucket not in ['A', 'B']:
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": "❌ Error: Bucket must be 'A' or 'B'"}
                })

            try:
                # 1. Check for duplicates
                existing = supabase.table("stocks").select("symbol").eq("symbol", symbol).execute()
                if existing.data:
                    return jsonify({
                        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                        "data": {"content": f"⚠️ **{symbol}** is already in your watchlist!\nUse `/edit_stock` to change the target price."}
                    })

                # 2. Insert if new
                data_payload = {"symbol": symbol, "target_price": target, "bucket": bucket}
                supabase.table("stocks").insert(data_payload).execute()
                
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"✅ Added **{symbol}** (Target: {target}) to Bucket **{bucket}**!"}
                })
            except Exception as e:
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"❌ Database error: {str(e)}"}
                })

        # Command: /list_stock
        elif command_name == "list_stock":
            try:
                response = supabase.table('stocks').select("*").order('bucket').execute()
                stocks = response.data
                
                if not stocks:
                    return jsonify({
                        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                        "data": {"content": "📭 Your watchlist is empty."}
                    })

                msg = "**📜 Current Watchlist Settings**\n*(Report sent daily at around 14:00)*\n\n"
                
                # Bucket A
                msg += "**Bucket A (Proven):**\n"
                bucket_a = [s for s in stocks if s['bucket'] == 'A']
                if bucket_a:
                    for s in bucket_a:
                        msg += f"• **{s['symbol']}** (Target: {s['target_price']})\n"
                else:
                    msg += "_(Empty)_\n"

                # Bucket B
                msg += "\n**Bucket B (High Risk):**\n"
                bucket_b = [s for s in stocks if s['bucket'] == 'B']
                if bucket_b:
                    for s in bucket_b:
                        msg += f"• **{s['symbol']}** (Target: {s['target_price']})\n"
                else:
                    msg += "_(Empty)_\n"

                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": msg}
                })
            except Exception as e:
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"❌ Error: {str(e)}"}
                })

        # Command: /delete_stock
        elif command_name == "delete_stock":
            symbol = data["data"]["options"][0]["value"].upper()
            try:
                check = supabase.table("stocks").select("*").eq("symbol", symbol).execute()
                if not check.data:
                    return jsonify({
                        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                        "data": {"content": f"❌ Error: Stock **{symbol}** not found in your list."}
                    })

                supabase.table("stocks").delete().eq("symbol", symbol).execute()
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"🗑️ **{symbol}** has been removed from your watchlist."}
                })
            except Exception as e:
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"❌ Database Error: {str(e)}"}
                })
            
        # Command: /edit_stock
        elif command_name == "edit_stock":
            options = {opt["name"]: opt["value"] for opt in data["data"].get("options", [])}
            symbol = options.get("symbol").upper()
            new_target = options.get("new_target")

            try:
                check = supabase.table("stocks").select("*").eq("symbol", symbol).execute()
                if not check.data:
                    return jsonify({
                        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                        "data": {"content": f"❌ Error: Stock **{symbol}** not found. Use `/add_stock` first."}
                    })

                supabase.table("stocks").update({"target_price": new_target}).eq("symbol", symbol).execute()
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"✅ Updated **{symbol}** target price to **{new_target}**."}
                })
            except Exception as e:
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"❌ Database Error: {str(e)}"}
                })

        # ==============================
        #      PARCEL TRACKER LOGIC
        # ==============================

        # Command: /track [number]
        elif command_name == "track":
            tracking_number = data["data"]["options"][0]["value"]
            
            # 1. Register with 17Track
            headers = {"17token": track17_key, "Content-Type": "application/json"}
            url = "https://api.17track.net/track/v2.2/register"
            payload = [{"number": tracking_number}] 
            
            try:
                resp = requests.post(url, json=payload, headers=headers)
                result = resp.json()
            except Exception as e:
                 return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"❌ API Error: Could not connect to 17Track.\n{str(e)}"}
                })
            
            # 2. Logic Check
            # Code 0 = Success. 
            # Code -18019901 = Duplicate (Already registered). We treat this as SUCCESS.
            code = result.get("code")
            
            if code == 0 or code == -18019901:
                
                # Double Check: Did they reject it inside the data packet?
                if result.get("data", {}).get("rejected"):
                    rej_msg = result["data"]["rejected"][0].get("error", {}).get("message", "Invalid Number")
                    return jsonify({
                        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                        "data": {"content": f"❌ **17Track Rejected:** {rej_msg}"}
                    })

                # Success! Save to Supabase
                db_data = {
                    "tracking_number": tracking_number,
                    "discord_user_id": user_id,
                    "last_status": "Registered"
                }
                try:
                    # Check for duplicates in OUR database
                    existing = supabase.table("parcels").select("*").eq("tracking_number", tracking_number).execute()
                    if not existing.data:
                        supabase.table("parcels").insert(db_data).execute()
                    
                    return jsonify({
                        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                        "data": {"content": f"📦 **Tracking Started!**\nNumber: `{tracking_number}`\nI will notify you when it moves."}
                    })
                except Exception as e:
                    return jsonify({
                        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                        "data": {"content": f"❌ Database Error: {str(e)}"}
                    })
            else:
                # Error from 17Track
                error_msg = result.get('message', 'Unknown error')
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"❌ **API Error:** {error_msg} (Code: {code})"}
                })

        # Command: /parcels
        elif command_name == "parcels":
            try:
                # Fetch only parcels for this specific user
                response = supabase.table('parcels').select("*").eq("discord_user_id", user_id).execute()
                parcels = response.data
                
                if not parcels:
