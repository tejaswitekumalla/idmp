from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom

common_cluster ={
    "bgcolor":"white",
    "fontsize" : "20",
    "pencolor" : "brown",
    "penwidth" : "1",
    "orientation" : "portrait"
}

temp_cluster = {
    "pencolor" : "brown",
    "penwidth" : "0",
    "bgcolor" : "white",
}

main_cluster ={
    "labelloc" : "t",
    "fontsize" : "28",
    "splines" : "spline"
}

with Diagram("Network Architecture", show=False, graph_attr= main_cluster):
    with Cluster("", graph_attr=temp_cluster): 
        with Cluster("Storage Backup 2", graph_attr=common_cluster):
            data_1 = Custom("Backup Server 2", "./images/DB_replicate_1.png")
        with Cluster("Storage Backup 1",graph_attr=common_cluster):
            data_2 = Custom("Backup Server 1","./images/DB_replicate_2.png")       

    with Cluster("",graph_attr=temp_cluster):
        with Cluster("  Application Layer \n ", graph_attr=common_cluster):
            server = [Custom("Application\n Server\n\n", "./images/Server.png")]
        with Cluster("  Database Layer",graph_attr=common_cluster):
            db = Custom("\nDatabase\nServer\n\n", "./images/Database.jpg")
    with Cluster("  Presentation Layer", graph_attr=common_cluster):
        clients = [Custom("Client","./images/Client.png") for i in range(3)]

    # Connections
    for index in range(len(clients)):
        clients[index] >> Edge(style="bold") >> server[0]
    server[0] << Edge(style="bold", minlen="2") >> db
    server[0] >> Edge(xlabel="  Application \n Backup", style="bold") >> data_1
    server[0] >> Edge(xlabel="\nApplication\n Backup", style="bold") >> data_2
    db >> Edge(label="\nDB Backup", style="bold") >> data_1
    db >> Edge(label="\nDB Backup", style="bold") >> data_2

