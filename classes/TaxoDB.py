import os
import json
import copy
from utils.misc import nested_dict
from collections import defaultdict

VALUES = 'values'


class TaxoDB(object):
    def __init__(self, path, template_fields):
        self.source = path
        self.db = self.load()
        self.template = list(template_fields)

    def load(self):
        """ Return the dict database from given json-file path """
        if os.path.isfile(self.source):
            f = open(self.source, 'r')
            db = json.load(f)
        else:
            db = {}
        return db

    def save(self):
        f = open(self.source, 'w')
        loader = json.dump(self.db, f, indent=4, separators=(',', ': '))
        f.close()

    def add_item(self, item_info, value):
        """
        Args:
        item_info <dict> -- keys: self.template elements
        values: identifier of the item keys
        value <dict> -- a dict containing values for the given item_info

        """
        # TODO: adjust to accept all kind of values, not only dicts
        nested_fields = self.db
        info = dict(item_info)
        for template_field in self.template:
            field = info.pop(template_field)  # check key not in dict
            if field not in nested_fields:
                nested_fields[field] = {}
            nested_fields = nested_fields[field]
        nested_fields.update(value)
        return self.db

    def get_item(self, item_info):
        selected_item = self.db
        for template_field in self.template:
            field = item_info[template_field]
            try:
                selected_item = selected_item[field]
            except KeyError:
                msg = "key " + field + " does not exist"
                print(msg)
                return template_field.index(field)
        return selected_item

    def update_source(self, item_info, value):
        updated_db = self.add_item(item_info, value)
        self.save()
        return updated_db

    def get_level(self, level_info):
        depth = len(level_info.keys())
        selected_fields = self.template[:depth]
        selected_level = self.db
        for selected_field in selected_fields:
            field = str(level_info[selected_field])
            try:
                selected_level = selected_level[field]
            except KeyError:
                msg = "key " + str(field) + " does not exist"
                print(msg)
                return template_field.index(field)
        return selected_level

    def level_keys(self, level_info):
        return list(self.get_level(level_info).keys())

    def item_infovalues(self, level=None, group_names=None):
        if level is None and group_names is None:
            level = self.db
            group_names = self.template
        group_names_copy = copy.deepcopy(group_names)
        data = copy.deepcopy(level)
        try:
            group, group_names_copy = group_names[0], group_names_copy[1:]
        except IndexError:  # most nested dict reached
            flattened = {}
            flattened[VALUES] = copy.deepcopy(data)
            yield flattened
            return
        try:
            for key, value in data.iteritems():
                for flattened in self.item_infovalues(value, group_names_copy):
                    flattened.update({group: key})
                    yield flattened
        except AttributeError:
            yield {group: data}

    def item_infos(self, level=None,  group_names=None):
        # group_names = list(self.template)
        if level is None and group_names is None:
            level = self.db
            group_names = self.template
        group_names_copy = copy.deepcopy(group_names)
        data = copy.deepcopy(level)
        try:
            group, group_names_copy = group_names[0], group_names_copy[1:]
        except IndexError:  # most nested dict reached
            flattened = {}
            yield flattened
            return
        try:
            for key, value in data.iteritems():
                for flattened in self.item_infos(value, group_names_copy):
                    flattened.update({group: key})
                    yield flattened
        except AttributeError:
            yield {group: data}

    def to_info(self, info_plus_smth):
        info = dict((field, info_plus_smth[field])
                    for field in TEMPLATE_FIELDS)
        return info

    def keys_tupler(self, item_info):
        """
        From item_info dict return a tuple of all keys in
        their depth order (i.e. following TEMPLATE_FIELDS)

        Note that this works also if item_info is not complete, i.e.
        is a level dict (see get_level() for infos), but tuple
        will be shorter than TEMPLATE_FIELDS

        """
        keys = tuple(item_info[field] for field in self.template
                     if item_info.get(field) is not None)
        return keys

    def namedkeys_tupler(self, item_info):
        """
        Same as keys_tupler but corresponding keys-field is provided

        TODO: give example

        """
        namedkeys = tuple((field, item_info[field])
                          for field in self.template
                          if item_info.get(field) is not None)
        return namedkeys

    def depth_field(self, level_info):
        depth = len(level_info)
        return self.template[depth]

    def field_products(self, fields):
        """
        Same as combine() but can select fields to combine.

        Args:
        fields (iterable) -- fields to get info of
        (e.g.['branch', 'sample'])

        """
        products = []
        for item_info in self.item_infos():
            comb = []
            for field in fields:
                comb.append(item_info.get(field))
            if comb not in products:
                products.append(comb)
        return products

    def updatable_copy(self):
        updatable = nested_dict()
        db = copy.deepcopy(self.db)
        for k, v in db.iteritems():
            if isinstance(v, dict):
                updatable[k] = defaultdict(dict, v)
                updatable_copy(v, updatable[k])
            else:
                updatable[k] = v
        return updatable

    def info_tupler(self, item_info):
        """
        From item_info dict return a tuple of all field names in 
        their depth order (i.e. following self.template)

        Note that this works also if item_info is not complete, i.e.
        is a level dict (see get_level() for infos), but tuple
        will be shorter than TEMPLATE_FIELDS

        """
        infos = tuple(item_info[field] for field in self.template
                      if item_info.get(field) is not None)
        return infos
