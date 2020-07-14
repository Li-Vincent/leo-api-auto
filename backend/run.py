from app import app, app_config

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=app_config.get_port())
    app.logger.info('start leo-api-auto-platform service successfully.')
