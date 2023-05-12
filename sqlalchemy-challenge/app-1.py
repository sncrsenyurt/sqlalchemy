# Import the dependencies.
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

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():

     return (
         f"Available Routes:<br/>"
         f"/api/v1.0/precipitation"
         f"- Dates and temperature observations from the last year<br/>"

         f"/api/v1.0/stations"
         f"- List of stations<br/>"

         f"/api/v1.0/tobs"
         f"- Temperature Observations from the past year<br/>"

         f"/api/v1.0/<start>"
         f"- Minimum temperature, the average temperature, and the max temperature for a given start day<br/>"

         f"/api/v1.0/<start>/<end>"
         f"- Minimum temperature, the average temperature, and the max temperature for a given range of days (start-end)<br/>"
     )




@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

   
    """ Convert the query results from your precipitation analysis 
    (i.e. retrieve only the last 12 months of data) to a dictionary 
    using date as the key and prcp as the value."""
    
    result = session.query(Measurement.date,Measurement.prcp).\
filter(Measurement.date >= '2016-08-23').all()

    session.close()

    
    results = []
        
    for date, prcp in result:
        results_dict = {}
        results_dict["date"] = date
        results_dict["prcp"] = prcp
        results.append(results_dict)

    
    return jsonify(results)


@app.route("/api/v1.0/stations")
def station():
    
    session = Session(engine)
    """Return a JSON list of stations from the dataset."""

    result = session.query(Station.station).all()
    
    result_ls = list(np.ravel(result))

    return jsonify(result_ls)




@app.route("/api/v1.0/tobs")

def tobs():

    session = Session(engine)

    query_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for date in query_date :
        latest_date= pd.to_datetime(date)
    
    recent = dt.date(latest_date.year-1,latest_date.month,latest_date.day)

    stations = session.query(Measurement.station,func.count(Measurement.id)).group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).all()
    

    temp = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == stations[0][0]).\
                    filter(Measurement.date >= recent).all()

    session.close()

    tobs_list = []
    for station,tobs in temp:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)
        
   
    return jsonify(tobs_list)
    
    
@app.route("/api/v1.0/<start>")

def start(start=None):

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                               func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(
        Measurement.date).all()
    from_start_list = list(from_start)
    return jsonify(from_start_list)


@app.route("/api/v1.0/<start>/<end>")

def start_end(start=None, end=None):


    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                  func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(
        Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list = list(between_dates)
    return jsonify(between_dates_list)

    


if __name__ == '__main__':
    app.run(debug=True)



































