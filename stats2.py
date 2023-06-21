import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height. Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load default font.
font = ImageFont.load_default()

# Set the display information for the two screens.
screen1 = [
    "CPU: ",
    "Mem: ",
    "Tmp: "
]

# Variable to track the current screen.
current_screen = 1

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    if current_screen == 1:
        # Retrieve system information for screen 1.
        cmd = 'cut -f 1 -d " " /proc/loadavg'
        cpu_load = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"%.2f/%.2f GB  %.2f%%\", $3/1024,$2/1024,($3*100/$2) }'"
        mem_usage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "cat /sys/class/thermal/thermal_zone0/temp"
        temperature = subprocess.check_output(cmd, shell=True).decode("utf-8")
        temperature = float(temperature) / 1000
        temperature_str = f"{temperature:.2f} °C"

        # Check if temperature is over 70 and adjust font color accordingly.
        if temperature > 70:
            temp_font = ImageFont.load_default()
            draw.rectangle((0, 20, width, height), outline=255, fill=255)
            draw.text((width // 2, 20), temperature_str, font=temp_font, fill=0, anchor="mm")
        else:
            draw.text((width // 2, 20), temperature_str, font=font, fill=255, anchor="mm")

        # Write three lines of text for screen 1.
        line_height = height // len(screen1)
        for i, line in enumerate(screen1):
            if i == 2 and temperature > 70:
                draw.text((0, line_height * i), line, font=temp_font, fill=0)
            else:
                draw.text((0, line_height * i), line, font=font, fill=255)
            draw.text((50, line_height * i), cpu_load if i == 0 else mem_usage if i == 1 else "",
                      font=font, fill=255)

        # Change to screen 2 after 3.5 seconds.
        time.sleep(3.5)
        current_screen = 2


    elif current_screen == 2:
        # Retrieve the hostname.
        cmd = "hostname"
        hostname = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()

        # Retrieve the IP address.
        cmd = "hostname -I | cut -d' ' -f1"
        ip_address = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()

        # Clear the display.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Write the hostname in large letters.
        host_font = ImageFont.truetype("arial.ttf", 16)
        host_x = 0
        host_y = 0
        draw.text((host_x, host_y), hostname, font=host_font, fill=255)

        # Write the IP address in smaller letters below the hostname.
        ip_font = ImageFont.load_default()
        ip_x = 0
        ip_y = 21
        draw.text((ip_x, ip_y), ip_address, font=ip_font, fill=255)

        # Change to screen 1 after 3.5 seconds.
        time.sleep(3.5)
        current_screen = 1

    # Display image.
    disp.image(image)
    disp.show()
