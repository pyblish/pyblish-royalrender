import pyblish.api


class PyblishRoyalRenderIntegrate(pyblish.api.ContextPlugin):
    """Submits to Royal Render."""

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
        from xml.etree.ElementTree import SubElement

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
        import os
        from xml.etree.ElementTree import ElementTree, Element
        import uuid
        import tempfile
        import platform
        import subprocess

        # Root element
        root_element = Element("rrJob_submitFile")
        root_element.attrib["syntax_version"] = "6.0"
        self.sub_element(root_element, "DeleteXML", "1")

        # Collect jobs
        jobs = []
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

            if instance.data.get("royalrenderData", {}):
                jobs.append(instance.data["royalrenderData"])

            jobs.extend(instance.data.get("royalrenderJobs", []))

        # Skip further processing if there are not any jobs
        if not jobs:
            return

        # Order jobs by PreID
        jobs_ordered = {}
        for job in jobs:
            preid = str(job.get("PreID", 0))
            if preid in jobs_ordered.keys():
                jobs_ordered[preid].append(job)
            else:
                jobs_ordered[preid] = [job]

        for count in range(0, len(jobs_ordered.keys())):
            for job in jobs_ordered[str(count)]:
                job_element = self.sub_element(root_element, "Job", "")
                self.dict_to_elements(job, job_element)

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
            root = os.path.join(rr_root, "bin", "win64")
            if "pyblishRoyalRenderUI" in context.data:
                arguments.append(os.path.join(root, "rrSubmitter.exe"))
            else:
                arguments.append(os.path.join(root, "rrSubmitterConsole.exe"))
        else:
            raise ValueError("Only Windows is currently supported.")

        arguments.append(xml_path)

        startupinfo = None
        if hasattr(subprocess, "STARTF_USESHOWWINDOW"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        proc = subprocess.Popen(
            arguments,
            stdout=subprocess.PIPE,
            startupinfo=startupinfo
        )

        # Blocks until finished..
        errors = []
        for line in iter(proc.stdout.readline, b""):
            self.log.debug(line)
            if "error" in line.lower():
                errors.append(line)

        if errors:
            raise ValueError(errors)


class PyblishRoyalRenderDisplayUI(pyblish.api.ContextPlugin):
    """Setting plugin for displaying the submitter UI."""

    order = PyblishRoyalRenderIntegrate.order - 0.1
    label = "Display Royal Render Submitter"
    active = False
    optional = True

    def process(self, context):

        context.data["pyblishRoyalRenderUI"] = True
