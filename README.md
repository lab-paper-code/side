TS-trie
=============
[VLDB'24] TS-Trie: A Temporal-Prefix based Indexing Scheme for Fast Spatiotemporal IoT Data Retrieval
* [What is TS-trie](#What-is-TS-trie)
* [Settings](#Settings)
    *  [Environments](#Environments)
    *  [Public datasets](#Public-datasets)
* [Building from source](#Building-from-source)
    * [Build TS-trie indexing server](#build-ts-trie-indexing-server)
    * [Build front application server](#Buil-front-application-server)
* [Main Features](#Main-Features)
    * [Point query](#Point-query)
    * [Trajectory query](#trajectory-query)
* [How to Use](#How-to-Use)
    * [Experiment input form](#experiment-input-form)
    * [Experiment process](#experiment-process)


## What is TS-trie

<p align="center">
  <img align="center" width="50%" src="figures/TS-Trie_structure.jpg"></img>
</p>
TS-trie is an trie-based indexing scheme that enables efficient spatiotemporal query by utilizing binary trie and single binary index data composed of spatial and temporal information. 
It involves encoding a one-dimensional indexing key by using the time information as a prefix and connecting it with the spatial information. Furthermore, it offers high compression efficiency, effectively utilizing space, and reducing costs incurred during indexing management and maintenance processes. Currently TS-trie provides spatiotemporal indexing on top of the general NoSQL database and capable of handling spatiotemporal range, k-NN, Top-k, and trajectory similarity query functionalities. 


## Settings

### Environments

* [Ubuntu 20.04 LTS]
* [C++17]
* [GCC 7.5.0]
* [MongoDB 6.0.4]
* [S2Geometry 0.9.0.]
* [Python 3.8.3]

### Public datasets
  - T-Drive : https://www.microsoft.com/en-us/research/publication/t-drive-trajectory-data-sample/
  - Chicago : https://data.cityofchicago.org/Transportation/Taxi-Trips-2013-2023-/wrvz-psew/about_data
  - NYC-yellow : https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
  - Porto : https://www.kaggle.com/c/pkdd-15-predict-taxi-service-trajectory-i/data


## Building from source


### Build TS-trie indexing server

 Before initiating the compilation process, you need to choose the desired dataset and index format in the location marked with *** in `config.txt` located at `CODE/index/`.

    DB_name = SIDE-***
    Index_name = ***

You can use __T-Drive__, __Chicago__, __NYC-yellow__, or __Porto__ for the DB_name,

And for the Index_name, choose __TSC-index__ for the point query or __TSC-index_traj__ for the trajectory query.

For example, if you want to check the Chicago dataset with point query, modify the config file as follows.

    DB_name = SIDE-Chicago
    Index_name = TSC-index




Move to `CODE/index/TS-trie` and then compile the code below.

```
sudo g++ --std=c++14 BinaryTrie.h iot_time.h iot_time.cpp cover.h cover.cpp iot_func.h iot_func.cpp ConfigParser.h ConfigParser.cpp main.cpp -o Index $(pkg-config --cflags --libs libmongocxx) -ls2 -lboost_system -lcrypto -lssl -lcpprest -O2 -Wall -lm -m64 -lpthread
```

After compiling, execute the generated `Index` file. This will start the server.

    ./Index


### Build front application server

Open a new terminal and move to `CODE/Web`.

Then execute the code below. 

    python3 app.py

Now you can access the experimental web page.


## Main Features

### Point query
 * #### Spatiotemporal range query

     - Find all spatiotemporal points satisfying the given spatiotemporal conditions.

 * #### k-NN query

     - Retrieve __k__ points in order of proximity from the given x, y coordinates while satisfying the spatiotemporal conditions

 * #### Top-k query

     - Retrieve __k__ points satisfying the given spatiotemporal conditions, selected from an arbitrary ordering criteria.
     - In our experiments, we sorted in descending order based on latitude.


### Trajectory query
 * ####  Spatiotemporal range query

     - Find all trajectories to which points satisfying the given spatiotemporal conditions.

 * ####  k-Similarity query

     - Identify a set of __k__ trajectories within a database that are most similar to a specific trajectory data


## How to Use

### Experiment input form
 - a time range with __two dates__, represented in the ISO 8601 standard format as `YYYY-MM-DD:hh`
 - a rectangular spatial range with __two spatial points__ for spatialtemporal range query, indicating coordinates in terms of __latitude__ and __longitude__.

    example:
    ```
    2013-07-01:09:00:00 ~ 2013-07-01:21:00:00

    (41.15255, -8.650274), (41.161985, -8.638086) #(latitude, longitude), (latitude, longitude)
    ```
 - a circular spatial range with __one spatial point__ for kNN, top-k query.

    example:
    ```
    2013-07-01:09:00:00 ~ 2013-07-01:21:00:00

    (41.15255, -8.650274), 1000 #(latitude, longitude), radius
    ```

### Experiment process

1. Access the web page through  `your_server_IP:8080`.

2. Place the cursor over the query format applied during compilation (__point__ or __trajectory__) at the top right corner of the webpage, and then choose a specific [query method.](#Main-features)

3. Choose the start and end dates under the time condition.

4. Click on the rectangle shape on the map, then drag to set the spatial range as desired.

    If you've incorrectly set the rectangle, select the trash can icon, click on the rectangles you want to delete, and press the save button next to the icon to remove them.

    > **Warning**
    > If you drag too much on the map, it could occur an error on the server.


5. Press the "Get Coordinate range" button to confirm the input of coordinates
    


6. Press the search button to review the query results.


