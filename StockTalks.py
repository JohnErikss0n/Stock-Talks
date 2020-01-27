import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from lxml import html
import requests
from flask import Flask, make_response, jsonify, request

#Get Spreadsheet Info
spreadsheet_name = "Portfolio"
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(spreadsheet_name).sheet1  # Open the spreadhseet
data = sheet.get_all_records()  # Get a list of all records


def find_ticker(stock_name):
    stock_name = stock_name.replace(" ","+")
    url = "https://www.google.com/search?q=cheese+stock"
    url = url.replace("cheese",stock_name)
    google_request = requests.get(url)
    tree = html.fromstring(google_request.content)
    try:
        tickr_list = tree.xpath('//span[@class="r0bn4c rQMQod"]/text()')
        for i in tickr_list:
            if "(" in i:
                split_list = i
        split_list = split_list.split("(")
        tickr = split_list[0]
        market = split_list[1].strip(")")
        if stock_name=="Google":
            tickr = "GOOG"
        return tickr, market
    except:
        return "Stock Not Found"

def add(sheet_name, name, ticker, market):
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    length = len(data) +1
    if length <=1:
        length = 2
    try:
        price = '=GOOGLEFINANCE("&","price")'.replace("&",ticker)
        current_time = str(datetime.now())
        pe = '=GOOGLEFINANCE("&","pe")'.replace("&",ticker)
        pct = '=GOOGLEFINANCE("&","changepct")'.replace("&",ticker)
        currency = '=GOOGLEFINANCE("&","currency")'.replace("&",ticker)
        insertRow = [name, ticker, price, price, current_time, pe, pct, currency, market]
        sheet.insert_row(insertRow, length, value_input_option='USER_ENTERED')
        static_val = sheet.cell(length,3,value_render_option="FORMATTED_VALUE").value
        sheet.update_cell(length,4,static_val)
        return "Stock Sucessfully Added"
    except:
        return "Stock Not Added"
    
def remove(sheet_name, name):
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    counter = 2
    for i in data:
        if i["Name"] == name:
            sheet.delete_row(counter)
            return "Stock Sucessfully Deleted"
        else:
            counter+=1
    return "Stock Not Found"

def check(sheet_name, name):
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    counter = 2
    for i in data:
        if i["Name"] == name:
            break
        else:
            counter +=1
    try:
        row_data = sheet.row_values(counter, value_render_option="FORMATTED_VALUE")
        print(sheet.cell(counter,3,value_render_option="FORMATTED_VALUE").value)
        current = float(sheet.cell(counter,3,value_render_option="FORMATTED_VALUE").value)
        previous = float(sheet.cell(counter,4,value_render_option="FORMATTED_VALUE").value)
        change_percent = ((float(current)-previous)/previous)*100
        ans_str = row_data[0] + " is currently trading at " + row_data[2] + row_data[7] +". It has a price to earning ratio of " + row_data[5] + " and is has a daily percent change of "+row_data[6]+". This stock has changed by "+str(change_percent)+" percent since it was first added."
        return ans_str
    except:
        return "Could not get updated info"
    
def bestperformer(sheet_name):
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    flag = 0
    if len(data)==0:
        return "Your portfolio is empty"
    for i in data:
        if flag == 0:
            max = i["Current Price"]/i["Added Price"]
            nom = i['Name']
        else:
            if (i["Current Price"]/i["Added Price"])>max:
                max = i["Current Price"]/i["Added Price"]
                nom = i["Name"]
    return nom #returns string name

def overview(sheet_name):
    data = sheet.get_all_records()
    string = ""
    flag = 0
    if len(data)==0:
        return "Your portfolio is empty"
    for i in data:
        if flag ==0:
            string+= "Your first stock is "+i['Name']
            string+=" with a price of "+str(i['Current Price'])+'. '
            string+="You added it to your portfolio with a price of "+str(i['Added Price'])+" for a percent change of "+str(round(((i["Current Price"]/i["Added Price"])-1)*100,2))+". "
            flag = 1
        else:
            string+= "Your next stock is "+i['Name']
            string+=" with a price of "+str(i['Current Price'])+'. '
            string+="You added it to your portfolio with a price of "+str(i['Added Price'])+" for a percent change of "+str(round(((i["Current Price"]/i["Added Price"])-1)*100,2))+". "
            flag = 1
    return string #returns string to explain your stocks

    
def find_add(sheet_name, name):
    try:
        stock = find_ticker(name)
        add(sheet_name, name, stock[0], stock[1])
        return "Stock Sucessfully Added"
    except:
        return "Stock Not Added"

def score(sheet_name):
    data = sheet.get_all_records()
    score = float(sheet.cell(2,10, value_render_option="FORMATTED_VALUE").value)
    for i in data:
        score +=float(i["Daily Percent Change"])
    sheet.update_cell(2,10,score)
    string = "Your Score is "+ str(score)
    return string

#Initialize the flask app
app = Flask(__name__)
@app.route('/', methods=['GET','POST'])
def hello():
    print("Cheese")
    response = "Hello"
    req = request.get_json(silent=True, force=True)
    result = req.get("queryResult")
    parameters = result.get("parameters")
    try:
        stock = parameters['any']
    except:
        pass
    intent_b = result.get("intent")
    intent = intent_b["displayName"]
    if intent == "Add":
        response = find_add(spreadsheet_name,stock)
    elif intent == "Remove":
        response = remove(spreadsheet_name, stock)
    elif intent == "Check":
        stock = parameters['Compname']
        response = check(spreadsheet_name, stock)
    elif intent == "Overview":
        response = overview(spreadsheet_name)
    elif intent == "BestPerformer":
        response = bestperformer(spreadsheet_name)
    elif intent == "Score":
        response = score(spreadsheet_name)
    reply = {
        "fulfillmentText": response,
    }
    return jsonify(reply)

#Run the app
if __name__ == '__main__':
   app.run()
