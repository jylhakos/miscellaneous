# Building Information Modeling

The document contains information to implement Building Information Modeling (BIM) application using open source BIM libraries.

The Building Information Model server enables you to store and manage the information of building related project.

Data is stored in the open data standard IFC.

BIMSurfer is a WebGL-based IFC model viewer for BIMServer.

Download BIM Server and extract the content of the JAR file in
Tomcat’s folder. Open BIM Server’s login page at
http://localhost:8080 and install BIM open source plugins by a
browser.

BIM object in IFC file is linked by its Global Unique Identifier
(GUID) and stored in the Berkeley database.

The bimvie.ws is JAR file that can be installed as plugin into BIM
Server. Use bimvie.ws to deserialize IFC file and upload IFC file as
BIM model into BIM Server.

The 3D_VIS_JSON_1.0 schema is used to display an alternative
visualization effects on BIM model.

Use xeokit's BIMServerLoaderPlugin to load models from BIMserver. Log in to the BIMServer through bimvie.ws client to get the number of the latest model revision for BIM project. 

Install Java JDK and JRE on Ubuntu

```

$ sudo apt install openjdk-8-jdk openjdk-8-jre

```

You can enable Tomcat service to start on Ubuntu bootby the following systemctl command.

```

$ sudo systemctl enable tomcat8

```
![alt text](https://github.com/jylhakos/miscellaneous/blob/main/BIM/1.png?raw=true)

Figure: Building Information Modeling

### References

https://bimserver.org/

https://github.com/opensourceBIM/BIMserver

https://github.com/opensourceBIM/bimvie.ws

https://github.com/opensourceBIM/BIMsurfer

http://ifcopenshell.org/

https://github.com/opensourceBIM/BIMserver-Repository/wiki/3D-Visualization-Effects

https://www.mvnjar.com/org.opensourcebim/list.html

https://github.com/xeokit/xeokit-sdk



