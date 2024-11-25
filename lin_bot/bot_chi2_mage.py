from threading import Thread, Lock
from time import sleep, time

from sympy.plotting.intervalmath import interval

from common.bot_utils import targets_ordered_by_distance, get_screen_position, find_next_target

import cv2 as cv
import pyautogui


class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    MOVING = 2
    MINING = 3
    BACKTRACKING = 4


class Chi2MageBot:
    
    # constants
    INITIALIZING_SECONDS = 5
    OUTER_IGNORE_RADIUS = 200
    INNER_IGNORE_RADIUS = 0
    STAIR_DETECT_RADIUS = 200
    # ignore same position targets if the distance gather than radius
    IGNORE_TARGET_POSITION_DISTANCE_RADIUS = 50
    # Ignore target error margin
    IGNORE_TARGET_ERROR_MARGIN_RADIUS = 10
    ATTACK_INTERVAL = 0.7
    SKILL_F7_DELAY = 4
    SKILL_F7_INTERVAL = 0.1
    SKILL_F7_AFTER_MOVE_DELAY = 3
    SKILL_F9_DELAY = 999999
    SKILL_MOVE_DELAY = 30
    DETECTION_WAITING_THRESHOLD = 3.5
    START_SEARCH_THRESHOLD = 2
    SEARCH_INTERVAL = 3
    # ENABLE FLAG
    ENABLE_F7 = True
    ENABLE_F9 = False
    ENABLE_MOVING = False

    # threading properties
    stopped = True
    lock = None

    # properties
    state = None
    targets = []
    stair_targets = []
    screenshot = None
    timestamp = None
    last_f7_time = time() - SKILL_F7_DELAY
    last_f9_time = time()
    last_move_time = time()
    last_detect_time = time()
    last_search_time = time()
    window_offset = (0, 0)
    window_w = 0
    window_h = 0
    # Values of ignore positions
    ignore_positions = []

    def __init__(self, window_offset, window_size):
        # create a thread lock object
        self.lock = Lock()

        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in 
        # the whole object
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        # pre-load the needle image used to confirm our object detection
        # self.limestone_tooltip = cv.imread('model/fireegg.jpg', cv.IMREAD_UNCHANGED)

        # start bot in the initializing mode to allow us time to get setup.
        # mark the time at which this started so we know when to complete it
        self.state = BotState.INITIALIZING
        self.timestamp = time()
        # our character is always in the center of the screen
        self.my_pos = (self.window_w / 2 + 5, self.window_h / 2)
        print('Character position: ', self.my_pos)

    def click_next_target(self):

        # Detect stairs
        s_targets = targets_ordered_by_distance(self.stair_targets, self.my_pos, outer_ignore_radius=self.STAIR_DETECT_RADIUS)
        if len(s_targets) > 0:
            print('Avoid the stair!')
            self.press_move()
            return True
        targets = targets_ordered_by_distance(self.targets, self.my_pos,
                                              self.INNER_IGNORE_RADIUS, self.OUTER_IGNORE_RADIUS)
        # print('Found {} potential Targets'.format(len(targets)))
        target_pos = find_next_target(targets, self.ignore_positions, self.IGNORE_TARGET_ERROR_MARGIN_RADIUS)
        if target_pos:
            self.last_detect_time = time()
            self.last_search_time = time()

            screen_x, screen_y = get_screen_position(target_pos, self.window_offset)
            print('Target position x:{} y:{}'.format(screen_x, screen_y))
            # move the mouse
            pyautogui.moveTo(x=screen_x, y=screen_y, duration=0.05)
            last_f7_time = time() - self.last_f7_time
            if (self.ENABLE_F7
                and (time() - self.last_move_time) > self.SKILL_F7_AFTER_MOVE_DELAY
                and last_f7_time > self.SKILL_F7_DELAY):
                print('Use F7 skill')
                pyautogui.press('f7')
                pyautogui.click()
                self.last_f7_time = time()
                sleep(self.SKILL_F7_INTERVAL)
            else:
                pyautogui.mouseDown()
                sleep(self.ATTACK_INTERVAL)
                pyautogui.mouseUp()
            # add to the ignore list if the distance is gather than radius
            if target_pos[2] > self.IGNORE_TARGET_POSITION_DISTANCE_RADIUS:
                self.ignore_positions.append(target_pos[0] + target_pos[1] + target_pos[2])
                print('Add {} to ignore positions: '.format(target_pos))
                print(self.ignore_positions)
            print('End a click round')
            # check whether to move
            if (time() - self.last_move_time) > self.SKILL_MOVE_DELAY:
                print('Reach move delay, press f5 to move')
                self.press_move()
            return True
        else:
            detect_time = time() - self.last_detect_time
            if detect_time > self.DETECTION_WAITING_THRESHOLD:
                print('Hit detection waiting threshold, press f5 to move')
                self.press_move()
            if (self.ENABLE_MOVING and detect_time > self.START_SEARCH_THRESHOLD
                and (time() - self.last_search_time) > self.SEARCH_INTERVAL):
                _x = (self.window_w - self.my_pos[0]) / 2
                _y = self.my_pos[1] + (self.window_h - self.my_pos[1]) / 2
                print('Searching targets, move to ({}, {})'.format(_x, _y))
                pyautogui.click(_x, _y, interval=1)
                self.last_search_time = time()
            return False

    def press_move(self):
        print('press f5')
        print('original last_detect_time {}', self.last_detect_time)
        pyautogui.press('f5', presses=2, interval=0.1)
        self.last_move_time = time()
        self.last_detect_time = time()
        self.last_search_time = time()
        self.ignore_positions = []
        print('New last_detect_time {}', self.last_detect_time)
        pyautogui.click(x=self.my_pos[0] + 50, y=self.my_pos[1] + 50, clicks=2, interval=0.2)

    # threading methods

    def update_targets(self, targets, stair_targets):
        self.lock.acquire()
        self.targets = targets
        self.stair_targets = stair_targets
        self.lock.release()

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    # main logic controller
    def run(self):
        while not self.stopped:
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the startup waiting period is complete
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()

            elif self.state == BotState.SEARCHING:
                # check the given click point targets,
                # then click it.
                self.click_next_target()
                pyautogui.press('esc', presses=2, interval=0.2)
