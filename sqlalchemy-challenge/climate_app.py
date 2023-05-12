

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

### A) Static Routes:
#--------------------

@app.route("/")
def home ():
    return (
        f"Welcome to Climate App Home API!<br/>"
        f"********************************<br/>"
        f"Available Routes:<br/>"
        f"----------------------<br/>"
        f" A) Static Routes:<br/>"
        f"------------------------<br/>"        
        f"  1) Precipitation: <br/>"
        f"  /api/v1.0/precipitation<br/>"
        f"  Precipitation Hyperlink Only if using http://127.0.0.1:5000/:    <a href=http://127.0.0.1:5000/api/v1.0/precipitation> /api/v1.0/precipitation</a> <br/>"
        f"  2) Stations List:  <br/>" 
        f"  /api/v1.0/stations<br/>"
        f"  Stations Hyperlink Only if using http://127.0.0.1:5000/:    <a href=http://127.0.0.1:5000/api/v1.0/stations> /api/v1.0/stations</a> <br/>"
        f"  3) Temperature for one year:  <br/>"
        f"  /api/v1.0/tobs<br/>"
        f"  Tobs Hyperlink Only if using http://127.0.0.1:5000/:   <a href=http://127.0.0.1:5000/api/v1.0/tobs> /api/v1.0/tobs</a> <br/>"
        f"-------------------<br/>"
        f" B) Dynamic Routes:<br/>"
        f"-------------------------<br/>"
        f"  4) Temperature stat from the start date(yyyy-mm-dd):     /api/v1.0/start_date/*Type-Start-Date-Here*<br/>"
#        f"      <a href=http://127.0.0.1:5000/api/v1.0/start_date/> /api/v1.0/start_date/Type-Start-Date-Here</a> <br/>"
        f"  5) Temperature stat from start to end dates(yyyy-mm-dd)/(yyyy-mm-dd):     /api/v1.0/start_to_end_date/*Type-Start-Date-Here*/*Type-End-Date-Here*<br/>"
#        f"      <a href=http://127.0.0.1:5000/api/v1.0//api/v1.0/start_to_end_date/Type-Start-Date-Here/Type-End-Date-Here> /api/v1.0/start_to_end_date/Type-Here-Start-Date/Type-Here-End-Date</a> <br/>"
        f" <br/>" 
        f"NOTE: If dates are not in format yyyy-mm-dd it will return an error <br>" 
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data as json"""
    session = Session(engine)

    query_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for date in query_date :
        latest_date= pd.to_datetime(date)

    year_from_recent = dt.date(latest_date.year-1,latest_date.month,latest_date.day)
    one_year = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= year_from_recent).all()
#    one_year

    session.close()

    # creating a list of dictionaries returns jsonify "preceipitation"
    precipitation = []
    for date, prcp in one_year:
        prcp_dict = {}
        # prcp_dict["Date"] = date
        # prcp_dict["Precipitation"] = prcp
        prcp_dict[date]= prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)



@app.route("/api/v1.0/stations")
def stations():
    """Return the stations data as json"""
    session = Session(engine)
    
    station_query = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()

    session.close()

    # creating a list of dictionaries returns jsonify "stations" list
    stations = []
    for station,name,lat,lon,el in station_query:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)



@app.route("/api/v1.0/tobs")
def tobs():
    """Return the stations data as json"""
    session = Session(engine)

    query_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for date in query_date :
        latest_date= pd.to_datetime(date)
    
    year_from_recent = dt.date(latest_date.year-1,latest_date.month,latest_date.day)

    active_stations = session.query(Measurement.station,func.count(Measurement.id)).group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).all()
    #  active_stations

    # most_active_stations = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    #     group_by(Measurement.station).\
    #     order_by(func.count(Measurement.id).desc()).first()
    # most_active_stations

    temp_results = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == active_stations[0][0]).\
                    filter(Measurement.date >= year_from_recent).all()

    session.close()


#    # 1st way to creating a list of dictionaries returns jsonify "tobs_list" list
    tobs_list = []
    for station,tobs in temp_results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)

#   # 2nd way to do a list of Dict
#    tobs_list = [dict(temp_results)]
   
    return jsonify(tobs_list)



### B) Dynamics Routes:
#----------------------

@app.route("/api/v1.0/start_date/<start_date>")
def start_date(start_date):
#    """Fetch the start_date character whose <start_date> matches
#       the path variable supplied by the user, or a 404 if not."""

    """Return the stations data as json"""
    session = Session(engine)

    Active_id = [func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    temp_stations = session.query(*Active_id).\
        filter(Measurement.date >= start_date).all()

# will be only used if need only most active station
        # group_by(Measurement.station).\
        # order_by(func.count(Measurement.id).desc()).first()

    session.close()

    # creating a list of dictionaries returns jsonify "stations_calc_list" (min, max, avg) list
    stations_calc_list = []
    for min,max,avg in temp_stations:
        stations_calc_dict = {}
#        stations_calc_dict["Start Date"] = start_date
        stations_calc_dict["Minimum"] = min
        stations_calc_dict["Maximum"] = max
        stations_calc_dict["Average"] = avg
        stations_calc_list.append(stations_calc_dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if stations_calc_dict['Minimum']:
        return jsonify(start_date,stations_calc_list)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range or dates not formatted correctly."}), 404



@app.route("/api/v1.0/start_to_end_date/<start_date>/<end_date>")
def start_to_end_date(start_date,end_date):
#    """Fetch the start_date character whose <start_date> matches
#       the path variable supplied by the user, or a 404 if not."""

    """Return the stations data as json"""
    session = Session(engine)

    Active_dtrange_id = [func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    temp_stations_dtrange = session.query(*Active_dtrange_id).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    # creating a list of dictionaries returns jsonify "stations_calc_list" (min, max, avg) list
    stations_calc_dtrange_list = []
    for min,max,avg in temp_stations_dtrange:
        stations_calc_dtrange_dict = {}
#        stations_calc_dtrange_dict["Start Date"] = start_date
#        stations_calc_dtrange_dict["End Date"] = end_date
        stations_calc_dtrange_dict["Minimum"] = min
        stations_calc_dtrange_dict["Maximum"] = max
        stations_calc_dtrange_dict["Average"] = avg
        stations_calc_dtrange_list.append(stations_calc_dtrange_dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if stations_calc_dtrange_dict['Minimum']:
        return jsonify(start_date,end_date,stations_calc_dtrange_list)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range or dates not formatted correctly."}), 404

if __name__ == "__main__":
    app.run(debug=True)
