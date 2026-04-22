from flask import Flask, request, jsonify, render_template
from orchestrator import orchestrator
from dotenv import load_dotenv
import sys

load_dotenv(override=True)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/run-task", methods=["POST"])
def run_task():
    try:
        data = request.json
        content = data.get("content")
        email = data.get("email")
        send_email = data.get("send_email", False)
        mode = data.get("mode", "research")
        profile = data.get("profile", {})
        super_agent = data.get("super_agent", False)

        if not content:
            return jsonify({"status": "fail", "message": "Query or topic is required"}), 400

        # Pass profile and super_agent to the orchestrator
        result = orchestrator(content, email, send_email, mode, profile, super_agent)
        return jsonify({"status": "success", "message": result})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

from agents.email_agent import email_agent

@app.route("/send-edited-email", methods=["POST"])
def send_edited_email():
    try:
        data = request.json
        content = data.get("content")
        email = data.get("email")

        if not content or not email:
            return jsonify({"status": "fail", "message": "Content and recipient email are required"}), 400

        # Call email_agent directly with the edited content
        email_agent(email, content)
        return jsonify({"status": "success", "message": "Wait... Your edited version has been sent successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/save-learning", methods=["POST"])
def save_learning():
    try:
        data = request.json
        topic = data.get("topic")
        content = data.get("content")

        if not topic or not content:
            return jsonify({"status": "fail", "message": "Missing topic or content"}), 400

        # Save to the local Learning Log
        log_path = os.path.join(os.getcwd(), 'data', 'learning_log.json')
        with open(log_path, 'r') as f:
            log = json.load(f)
        
        # Add the new learned pattern
        log['queries'].append({"topic": topic, "content": content})
        
        with open(log_path, 'w') as f:
            json.dump(log, f, indent=2)

        return jsonify({"status": "success", "message": "Brain successfully updated with your correction! I'll remember this next time."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)