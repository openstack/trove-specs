# Copyright [2015] Hewlett-Packard Development Company, L.P.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re

import docutils.core
import testtools


class TestTitles(testtools.TestCase):

    def _get_title(self, section_tree):
        section = {
            'subtitles': [],
        }
        for node in section_tree:
            if node.tagname == 'title':
                section['name'] = node.rawsource
            elif node.tagname == 'section':
                subsection = self._get_title(node)
                section['subtitles'].append(subsection['name'])
        return section

    def _get_titles(self, spec):
        titles = {}
        for node in spec:
            if node.tagname == 'section':
                # Note subsection subtitles are thrown away
                section = self._get_title(node)
                titles[section['name']] = section['subtitles']
        return titles

    def _check_titles(self, filename, expect, actual):
        missing_sections = [x for x in expect.keys() if x not in actual.keys()]
        extra_sections = [x for x in actual.keys() if x not in expect.keys()]

        msgs = []
        if len(missing_sections) > 0:
            msgs.append("Missing sections: %s" % missing_sections)
        if len(extra_sections) > 0:
            msgs.append("Extra sections: %s" % extra_sections)

        for section in expect.keys():
            if section in actual:
                missing_subsections = [x for x in expect[section]
                                       if x not in actual[section]]
                # extra subsections are allowed
                if len(missing_subsections) > 0:
                    msgs.append("Section '%s' is missing subsections: %s"
                                % (section, missing_subsections))

        if len(msgs) > 0:
            self.fail("While checking '%s':\n  %s"
                      % (filename, "\n  ".join(msgs)))

    def _check_lines_wrapping(self, tpl, raw):
        for i, line in enumerate(raw.split("\n")):
            # allow lines that start with 4 spaces to have 4 extra characters
            # This is to facilitate not having to reformat code blocks just for
            # an arbitrary line limit
            line_limit = 79
            if line.startswith('    '):
                line_limit += 4
            # ignore lines that have more than one '/' - this will exclude
            # web addresses and long file system paths.
            if line.count('/') > 1:
                continue
            # ignore lines that start with '+' or '|'
            # this should exclude tables and lists
            if re.match('[|+]', line.lstrip()):
                continue
            # ignore lines that contain '<% $' as it's probably yaml
            if '<% $' in line:
                continue
            self.assertTrue(
                len(line) < line_limit + 1,
                msg="%s:%d: Line limited to a maximum of %d characters." %
                (tpl, i+1, line_limit))

    def _check_no_cr(self, tpl, raw):
        matches = re.findall('\r', raw)
        self.assertEqual(
            0, len(matches),
            "Found %s literal carriage returns in file %s" %
            (len(matches), tpl))

    def _check_trailing_spaces(self, tpl, raw):
        for i, line in enumerate(raw.split("\n")):
            trailing_spaces = re.findall(" +$", line)
            self.assertEqual(
                0, len(trailing_spaces),
                "Found trailing spaces on line %s of %s" % (i+1, tpl))

    def test_template(self):
        with open("specs/template.rst") as f:
            template = f.read()
        spec = docutils.core.publish_doctree(template)
        template_titles = self._get_titles(spec)

        # Get the current release directory - since we're moving up
        # alphabetically, grab the highest name in the spec directory
        generator = os.walk('specs')
        dirname, subdirs, files = next(generator)
        current_release = max(subdirs)
        found = False
        for dirname, subdirs, files in generator:
            if dirname.endswith("/" + current_release):
                found = True
                break
        self.assertTrue(found, "No specs found.")
        for filename in files:
            filename = "%s/%s" % (dirname, filename)
            self.assertTrue(filename.endswith(".rst"),
                            "spec's file must uses 'rst' extension.")
            with open(filename) as f:
                data = f.read()

            spec = docutils.core.publish_doctree(data)
            titles = self._get_titles(spec)
            self._check_titles(filename, template_titles, titles)
            self._check_lines_wrapping(filename, data)
            self._check_no_cr(filename, data)
            self._check_trailing_spaces(filename, data)
