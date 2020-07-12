from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import plotly
import plotly.graph_objects as go
import json
from io import BytesIO
import base64

# https://medium.com/@francescaguiducci/how-to-build-a-simple-personal-website-with-python-flask-and-netlify-d800c97c283d

app = Flask(__name__)

def figStatic(df):
    df = df[df["denominazione_provincia"]=="Bologna"]
    df["data"] = pd.to_datetime(df["data"]).dt.date
    with plt.style.context('dark_background'):
        plt.rcParams['lines.linewidth'] = 2
        plt.rcParams['lines.linestyle'] = '-.'
        plt.rc('lines', marker='o', markerfacecolor='r', markersize=8, markeredgecolor="r")
        #plt.rc('lines', linewidth=2, color='red',linestyle='-.')
        plt.rcParams['figure.figsize'] = (20,9)
        plt.rc("axes",titlesize=30, titlecolor="cyan",titlepad=10)
        plt.rcParams.update({"axes.grid" : True, "grid.color": "red", "grid.alpha" : 0.5})
        plt.rc("font", family="DejaVu Serif", fantasy="Comic Neue", size=20)
        plt.rcParams["date.autoformatter.day"]= "%m-%d" #"%Y-%m"
        # Sample half element of a series
        xlist = []
        data_list = list(df['data'])
        for i in range(0, len(data_list),4):
            xlist.append(data_list[i])
        fig, ax = plt.subplots()
        plt.plot(df["data"], df["totale_casi"])
        ax.set_title("Titolo")
        ax.set_xticks( xlist)
        ax.tick_params(axis='x',labelrotation=45,labelcolor='orange')
        #ax.yaxis.grid(False)

        figfile = BytesIO()
        plt.savefig(figfile, format='png')
        figfile.seek(0)  # rewind to beginning of file
        #figdata_png = base64.b64encode(figfile.read())
        figdata_png = base64.b64encode(figfile.getvalue())

        #plt.savefig("static/image.png")
        #fig.savefig("matplotlib_rcparams.png")
        fig_decoded = figdata_png.decode('utf8')
        return fig_decoded
    
def figPlotly(df):

    df = df[df["denominazione_provincia"]=="Bologna"]
    #df["data"] = pd.to_datetime(df["data"]).dt.date

    xx = df["data"].values.tolist()
    yy = df["totale_casi"].values.tolist()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
            x = xx,
            y = yy,
            name="Totale Casi",
            mode="lines+markers",
            showlegend=True,
            marker=dict(
                symbol="circle-dot",
                size=6,
            ),
            line=dict(
                width=1,
                color="rgb(0,255,0)",
                dash="longdashdot"
            )
        )
    )
    fig.update_layout(
        title=dict(
            text ="Totale Casi Bologna",
            y = 0.9,
            x = 0.5,
            xanchor = "center",
            yanchor = "top",
        ),
        legend=dict(
            y = 0.9,
            x = 0.03,
        ),
        xaxis_title="data",
        yaxis_title="totale casi",
        font=dict(
            family="Courier New, monospace",
            size=20,
            color="orange", #"#7f7f7f", 
        ),
        hovermode='x',  #['x', 'y', 'closest', False]
        plot_bgcolor = "rgb(10,10,10)",
        paper_bgcolor="rgb(0,0,0)"
    )

    #htmlfig = fig.write_html("fig.html")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route("/")
def index():
    df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv")
    dfhtml = df.head(300).to_html(index=False)
    graphJSON = figPlotly(df)
    figstatic= figStatic(df)
    return render_template('index.html', table=dfhtml,graphJSON=graphJSON,figstatic=figstatic)

if __name__ == '__main__':
    app.run(debug=True)