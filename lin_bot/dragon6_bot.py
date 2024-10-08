import cv2 as cv
import pyautogui
from time import sleep, time
from threading import Thread, Lock
from math import sqrt


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
    TOOLTIP_MATCH_THRESHOLD = 0.72
    ATTACK_INTERVAL = 2
    SKILL_F7_DELAY = 3
    SKILL_F7_AFTER_MOVE_DELAY = 1.5
    SKILL_F9_DELAY = 60
    SKILL_MOVE_DELAY = 18
    DETECTION_WAITING_THRESHOLD = 6
    START_SEARCH_THRESHOLD = 2
    SEARCH_INTERVAL = 3

    # threading properties
    stopped = True
    lock = None

    # properties
    state = None
    targets = []
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
        self.limestone_tooltip = cv.imread('model/fireegg.jpg', cv.IMREAD_UNCHANGED)

        # start bot in the initializing mode to allow us time to get setup.
        # mark the time at which this started so we know when to complete it
        self.state = BotState.INITIALIZING
        self.timestamp = time()
        # our character is always in the center of the screen
        self.my_pos = (self.window_w / 2 + 5, self.window_h / 2)
        print('Character position: ', self.my_pos)

    def click_next_target(self):
        # 1. order targets by distance from center
        # loop:
        #   2. hover over the nearest target
        #   3. confirm that it's limestone via the tooltip
        #   4. if it's not, check the next target
        # endloop
        # 5. if no target was found return false
        # 6. click on the found target and return true
        if (time() - self.last_move_time) > self.SKILL_MOVE_DELAY:
            print('Reach move delay, press f5 to move')
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
        print('New last_detect_time {}', self.last_detect_time)
        pyautogui.press('esc', presses=2, interval=0.1)
        pyautogui.moveTo(x=self.my_pos[0]+20, y=self.my_pos[1], duration=0.5)

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

    def confirm_tooltip(self, target_position):
        # check the current screenshot for the limestone tooltip using match template
        result = cv.matchTemplate(self.screenshot, self.limestone_tooltip, cv.TM_CCOEFF_NORMED)
        # get the best match postition
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        # if we can closely match the tooltip image, consider the object found
        if max_val >= self.TOOLTIP_MATCH_THRESHOLD:
            # print('Tooltip found in image at {}'.format(max_loc))
            # screen_loc = self.get_screen_position(max_loc)
            # print('Found on screen at {}'.format(screen_loc))
            # mouse_position = pyautogui.position()
            # print('Mouse on screen at {}'.format(mouse_position))
            # offset = (mouse_position[0] - screen_loc[0], mouse_position[1] - screen_loc[1])
            # print('Offset calculated as x: {} y: {}'.format(offset[0], offset[1]))
            # the offset I always got was Offset calculated as x: -22 y: -29
            return True
        #print('Tooltip not found.')
        return False

    def click_backtrack(self):
        # pop the top item off the clicked points stack. this will be the click that
        # brought us to our current location.
        last_click = self.click_history.pop()
        # to undo this click, we must mirror it across the center point. so if our
        # character is at the middle of the screen at ex. (100, 100), and our last
        # click was at (120, 120), then to undo this we must now click at (80, 80).
        # our character is always in the center of the screen
        mirrored_click_x = self.my_pos[0] - (last_click[0] - self.my_pos[0])
        mirrored_click_y = self.my_pos[1] - (last_click[1] - self.my_pos[1])
        # convert this screenshot position to a screen position
        screen_x, screen_y = self.get_screen_position((mirrored_click_x, mirrored_click_y))
        print('Backtracking to x:{} y:{}'.format(screen_x, screen_y))
        pyautogui.moveTo(x=screen_x, y=screen_y)
        # short pause to let the mouse movement complete
        sleep(0.500)
        pyautogui.click()

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the WindowCapture __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])

    # threading methods

    def update_targets(self, targets):
        self.lock.acquire()
        self.targets = targets
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

            # elif self.state == BotState.MOVING or self.state == BotState.BACKTRACKING:
            #     # see if we've stopped moving yet by comparing the current pixel mesh
            #     # to the previously observed mesh
            #     if not self.have_stopped_moving():
            #         # wait a short time to allow for the character position to change
            #         sleep(0.500)
            #     else:
            #         # reset the timestamp marker to the current time. switch state
            #         # to mining if we clicked on a deposit, or search again if we
            #         # backtracked
            #         self.lock.acquire()
            #         if self.state == BotState.MOVING:
            #             self.timestamp = time()
            #             self.state = BotState.MINING
            #         elif self.state == BotState.BACKTRACKING:
            #             self.state = BotState.SEARCHING
            #         self.lock.release()
            #
            # elif self.state == BotState.MINING:
            #     # see if we're done mining. just wait some amount of time
            #     if time() > self.timestamp + self.MINING_SECONDS:
            #         # return to the searching state
            #         self.lock.acquire()
            #         self.state = BotState.SEARCHING
            #         self.lock.release()
