from flask import Flask
import pandas as pd
import os

app = Flask(__name__)

ARQUIVO = "data.csv"

@app.route("/")

def home():

    if not os.path.exists(ARQUIVO):

        return "<h1>No existe data.csv</h1>"

    try:

        df = pd.read_csv(
            ARQUIVO,
            sep=";"
        )

        html = """
        <html>
        <head>
            <title>GPS FLOTA</title>
            <style>
                body{
                    background:#0D1117;
                    color:white;
                    font-family:Arial;
                    padding:20px;
                }

                h1{
                    color:#00E5FF;
                }

                table{
                    width:100%;
                    border-collapse:collapse;
                    background:#161B22;
                }

                th,td{
                    border:1px solid #30363D;
                    padding:10px;
                    text-align:center;
                }

                th{
                    background:#21262D;
                    color:#00E5FF;
                }

                tr:hover{
                    background:#1F2937;
                }
            </style>
        </head>
        <body>

        <h1>🚛 GPS FLOTA</h1>

        """

        html += df.to_html(index=False)

        html += """
        </body>
        </html>
        """

        return html

    except Exception as e:

        return f"<h1>Error:</h1><pre>{str(e)}</pre>"

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )