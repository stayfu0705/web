from app import create_app
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
from app1 import app as app1
from app2 import app as app2
from app3 import app as app3


app = create_app("production")

application = DispatcherMiddleware(app, {
    '/app1': app1.server,
    '/app2': app2.server,
    '/app3': app3.server,
})



if __name__ == '__main__':
    run_simple('localhost', 5000, application)



