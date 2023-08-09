import os
from flask import Flask, render_template, request, redirect, url_for, session
from whatstk import df_from_txt_whatsapp
from hashlib import md5
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

UPLOAD_FOLDER = '/home/aloncohen/whatsapp-analyzer/data'
# UPLOAD_FOLDER = '/Users/aloncohen/private_repos/whatsapp-analyzer/data'

ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route(f'/general_statistics/<filename>')
def general_statistics(filename):
    return session["data"].head().to_html()

@app.route(f'/user_level_analysis/<filename>')
def user_level_analysis(filename):
    return "User Level Analysis"

@app.route(f'/text_analysis/<filename>')
def text_analysis(filename):
    return "Text Analysis"

@app.route('/about/')
def about():
    return "About"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], md5(file.filename.encode()).hexdigest()+'.txt')
            file.save(filename)
            return redirect(url_for('view_data', filename=md5(file.filename.encode()).hexdigest()+'.txt'))

    return render_template('upload.html')


@app.route('/view/<filename>')
def view_data(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        data = df_from_txt_whatsapp(file_path)
        session["data"] = data
        session['file_name'] = filename

        os.system(f'rm {file_path}')
        return render_template('view_data.html', data=session["data"].to_html(classes='data'), value=filename)
    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    app.run(debug=True)