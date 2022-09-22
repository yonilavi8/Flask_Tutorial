import os

from flask import Flask

# create_app is the application factory function
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # set some default configurations:
    # SECRET_KEY set to 'dev' during development, but overriden with random value when deploying
    # DATABASE is the path where the SQLite database file will be saved
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flask.sqlite'),
    )

    # app.config.from_pyfile() overrides default configuration with values taken from the config.py file in
    # the instance folder if it exists. Can be used to set a real SECRET_KEY
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello World!'

    # register db functions with application
    from . import db
    db.init_app(app)

    # import and register blueprint from factory
    from . import auth
    app.register_blueprint(auth.bp)

    return app
