#! /usr/bin/python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2018-06-10 16:45:18

import logging
import sys
import json
import pandas as pd
from flask import (Flask, request, render_template, jsonify)
from flask import url_for
from flaskext.mysql import MySQL
import urllib
import xml.etree.ElementTree as ET
from datetime import datetime

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'aws_ubuntu'
app.config['MYSQL_DATABASE_PASSWORD'] = 'jay'
app.config['MYSQL_DATABASE_DB'] = 'Flask_DB'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(
        filename, lineno, exc_type, exc_obj))


@app.route('/')
def main():
    try:
        return render_template('firstpage.html', PM25=PM25(), citys=get_citys())
    except:
        return render_template('firstpage.html', citys=get_citys())


def PM25():
    air_box_json = pd.read_json('https://pm25.lass-net.org/data/last-all-airbox.json')
    PM25points = [[s['gps_lat'], s['gps_lon'], s['s_d0']] for s in air_box_json['feeds']]
    return PM25points


def get_pneumonia():
    return pd.read_json('https://quality.data.gov.tw/dq_download_json.php?nid=14595&md5_url=8281b7ff9faf81e7399c6f734ed5f34b')


@app.route('/citys')
def get_citys():
    pneumonia = get_pneumonia()
    citys = pneumonia[['縣市']].drop_duplicates()
    return citys['縣市']


@app.route('/city_pneumonia', methods=['GET', 'POST'])
def City_pneumonia():
    city = request.args.get('city', None, type=str)
    pneumonia = get_pneumonia()
    pneumonia = pneumonia[pneumonia['縣市'] == city].groupby(
        '年')['健保就診總人次', '其他肺炎健保就診人次'].sum()
    logging.debug(pneumonia.to_json())
    return pneumonia.to_json()


@app.route('/weather_from_city', methods=['GET'])
def get_weather_from_city():
    city = request.args.get('city', None, type=str)
    date = request.args.get('date', None, type=int)
    return get_weather(city, date)


def get_weather_icon(condition: int):
    icon = ''
    condition=int(condition)
    if condition == 2:
        icon = 'cloud'
    elif condition == 8:
        icon = 'sun_with_cloud'
    elif condition == 17:
        icon = 'flash'
    elif condition == 36:
        icon = 'flash'
    elif condition == 7:
        icon = 'sun_with_cloud'
    elif condition == 5:
        icon = 'cloud'
    elif condition == 18:
        icon = 'rain_with_sun'
    elif condition == 12:
        icon = 'rain'
    else:
        icon = 'sun'
    return url_for('static', filename='pic/weather/{}.png'.format(icon))


def get_weather(city='台中市', date=0):
    weather = parse_weather_xml()
    return weather.date_dump(city, date)


def request_weather():
    weather_file = urllib.request.urlopen(
        'http://opendata.cwb.gov.tw/govdownload?dataid=F-C0032-005&authorizationkey=rdec-key-123-45678-011121314')
    weather_data = weather_file.read()
    weather_file.close()
    xml_np = {'default': 'urn:cwb:gov:tw:cwbcommon:0.1'}
    return weather_data, xml_np

def temp_c_to_f(temp_c):
        return temp_c * 1.8 + 32

class Time_element:

    def __init__(self, start_time: str, end_time: str, parameterName: str, parameterValue: str):
        self.start_time = start_time
        self.end_time = end_time
        self.parameterName = parameterName
        self.parameterValue = parameterValue
    
    def __str__(self):
        return '{},{},{},{}'.format(self.start_time,self.end_time,self.parameterName,self.parameterValue)


class Weather_element:

    def __init__(self, element_name: str):
        self.element_name = element_name
        self.time_element = []

    def append(self, time_element: Time_element):
        self.time_element.append(time_element)

    def __str__(self):
        return self.element_name

    def get_on_date(self, date: int):
        return self.time_element[date]


class Weather:

    def __init__(self, Wx: Weather_element, MinT: Weather_element, MaxT: Weather_element):
        self.Wx = Wx
        self.MinT = MinT
        self.MaxT = MaxT

    def get_weather_on_date(self, date: int):
        return self.Wx.get_on_date(date)

    def get_max_temperature_on_date(self, date: int):
        return self.MaxT.get_on_date(date)

    def get_min_temperature_on_date(self, date: int):
        return self.MinT.get_on_date(date)

    def get_date_of_weather(self, date: int):
        return self.get_weather_on_date(date), self.get_max_temperature_on_date(date), self.get_min_temperature_on_date(date)

    def date_dump(self, date):
        wx, min_t, max_t = self.get_date_of_weather(date)
        condition = {"text": wx.parameterName,
                     "icon": get_weather_icon(wx.parameterValue)}
        max_tc = max_t.parameterName
        min_tc = min_t.parameterName
        return {"max_temp_c": int(max_tc),
                "max_temp_f": temp_c_to_f(int(max_tc)),
                "min_temp_c": int(min_tc),
                "min_temp_f": temp_c_to_f(int(min_tc)),
                "condition": condition}


class Weathers(dict):

    def date_dump(self, city, date):
        weather = self.get(city)
        return json.dumps({"location": {
            "name": city,
            "country": "Taiwan"
        },
            "current": weather.date_dump(date)})


def parse_weather_xml():
    data, xml_np = request_weather()
    root = ET.fromstring(data)
    dataset = root.find('default:dataset', xml_np)
    weathers = Weathers()
    for location in dataset.findall('default:location', xml_np):
        city = location.find('default:locationName', xml_np).text
        weth_eles = []

        for w_ele in location.findall('default:weatherElement', xml_np):
            ele_name = w_ele.find('default:elementName', xml_np).text
            weth_ele = Weather_element(ele_name)
            if ele_name =='Wx':
                parameterValueRe='default:parameterValue'
            else:
                parameterValueRe='default:parameterUnit'

            for time in w_ele.findall('default:time', xml_np):
               
                    start_time=time.find('default:startTime',xml_np).text
                    end_time=time.find('default:endTime',xml_np).text
                    parameter=time.find('default:parameter',xml_np)
                    parameterName=parameter.find('default:parameterName',xml_np).text
                    parameterValue=parameter.find(parameterValueRe,xml_np).text
                    time_ele = Time_element(start_time, end_time,
                                        parameterName, parameterValue)
                    weth_ele.append(time_ele)
            weth_eles.append(weth_ele)

        weathers[city] = Weather(weth_eles[0], weth_eles[1], weth_eles[2])

    return weathers


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        app.run()
    except:
        PrintException()
