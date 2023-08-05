from flask import Flask, render_template, request, redirect, url_for
from whatstk import df_from_txt_whatsapp
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# EXPORT_PATH =   '/Users/aloncohen/private_repos/whatsapp-analyzer/data'
EXPORT_PATH = '/home/aloncohen/whatsapp-analyzer/data'



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(EXPORT_PATH, secure_filename(f.filename)))
        return redirect(url_for('display_file', content=os.path.join(EXPORT_PATH, secure_filename(f.filename))))
    return render_template('index.html')


@app.route('/display')
def display_file():
    try:
        f_path = request.args.get('content', '')

        df = df_from_txt_whatsapp(f_path)
        os.system(f'rm {f_path}')
        #return render_template(df.to_html())
        return render_template('display.html', tables=[df.to_html(classes='data', header="true")])
    except Exception as e:
        return f'<html><body><h1>ERROR: {e}</h1></body></html>'
    # return render_template('display.html', tables=[df.to_html(classes='data', header="true")])

if __name__ == '__main__':
    app.run(debug=True)





