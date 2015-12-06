
from flask import render_template, flash, redirect, url_for
import requests
import pandas as pd
from app import app
from .forms import LoginForm
import datetime

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.templates import JS_RESOURCES
from bokeh.util.string import encode_utf8

@app.route('/')
def main():
    return redirect(url_for('index'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    stockcode = form.openid.data
    stockperiod = "1M"
    if  stockcode and stockcode.strip():
    #request data from QuanDL
        baseURL='https://www.quandl.com/api/v1/datasets/WIKI/'
        periodURL={'1M':'?trim_start=' + (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
            '6M':'?trim_start=' + (datetime.datetime.now() - datetime.timedelta(days=183)).strftime('%Y-%m-%d'),
            '1Y':'?trim_start=' + (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d'),
            'All':'',
            'None':''}
        jsonURL=baseURL + stockcode + '.json' + periodURL[stockperiod]
        jsonRespond = requests.get(jsonURL)
        HTTPstatusCode=jsonRespond.status_code
            
        print '[URL]      ' + jsonURL
        print '[HTTP]     ' + str(HTTPstatusCode)
        print '[Stockcode]' + stockcode
        print '[Period]   ' + stockperiod




    else:
        jsonURL = None
        HTTPstatusCode = None

    # If http status is ok.
    if HTTPstatusCode == 200:
        jheader = (jsonRespond.json())['column_names']
        jdata = (jsonRespond.json())['data']

        stockdata = pd.DataFrame(jdata, columns=jheader)
        print stockdata.head()

        mids = (stockdata.Open + stockdata.Close)/2
        spans = abs(stockdata.Close-stockdata.Open)
        #To check the up/down of the day to determin the bar color
        inc = stockdata.Close > stockdata.Open
        dec = stockdata.Open > stockdata.Close

        fig = figure(title=None, plot_width=600, plot_height=480,x_axis_type="datetime", toolbar_location="below", tools = "crosshair, pan,wheel_zoom,box_zoom,reset,resize")

        fig.segment(stockdata.Date, stockdata.High, stockdata.Date, stockdata.Low, color="black")
        fig.rect(stockdata.Date[inc], mids[inc], w, spans[inc], fill_color="#D5E1DD", line_color="black")
        fig.rect(stockdata.Date[dec], mids[dec], w, spans[dec], fill_color="#F2583E", line_color="black")

        plot_resources = JS_RESOURCES.render(
                                                                                            js_raw=INLINE.js_raw,
            css_raw=INLINE.css_raw,
            js_files=INLINE.js_files,
            css_files=INLINE.css_files,
            )

        script, div = components(fig, INLINE)
        return render_template('index.html', form = form, 
                stock = {'id':form.openid.data}, 
                jsonURL = jsonURL, HTTPstatusCode = 'OK', 
                plot = {'script':script, 'div':div, 'resources':plot_resources})
    else:
        jdata = '' 
        return render_template('index.html', form = form, stock = {'id':form.openid.data}, jsonURL = jsonURL, HTTPstatusCode = 'code not found', stockdata = jdata)

