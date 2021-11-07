import time
import board
import pwmio
import neopixel
from touchio import TouchIn

# PWM (fading) LEDs are connected on D2
pwm_leds = board.D2
pwm = pwmio.PWMOut(pwm_leds, frequency=1000, duty_cycle=0)
counter = 0  # counter to keep track of cycles
brightness = 0  # how bright the LED is
fade_amount = 1285  # 2% stepping of 2^16

pixel_pin = board.D1
num_pixels = 7
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.33, auto_write=False, pixel_order=neopixel.GRBW)
WHITE = (255, 255, 255, 255)
BLUE = (0, 0, 255, 10)
BLACK = (0, 0, 0, 0)
wheel_count = 0

chase_count = 0
chase_delay = 0

# Capacitive touch on A2
touch = TouchIn(board.A2)
touch.threshold = 1700
previous_touch = False
current_touch = False
touch_event = False
touch_event_type = 'SINGLE'
current_touch_event_time = 0
previous_touch_event_time = 0


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


def flashlight():
    for x in range(0, 7):
        pixels[x] = WHITE
    pwm.duty_cycle = 0


# We store two debounced touch event times
def touch_check():
    global current_touch, previous_touch, touch_event
    global current_touch_event_time, previous_touch_event_time, touch_event_type
    current_touch = touch.value
    if current_touch and not previous_touch:
        # print('touch: ', touch.raw_value)
        previous_touch_event_time = current_touch_event_time
        current_touch_event_time = int(time.monotonic() * 100)

        if current_touch_event_time - previous_touch_event_time > 25:
            touch_event_type = 'SINGLE'
        else:
            touch_event_type = 'DOUBLE'

        touch_event = True
        # print('touch time: ', current_touch_event_time)
        # print('touch type: ', touch_event_type)
    previous_touch = current_touch


RELAXED_MODE = 'relaxed'
FIGHT_MODE = 'fighting'
FLASHLIGHT_MODE = 'flashlight'
current_mode = RELAXED_MODE


def handle_touch():
    global touch_event, current_touch_event_time, touch_event_type, current_mode

    if touch_event and int(time.monotonic() * 100) - current_touch_event_time > 30:
        touch_event = False
        switch = {
            RELAXED_MODE: FIGHT_MODE,
            FIGHT_MODE: RELAXED_MODE,
            FLASHLIGHT_MODE: RELAXED_MODE
        }
        current_mode = switch.get(current_mode)
        if touch_event_type == 'DOUBLE':
            current_mode = FLASHLIGHT_MODE


def animate():
    if current_mode == RELAXED_MODE:
        sequin_pulse()
        wheel()
    if current_mode == FIGHT_MODE:
        sequin_pulse()
        wheel()
        comet_tail()
    if current_mode == FLASHLIGHT_MODE:
        flashlight()


while True:
    touch_check()
    handle_touch()

    pixels.fill(BLACK)
    animate()
    pixels.show()

    time.sleep(0.015)
