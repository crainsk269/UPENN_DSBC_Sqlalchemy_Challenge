# Import the dependencies.
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Start and End Dates
current_year_date = dt.date(2017, 8, 23)
previous_year_date = current_year_date - dt.timedelta(days=365)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"start and end date format: (yyyy-mm-dd)"
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    # Results filtered for previous year
    results = session.query(measurement.prcp, measurement.date).filter(measurement.date >= previous_year_date).all()

    session.close()

    # List builder to turn into json
    prcp_results = [{date:prcp} for prcp, date in results]
    
    return jsonify(prcp_results)

# Station Route
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    results = session.query(station.station).all()

    session.close()

    # Convert tuples list into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# Temperature Observations Route
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    results = session.query(measurement.date, measurement.prcp, measurement.tobs).\
                filter(measurement.date >= previous_year_date).\
                filter(measurement.station =='USC00519281').all()

    session.close()

    # List builder to turn into json
    all_tobs = [{"date":date, "prcp":prcp, "tobs":tobs} for date, prcp, tobs in results]

    return jsonify(all_tobs)

#################################################
# Dynamic Flask Routes
#################################################

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    session = Session(engine)

    results = session.query(func.avg(measurement.tobs),func.max(measurement.tobs),func.min(measurement.tobs)).filter(measurement.date >= previous_year_date).all()
    
    session.close() 

    # List builder for json
    start_date_tobs_values =[{"1. start_date":previous_year_date, "2. avg":avg, "3. max":max, "4. min":min} for avg, max, min in results]

    return jsonify(start_date_tobs_values)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    session = Session(engine)

    results = session.query(func.avg(measurement.tobs),func.max(measurement.tobs),func.min(measurement.tobs)).filter(measurement.date <= current_year_date).filter(measurement.date >= previous_year_date).all()

    session.close()

    # List builder for json
    start_end_date_tobs = [{"1. start_date":previous_year_date, "2. end_date":current_year_date, "3. avg":avg, "4. max":max, "5. min":min} for avg, max, min in results]

    return jsonify(start_end_date_tobs)

if __name__ == '__main__':
    app.run(debug=True)

