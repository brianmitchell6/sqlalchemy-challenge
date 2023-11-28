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
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Get last date of data
    recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    # Query returned a tuple.  Need to convert to string for strptime function
    for row in recent:
        recent_date = row

    # Calculate the date one year from the last date in data set.
    date_format = '%Y-%m-%d'      # Set date format
    start_date = dt.datetime.strptime(recent_date, date_format).date()   # Convert string to datetime date
    year_ago = start_date - dt.timedelta(days=365)   # Calculate date one year ago

    # Perform a query to retrieve the data and precipitation scores
    date_prcp = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()
    date_prcp_list = list(np.ravel(date_prcp))
    
    return jsonify(date_prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(measurement.station).group_by(measurement.station).all()
    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Get last date of data
    recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    # Query returned a tuple.  Need to convert to string for strptime function
    for row in recent:
        recent_date = row

    # Calculate the date one year from the last date in data set.
    date_format = '%Y-%m-%d'      # Set date format
    start_date = dt.datetime.strptime(recent_date, date_format).date()   # Convert string to datetime date
    year_ago = start_date - dt.timedelta(days=365)   # Calculate date one year ago
    
    # Get list of stations with row counts and reverse sort
    station_count = session.query(measurement.station, func.count(measurement.station))\
        .group_by(measurement.station)\
        .order_by(func.count(measurement.station)).all()
    station_count = sorted(station_count, key=lambda count: count[1], reverse=True)
    # Get most active station name
    active = station_count[0][0]
    year_temps = session.query(measurement.date, measurement.tobs).filter(measurement.station==active, measurement.date>=year_ago).all()
    year_temps_list = list(np.ravel(year_temps))

    return jsonify(year_temps_list)


@app.route("/api/v1.0/<start>")
def start_only(start):
    # Get last date of data
    recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    # Query returned a tuple.  Need to convert to string for strptime function
    for row in recent:
        recent_date = row

    # Convert string to datetime
    date_format = '%Y-%m-%d'      # Set date format
    last_date = dt.datetime.strptime(recent_date, date_format).date()   




if __name__ == "__main__":
    app.run(debug=True)

session.close()