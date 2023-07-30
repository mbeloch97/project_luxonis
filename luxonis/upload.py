from flask import Flask
import time
import psycopg2

app = Flask(__name__)


def data_ready():
    try:
        conn = psycopg2.connect(host="db", database="mydatabase", user="postgres", password="1234", port="5432")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scrab")
        result = cursor.fetchone()
        conn.close()
        print(result[0])
        return result[0] > 0
    except:
        return False


@app.route('/')
def index():
    """
    This function updates the main (index) webpage with html content using Flask.
    We get the content from database and create a simple html.
    """
    if data_ready():
        conn = psycopg2.connect(host="db", database="mydatabase", user="postgres", password="1234", port="5432")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scrab")
        rows = cursor.fetchall()
        html = ""
        for rows in rows:
            html += "<h1>%s</h1>\n" \
                    "<h2>%s</h2>\n" \
                    "<h3>%s CZK</h3>\n" \
                    "<img src=\"%s\">\n\n" % (rows[1], rows[2], rows[3], rows[4])
        conn.close()
        return html
    else:
        return '<h1>Data not ready!</h1>'


if __name__ == '__main__':
    """
    The app will run on 0.0.0.0, that means, 
    that it will listen on host computer outside of container on port 8080.
    """
    app.run(host='0.0.0.0', port='8080')