#disable a desk
def disable_desk(desk):
    desk.is_start = true
    desk.save()