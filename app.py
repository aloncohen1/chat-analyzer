import os
from flask import Flask, render_template, request, redirect, url_for
from whatstk import df_from_txt_whatsapp
from hashlib import md5
from werkzeug.utils import secure_filename

import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        os.system(f'rm {file_path}')
        return render_template('view_data.html', data=data.to_html(classes='data'))
    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    app.run(debug=True)