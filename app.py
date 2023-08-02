from whatstk import df_from_txt_whatsapp

from flask import *

app = Flask(__name__)


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        f.save('data/'+f.filename)
        print('data/'+f.filename)
        df = df_from_txt_whatsapp('data/'+f.filename)
        return df.to_html()
        # return render_template("Acknowledgement.html", name=f.filename)


if __name__ == '__main__':
    app.run(debug=True)