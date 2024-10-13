from math import sqrt

def pythagorean_distance(pos, my_pos):
    return sqrt(
        (pos[0] - my_pos[0]) ** 2 + (pos[1] - my_pos[1]) ** 2)
def targets_ordered_by_distance(targets, my_pos, inner_ignore_radius=0, outer_ignore_radius=300):
    if len(targets) > 0:
        _targets = []
        # fileter close targets
        for target in targets:
            d = pythagorean_distance(target, my_pos)
            if outer_ignore_radius > d > inner_ignore_radius:
                _targets.append((target[0], target[1], d))

        def get_distance(t):
            return t[2]
        _targets.sort(key=get_distance)
        # print('Sorted targets: ', _targets)
        return _targets

    return []

def get_screen_position(pos, window_offset):
    return pos[0] + window_offset[0], pos[1] + window_offset[1]

def find_next_target(input_targets, ignore_positions, error_margin):
    for target in input_targets:
        t = target[0] + target[1] + target[2]
        if is_duplicated_target(t, ignore_positions, error_margin):
            continue
        return target
    return None

def is_duplicated_target(value, ignore_positions, error_margin):
    for ip in ignore_positions:
        if abs(value - ip) <= error_margin:
            return True
    return False

if __name__ == "__main__":
    print('main')
    # pos = (50, 100)
    # my_pos = (200, 400)
    # distance = pythagorean_distance(pos, my_pos)
    # print(distance)
    # my_pos = (0, 0)
    # targets = [(100, 400), (400, 100)]
    # print(targets)
    # targets = targets_ordered_by_distance(targets, my_pos, outer_ignore_radius=1000)
    # print(targets)
    # print('is_duplicate_target: ', is_duplicate_target(400 + 100 + 412, 400 + 100 + 412, 10))
    # value = 200 + 400
