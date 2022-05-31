from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom

test = {
    "bgcolor":"white",
    "fontsize" : "15",
    "pencolor" : "brown",
    "penwidth" : "0",
    "fontsize" : "20",
}

main_diagram_cluster ={ 
    "labelloc" : "t",
    "fontsize" : "28",
    # "splines" : "spline"
}

edge_attr = {
    "fontsize" : "14"
}
outer_cluster = {
    "bgcolor":"white",
    "fontsize" : "15",
    "pencolor" : "brown",
    "penwidth" : "1",
    "fontsize" : "20"
}
with Diagram("Function Flow of IDMP Application",direction="LR" ,show=False, graph_attr=main_diagram_cluster) as diag:
    with Cluster("", graph_attr= outer_cluster):
        with Cluster("", direction="RL", graph_attr=test):
            app = [Custom("Initiators", "./images/Users.jpg"),
                Custom("IDMP\nApplication", "./images/idmp.jpeg"),
                Custom("Reports\n", "./images/Reports.png"), 
                Custom("Excel\nReport\n \t", "./images/Excel_Report.png")
                ]
            app[0] >> Edge(label="Importing\n XEVMD files\n\t", style="bold", **edge_attr) >> \
            app[1] >> Edge(label="Processing\n Extracting Data\n\t", style="bold", **edge_attr) >> \
            app[2] >> Edge(label=" \t  Generating\t         \t\n  \t", style="bold", **edge_attr) >> app[3]

        with Cluster("", direction="LR", graph_attr=test):
            app_1 = [Custom("Updating\nReport\n", "./images/Update_Report_1.png"),
                    Custom("Initiators\n", "./images/Users.jpg"),
                    Custom("IDMP\nApplication\n", "./images/idmp.jpeg"),
                    Custom("Processed Data\n", "./images/Processed_Data_1.png"), 
                    Custom("QC\nReviewer\n", "./images/Quality_Check.png"),
                    Custom("Final\nReport\n", "./images/Excel_Report.png")

                ]
            app_1[4] >> Edge(label="Review \nRecords\n",style="bold") >>  app_1[5]
            app_1[4] << Edge(label="  \t \t \t\t Generating ", style="bold",minlen="0.5",**edge_attr) << \
            app_1[3] << Edge(label="  \n Submit \nfor review\n\t", style="bold",**edge_attr) << \
            app_1[2] << Edge(label="Processing &\n Extracting Data\n\t", style="bold",**edge_attr) << \
            app_1[1] << Edge(label="Importing \t \nExcel files \t \n\t \t ", style="bold",**edge_attr) << \
            app_1[0] 
        
        app_1[0] << Edge(minlen="0.5", style="bold") << app[3]







