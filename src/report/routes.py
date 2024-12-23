from os import error
from flask import Blueprint, render_template, current_app, request, session
from access import login_required
from auth.auth import check_authorization
from report.model_route import check_report_exists, create_new_report, \
    get_report_orders_db, ReportInfoResponse


report_blueprint = Blueprint(
    'report_bp',
    __name__,
    template_folder='templates'
)


@report_blueprint.route('/')
@login_required
def reports_menu():
    ''' Reports menu '''
    return render_template('reports_menu.html', auth_msg=check_authorization()[0])


@report_blueprint.route('/create', methods=['GET'])
@login_required
def create_report():
    ''' Page with a form for user to input report parameters to create respective report '''
    report_name = request.args.get('name')
    return render_template(f"create_{report_name}_report.html", 
                           auth_msg=check_authorization()[0])


@report_blueprint.route('/create', methods=['POST'])
@login_required
def insert_report():
    ''' Function that invokes the creation of report in DB '''
    report_name = request.args.get('name')

    request_data = request.form
    # Check whether report for such data already exists
    exist_info: ReportInfoResponse = check_report_exists(current_app.config['db_config'], 
                                                         request_data, report_name)
    if exist_info.status:  # if exists
        return render_template("report_status.html", 
                               status_title='Отчёт на данный период уже существует',
                               status_msg=exist_info.error_message, report_name=report_name,
                               auth_msg=check_authorization()[0])
    
    # Execute procedure:
    res_info: ReportInfoResponse = create_new_report(current_app.config['db_config'], 
                                                     request_data, report_name)
    if res_info.status:
        return render_template("report_status.html", status_title='Отчёт успешно создан', report_name=report_name,
                                auth_msg=check_authorization()[0])
    return render_template("report_status.html", status_title='Отчёт не был создан',
                            status_msg=res_info.error_message, report_name=None,
                            auth_msg=check_authorization()[0])


@report_blueprint.route('/view', methods=['GET'])
@login_required
def view_report():
    ''' Page with a form for user to input report parameters to view respective report '''
    report_name = request.args.get('name')
    return render_template(f"get_{report_name}_report.html", 
                           auth_msg=check_authorization()[0])


@report_blueprint.route('/view', methods=['POST'])
@login_required
def extract_report():
    ''' Function that extracts report from DB '''
    report_name = request.args.get('name')
    request_data = request.form
    # Check whether report for such data already exists
    exist_info: ReportInfoResponse = check_report_exists(current_app.config['db_config'], 
                                                         request_data, report_name)
    if not exist_info.status:  # if not exists
        return render_template("report_status.html", 
                               status_title='Отчёт на данный период не существует',
                               status_msg=exist_info.error_message,
                               auth_msg=check_authorization()[0])
    
    res_info: ReportInfoResponse = get_report_orders_db(current_app.config['db_config'], 
                                                        request_data, report_name)
    if not res_info.status:
        return render_template("report_status.html", 
                               status_title='Отчёт не найден',
                               status_msg=res_info.error_message,
                               auth_msg=check_authorization()[0])
    
    rows, schema = res_info.result
    if rows[0][1] == 0:  # If no orders were done that month
        return render_template("report_status.html", 
                               status_title='В данный месяц не было совершено ни одного заказа',
                               auth_msg=check_authorization()[0])
    return render_template("dynamic_report.html", 
                           table_title=f'Отчёт за {request_data['year_month']}',
                           header=schema, rows=rows,
                           auth_msg=check_authorization()[0])