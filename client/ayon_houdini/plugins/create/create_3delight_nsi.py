# -*- coding: utf-8 -*-
"""Creator plugin for creating 3Delight NSi files."""
from ayon_houdini.api import plugin
from ayon_core.lib import EnumDef


class Create3DelightNsi(plugin.HoudiniCreator):
    """3Delight .nsi Archive"""

    identifier = "io.openpype.creators.houdini.nsi"
    label = "3Delight NSI"
    product_type = "nsi"
    icon = "magic"

    # Default extension: `.nsi`
    # however calling HoudiniCreator.create()
    # will override it by the value in the project settings
    ext = ".nsi"

    # Default render target
    render_target = "local"

    def create(self, product_name, instance_data, pre_create_data):
        import hou

        instance_data.update({"node_type": "3delight"})
        creator_attributes = instance_data.setdefault(
            "creator_attributes", dict())
        creator_attributes["render_target"] = pre_create_data["render_target"]

        instance = super(Create3DelightNsi, self).create(
            product_name,
            instance_data,
            pre_create_data)

        instance_node = hou.node(instance.get("instance_node"))

        # Hide Properties Tab on Arnold ROP since that's used
        # for rendering instead of .ass Archive Export
        parm_template_group = instance_node.parmTemplateGroup()
        parm_template_group.hideFolder("Properties", True)
        instance_node.setParmTemplateGroup(parm_template_group)

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
            # create params and setup the node
            # quality
            "shading_samples": 512,
            "pixel_samples": 128,
            "volume_samples": 1,

            # scene elements
            "override_display_flags": 1,
            "objects_to_render": "RND_*",

            # output
            "default_image_filename": filepath,
            "save_rendered_images": 0,
            "display_rendered_images": 0,
            "output_nsi_files": 1,
            "default_export_nsi_filename": nsi_filepath,

            # image_layers
            "aov": 16,
            "add_layer": 16,

            "multi_light_selection": "selection",
            "light_sets": 2,

            # set aovs
            "active_layer_1": 1,
            "aov_name_1": "Ci",
            "aov_clear_1,": 0,

            "active_layer_2": 1,
            "aov_name_2": "Diffuse",
            "aov_clear_2,": 0,

            "active_layer_3": 1,
            "aov_name_3": "Reflection",
            "aov_clear_3,": 0,

            "active_layer_4": 1,
            "aov_name_4": "Refraction",
            "aov_clear_4,": 0,

            "active_layer_5": 1,
            "aov_name_5": "Incandescence",
            "aov_clear_5,": 0,

            "active_layer_6": 1,
            "aov_name_6": "Z (depth)",
            "aov_clear_6,": 0,

            "active_layer_7": 1,
            "aov_name_7": "World Space Position",
            "aov_clear_7,": 0,

            "active_layer_8": 1,
            "aov_name_8": "World Space Normal",
            "aov_clear_8,": 0,

            "active_layer_9": 1,
            "aov_name_9": "Surface Shader Cryptomatte",
            "aov_clear_9,": 0,

            "active_layer_10": 1,
            "aov_name_10": "Ambient Occlusion",
            "aov_clear_10,": 0,

            "active_layer_11": 1,
            "aov_name_11": "Albedo",
            "aov_clear_11,": 0,

            "active_layer_12": 1,
            "aov_name_12": "UV",
            "aov_clear_12,": 0,

            "active_layer_13": 1,
            "aov_name_13": "Geometry Cryptomatte",
            "aov_clear_13,": 0,

            "active_layer_14": 1,
            "aov_name_14": "Ci (direct)",
            "aov_clear_14,": 0,

            "active_layer_15": 1,
            "aov_name_15": "Ci (indirect)",
            "aov_clear_15,": 0,

            "active_layer_16": 1,
            "aov_name_16": "Shadow Mask",
            "aov_clear_16,": 0,

            "use_light_set_1": 1,
            "light_set_1": "/obj/ambient",
            "use_rgba_only_set_1": 1,
            "use_light_set_2": 1,
            "light_set_2": "/obj/distantlight1",
            "use_rgba_only_set_2": 1

        }


        instance_node.setParms(parms)

        # Lock any parameters in this list
        to_lock = ["output_nsi_files", "productType", "id"]
        self.lock_parameters(instance_node, to_lock)

    def get_instance_attr_defs(self):
        render_target_items = {
            "local": "Local machine rendering",
            "local_no_render": "Use existing frames (local)",
            "farm": "Farm Rendering",
        }

        return [
            EnumDef("render_target",
                    items=render_target_items,
                    label="Render target",
                    default=self.render_target)
        ]

    def get_pre_create_attr_defs(self):
        attrs = super().get_pre_create_attr_defs()
        # Use same attributes as for instance attributes
        return attrs + self.get_instance_attr_defs()
