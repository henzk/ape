from __future__ import unicode_literals, print_function
import codecs, json

__all__ = ['ProductSpecValidator']

class ProductSpecValidator(object):
    def __init__(self, spec_path, product_name, feature_list):
        """
        Constructor
        :param spec_path: file path to the product spec json
        :param product_name: the name of the product to extract the concrete spec
        :param feature_list: the list of features that will be checked
        """
        self.product_spec = self._read(spec_path, product_name)
        self.feature_list = feature_list
        self.errors_mandatory = []
        self.errors_never = []

    def is_valid(self):
        """
        Checks the feature list product spec against.
        Checks if all mandartory features are contained;
        Checks that all "never" features are not contained
        :return: boolean
        """
        for feature in self.product_spec.get('mandatory'):
            if feature.replace('__', '.') not in self.feature_list:
                self.errors_mandatory.append(feature)

        for feature in self.product_spec.get('never'):
            if feature.replace('__', '.') in self.feature_list:
                self.errors_never.append(feature)

        return not self.has_errors()

    def get_errors_mandatory(self):
        """
        Returns the list of features that are mandatory but missing in the passed feature list.
        :return: list
        """
        return self.errors_mandatory

    def get_errors_never(self):
        """
        Returns the list if featzres that are declaed as "never" but are contained in the feature list.
        :return:
        """
        return self.errors_never

    def has_errors(self):
        """
        Returns true if any error occured.
        :return: boolean
        """
        return len(self.get_errors_mandatory()) > 0 or len(self.get_errors_never()) > 0

    def _read(self, spec_path, product_name):
        """
        Reads the spec files and extracts the concrete product spec.
        :param spec_path:
        :param product_name:
        :return:
        """
        with codecs.open(spec_path, 'r') as f:
            for entry in json.loads(f.read()):
                if product_name in entry.get('products'):
                    return entry
