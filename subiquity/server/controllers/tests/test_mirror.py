# Copyright 2021 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import jsonschema
import unittest
from unittest import mock

from subiquitycore.tests.mocks import make_app
from subiquity.models.mirror import MirrorModel
from subiquity.server.controllers.mirror import MirrorController


class TestMirrorSchema(unittest.TestCase):
    def validate(self, data):
        jsonschema.validate(data, MirrorController.autoinstall_schema)

    def test_empty(self):
        self.validate({})

    def test_disable_components(self):
        self.validate({'disable_components': ['universe']})

    def test_no_disable_main(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate({'disable_components': ['main']})

    def test_no_disable_random_junk(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate({'disable_components': ['not-a-component']})


class TestMirrorController(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        app = make_app()
        self.controller = MirrorController(app)
        self.controller.apt_configurer = mock.AsyncMock()

    def test_make_autoinstall(self):
        self.controller.model = MirrorModel()
        config = self.controller.make_autoinstall()
        self.assertIn("disable_components", config.keys())
        self.assertIn("primary", config.keys())
        self.assertIn("geoip", config.keys())
