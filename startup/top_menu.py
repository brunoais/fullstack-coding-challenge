from collections import namedtuple

TopMenuEntry = namedtuple('TopMenuEntry', ['section_key', 'section_permission', 'order', 'redirect_order'])
SpecialPageEntry = namedtuple('SpecialPageEntry', ['section_key', 'section_permission', 'redirect_order'])


class TopMenu(object):

    def __init__(self):
        self.top_menu = []

    def add_menu_entry(self, entry: TopMenuEntry):
        self.top_menu.append(entry)
        self.top_menu.sort(key=lambda entry: entry.order)  # <- Slows down starting but keeps the speed later

    def __iter__(self):
        return iter(self.top_menu)


top_menu = TopMenu()