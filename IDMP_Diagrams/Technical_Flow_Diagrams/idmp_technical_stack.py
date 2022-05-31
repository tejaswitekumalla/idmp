from diagrams import Diagram, Cluster, Edge
from diagrams.programming.framework import Angular
from diagrams.programming.language import Nodejs
from diagrams.onprem.database import Mysql
from diagrams.onprem.inmemory import Redis
from diagrams.custom import Custom

graph_attr_style = {
    "labelloc" : "t",
    "splines" : "curved",
    "fontsize": "24"
}

common_cluster = {
    "bgcolor" : "white",
    "pencolor" : "brown",
    "penwidth" : "0"
    
}

with Diagram("Technical Stack", show=False, direction="TB", graph_attr= graph_attr_style):
    
    with Cluster("",graph_attr= common_cluster):
        app = [
            Angular("(Client Side Technology)\n\n"),
            Custom("(Server Side Technology)\n\n","./images/nodejs.png")
        ]
    
    # redis = Redis("Redis")
    
    mysql = Mysql("Database")
    
    app[0] << Edge(label="") >> app[1]
    app[1] << Edge() >> mysql
    # app[1] << Edge() >> redis


