#!python3

'''
This widget script shows:
1. Weibo trendings social events
2. Adice simulates a dice roll.
'''

import appex
import ui
import random
import requests
import webbrowser
from bs4 import BeautifulSoup


WIDTH = ui.get_screen_size()[0] - 40
HEIGHT = 180
MARGIN_H = 20
MARGIN_V = 8
TEXT_HEIGHT = 15


def addRollDice(view):
    def randDice():
        symbols = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']
        return random.choice(symbols)

    def roll_action(sender):
        sender.title = randDice()

    button = ui.Button(
        title=randDice(),
        font=('<System>', 60),
        tint_color='#058673',
        flex='lwh',
        alignment=ui.ALIGN_CENTER,
        action=roll_action
    )
    button.frame = (WIDTH / 2 + MARGIN_H, 100, 100, 60)
    view.add_subview(button)


def truncateWidth(text, width):
    ''' truncate a text's tail to width '''
    cnt = 0
    for idx, ch in enumerate(text):
        if '\u4e00' <= ch <= '\u9fa5':  # is Chinese character
            if cnt >= width - 1:
                return text[:idx]
            cnt += 2
        else:
            if cnt >= width:
                return text[:idx]
            cnt += 1.3
    return text


class Trendings:
    def __init__(self):
        self._y = MARGIN_V
        # self._col flips between 0 and 1
        # indicating column: 0 for left and 1 for right
        self._col = 0
        self._colX = [MARGIN_H, (WIDTH + MARGIN_H) / 2]
        self._x = self._colX[self._col]

    def _addLabel(self, view, title, url):
        title = truncateWidth(title, 16) + "..."
        entry = ui.Button(
            title=title,
            name=url,
            font=('<System>', 15),
            tint_color='#363636' if ui.get_ui_style() == 'light' else '#eeeeee',
            alignment=ui.ALIGN_LEFT,
            flex='r',
            action=lambda sender: webbrowser.open(sender.name)
        )
        entry.frame = (self._x, self._y, (WIDTH-MARGIN_H*3)/2, TEXT_HEIGHT)
        # update x and y
        self._col = 1 - self._col
        self._x = self._colX[self._col]
        if self._col == 0:
            self._y += TEXT_HEIGHT + MARGIN_V
        view.add_subview(entry)

    def getWeiboTrendings(self):
        ''' return a list with pairs<title, url> '''
        urlPrefix = 'https://s.weibo.com'
        trendingsUrl = urlPrefix + '/top/summary/'
        trendings = []
        r = requests.get(trendingsUrl, params={'cate': 'socialevent'})
        soup = BeautifulSoup(r.text, 'html5lib')

        entries = soup.select('#pl_top_realtimehot > table > tbody > tr')
        for entry in entries:
            if random.random() < 0.6:
                entryContent = entry.select('td.td-02 > a')[0]
                entryTitle = entryContent.get_text().strip('#')
                entryUrl = (f"sinaweibo://"
                            f"{entryContent['href'].replace('weibo', 'searchall')}")
                trendings.append((entryTitle, entryUrl))
                if len(trendings) == 8:
                    break
        return trendings

    def addTo(self, view):
        trendings = self.getWeiboTrendings()
        for title, url in trendings:
            self._addLabel(view, title, url)


view = ui.View(frame=(0, 0, WIDTH, HEIGHT))
trendings = Trendings()
trendings.addTo(view)
addRollDice(view)
appex.set_widget_view(view)
