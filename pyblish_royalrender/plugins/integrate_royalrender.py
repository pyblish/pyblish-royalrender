import os
from xml.etree.ElementTree import ElementTree, Element, SubElement
import uuid
import tempfile
import platform
import subprocess

import pyblish.api


class PyblishRoyalRenderIntegrate(pyblish.api.ContextPlugin):
    """ Submits to Royal Render. """

    order = pyblish.api.IntegratorOrder
    label = "Royal Render"

    def indent(self, elem, level=0):
        i = "\n" + level * "\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            for e in elem:
                self.indent(e, level + 1)
                if not e.tail or not e.tail.strip():
                    e.tail = i + "\t"
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        return True

    def sub_element(self, r, e, text):
        sub = SubElement(r, e)
        if (type(text) == unicode):
            sub.text = text.encode('utf8')
        else:
            sub.text = str(text).decode("utf8")
        return sub

    def dict_to_elements(self, data, element):
        for key, value in data.iteritems():
            if isinstance(value, dict):
                self.dict_to_elements(
                    value, self.sub_element(element, key, "")
                )
            if isinstance(value, list):
                for item in value:
                    self.sub_element(element, key, item)
            else:
                self.sub_element(element, key, value)

    def process(self, context):

        # Root element
        root_element = Element("rrJob_submitFile")
        root_element.attrib["syntax_version"] = "6.0"
        self.sub_element(root_element, "DeleteXML", "1")

        # Job element
        job_count = 0
        for instance in context:

            # Only consider enabled instances
            if not instance.data.get("publish", True):
                continue

            # skipping instance if not part of the family
            if "royalrender" not in instance.data.get("families", []):
                msg = "No \"royalrender\" family assigned. "
                msg += "Skipping \"%s\"." % instance
                self.log.debug(msg)
                continue

            job_element = self.sub_element(root_element, "Job", "")
            self.dict_to_elements(
                instance.data["royalrenderData"], job_element
            )
            job_count += 1

        # Skip further processing if there are not any jobs
        if not job_count:
            return

        # Writing to disk
        tree_element = ElementTree(root_element)
        self.indent(tree_element.getroot())

        xml_path = os.path.join(
            tempfile.gettempdir(),
            "pyblish_royalrender_{0}.xml".format(uuid.uuid4())
        )
        with open(xml_path, "w") as f:
            tree_element.write(f)

        with open(xml_path, "r") as f:
            self.log.debug(f.read())

        # Submitting to RoyalRender
        arguments = []

        rr_root = os.environ["RR_Root"]

        # Windows arguments
        if platform.system() == "Windows":
            arguments.append(
                os.path.join(rr_root, "bin", "win", "rrStartLocal.exe"),
            )
            if "pyblishRoyalRenderUI" in context.data:
                arguments.append("rrSubmitter.exe")
            else:
                arguments.append("rrSubmitterConsole.exe")

        arguments.append(xml_path)

        startupinfo = None
        if hasattr(subprocess, "STARTF_USESHOWWINDOW"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        proc = subprocess.Popen(
            arguments,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo
        )
        proc.stdin.close()
        proc.stderr.close()

        output = proc.stdout.read()
        self.log.debug(output)


class PyblishRoyalRenderDisplayUI(pyblish.api.ContextPlugin):
    """ Setting plugin for displaying the submitter UI """

    order = PyblishRoyalRenderIntegrate.order - 0.1
    label = "Display Royal Render Submitter"
    active = False
    optional = True

    def process(self, context):

        context.data["pyblishRoyalRenderUI"] = True
