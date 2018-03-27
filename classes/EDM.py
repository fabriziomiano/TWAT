from utils.misc import timestamp_to_datetime, set_archive_path
from dateutil.parser import parse
from collections import OrderedDict
from classes.TaxoDB import TaxoDB
import copy

REFERENCE_KEY = 'reference'
RANGE_ACCEPTED = 0.05


class EDM(TaxoDB):
    def __init__(self, path, template):
        TaxoDB.__init__(self, path, template)

    def add_ref(self, item_info, ref_size):
        ref = {REFERENCE_KEY: ref_size}
        self.add_item(item_info, ref)

    def add_test(self, item_info, test):
        """ 
        Args:
        test (dict) -- key: test timestamp, value (float): test size

        """
        timestamp = next(iter(test))
        if is_date(timestamp):
            self.add_item(item_info, test)
        else:
            print("the key of given test dict is not \
            a valid timestamp. Check documentation for more infos")

    def get_runs(self, item_info):
        item = copy.deepcopy(self.get_item(item_info))
        reference = item.pop(REFERENCE_KEY, None)
        return item

    def last_to_first(self, item_info):
        unordered = self.get_runs(item_info)
        ordered_dates = sorted(unordered, reverse=True)
        ordered_runs = OrderedDict([(date, unordered[date])
                                    for date in ordered_dates])
        return ordered_runs

    def first_to_last(self, item_info):
        unordered = self.get_runs(item_info)
        ordered_dates = sorted(unordered)
        ordered_runs = OrderedDict([(date, unordered[date])
                                    for date in ordered_dates])
        return ordered_runs

    def most_recent(self, item_info):
        runs = self.get_runs(item_info)
        last_update = max(runs.keys())
        return {last_update: runs[last_update]}

    def most_recent_nonzero(self, item_info):
        ordered_runs = self.last_to_first(item_info)
        for date in ordered_runs:
            size = ordered_runs[date]
            if size > 0:
                return {date: size}

    def is_goodtest(self, item_info, size):
        item = self.get_item(item_info)
        nominal = item.get(REFERENCE_KEY)
        if size > 0 and (nominal is not None):
            size = float(size)
            nominal = float(nominal)
            tolerance = nominal * RANGE_ACCEPTED
            min, max = nominal - tolerance, \
                nominal + tolerance
            if (size > max) or (size < min):
                return False
        return True

    def date_in_keys(self, item_info):
        """ Return first encountered date found in item keys """
        item = self.get_item(item_info)
        for key in item:
            if is_date(key):
                return key
        return None

    def is_red_item(self, item_info):
        """
        Return True if most recent non zero size for a given item info
        is out of range, i.e. is not a good test

        """
        item = self.get_item(item_info)
        size_to_check = self.most_recent_nonzero(item_info).values()[0]
        if self.is_goodtest(item_info, size_to_check):
            return False
        return True

    def test_to_archive(self, item_info, timestamp):
        item_datetime = timestamp_to_datetime(timestamp)
        test = dict(item_info)
        test["datetime"] = item_datetime
        return set_archive_path(test)

    def bad_list(self):
        """
        Return a list of all items with most recent test out of range

        Single list element is a item_info dictionary 
        of the corresponding out-of-range tes plus its {date: size}

        """
        bad_list = []
        for item_info in self.item_infos():
            if self.is_red_item(item_info):
                last_test = self.most_recent_nonzero(item_info)
                item_info.update(last_test)
                bad_list.append(item_info)
        return bad_list

    def item_string(self, level, separator='_'):
        depth = len(level)
        fields = list(self.template[:depth])
        return separator.join([str(level[field]) for field in fields])
