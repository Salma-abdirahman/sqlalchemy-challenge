import datetime as dt
import numpy as np
import pandas as pd

#Python SQLtoolkit, object relational mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# Importing Flask
from flask import Flask, jsonify

#Creating engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflecting database into a new model
Base = automap_base()

# reflecting the table
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save reference to the tables
#Measurement
Measurement = Base.classes.measurement
#show
Measurement

#Station
Station = Base.classes.station
#Show
Station

#Creating session
session = Session(engine)



# query, mst active station
most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

# most recent date
MostRecentDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
MostRecentDate

# Oldest date
oldest_date = session.query(Measurement.date).order_by(Measurement.date).first()

# Close Session
session.close()

# For landing
MostRecentDate_dt = dt.datetime.strptime(MostRecentDate[0], '%Y-%m-%d').date()
recent_dt_last_yr = MostRecentDate_dt - dt.timedelta(days=365)
date_last_yr = recent_dt_last_yr.strftime('%Y-%m-%d')

#Setting up flask
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/> List of Daily Precipitation in Honolulu, Hawaii between {date_last_yr} and {MostRecentDate_dt}<br/><br/>"
        f"/api/v1.0/stations<br/> List of stations<br/><br/>"
        f"/api/v1.0/tobs<br/> List of the dates and temperature observations of the most active station ({most_active_station[0]}) between {date_last_yr} and {MostRecentDate_dt}<br/><br/>"
        f"/api/v1.0/start_date<br/> List of MIN, AVE and MAX temperatures between the specified start date and {MostRecentDate_dt}, please input specified date<br/><br/>"
        f"/api/v1.0/start_date/end_date<br/> List of MIN, AVE and MAX temperatures of specified date, please input specifed date<br/><br/>"
       
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
   
    # Creating session
    session = Session(engine)
 
    # Query
    data_12_months = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= date_last_yr)

    # Close Session
    session.close()

    # Convert the query results to a dictionary 
    prcp_dict = dict(data_12_months)

    # Return the JSON representation of the dictionary
    return jsonify(prcp_dict)




# stations route
@app.route("/api/v1.0/stations")
def stations():
    
    # Creating session
    session = Session(engine)

    # Query
    stations = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Close Session
    session.close()

    # Convert the query results to dictionary
    station_data = []
    for id, station, name, lat, lng, ele in stations:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = lat
        station_dict["longitude"] = lng
        station_dict["elevation"] = ele
        station_data.append(station_dict)

    # Return the JSON representation of the dictionary
    return jsonify(station_data)




# tobs route for the most active station
@app.route("/api/v1.0/tobs")
def tobs():
   
    # Creating session
    session = Session(engine)
   
    # Query
    temp_observation = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station[0]).filter(Measurement.date >= date_last_yr).all()

    # Close Session
    session.close()

    # Convert the query results to dictionary
    tobs_dict = dict(temp_observation)
    tobs_dict["station"] = most_active_station[0]

    # Return the JSON representation of the dictionary
    return jsonify(tobs_dict)




# temperature routes
@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def temperature(start, end):

    # Creating sessopm
    session = Session(engine)

    # If date specified not between (2010-01-01 to 2017-08-23) Return "Invalid Input Dates".
    # If so, queries carried forward.
    if start > MostRecentDate[0] or (end !=None and end < oldest_date[0]):
        return ("Invalid Input Dates")
    else:
        if end:
            temp_calc = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        else:
            temp_calc = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

        # Close Session
        session.close()

    # Convert the query results to dictionary
    temp_data = []
    for min, avg, max in temp_calc:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = min
        temp_dict["Maximum Temperature"] = max
        temp_dict["Average Temperature"] = avg
        
    temp_dict["Start Date"] = start
    if end:
        temp_dict["End Date"] = end
    else:
        temp_dict["End Date"] = MostRecentDate[0]
    temp_data.append(temp_dict)

    # Return the JSON representation of the dictionary
    return jsonify(temp_data)


if __name__ == "__main__":
    app.run(debug=True)