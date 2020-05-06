from utils import seleniumLib, utils
from UIElements import statistics_overview


class StatisticsOverview:
    def __init__(self, driver):
        self.slb = seleniumLib.SeleniumLib(driver)

    def get_cards_text(self):
        utils.log("get cards text list in [Statistics Overview].")
        card_list = self.slb.get_elements_text_list(statistics_overview.card_text)
        utils.debug("got cards text list: {}".format(card_list))
        return card_list

    def click_statistics_overview(self):
        utils.log("click menu [Statistics Overview].")
        self.slb.move_to_click(statistics_overview.statisticsOverview_link)





