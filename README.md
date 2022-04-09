
# Optical Resistor Identifier Scanner (ORIS)

The ORIS is a camera-based scanner device that will reliably identify axial leaded resistors using the standard color code.
More specifically, the ORIS interprets the axial leaded resistor color code of the given resistor and reports the resistor parameters (resistance & tolerance) to the user.

## Hardware Components

| Component   | Description |
| ----------- | ----------- |
| Raspberry Pi 3 Model B+           | Runs the ORIS software including the ML-based resistor identification algorithm. |
| Raspberry Pi Camera Module v1.3   | Captures image of the resistor for identification. |
| 3.5" LCD Touchscreen HAT for RPi  | Provides user interface for interacting with the user. |

## Required Softwares on RPi

Before any installation steps, ensure that all packages on the Raspberry Pi OS are up-to-date by the following commands:
```
sudo apt update
sudo apt upgrade
```

1. Update pip and setuptools:
```
pip3 install --upgrade pip
pip3 install --upgrade setuptools
```

2. Install TensorFlow Lite Runtime Package:
```
pip3 install tflite-runtime
```

3. Install TensorFlow Lite Support Package:
```
pip3 install tflite-support
```

4. Install OpenCV Python Package:
```
sudo apt install python3-opencv
```

5. Install/Upgrade Pillow Package:
```
sudo apt install libjpeg-dev zlib1g-dev
pip3 install --upgrade Pillow
```

6. Install 3.5" Touchscreen HAT driver by following the instruction here: <http://www.lcdwiki.com/3.5inch_RPi_Display#Driver_Installation>

## Usage/Examples

The ORIS software resides under `./oris`. To run it, first navigate to `./oris` in the terminal, then start the main program by:
```
python3 main.py
```
