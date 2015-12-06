
from flask import render_template, flash, redirect, url_for
import requests
import numpy as np
import pandas as pd
from app import app
from .forms import LoginForm, TypeForm, RangeForm
import datetime

from bokeh.embed import components
from bokeh.plotting import figure, show, output_file
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

@app.route('/')
def main():
    return redirect(url_for('index'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    typeform = TypeForm()
    rangeform = RangeForm()
    stockcode = form.openid.data
    stockperiod = "6M"
    colName = "Adj. Close"

    if not ( stockcode and stockcode.strip() ):
        stockcode = "GOOG"

    if rangeform.date_type.data:
        stockperiod = rangeform.date_type.data


    #request data from QuanDL
    api_key = "TkW9xrpVCzTLCMwZDGK9"
    baseURL='https://www.quandl.com/api/v1/datasets/WIKI/'
    periodURL={'1M':'?trim_start=' + (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
            '6M':'?trim_start=' + (datetime.datetime.now() - datetime.timedelta(days=183)).strftime('%Y-%m-%d'),
            '1Y':'?trim_start=' + (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d'),
            'All':'',
            'None':''}

    if not periodURL[stockperiod]:
        jsonURL = baseURL + stockcode + '.json?api_key=' + api_key
    else:
        jsonURL=baseURL + stockcode + '.json' + periodURL[stockperiod] + '&api_key=' + api_key
    jsonRespond = requests.get(jsonURL)
    HTTPstatusCode=jsonRespond.status_code

    print jsonURL
            

    # If http status is ok.
    if HTTPstatusCode == 200:
        jheader = (jsonRespond.json())['column_names']
        jdata = (jsonRespond.json())['data']
        stock_full_name = (jsonRespond.json())['name'].split(',')[0]
        stockdata = pd.DataFrame(jdata, columns=jheader)
        stockdata["Date"] = pd.to_datetime(stockdata["Date"])

        print jsonURL
        print HTTPstatusCode
        print stockcode
        print stockperiod
        print typeform.stock_type.data, colName

        if typeform.stock_type.data != u'None':
            colName = typeform.stock_type.data

        output_file(stockcode + ".html", title=stockcode + " example")
        fig = figure(title=stock_full_name + ", "+ colName, 
                plot_width=600, plot_height=480,x_axis_type="datetime", 
                toolbar_location="below", 
                tools = "pan,wheel_zoom,box_zoom,reset,resize")
        fig.line(np.array(stockdata.Date), np.array(stockdata[colName]))

        js_resources = INLINE.js_raw
        css_resources = INLINE.css_raw

        script, div = components(fig)

        return render_template('index.html', form = form, 
            typeform = typeform,
            rangeform = rangeform,
            stock = {'id':form.openid.data}, 
            jsonURL = jsonURL, HTTPstatusCode = 'OK',
            plot = {'script':script, 'div':div, 
            'js_resources':js_resources, 'css_resources':css_resources})
    else:

        return render_template('index.html', form = form, 
            typeform = typeform,
            rangeform = rangeform,
            stock = {'id':form.openid.data}, 
            plot = {'script':"", 'div':"Stock Symbol not Found, please try a different symbol.", 
            'js_resources':None, 'css_resources':None})

