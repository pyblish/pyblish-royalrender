import pyblish.api


class PyblishRoyalRenderValidate(pyblish.api.ContextPlugin):
    """ Validates the installation of Royal Render."""

    order = pyblish.api.ValidatorOrder
    label = "Royal Render"

    def process(self, context):
        import os

        msg = "\"RR_Root\" environment variable could not be found."
        assert "RR_Root" in os.environ, msg
