"""
WSGI configuration for subdirectory deployment
This file handles the /aureumflaskapp/ prefix automatically
"""
import os
from app import app

class PrefixMiddleware:
    """
    Middleware to handle application prefix for subdirectory deployment
    This allows the app to work at http://domain.com/aureumflaskapp/
    """
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix.rstrip('/')

    def __call__(self, environ, start_response):
        # If the path starts with our prefix, remove it before passing to Flask
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            if environ['PATH_INFO'] == '':
                environ['PATH_INFO'] = '/'
        return self.app(environ, start_response)

# Get the application root from environment variable
APPLICATION_ROOT = os.getenv('APPLICATION_ROOT', '/')

# Only wrap with prefix middleware if not deploying at root
if APPLICATION_ROOT and APPLICATION_ROOT != '/':
    application = PrefixMiddleware(app.wsgi_app, prefix=APPLICATION_ROOT)
    app.wsgi_app = application
else:
    application = app

# For gunicorn
if __name__ == "__main__":
    app.run()

