from whatstk import df_from_txt_whatsapp
from werkzeug.utils import secure_filename
import os
from flask import *

app = Flask(__name__)

EXPORT_PATH = '/home/aloncohen/whatsapp-analyzer/data' # '/Users/aloncohen/private_repos/whatsapp-analyzer/data'


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        try:
            f = request.files['file']

            f.save(os.path.join(EXPORT_PATH, secure_filename(f.filename)))
            print(os.path.join(EXPORT_PATH, secure_filename(f.filename)))
            df = df_from_txt_whatsapp(os.path.join(EXPORT_PATH, secure_filename(f.filename)))
            os.system(f'rm {os.path.join(EXPORT_PATH, secure_filename(f.filename))}')
            return df.to_html()
        except Exception as e:
            return f'<html><title>ERROR: {e}</title></html>'


if __name__ == '__main__':
    app.run(debug=True)