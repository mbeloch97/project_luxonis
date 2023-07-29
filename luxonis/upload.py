from flask import Flask
import time
import psycopg2

app = Flask(__name__)

def data_ready():
    try:
        print(1)
        conn = psycopg2.connect(host="db", database="mydatabase", user="postgres", password="1234", port="5432")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scrab")
        print(2)
        result = cursor.fetchone()
        #cursor.close()
        conn.close()
        print(result[0])
        return result[0] > 0
    except:
        return False


@app.route('/')
def index():
    print("INDEX 1")
    if data_ready():
        print("INDEX 2")
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
        #cursor.close()
        conn.close()
        return html
    else:
        return '<h1>Data not ready!</h1>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080')