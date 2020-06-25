def get_stars(level: int):

    if level == 1:
        return 0

    stars = round(0.0066 * level ** 3 + 0.348 * level ** 2 + 18.2 * level - 28.7)
    return stars


def get_level(stars: int):
    level = round(0.00000000183 * stars ** 3 - 0.0000152 * stars ** 2 + 0.0454 * stars + 1.72)
    return level
