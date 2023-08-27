
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import os
from whatstk import df_from_txt_whatsapp
from hashlib import md5

from archive.dash_apps import table_das_app
from archive.whtasup_utils import plot_user_message_responses_flow, plot_monthly_activity_plot, add_timestamps_df, \
    get_locations_markers, plot_table, get_hourly_activity_plot, allowed_file, random_string

server = Flask(__name__)

server.config["SESSION_PERMANENT"] = False
server.config["SESSION_TYPE"] = "filesystem"

Session(server)

UPLOAD_FOLDER = './data'

server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@server.route('/general_statistics/<filename>')
def general_statistics(filename):
    # plot = get_hourly_activity_plot(session['data'])

    graph_a, graph_b = plot_monthly_activity_plot(session["data"]), get_hourly_activity_plot(session["data"])


    return render_template('templates/general_statistics.html', graph_a=graph_a, graph_b=graph_b, value=filename)

@server.route('/user_level_analysis/<filename>')
def user_level_analysis(filename):
    plot = plot_user_message_responses_flow(session['data'])
    return render_template('templates/user_level_analysis.html', graphJSON=plot, value=filename)

@server.route('/text_analysis/<filename>')
def text_analysis(filename):
    plot = plot_table(session['data'])
    return render_template('templates/text_analysis.html', graphJSON=plot, value=filename)

@server.route('/geographics/<filename>')
def geographics(filename):

    markers = get_locations_markers(session['data'])

    return render_template('templates/geographics.html', markers=markers, value=filename)

@server.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            rand_s = random_string(5)
            filename = os.path.join(server.config['UPLOAD_FOLDER'], md5(file.filename.encode() + rand_s).hexdigest() + '.txt')
            file.save(filename)
            return redirect(url_for('view_data', filename=md5(file.filename.encode() + rand_s).hexdigest()+'.txt'))

    return render_template('templates/upload.html')


@server.route('/view/<filename>')
def view_data(filename):
    file_path = os.path.join(server.config['UPLOAD_FOLDER'], filename)

    try:
        data = df_from_txt_whatsapp(file_path)
        data = add_timestamps_df(data)
        session["data"] = data
        session['file_name'] = filename

        os.system(f'rm {file_path}')

        graph_a, graph_b = plot_monthly_activity_plot(session["data"]), get_hourly_activity_plot(session["data"])

        return render_template('templates/general_statistics.html', graph_a=graph_a, graph_b=graph_b, value=filename)
    except Exception as e:
        return f"Error: {e}"

app = table_das_app(server)

if __name__ == '__main__':
    server.run(debug=True)