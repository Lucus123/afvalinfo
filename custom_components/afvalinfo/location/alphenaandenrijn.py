from ..const.const import (
    MONTH_TO_NUMBER,
    SENSOR_LOCATIONS_TO_URL,
    _LOGGER,
)
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import urllib.request
import urllib.error


class AlphenAanDenRijnAfval(object):
    def get_date_from_afvaltype(self, ophaaldata, afvaltype):
        try:
            html = ophaaldata.find(href="/afvalstroom/" + str(afvaltype))
            date = html.i.string[3:]
            day = date.split()[0]
            month = MONTH_TO_NUMBER[date.split()[1]]
            year = str(
                datetime.today().year
                if datetime.today().month <= int(month)
                else datetime.today().year + 1
            )
            return year + "-" + month + "-" + day
        except Exception as exc:
            _LOGGER.error("Error occurred while splitting data: %r", exc)
            return ""

    def get_data(self, city, postcode, street_number):
        _LOGGER.debug("Updating Waste collection dates")

        try:
            url = SENSOR_LOCATIONS_TO_URL["alphenaandenrijn"][0].format(
                postcode, street_number
            )
            req = urllib.request.Request(url=url)
            f = urllib.request.urlopen(req)
            html = f.read().decode("utf-8")

            soup = BeautifulSoup(html, "html.parser")
            ophaaldata = soup.find(id="ophaaldata")

            # Place all possible values in the dictionary even if they are not necessary
            waste_dict = {}
            # find afvalstroom/112 = gft
            waste_dict["gft"] = self.get_date_from_afvaltype(ophaaldata, 112)
            # find afvalstroom/87 = papier
            waste_dict["papier"] = self.get_date_from_afvaltype(ophaaldata, 87)
            # find afvalstroom/113 = pbd
            waste_dict["pbd"] = self.get_date_from_afvaltype(ophaaldata, 113)
            # find afvalstroom/101 = restafval
            waste_dict["restafval"] = self.get_date_from_afvaltype(ophaaldata, 101)

            return waste_dict
        except urllib.error.URLError as exc:
            _LOGGER.error("Error occurred while fetching data: %r", exc.reason)
            return False
