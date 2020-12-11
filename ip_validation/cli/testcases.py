#!/usr/bin/env python
# coding=UTF-8
#
# E-ARK Validation
# Copyright (C) 2019
# All rights reserved.
#
# Licensed to the E-ARK project under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The E-ARK project licenses
# this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#
"""
E-ARK : Information package validation
        E-ARK Test Case processing
"""
import lxml.etree as ET

from importlib_resources import files

import ip_validation.cli.resources as RES

TC_SCHEMA = ET.XMLSchema(file=str(files(RES).joinpath('testCase.xsd')))

class TestCase():
    """
    Encapsulates the E-ARK XML Test Case files.

    Parameters / attributes
     - case_id: a CaseId instance that is the compound test case id.
     - testable: boolean, True if test case is "testable", False otherwise
     - references: a list of references to relavent requirements.
    """
    def __init__(self, case_id, testable=True, references=None, text="", rules=None):
        self._case_id = case_id
        self._testable = testable
        self._references = [] if references is None else references
        self._text = text
        self._rules = [] if rules is None else rules

    @property
    def case_id(self):
        """Return the test case id instance."""
        return self._case_id

    @property
    def testable(self):
        """Return True if the test case is considered testable, otherwise False."""
        return self._testable == 'TRUE'

    @property
    def unknown(self):
        """Return True if the test case testability is unknown, otherwise False."""
        return self._testable == 'UNKNOWN'

    @property
    def references(self):
        """Return the list of relavent requirements."""
        return self._references

    @property
    def requirement_text(self):
        """Return the requirment text."""
        return self._text

    @property
    def rules(self):
        """Return the rules associated with the test case."""
        return self._rules

    def __str__(self):
        return "case_id:" + str(self.case_id) + ", testable:" + \
            self.testable + ", requirement:" + self.requirement_text

    class CaseId():
        """
        Encapsulates an E-ARK XML Test Case ID.

        Parameters / attributes
         - requirement_id: a requirement ID string from the specification.
         - specification: the name of the specification.
         - version: the version of the specifciation.
        """
        def __init__(self, requirement_id, specification="CSIP", version="2.0"):
            self._requirement_id = requirement_id
            self._specification = specification
            self._version = version

        @property
        def requirement_id(self):
            """Return the requirement ID."""
            return self._requirement_id

        @property
        def specification(self):
            """Return the specification name."""
            return self._specification

        @property
        def version(self):
            """Return the version."""
            return self._version

        @classmethod
        def from_element(cls, case_id_ele):
            """Create a TestCase from an XML element."""
            requirement_id = case_id_ele.get('requirementId')
            specification = case_id_ele.get('specification')
            version = case_id_ele.get('version')
            return cls(requirement_id, specification, version)

        def __str__(self):
            return "req_id:" + self.requirement_id + ", specification:" + \
                self.specification + ", version:" + self.version

    class Rule():
        """docstring for Rule."""
        def __init__(self, rule_id, description, error, packages):
            self._rule_id = rule_id
            self._description = description
            self._error = error
            self._packages = packages

        @property
        def rule_id(self):
            """Return the rule ID."""
            return self._rule_id

        @property
        def description(self):
            """Return the description."""
            return self._description

        @property
        def error(self):
            """Return the error."""
            return self._error

        @property
        def packages(self):
            """Return the corpus packages."""
            return self._packages

        def __str__(self):
            return "rule_id:" + self.rule_id + ", description:" + \
                self.description + ", error:" + str(self.error)

        @classmethod
        def from_element(cls, rule_ele):
            """Create a Rule from an XML element."""
            rule_id = rule_ele.get('id')
            description = ""
            error = None
            packages = []
            for child in rule_ele:
                if child.tag == 'description':
                    description = child.text
                elif child.tag == 'error':
                    error = cls.Error.from_element(child)
                elif child.tag == 'corpusPackages':
                    packages = cls._parse_package_list(child)
            return cls(rule_id, description, error, packages)

        @staticmethod
        def _parse_package_list(packages_ele):
            packages = []
            for child in packages_ele:
                if child.tag == 'package':
                    packages.append(TestCase.Rule.Package.from_element(child))
            return packages

        class Error():
            """docstring for Error."""
            def __init__(self, level, message):
                self._level = level
                self._message = message

            @property
            def level(self):
                """Return the level."""
                return self._level

            @property
            def message(self):
                """Return the message."""
                return self._message

            @classmethod
            def from_element(cls, error_ele):
                """Return a Errpr instance from an XML element."""
                level = error_ele.get('level')
                message = ''
                for child in error_ele:
                    if child.tag == 'message':
                        message = child.text
                return cls(level, message)

        class Package():
            """docstring for Package."""
            def __init__(self, name, path, is_valid, description):
                self._name = name
                self._path = path
                self._is_valid = is_valid
                self._description = description

            @property
            def name(self):
                """Return the name."""
                return self._name

            @property
            def path(self):
                """Return the path."""
                return self._path

            @property
            def is_valid(self):
                """Return the is_valid."""
                return self._is_valid

            @property
            def description(self):
                """Return the description."""
                return self._description

            @classmethod
            def from_element(cls, package_ele):
                """Return a Package instance from an XML element."""
                is_valid = package_ele.get('isValid')
                name = package_ele.get('name')
                path = ""
                description = ""
                for child in package_ele:
                    if child.tag == 'path':
                        path = child.text
                    elif child.tag == 'description':
                        description = child.text
                return cls(name, path, is_valid, description)


    @classmethod
    def from_xml_string(cls, xml, schema=TC_SCHEMA):
        """Create a test case from an XML string."""
        tree = ET.fromstring(xml)
        return cls.from_element(tree.getroot(), schema)

    @classmethod
    def from_xml_file(cls, xml_file, schema=TC_SCHEMA):
        """Create a test case from an XML file."""
        tree = ET.parse(xml_file)
        return cls.from_element(tree.getroot(), schema)

    @classmethod
    def from_element(cls, case_ele, schema=TC_SCHEMA):
        """Create a TestCase from an XML element."""
        # Grab the testable att
        schema.validate(case_ele)
        testable = case_ele.get('testable')
        req_id = None
        text = ""
        rules = []
        # Loop through the child eles
        for child in case_ele:
            if child.tag == 'id':
                # Process the id element
                req_id = cls.CaseId.from_element(child)
            elif child.tag == 'requirementText':
                # Grab the requirement text value
                text = child.text
            elif child.tag == 'rules':
                for rule_ele in child:
                    rules.append(cls.Rule.from_element(rule_ele))

        # Return the TestCase instance
        return cls(req_id, testable=testable, text=text, rules=rules)
