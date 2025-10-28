from math import sqrt
from threading import Thread, Lock
from time import sleep, time

import cv2 as cv
import pyautogui


class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    MOVING = 2
    MINING = 3
    BACKTRACKING = 4


class Dragon6Bot:
    
    # constants
    INITIALIZING_SECONDS = 8
    MINING_SECONDS = 14
    MOVEMENT_STOPPED_THRESHOLD = 0.975
    OUTER_IGNORE_RADIUS = 150
    INNER_IGNORE_RADIUS = 2.5
    STAIR_DETECT_RADIUS = 350
    TOOLTIP_MATCH_THRESHOLD = 0.72
    ATTACK_INTERVAL = 2
    SKILL_F7_DELAY = 3
    SKILL_F7_AFTER_MOVE_DELAY = 1.5
    SKILL_F9_DELAY = 60
    SKILL_MOVE_DELAY = 12
    DETECTION_WAITING_THRESHOLD = 4
    START_SEARCH_THRESHOLD = 2
    SEARCH_INTERVAL = 3

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
    movement_screenshot = None
    window_offset = (0,0)
    window_w = 0
    window_h = 0
    limestone_tooltip = None
    click_history = []

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

        if (time() - self.last_move_time) > self.SKILL_MOVE_DELAY:
            print('Reach move delay, press f5 to move')
            self.press_move()

        # Detect stairs
        s_targets = self.stair_targets_ordered_by_distance(self.stair_targets)
        if len(s_targets) > 0:
            print('Avoid the stair!')
            self.press_move()

        targets = self.targets_ordered_by_distance(self.targets)
        if len(targets) > 0:
            print('Found {} Targets'.format(len(targets)))
            self.last_detect_time = time()
            self.last_search_time = time()
            target_pos = targets[0]
            screen_x, screen_y = self.get_screen_position(target_pos)
            print('Moving mouse to x:{} y:{}'.format(screen_x, screen_y))
            # move the mouse
            pyautogui.moveTo(x=screen_x, y=screen_y)
            pyautogui.mouseDown()
            sleep(self.ATTACK_INTERVAL)
            pyautogui.mouseUp()
            print('End a click round')
            return True
        else:
            detect_time = time() - self.last_detect_time
            if detect_time > self.DETECTION_WAITING_THRESHOLD:
                print('Hit detection waiting threshold, press f5 to move')
                self.press_move()
            if detect_time > self.START_SEARCH_THRESHOLD and (time() - self.last_search_time) > self.SEARCH_INTERVAL:
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
        print('New last_detect_time {}', self.last_detect_time)
        pyautogui.press('esc', presses=2, interval=0.1)
        pyautogui.click(x=self.my_pos[0], y=self.my_pos[1] + 20)

    def have_stopped_moving(self):
        # if we haven't stored a screenshot to compare to, do that first
        if self.movement_screenshot is None:
            self.movement_screenshot = self.screenshot.copy()
            return False

        # compare the old screenshot to the new screenshot
        result = cv.matchTemplate(self.screenshot, self.movement_screenshot, cv.TM_CCOEFF_NORMED)
        # we only care about the value when the two screenshots are laid perfectly over one 
        # another, so the needle position is (0, 0). since both images are the same size, this
        # should be the only result that exists anyway
        similarity = result[0][0]
        print('Movement detection similarity: {}'.format(similarity))

        if similarity >= self.MOVEMENT_STOPPED_THRESHOLD:
            # pictures look similar, so we've probably stopped moving
            print('Movement detected stop')
            return True

        # looks like we're still moving.
        # use this new screenshot to compare to the next one
        self.movement_screenshot = self.screenshot.copy()
        return False

    def targets_ordered_by_distance(self, targets):
        # searched "python order points by distance from point"
        # simply uses the pythagorean theorem
        # https://stackoverflow.com/a/30636138/4655368
        def pythagorean_distance(pos):
            return sqrt((pos[0] - self.my_pos[0])**2 + (pos[1] - self.my_pos[1])**2)
        targets.sort(key=pythagorean_distance)

        # fileter close targets
        if len(targets) > 0:
            # Remove the target too far or on the character
            targets = [t for t in targets if self.INNER_IGNORE_RADIUS < pythagorean_distance(t) < self.OUTER_IGNORE_RADIUS]

        return targets

    def stair_targets_ordered_by_distance(self, targets):
        def pythagorean_distance(pos):
            return sqrt((pos[0] - self.my_pos[0]) ** 2 + (pos[1] - self.my_pos[1]) ** 2)

        targets.sort(key=pythagorean_distance)

        # fileter close targets
        if len(targets) > 0:
            # Remove the target too far or on the character
            targets = [t for t in targets if pythagorean_distance(t) < self.STAIR_DETECT_RADIUS]

        return targets

    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

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
