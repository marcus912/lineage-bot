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


class AlbionBot:
    
    # constants
    INITIALIZING_SECONDS = 3
    MINING_SECONDS = 14
    MOVEMENT_STOPPED_THRESHOLD = 0.975
    IGNORE_RADIUS = 200
    TOOLTIP_MATCH_THRESHOLD = 0.72
    ATTACK_INTERVAL = 1.5
    SKILL_F7_DELAY = 3.5
    SKILL_F7_AFTER_MOVE_DELAY = 1.5
    SKILL_F9_DELAY = 60
    SKILL_MOVE_DELAY = 20
    DETECTION_WAITING_THRESHOLD = 8

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
        self.my_pos = (self.window_w / 2, self.window_h / 2)

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
            target_pos = targets[0]
            screen_x, screen_y = self.get_screen_position(target_pos)
            print('Moving mouse to x:{} y:{}'.format(screen_x, screen_y))
            # move the mouse
            pyautogui.moveTo(x=screen_x, y=screen_y)
            # check skill
            last_f7_time = time() - self.last_f7_time
            if (time() - self.last_move_time) > self.SKILL_F7_AFTER_MOVE_DELAY:
                if len(targets) > 2 or last_f7_time > self.SKILL_F7_DELAY:
                    pyautogui.press('f7')
                    pyautogui.click()
                    pyautogui.press('f7')
                    pyautogui.click()
                    pyautogui.press('f7')
                    pyautogui.press('f7')
                    pyautogui.click()
                    print('Use F7 skill')
                    self.last_f7_time = time()
            pyautogui.mouseDown()
            pyautogui.moveTo(x=self.my_pos[0], y=self.my_pos[1], duration=0.5)
            sleep(self.ATTACK_INTERVAL)
            pyautogui.mouseUp()
            pyautogui.click()
            if (time() - self.last_f9_time) > self.SKILL_F9_DELAY:
                pyautogui.press('f9', interval=1)
                self.last_f9_time = time()
            print('End a click round')
            return True
        else:
            if (time() - self.last_detect_time) > self.DETECTION_WAITING_THRESHOLD:
                print('Hit detection waiting threshold, press f5 to move')
                self.press_move()
            return False

    def press_move(self):
        print('press f5')
        print('original last_detect_time {}', self.last_detect_time)
        pyautogui.press('f5', presses=2, interval=0.1)
        self.last_move_time = time()
        self.last_detect_time = time()
        print('New last_detect_time {}', self.last_detect_time)
        pyautogui.press('esc', presses=2, interval=0.1)
        pyautogui.moveTo(x=self.my_pos[0], y=self.my_pos[1], duration=0.5)

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

        # print(my_pos)
        # print(targets)
        # for t in targets:
        #    print(pythagorean_distance(t))

        # ignore targets at are too close to our character (within 130 pixels) to avoid 
        # re-clicking a deposit we just mined
        if len(targets) > 0:
            targets = [t for t in targets if pythagorean_distance(t) < self.IGNORE_RADIUS]

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
                success = self.click_next_target()
                # if not successful, try one more time
                if not success:
                    success = self.click_next_target()

                # if successful, switch state to moving
                # if not, backtrack or hold the current position
                if success:
                    self.lock.acquire()
                    # self.state = BotState.MOVING
                    self.lock.release()
                elif len(self.click_history) > 0:
                    self.click_backtrack()
                    self.lock.acquire()
                    self.state = BotState.BACKTRACKING
                    self.lock.release()
                else:
                    # stay in place and keep searching
                    pass

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
