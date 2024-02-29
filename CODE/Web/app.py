from flask import Flask, render_template, request, make_response
from datetime import datetime
from time import time
import os

# User defined Library
import queryProcessor
import utility

app = Flask(__name__)
app.config["DEBUG"] = True


# home page rendering
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template(
        'index.html',
        title = 'KIDARI Demo page'
    )

# Render search tab
@app.route('/search')

# Point type query
@app.route('/search/range', methods=['GET', 'POST'])
def range_query():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    conf_path = "/home/air7/SIDE/yjooy/CODE/index/config.txt"
    search_string = 'DB_name ='

    with open(conf_path, 'r', encoding='utf-8') as file:
        for line in file:
            if search_string in line:
                db_str = line.strip()

    return render_template(
        'search_range.html',
        db_ = db_str 
    )

@app.route('/search/knn', methods=['GET', 'POST'])
def knn_query():
    conf_path = "/home/air7/SIDE/yjooy/CODE/index/config.txt"
    search_string = 'DB_name ='

    with open(conf_path, 'r', encoding='utf-8') as file:
        for line in file:
            if search_string in line:
                db_str = line.strip()

    return render_template(
        'search_knn.html',
        db_ = db_str 
    )
    

@app.route('/search/topk', methods=['GET', 'POST'])
def topk_query():
    conf_path = "/home/air7/SIDE/yjooy/CODE/index/config.txt"
    search_string = 'DB_name ='

    with open(conf_path, 'r', encoding='utf-8') as file:
        for line in file:
            if search_string in line:
                db_str = line.strip()

    return render_template(
        'search_topk.html',
        db_ = db_str 
    )

# Trajectory type query
@app.route('/search/trajectory')
@app.route('/search/trajectory/range', methods=['GET','POST'])
def traj_range_query():
    conf_path = "/home/air7/SIDE/yjooy/CODE/index/config.txt"
    search_string = 'DB_name ='

    with open(conf_path, 'r', encoding='utf-8') as file:
        for line in file:
            if search_string in line:
                db_str = line.strip()

    return render_template(
        'search_traj_range.html',
        db_ = db_str 
    )

@app.route('/search/trajectory/similarity', methods=['GET','POST'])
def traj_similarity_query():
    conf_path = "/home/air7/SIDE/yjooy/CODE/index/config.txt"
    search_string = 'DB_name ='

    with open(conf_path, 'r', encoding='utf-8') as file:
        for line in file:
            if search_string in line:
                db_str = line.strip()

    return render_template(
        'search_traj_similarity.html',
        db_ = db_str 
    )




# [Point] - Spatio-temporal range
@app.route('/result/range', methods=['GET', 'POST'])
def result_range():
    query_data = None
    index_key = None

    if request.method == 'POST':
        query_data = utility.input_parser(request.form)
    print('user input: ',query_data)

    # query process time
    start_time = time()
    res = queryProcessor.range_query(query_data, index_key)
    end_time = time()

    print("searched data : {}" .format(len(res)))
    elapsed_time = round(end_time - start_time, 3)
    print("total elapesd time : {}\n" .format(elapsed_time))


    # Visualization
    index_type = "stc" if query_data['trie_type'] == 'ST' else 'tsc'
    utility.S2CellMapJS(index_type, index_key, query_data)


    return render_template(
        'result_range.html',
        res = res,
        query_data = query_data,
        elapsed_time = elapsed_time
    )


# [Point] - k-NN
@app.route('/result/knn', methods=['GET', 'POST'])
def result_knn():
    query_data = None

    if request.method == 'POST':
        query_data = utility.input_parser(request.form)
    print('user input: ',query_data)

    # query process time
    start_time = time()
    res = queryProcessor.knn_query(query_data)
    end_time = time()

    print("searched data : {}" .format(len(res)))
    elapsed_time = round(end_time - start_time, 3)
    print("total elapesd time : {}\n" .format(elapsed_time))

    return render_template(
        'result_knn.html',
        res = res,
        query_data = query_data,
        elapsed_time = elapsed_time,
    )


# [Point] - Top-k
@app.route('/result/topk', methods=['GET', 'POST'])
def result_topk():
    query_data = None

    if request.method == 'POST':
        query_data = utility.input_parser(request.form)
    print('user input: ', query_data)

    # query process time
    start_time = time()
    origin, res = queryProcessor.topk_query(query_data)
    end_time = time()

    print("searched data : {}" .format(len(res)))
    elapsed_time = round(end_time - start_time, 3)
    print("total elapesd time : {}\n" .format(elapsed_time))

    return render_template(
        'result_topk.html',
        origin=origin,
        res=res,
        query_data = query_data,
        elapsed_time=elapsed_time,
    )


# [Trajectory] - Spatio-temporal range
@app.route('/result/trajectory/range', methods=['GET', 'POST'])
def result_traj_range():
    query_data = None

    if request.method == 'POST':
        query_data = utility.input_parser(request.form)
    print('user input: ', query_data)

    # query process time
    start_time = time()
    res = queryProcessor.trajectory_range_query(query_data)
    end_time = time()

    # print count of searched trajectories
    print("searched trajectory data : {}" .format(len(res)))
    elapsed_time = round(end_time - start_time, 3)
    print("total elapesd time : {}\n" .format(elapsed_time))

    # Visualization
    utility.S2CellMapJS(None, None, query_data, 'Trajectory', res)
    
    return render_template(
        'result_traj_range.html',
        res = res,
        query_data = query_data,
        elapsed_time = elapsed_time,
    )


# [Trajectory] - Similarity Query
@app.route('/result/trajectory/similarity', methods=['GET', 'POST'])
def result_traj_similarity():
    query_data = None

    if request.method == 'POST':
        query_data = utility.input_parser(request.form)
    print('user input: ', query_data)

    # query process time
    start_time = time()
    res = queryProcessor.trajectory_similarity_query(query_data, request.form['querying_traj'])
    end_time = time()
    elapsed_time = round(end_time - start_time, 3)
    print("total elapesd time : {}\n" .format(elapsed_time))

    
    return render_template(
        'result_traj_similarity.html',
        res = res,
        query_data = query_data,
        elapsed_time = elapsed_time,
    )




if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=8080)
    app.jinja_env.auto_reload = True
