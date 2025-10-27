from time import sleep

import pyautogui

def login():
    print('Start a login process')
    #
    pyautogui.moveTo(500, 400)
    pyautogui.moveTo(400, 500)

while True:
    login()
    sleep(120)
