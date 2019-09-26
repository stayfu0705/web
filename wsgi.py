from werkzeug.wsgi import DispatcherMiddleware
from manage import app
from app1 import app as app1
from app2 import app as app2
from app3 import app as app3

application = DispatcherMiddleware(app, {
    '/app1': app1.server,
    '/app2': app2.server,
    '/app3': app3.server,
})