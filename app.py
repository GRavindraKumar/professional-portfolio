import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_mail import Mail, Message
from flask_cors import CORS
from dotenv import load_dotenv

# Get the absolute path of the current directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
CORS(app)  # Add CORS support

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for sending messages
@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        
        # Validate input
        if not all(key in data for key in ['name', 'email', 'message']):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        name = data['name'].strip()
        email = data['email'].strip()
        message = data['message'].strip()

        if not all([name, email, message]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400

        # Send email
        msg = Message(
            subject=f'New Portfolio Message from {name}',
            recipients=[app.config['MAIL_USERNAME']],
            body=f'From: {name}\nEmail: {email}\n\nMessage:\n{message}'
        )
        mail.send(msg)

        return jsonify({
            'success': True,
            'message': 'Thank you for your message! I\'ll get back to you soon.'
        })
    except Exception as e:
        app.logger.error(f'Error sending message: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Failed to send message. Please try again later.'
        }), 500

# Route for static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Route for downloading resume
@app.route('/download_resume')
def download_resume():
    try:
        return send_from_directory('static/assets', 'resume.pdf', as_attachment=True)
    except Exception as e:
        return str(e), 404

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True) 