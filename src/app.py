from flask import Flask, render_template, session, json
from auth.auth import check_authorization


app = Flask(__name__)
app.secret_key = 'dasecretkey'


@app.route('/')
def main_menu():
    auth_msg, auth_status = check_authorization()
    return render_template('main_menu.html', auth_status=auth_status, auth_msg=auth_msg)


@app.route('/exit')
def exit_func():
    session.clear()
    return render_template('error.html', error_title='Вы вышли из аккаунта', 
                           auth_msg=check_authorization()[0])


def register_configs(app):
    from os.path import dirname, join as pathjoin
    
    cur_dir = dirname(__file__)

    with open(pathjoin(cur_dir, "data/dbconfig.json")) as f:
        app.config['db_config'] = json.load(f)

    with open(pathjoin(cur_dir, "data/db_access.json")) as f:
        app.config['db_access'] = json.load(f)

    with open(pathjoin(cur_dir, "data/cache_config.json")) as f:
        app.config['cache_config'] = json.load(f)


def register_blueprints(app):
    from query.routes import query_blueprint
    from auth.routes import auth_blueprint
    from report.routes import report_blueprint
    from order.routes import order_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(query_blueprint, url_prefix='/query')
    app.register_blueprint(report_blueprint, url_prefix='/report')
    app.register_blueprint(order_blueprint, url_prefix='/order')


if __name__ == '__main__':
    register_configs(app)
    register_blueprints(app)
    app.run(host="127.0.0.1", port=5001, debug=True)
