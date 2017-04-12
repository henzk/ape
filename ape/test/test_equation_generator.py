from __future__ import unicode_literals, print_function
from django_productline.testingutils import NoMigrationsTestCase
from ape.container_mode import equation_generator as generator
from ape.container_mode import exceptions
import os.path

class EquationGeneratorTests(NoMigrationsTestCase):


    def setUp(self):
        """
        Setup test data such as the container dir path and the product name according
        to tests/__testdata__
        :return:
        """
        testdata_dir = os.path.join(os.path.dirname(__file__), '__testdata__')
        self.container_dir = os.path.join(testdata_dir, 'samplecontainer')


    def _get_patched_generator_module(self):
        """
        Returns a patched version of the EquationGenerator which can be tested in isolation.
        :return:
        """
        # path the repo name retrieval method as we dont have a real repo
        generator._get_real_repo_name = lambda container_dir: 'samplecontainer'
        return generator


    def test_get_feature_model_config_file_path(self):
        """
        _get_feature_model_config_file_path returns the correct path to the product equation config file.
        :return:
        """

        eg = self._get_patched_generator_module()

        self.assertEqual(
            eg._get_feature_model_config_file_path(self.container_dir, 'dev'),
            os.path.join(self.container_dir, '_lib/featuremodel/productline/products/samplecontainer/dev/product.equation.config')
        )

    def test_get_feature_model_config_file_path_does_not_exist(self):
        """
        _get_feature_model_config_file_path raises if the the product equation config file calculated from
        passed container_dir and product name does not exist
        :return:
        """

        eg = self._get_patched_generator_module()

        with self.assertRaises(exceptions.FileDoesNotExistError):
            eg._get_feature_model_config_file_path(self.container_dir, 'somenonexistentdirname')


    def test_get_product_equation_file_path(self):
        """
        _get_product_equation_file_path returns the correct path to the product equation file.
        :return:
        """

        eg = self._get_patched_generator_module()

        self.assertEqual(
            eg._get_product_equation_file_path(self.container_dir, 'dev'),
            os.path.join(self.container_dir, 'products', 'dev/product.equation')
        )





    def test_transform_config_to_equation(self):
        """
        _transform_config_to_equation produces the correct formatted product equation file format.
        :return:
        """

        eg = self._get_patched_generator_module()

        self.assertEqual(
            eg._transform_config_to_equation(
                eg._get_feature_model_config_file_path(self.container_dir, 'dev')
            ),
            'aaa\naaa.features.bbb\nccc'
        )





