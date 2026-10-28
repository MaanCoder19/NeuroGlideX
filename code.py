import board
import busio

# Initialize I2C bus
i2c = busio.I2C(board.GP15, board.GP14)  # Adjust to your connections

while not i2c.try_lock():
    pass

devices = i2c.scan()  # Scan for devices on the I2C bus
print("I2C devices found:", devices)

i2c.unlock()
