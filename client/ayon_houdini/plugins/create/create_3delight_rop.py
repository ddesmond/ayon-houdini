from ayon_houdini.api import plugin
from ayon_core.lib import EnumDef, BoolDef


class Create3DelightRop(plugin.HoudiniCreator):
    """3Delight ROP"""

    identifier = "io.openpype.creators.houdini.arnold_rop"
    label = "3Delight ROP"
    product_type = "3delight_rop"
    icon = "magic"

    # Default extension
    ext = "exr"

    # Default render target
    render_target = "farm_split"

    def create(self, product_name, instance_data, pre_create_data):
        import hou
        # Transfer settings from pre create to instance
        creator_attributes = instance_data.setdefault(
            "creator_attributes", dict())
        for key in ["render_target", "review"]:
            if key in pre_create_data:
                creator_attributes[key] = pre_create_data[key]

        # Remove the active, we are checking the bypass flag of the nodes
        instance_data.update({"node_type": "3Delight"})

        instance = super(Create3DelightRop, self).create(
            product_name,
            instance_data,
            pre_create_data)

        instance_node = hou.node(instance.get("instance_node"))

        ext = pre_create_data.get("image_format")

        renders_dir = hou.text.expandString("$HIP/pyblish/renders/")
        # image
        filepath = f"{renders_dir}{product_name}/{product_name}.$F4.{ext}"
        # nsi
        nsi_filepath = "{export_dir}{product_name}/{product_name}.$F4.nsi".format(
                                                export_dir=hou.text.expandString("$HIP/pyblish/nsi/"),
                                                product_name=product_name,
                                                )

        parms = {
            # Render frame range
            "trange": 1,
            # 3Delight ROP settings
            "display_rendered_images": 1,
            "default_image_filename": filepath,
            "save_rendered_images": 0,
            "display_rendered_images": 0,
            "output_nsi_files": 0,
        }

        if pre_create_data.get("render_target") == "farm_split":
            parms["output_nsi_files"] = 1
            parms["default_export_nsi_filename"] = nsi_filepath

        instance_node.setParms(parms)

        # Lock any parameters in this list
        to_lock = ["productType", "id"]
        self.lock_parameters(instance_node, to_lock)

    def get_instance_attr_defs(self):
        """get instance attribute definitions.

        Attributes defined in this method are exposed in
            publish tab in the publisher UI.
        """

        render_target_items = {
            "local": "Local machine rendering",
            "local_no_render": "Use existing frames (local)",
            "farm": "Farm Rendering",
            "farm_split": "Farm Rendering - Split export & render jobs",
        }

        return [
            BoolDef("review",
                    label="Review",
                    tooltip="Mark as reviewable",
                    default=True),
            EnumDef("render_target",
                    items=render_target_items,
                    label="Render target",
                    default=self.render_target),
        ]

    def get_pre_create_attr_defs(self):
        image_format_enum = [
            "bmp", "cin", "exr", "jpg", "pic", "pic.gz", "png",
            "rad", "rat", "rta", "sgi", "tga", "tif",
        ]

        attrs = [
            EnumDef("image_format",
                    image_format_enum,
                    default=self.ext,
                    label="Image Format Options"),
        ]
        return attrs + self.get_instance_attr_defs()
