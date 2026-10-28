import board
import digitalio
import busio
import time
from adafruit_hid.mouse import Mouse
from adafruit_mpu6050 import MPU6050
import usb_hid


# Setup for MPU6050 sensor
i2c = busio.I2C(scl=board.GP15, sda=board.GP14)  # I2C SDA -> GP15, SCL -> GP14
mpu = MPU6050(i2c)

# HID mouse setup
mouse = Mouse(usb_hid.devices)

# Button pins
left_click_pin = board.GP2
right_click_pin = board.GP3
calibrate_pin = board.GP4

# Button setup
left_click = digitalio.DigitalInOut(left_click_pin)
left_click.direction = digitalio.Direction.INPUT
left_click.pull = digitalio.Pull.DOWN

right_click = digitalio.DigitalInOut(right_click_pin)
right_click.direction = digitalio.Direction.INPUT
right_click.pull = digitalio.Pull.DOWN

calibrate = digitalio.DigitalInOut(calibrate_pin)
calibrate.direction = digitalio.Direction.INPUT
calibrate.pull = digitalio.Pull.DOWN

# Calibration offsets and sensitivity
x_offset = 0
y_offset = 0
horizontal_sensitivity = 34  # Sensitivity for left/right
vertical_sensitivity = 9  # Sensitivity for up/down
is_paused = False

# Button state tracking
calibrate_pressed = False
left_pressed = False
right_pressed = False

def calibrate_sensor(samples=10):
    """Calibrates the sensor by averaging multiple readings."""
    global x_offset, y_offset
    x_sum = 0
    y_sum = 0

    for _ in range(samples):
        x_sum += mpu.acceleration[0]
        y_sum += mpu.acceleration[1]
        time.sleep(0.01)  # Small delay between readings

    x_offset = x_sum / samples
    y_offset = y_sum / samples
    print("Sensor calibrated!")

while True:
    # Calibration button handling
    if calibrate.value:
        if not calibrate_pressed:  # Trigger only on transition
            is_paused = not is_paused  # Toggle pause state
            if is_paused:
                print("Mouse movement paused")
            else:
                print("Calibrating and resuming mouse movement")
                calibrate_sensor()  # Only calibrate when resuming
            calibrate_pressed = True
    else:
        calibrate_pressed = False  # Reset on release

    # Left-click button handling
    if left_click.value:
        if not left_pressed:  # Trigger only on transition
            if not is_paused:  # Check if not paused before clicking
                mouse.press(Mouse.LEFT_BUTTON)
            left_pressed = True
    else:
        if left_pressed:  # Release only on transition
            mouse.release(Mouse.LEFT_BUTTON)
            left_pressed = False

    # Right-click button handling
    if right_click.value:
        if not right_pressed:  # Trigger only on transition
            if not is_paused:  # Check if not paused before clicking
                mouse.press(Mouse.RIGHT_BUTTON)
            right_pressed = True
    else:
        if right_pressed:  # Release only on transition
            mouse.release(Mouse.RIGHT_BUTTON)
            right_pressed = False

    # If paused, skip mouse movement
    if is_paused:
        continue

    # Read MPU6050 for aim control
    z_rotation_rate = mpu.gyro[2]  # Gyroscope Z-axis for left/right rotation
    y_acceleration = mpu.acceleration[0]  # X-axis acceleration for up/down

    # Convert gyroscope and accelerometer data to mouse movement
    x_movement = int(-z_rotation_rate * horizontal_sensitivity)  # Left/right
    y_movement = int(y_acceleration * vertical_sensitivity)  # INVERTED up/down

    # Move the mouse only if there's significant movement
    if x_movement != 0 or y_movement != 0:
        mouse.move(x=x_movement, y=y_movement)

    # Small delay for stability
    time.sleep(0.01)  # Delay for smoother performance
