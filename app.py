
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import os
from whatstk import df_from_txt_whatsapp
from hashlib import md5
from random import choice

from utils.whtasup_utils import plot_user_message_responses_flow, plot_monthly_activity_plot, add_timestamps_df, \
    get_locations_markers, plot_table, get_hourly_activity_plot

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

UPLOAD_FOLDER = './data'

ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def random_string(n):
    return ''.join([choice('qwertyuiopasdfghjklzxcvbnm') for _ in range(n)]).encode()

@app.route('/general_statistics/<filename>')
def general_statistics(filename):
    plot = get_hourly_activity_plot(session['data'])
    return render_template('general_statistics.html', graphJSON=plot, value=filename)

@app.route('/user_level_analysis/<filename>')
def user_level_analysis(filename):
    plot = plot_user_message_responses_flow(session['data'])
    return render_template('user_level_analysis.html', graphJSON=plot, value=filename)

@app.route('/text_analysis/<filename>')
def text_analysis(filename):
    plot = plot_table(session['data'])
    return render_template('text_analysis.html', graphJSON=plot, value=filename)

@app.route('/geographics/<filename>')
def geographics(filename):

    markers = get_locations_markers(session['data'])

    return render_template('geographics.html', markers=markers, value=filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            rand_s = random_string(5)
            filename = os.path.join(app.config['UPLOAD_FOLDER'], md5(file.filename.encode() + rand_s).hexdigest()+'.txt')
            file.save(filename)
            return redirect(url_for('view_data', filename=md5(file.filename.encode() + rand_s).hexdigest()+'.txt'))

    return render_template('upload.html')


@app.route('/view/<filename>')
def view_data(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        data = df_from_txt_whatsapp(file_path)
        data = add_timestamps_df(data)
        session["data"] = data
        session['file_name'] = filename

        os.system(f'rm {file_path}')
        return render_template('view_data.html', data=session["data"].head().to_html(classes='data'), value=filename)
    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    app.run(debug=True)