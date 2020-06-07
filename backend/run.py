from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
    app.logger.info('start leo-api-auto-platform service')
