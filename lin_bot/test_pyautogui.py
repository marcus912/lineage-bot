from time import sleep

import pyautogui

while True:
    pyautogui.moveTo(x=209, y=290)
    pyautogui.click(button='left',
                    x=209, y=290, clicks=5, interval=0.1)
    print('Done.')
    sleep(3)
