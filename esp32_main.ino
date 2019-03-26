/*
   code to publish sensor data from ESP32 to Raspberry Pi via ROS
   Hardware to pull data from:
   TCA9548A I2C Multiplexer
   4x MLX90640 IR Array
   BME680 Humidity Sensor
   VL53L0X IR Range Finder
*/

#include <limits>
#include <stdlib.h>

// ros and message types
#include <ros.h>
#include <sensor_msgs/Range.h>
#include <sensor_msgs/Temperature.h>
#include <sensor_msgs/RelativeHumidity.h>
#include <std_msgs/Int16MultiArray.h>

// publisher declarations
ros::NodeHandle nh;
sensor_msgs::Range range_msg;
ros::Publisher range_pub("range", &range_msg);
sensor_msgs::Temperature temp_msg;
ros::Publisher temp_pub("intern_temp", &temp_msg);
sensor_msgs::RelativeHumidity humid_msg;
ros::Publisher humid_pub("intern_humidity", &humid_msg);
std_msgs::Int16MultiArray thermal_msg;
std_msgs::MultiArrayLayout thermal_msg_layout;
std_msgs::MultiArrayDimension thermal_msg_dim[1];
std_msgs::MultiArrayDimension thermal_msg_row;
int16_t thermal_data[64];
int j = 0;  // row counter
ros::Publisher thermal_pub0("thermal_0i", &thermal_msg);
ros::Publisher thermal_pub1("thermal_1i", &thermal_msg);
ros::Publisher thermal_pub2("thermal_2i", &thermal_msg);
ros::Publisher thermal_pub3("thermal_3i", &thermal_msg);

// I2C lib
#include <Wire.h>

// sensor libraries and class initializations
#include "MLX90640_API.h"
#include "MLX90640_I2C_Driver.h"
// https://github.com/sparkfun/SparkFun_MLX90640_Arduino_Example/issues/2
const byte MLX90640_address = 0x33; //Default 7-bit unshifted address of the MLX90640
#define TA_SHIFT 8 //Default shift for MLX90640 in open air
static float mlx90640To[768];
paramsMLX90640 mlx90640;

#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#define SEALEVELPRESSURE_HPA (1013.25)
Adafruit_BME680 bme; // I2C

#include "Adafruit_VL53L0X.h"
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

// multiplexer address
#define TCAADDR 0x70

// muliplexer port assignments
#define THERMAL_0 0
#define THERMAL_1 1
#define THERMAL_2 2
#define THERMAL_3 3
#define BME 4
#define RANGE 5

// initialize ROS publishers and each sensor
void setup() {
  // ros initializations
  nh.initNode();
  nh.advertise(range_pub);
  nh.advertise(temp_pub);
  nh.advertise(humid_pub);
  nh.advertise(thermal_pub0);
  nh.advertise(thermal_pub1);
  //nh.advertise(thermal_pub2);
  nh.advertise(thermal_pub3);

  // I2C init
  Wire.begin();
  Serial.begin(57600);
  // BME init
  tcaselect(BME);
  if (!bme.begin()) {
    // could not find BME
    Serial.println("Failed to connect to BME");
    while (1);
  }

  // Set up oversampling and filter initialization
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms

  // range init
  tcaselect(RANGE);
  if (!lox.begin()) {
    // could not find IR range
    Serial.println("Failed to connect to IR Range");
    while (1);
  }

  // thermal inits
  MLX_init(THERMAL_0);
  MLX_init(THERMAL_1);
  //MLX_init(THERMAL_2);
  MLX_init(THERMAL_3);

  // init some constant data for ROS messages
  temp_msg.variance = 1.0;
  humid_msg.variance = 0.03;
  
  const char row[4] = "row";
  thermal_msg_row.label = row;
  thermal_msg_row.size = 64;
  thermal_msg_row.stride = 64;

  thermal_msg_dim[0] = thermal_msg_row;

  thermal_msg_layout.dim = thermal_msg_dim;
  thermal_msg_layout.dim_length = 1;

  thermal_msg.layout = thermal_msg_layout;
  thermal_msg.data_length = 64;

}

// repeatedly read from each sensor and publish to ROS
void loop() {

  // read from BME sensor
  tcaselect(BME);
  temp_msg.header.stamp = nh.now();
  humid_msg.header.stamp = nh.now();
  if (bme.performReading()) {
    temp_msg.temperature = bme.temperature;
    humid_msg.relative_humidity = bme.humidity / 100.0;
  } else {
    temp_msg.temperature = 0.0;
    humid_msg.relative_humidity = -1.0;
  }
  temp_pub.publish(&temp_msg);
  humid_pub.publish(&humid_msg);

  // read from TOF sensor
  VL53L0X_RangingMeasurementData_t measure;

  tcaselect(RANGE);
  lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!

  range_msg.header.stamp = nh.now();
  range_msg.radiation_type = sensor_msgs::Range::INFRARED;
  if (measure.RangeStatus != 4) {  // phase failures have incorrect data
    int range_msr = measure.RangeMilliMeter;
    range_msg.range = (float)range_msr;
    range_msg.max_range = (float)measure.RangeDMaxMilliMeter;
  } else {

    range_msg.range = std::numeric_limits<float>::infinity();
    range_msg.max_range = 0.0;
  }
  range_pub.publish(&range_msg);

  // IR Array readings
  j += 64;
  if(j >= 768) j = 0;
  char buffer[7];
  nh.loginfo(itoa(j, buffer, 10));
  thermal_msg_layout.data_offset = j;
  MLX_read(THERMAL_0, j);
  thermal_pub0.publish(&thermal_msg);
  MLX_read(THERMAL_1, j);
  thermal_pub1.publish(&thermal_msg);
  //MLX_read(THERMAL_2, j);
  //thermal_pub2.publish(&thermal_msg);
  MLX_read(THERMAL_3, j);
  thermal_pub3.publish(&thermal_msg);

  nh.spinOnce();
  Serial.println("loop");
}

// initialize an MLX sensor
void MLX_init(int port) {
  tcaselect(port);
  if (isConnected() == false)
  {
    // sensor not detected
    Serial.printf("Failed to connect to MLX %d\n", port);
    while (1);
  }
  int status;
  uint16_t eeMLX90640[832];
  status = MLX90640_DumpEE(MLX90640_address, eeMLX90640);
  if (status != 0) {
    Serial.printf("Failed to load params MLX %d\n", port);
    while (1); // failed to load system parameters
  }
  status = MLX90640_ExtractParameters(eeMLX90640, &mlx90640);
  if (status != 0) {
    Serial.printf("Failed to extract params MLX %d\n", port);
    while (1); // failed to extract parameters
  }
}

void MLX_read(int port, int start) {
  tcaselect(port);
  for (byte x = 0 ; x < 2 ; x++) //Read both subpages
  {
    uint16_t mlx90640Frame[834];
    
    int status = MLX90640_GetFrameData(MLX90640_address, mlx90640Frame);
//    if (status >= 0) {
//
//      float vdd = MLX90640_GetVdd(mlx90640Frame, &mlx90640);
//      float Ta = MLX90640_GetTa(mlx90640Frame, &mlx90640);
//
//      float tr = Ta - TA_SHIFT; //Reflected temperature based on the sensor ambient temperature
//      float emissivity = 0.95;
//      
//      MLX90640_CalculateTo(mlx90640Frame, &mlx90640, emissivity, tr, mlx90640To);
//    }
    
  for(int i = start; i < 64+start; i++) {
    thermal_data[i%64] = mlx90640Frame[i];
  }
  thermal_msg.data = thermal_data;
  }
}

//Returns true if the MLX90640 is detected on the I2C bus
boolean isConnected()
{
  Wire.beginTransmission((uint8_t)MLX90640_address);
  if (Wire.endTransmission() != 0)
    return (false); //Sensor did not ACK
  return (true);
}

// select multiplexer port
void tcaselect(uint8_t i) {
  if (i > 7) return;

  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}
