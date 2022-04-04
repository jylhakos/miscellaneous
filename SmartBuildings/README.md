# Smart Buildings

The document describes an infrastructure that uses information technology to automate building operations and processes, such as heating, ventilation, lighting, control of elevators, water, security, power meters, and etc. other systems.

Internet of Things (IoT), which is made up of internet connected devices, such as light fixtures, are fitted with sensors and meters that generate and transmit real time data over a network to a database and data is analyzed.

Bluetooth mesh can be utilized in the building automation, with the deployments in connected lighting.

By using Bluetooth mesh in lights, you can create IoT network capable of controlling lighting.

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/SmartBuildings/1.png?raw=true)

Figure: Adjustment of lighting

A use case is controls of lighting, where connected lights refers to a system of light fixtures that are integrated with sensors to enable for example automatic light adjustments according to time of day for energy efficiency in smart buildings.

## IoT gateway

IoT gateway is a device and software that serves as the connection point between the cloud and controllers, sensors and intelligent devices.

IoT gateway will process and forward messages to and from the Internet.

IoT gateway acts as a network router, routing data between IoT devices and the cloud.

IoT gateway device can preprocess that data locally at the edge before sending it to the cloud.

IoT gateway allows the Bluetooth mesh device to access the internet, enabling it to perform remote control functions.

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/SmartBuildings/2.png?raw=true)

Figure: Software components of IoT gateway

### User Applications

User Applications have user interfaces to interact with features required in
Bluetooth mesh provisioning, configuration and device management.

Bluetooth mesh provisioning and configuration is provided by either an
external app like a mobile app or calling functions in device management.

### Data Management

The provisioning data is stored in format of JavaScript Object Notation
(JSON) containing essential information to use Bluetooth mesh commands
for controlling of Bluetooth mesh nodes.

Data Management has service to export provisioning JSON file to be
available in Device Management.

Data Management parses JSON file content and stores data of JSON file on
the file system or a database.

### Security

Integrating features for Bluetooth mesh models are secured by the common
security practices required by the framework.

### Device Management

The actions to control Bluetooth mesh nodes are implemented by Device
Management.

A script for Bluetooth mesh commands could implement the commands to
control Bluetooth nodes.

### Device Connectivity

The connection to access external Serial to Bluetooth mesh interface is
managed by Device Connectivity.

### Communication Protocols

Serial protocol is obligatory to connect to external Serial to Bluetooth mesh device attached onto the hardware.

### Operating System

Canonical has enabled Ubuntu on the Raspberry Pi.

Operating System runs the application with functions providing the solution for Bluetooth mesh.

## Bluetooth mesh

Bluetooth mesh runs on top of the Bluetooth Low Energy (LE) stack.

Bluetooth mesh relies on devices scanning and advertising in the same way as beacons.

Received packets are broadcasted by relays until the packet is received by other nodes.

Bluetooth mesh networks communicate via messages.

Models implement and define the functionality of nodes.

Elements can be in various conditions and this is represented in Bluetooth mesh by the concept of state values.

States are data items that indicate the condition of the device, such as on or off and high or low.

As an example, a light which may either be on or off.

Models talk to each other by sending and receiving messages.

Messages are the mechanism by which operations on the mesh are invoked.

Messages are used to transfer data between nodes, and addresses are used to define where the messages come from (source) and go to (destination).

Messages are identified by opcodes and have associated parameters. An opcode identifies the operation of the message.

Messages fall within one of two broad categories: acknowledged or unacknowledged.

The sender of an acknowledged message may resend the message if it does not receive the expected response.

Unacknowledged messages do not require a response.

The act of sending a message is known as publishing.

Bluetooth mesh beacons are being used to publish advertising information in lighting, building automation, asset tracking and the case of IoT for many industries.

### BlueZ

BlueZ is the official Linux Bluetooth protocol stack.

The applications which run as independent processes in Linux make inter-process communication (IPC) calls to BlueZ APIs via an IPC broker called D-Bus.

BlueZ runs as a system daemon, either bluetoothd to provide applications with support for GAP and GATT or bluetooth-meshd when the physical device is to be used to run applications that act as Bluetooth mesh nodes.

The applications work with BlueZ by sending and receiving D-Bus messages and signals.

### D-Bus

D-Bus allows communication between multiple processes running concurrently on the same machine.

In the case of BlueZ this is between the Bluetooth Daemon (bluetoothd) and the IoT application.

### PyACI

The Interactive Python Application Controller Interface (PyACI) (interactive_pyaci.py) can be used to interactively control devices running the mesh stack and the serial interface.

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/SmartBuildings/3.png?raw=true)

Figure: Python scripts

### Provisioning
	
Python scripts use commands from Nordic’s Serialization of Bluetooth mesh libraries interface.

Prerequisites for Python scripts is to install packages using pip command.

```

$ pip install -r requirements.txt

```

The aci/aci_cmd.py and aci/aci_evt.py files are auto-generated from the 	Nordic's C header files of the serial interface by tools/serial_doc scripts.

An example Bluetooth mesh database file is located in database folder and you can use the backup file if you want to clear a modified database.

The provisioning interface module is located in mesh folder.
The Bluetooth mesh models and configuration client scripts are located in mesh folder.

The Python commands are imported from the cmd namespace and events are available in the evt namespace located in aci/aci_evt.py file.

The python commands script is used to communicate with the serial interface and carry out the provisioning and configuration of the unprovisioned Bluetooth mesh device.

After that, a Python based Bluetooth mesh client is used to communicate with the provisioned Bluetooth mesh node that is running the Bluetooth mesh server.

To start the serial interface, run the following command in the directory of the script.

```

$ python commands.py -d <COM>

```

In this command, <COM> is the COM port of the device connected to serial interface.

The COM port variable is usually labelled as /dev/tty* on Linux operating system.

After serial interface has been started by Python script, then Python script loads the Bluetooth mesh network database by creating the following Python object from MeshDB class.

```

db = MeshDB("database/example_database.json")

```

The Python objects can use Python data variables in the following syntax.

```

db.provisioners

```

When the serial interface is connected and the database is loaded, then complete the following steps for provisioning the Bluetooth mesh devices.

Create a Provisioner object by Python script.

```
p = Provisioner(device, db)

```

After the provisioner has been created, the Python scripts starts scanning for unprovisioned devices.

```
p.scan_start()

```

The Python script sends command to show unprovisioned devices with UUID and Python script stops scanning.

```

p.scan_stop()

```

The provisioning uses UUID to uniquely identify the Bluetooth mesh device.

```

p.provision(uuid="a502d90ecfb0416db1ddb7a93b10f335", name="lights")

```

The Python script sets the local unicast address of the device and adds the application and network keys into the database.

The Python script receives the key handles, as they will be used for sending messages to provisioned nodes.

Python script uses the values of devkey_handle and address_handle to configure the devices.

### Configuration

The Python script is used to configure the provisioned Bluetooth mesh devices.

To be able to configure Bluetooth mesh network, the configuration needs to be completed by adding the Configuration Client model.

Create an instance of the Configuration Client model class.

```

cc = ConfigurationClient(db)

```
Add the instance to the device.

```

device.model_add(cc)

```

Set its publication state to match the first device.

```

cc.publish_set(8, 0)

```

The 8 and 0 are the device key and publish address handle, which were received at the end of the provisioning procedure.

In the composition data, the Python script can parse the elements Bluetooth mesh models.

```

cc.composition_data_get()

```

The example_database.json file is updated automatically with the information from the node.

To enable applications and models on Bluetooth mesh nodes in the network to communicate, Python script adds an application key to the device and binds it to Bluetooth mesh model.

```

cc.appkey_add(0)

```

In the example_database.json file, Python script can find the application key "lights" with key index 0.

This key was added to the device by the provisioner during provisioning, with the appkey_handle 0.


Python script adds AppKey 0 to the device and binds it to the Bluetooth mesh server by running the following commands.

```

cc.model_app_bind(db.nodes[0].unicast_address, 0, mt.ModelId(0x1000))

```

### Device Management

The configuration of the Bluetooth mesh model for the client is done by adding the device key and publish address handle.

```

gc = GenericOnOffClient()

device.model_add(gc)

gc.publish_set(0,0)

```

After completing configuration steps the client can send messages to change the state of the Bluetooth mesh device.

```

gc.set(True)

```

### Messaging

gRPC is Remote Procedure Call (RPC) protocol, that uses Protocol buffers as it's message format as an alternative to formats like JSON or XML.

With gRPC we can define our service in a .proto file and generate clients and servers in any of gRPC's supported languages.

Protocol buffers are Google's defined interface for serializing structured data.

ProtoBuf interface describes the structure of the data to be sent.

Payload structures are defined as messages in proto files end with a .proto extension.

The proto files are used to generate classes or stubs for the language of your choice using code generators within the protoc compiler.

Protocol buffers allow the creation of elements by instantiating new messages, based on the .proto files, which are then used for serialization.

The messages are serialized into binary format and sent over the network as byte stream.

The sent byte stream is deserialized using the parse method of our compiled class.

We need to define services and their gRPC methods that are implemented on server side and called from client side.

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/SmartBuildings/4.png?raw=true)

Figure: Protocol buffers

### Raspberry Pi

Raspberry Pi can be used as IoT gateway to enable IoT devices such as Bluetooth devices and sensors to publish and receive data from the cloud.

Raspberry Pi comes with Gigabit Ethernet, wireless networking and Bluetooth.

Raspberry Pi, which can connect IoT devices to the private network and prevent IoT devices from being exposed to outside networks.

You can use the apt command to install software in Raspberry Pi using package manager that is included with Debian based Linux distributions.

Use ifconfig to display the network configuration details for the interfaces on the current system.

The ping utility is usually used to check if communication can be made with another host.

After setting up BlueZ on Raspberry Pi, you can use the meshctl utility of BlueZ as a Bluetooth mesh provisioner.

### References

https://www.nordicsemi.com/Products/Bluetooth-mesh

https://www.bluetooth.com/blog/how-to-setup-bluez-on-raspberry-pi-and-support-pb-adv/

https://cloud.google.com/iot/docs/how-tos/gateways




