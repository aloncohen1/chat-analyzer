from whatstk import df_from_txt_whatsapp
from werkzeug.utils import secure_filename
import os
from flask import *

app = Flask(__name__)

EXPORT_PATH = '/home/aloncohen/whatsapp-analyzer/data'


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']

        f.save(os.path.join(EXPORT_PATH, secure_filename(f.filename)))
        print(os.path.join(EXPORT_PATH, secure_filename(f.filename)))
        df = df_from_txt_whatsapp(os.path.join(EXPORT_PATH, secure_filename(f.filename)))
        return df.to_html()
        # return render_template("Acknowledgement.html", name=f.filename)


if __name__ == '__main__':
    app.run(debug=True)