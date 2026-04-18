from flask import Flask, jsonify, request
from config import Config
from app.extensions import db, migrate
from sqlalchemy.exc import IntegrityError, StatementError
from werkzeug.exceptions import HTTPException

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models
    from app.api import register_blueprints
    from app.web import web_bp

    register_blueprints(app)
    app.register_blueprint(web_bp)

    @app.route('/health')
    def health_check():
        return {'status': 'ok'}

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': error.description, 'success': False}), error.code
        return error

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Du lieu bi trung hoac vi pham rang buoc', 'success': False}), 409
        raise error

    @app.errorhandler(StatementError)
    def handle_statement_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Du lieu gui len khong hop le', 'success': False}), 400
        raise error

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Loi may chu', 'success': False}), 500
        return 'Internal Server Error', 500

    return app
