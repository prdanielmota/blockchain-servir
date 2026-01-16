from app import create_app

app = create_app()

if __name__ == '__main__':
    # Listen on all interfaces (0.0.0.0) to allow external access (n8n/ngrok)
    # Using port 5001 to avoid conflict with macOS AirPlay (port 5000)
    app.run(debug=True, host='0.0.0.0', port=5001)
