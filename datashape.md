# Neural Data Shape (.NDS) file format

For a general model loader the following information must be accessible before attempting to parse the network:

* input layer data shape ( eg. angular velocity on axis Z = 1 + 320x240x3 camera stream )
  * topic/s to subscribe to
    * name of the topic ( optional default string - as this shall be remappable )
    * the format of the message on the said topic
    * which data leafs to associate with the input layer/s


* output layer data shape
  * topic/s to be published
    * name of the topic ( optional default string - as this shall be remappable )
    * the format of the message on the said topic
    * which data leafs to associate with the output layer/s

## Example network

```python
Input_1 = Input(shape=(6,), name='Input_1')
Dense_1 = Dense(name='Dense_1',output_dim= 24,activation= 'sigmoid' )(Input_1)
Dropout_1 = Dropout(name='Dropout_1',p= 0.2)(Dense_1)
Dense_14 = Dense(name='Dense_14',output_dim= 2)(Dropout_1)
model = Model([Input_1],[Dense_14])
```
## Example DLS file
```yaml
input_layer:
  name: "Input_1"
  buffer_size: 0 # no temporal buffer required
  shape: [6]
  subscribe: {"angular","linear"}
    angular:
      type: "geometry_msgs/Vector3"
      topic: "/imu/data"
      leaf: "sensor_msgs/Imu/angular_velocity"
      dim: 3
      index: 0
    linear:
      type: "geometry_msgs/Vector3"
      topic: "/imu/data"
      leaf: "sensor_msgs/Imu/linear_acceleration"
      dim: 3
      index: 3

output_layer:
  name: "Dense_14"
  shape: [2]
  publish: {"joystick"}
    joystick:
      type: "sensor_msgs/Joy"
      topic: "/joystick"
      leaf: "sensor_msgs/joy/axes"
      dim: 2
      index: 0
```
