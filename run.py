from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("  CareerAssistant Pro - Web App")
    print("=" * 50)
    print()
    print("  Local URL: http://127.0.0.1:5000")
    print("  Network URL: http://0.0.0.0:5000")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
