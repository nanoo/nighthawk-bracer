import time
import board
import pwmio
import neopixel

# PWM (fading) LEDs are connected on D2
pwm_leds = board.D2
pwm = pwmio.PWMOut(pwm_leds, frequency=1000, duty_cycle=0)
counter = 0  # counter to keep track of cycles
brightness = 0  # how bright the LED is
fade_amount = 1285  # 2% stepping of 2^16

pixel_pin = board.D1
num_pixels = 7
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.33, auto_write=False, pixel_order=neopixel.GRBW)
BLUE = (0, 0, 255, 10)
BLACK = (0, 0, 0, 0)
wheel_count = 0

chase_count = 0
chase_delay = 0


def sequin_pulse():
    global brightness, fade_amount, counter
    # And send to LED as PWM level
    pwm.duty_cycle = brightness
    # change the brightness for next time through the loop:
    brightness = brightness + fade_amount
    # reverse the direction of the fading at the ends of the fade:
    if brightness <= 0:
        fade_amount = -fade_amount
        counter += 1
    elif brightness >= 65535:
        fade_amount = -fade_amount
        counter += 1


# Helper to give us a nice color swirl
def wheel():
    global pixels, wheel_count
    pos = wheel_count
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.

    if pos < 85:
        color = [int(pos * 3), int(255 - (pos * 3)), 0]
    elif pos < 170:
        pos -= 85
        color = [int(255 - pos * 3), 0, int(pos * 3)]
    else:
        pos -= 170
        color = [0, int(pos * 3), int(255 - pos * 3)]

    wheel_count = (wheel_count + 1) % 256  # run from 0 to 255
    pixels[0] = color


def comet_tail():
    global chase_count, chase_delay
    next_count = chase_count + 1
    pixels[next_count] = BLUE
    pixels[((next_count + 4) % 6) + 1] = (0, 0, 100)
    pixels[((next_count + 3) % 6) + 1] = (0, 0, 50)
    pixels[((next_count + 2) % 6) + 1] = (0, 0, 10)

    if chase_delay == 2:
        chase_count = (chase_count + 1) % 6

    chase_delay = (chase_delay + 1) % 3


while True:
    pixels.fill(BLACK)

    sequin_pulse()
    wheel()
    comet_tail()

    pixels.show()

    time.sleep(0.015)
