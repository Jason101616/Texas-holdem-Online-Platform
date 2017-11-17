#disable a desk
def disable_desk(desk):
    desk.is_start = True
    desk.save()