import time
import board
import pwmio

# PWM (fading) LEDs are connected on D2
pwm_leds = board.D2
pwm = pwmio.PWMOut(pwm_leds, frequency=1000, duty_cycle=0)
counter = 0  # counter to keep track of cycles
brightness = 0  # how bright the LED is
fade_amount = 1285  # 2% stepping of 2^16


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


while True:
    time.sleep(0.015)
    sequin_pulse()
