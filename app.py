from flask import Flask, jsonify

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route('/')
def welcome():
    #List all avaialable API Routes
    return(
    f'<strong>Available Routes:<br></strong>'
    f'<a href = "/api/v1.0/precipation">/api/v1.0/precipation</a><br>'
    f'Use this to find the amount of precipitation recorded per day.<br>'
    f'<a href = "/api/v1.0/stations">/api/v1.0/stations</a><br>'
    'Return a list of stations from the dataset<br>. Returns Station identifier, name, latitude, longitude, and elevation.'
    f'<a href = "/api/v1.0/tobs">/api/v1.0/tobs</a><br>'
    'Return a list of the observed temperatures at the most active station<br>'
    f'/api/v1.0/[start] and /api/v1.0/[start]/[end]<br>'
    'Takes a start and end date in the format YEAR-MM-DD, and returns the minimum, average, and maximum temperatures across that timeframe.'
    )


@app.route('/api/v1.0/precipation')
def precipation():
    session= Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    results_dict = {}

    for i in results:
        results_dict[i[0]] = i[1]

    return jsonify(results_dict)


@app.route('/api/v1.0/stations')
def stations():

    session = Session(engine)

    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    results_list = []
    for i in results:
        temp_dict = {}
        temp_dict['elevation'] = i[4]
        temp_dict['lng'] = i[3]
        temp_dict['lat'] = i[2]
        temp_dict['name'] = i[1]
        temp_dict['station'] = i[0]
        results_list.append(temp_dict)
    return jsonify(results_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).\
                            filter(Measurement.station == 'USC00519281').\
                            filter(Measurement.date > "2016-08-23").\
                            order_by(Measurement.date).all()
    session.close()
    results_dict = {}
    for i in results:
        results_dict[i[0]] = i[1]

    return jsonify(results_dict)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)

    results = session.query(Measurement.station, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        group_by(Measurement.station).\
                        filter(Measurement.date >= start).all()
    session.close()
    results_list = []
    for i in results:
        temp_dict = {
            'station':i[0],
            'min':i[1],
            'avg':i[2],
            'max':i[3]
        }
        results_list.append(temp_dict)
    return jsonify(results_list)


@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)

    results = session.query(Measurement.station, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        group_by(Measurement.station).\
                        filter(Measurement.date <= end).\
                        filter(Measurement.date >= start).all()
    session.close()
    results_list = []
    for i in results:
        temp_dict = {
            'station':i[0],
            'min':i[1],
            'avg':i[2],
            'max':i[3]
        }
        results_list.append(temp_dict)
    return jsonify(results_list)








if __name__ == '__main__':
    app.run(debug=True)
