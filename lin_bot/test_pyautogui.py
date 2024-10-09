from time import sleep

import pyautogui

while True:
    pyautogui.click(button='left',
                    x=402, y=251, clicks=3, interval=1)
    print('Done.')
    sleep(3)
