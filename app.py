import quandl
import requests
import pandas as pd
import datetime
from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure, output_notebook, show
from bokeh.embed import components
from bokeh.resources import CDN
import sys
import logging


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


@app.route('/')
def main():
    return redirect('/stocks')


@app.route('/stocks', methods=['GET', 'POST'])
def stockprice():
    if request.method == 'GET':
        return render_template('stocks.html')
    elif request.method == 'POST':
        theTicker = request.form['ticker']
        theOption = request.form.getlist('features')
        theDate = request.form['daterange']
# call function to build graph        
        plot = build_graph(theTicker, theOption, theDate)
# get the plot components        
        script, div = components(plot)
# render plot on HTML page        
        return render_template('stocks.html', script=script, div=div, bokeh_css=CDN.render_css(), bokeh_js=CDN.render_js())


def build_graph(ticker, option, date):
    quandl.ApiConfig.api_key = 'SsSxscVajXnHr-xdF98d'
    quandl.ApiConfig.api_version = '2015-04-09'

# Last 30 Days
    if date == 'days30':
        toDate = datetime.date.today()
        fromDate = toDate - datetime.timedelta(days=30)
# Previous Month
    if date == 'pmonth':
        first = datetime.date.today().replace(day=1)
        toDate = first - datetime.timedelta(days=1)
        fromDate = toDate.replace(day=1)

# Option selection
    if len(option) == 2:
        choice = option[0] + "," + option[1]
    elif len(option) == 1:
        choice = option[0]

# Based on ticker, option and date range, form URL to extract data from Quandl 
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?'
    params = "date.gte=" + fromDate.strftime('%Y%m%d') + "&date.lt=" + toDate.strftime('%Y%m%d') + "&ticker=" + ticker + "&qopts.columns=date," + choice +"&api_key=SsSxscVajXnHr-xdF98d"

# Get data from Quandl into dataframe
    r = requests.get(url + params)
    df = pd.DataFrame(r.json())

# slice dataframe df to get only required columns and format date column
    columns = ['date']
    if len(option) == 2:
        columns = columns + ['close', 'open']
    else:
        columns.append(choice)
    stock_data = pd.DataFrame(df.loc["data", "datatable"], columns=columns)
    stock_data.date = pd.to_datetime(stock_data.date)

# start Bokeh Plot
    p = figure(x_axis_type="datetime", width=500, height=500)
    p.xaxis.axis_label = "Date"
    p.xaxis.axis_label_text_color = "blue"
    p.yaxis.axis_label = "Price"
    p.yaxis.axis_label_text_color = "blue" 
    p.title = "Stock Prices for: " + ticker
#    p.title.text_color = "#4169e1"  
    p.title.text_font_size = '18pt'

# based on option build graph
    if len(option) == 2:
        p.line(stock_data.date, stock_data.close, color="red", legend = "Closing Price")
        p.line(stock_data.date, stock_data.open, color="blue", legend = "Opening Price")    
        p.legend.location = "top_left"    
    else:
        if choice == 'close':
            p.line(stock_data.date, stock_data.close, color="red")
        else:
            p.line(stock_data.date, stock_data.open, color="blue")
    return(p)


if __name__ == '__main__':
	app.run(debug=True)
