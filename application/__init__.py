from flask import Flask, escape, request


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    with app.app_context():

        from application.spreadsheet.backend import BackendServer

        backendServer = BackendServer()
        backendServer.start()

        from application.spreadsheet.client import SyncService

        syncService = SyncService()
        syncService.start()

        import application.spreadsheet.routes as spreadsheet_routes

        app.register_blueprint(spreadsheet_routes.spreadsheet_bp)

        return app
