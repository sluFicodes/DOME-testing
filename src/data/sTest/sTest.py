import json
import os
from wstore.asset_manager.resource_plugins.plugin import Plugin
from bson.objectid import ObjectId

class STestPlugin(Plugin):

    def _register_call(self, method, param):

        if "call_registry" not in os.environ:
            os.environ["call_registry"] = '{"name": "sTest"}'
        registry = os.environ["call_registry"]
        registry = json.loads(registry)
        if method in registry:
            registry[method].append(param)
        else:
            registry[method] = [param]
        os.environ["call_registry"] = json.dumps(registry, indent=4)

    def on_pre_product_spec_validation(self, provider, asset_t, media_type, url):
        self._register_call("on_pre_product_spec_validation", [provider.name, asset_t, media_type, url])

    def on_post_product_spec_validation(self, provider, asset):
        self._register_call("on_post_product_spec_validation", [provider.name, str(asset._id)]) #TODO

    def on_pre_service_spec_attachment(self, asset, asset_t, service_spec):
        self._register_call("on_pre_service_spec_attachment", [str(asset._id), asset_t, service_spec["id"]])

    def on_post_service_spec_attachment(self, asset, asset_t, service_spec):
        self._register_call("on_post_service_spec_attachment", [str(asset._id), asset_t, service_spec["id"]])

    def on_pre_service_spec_validation(self, provider, asset_t, media_type, url):
        self._register_call("on_pre_service_spec_validation", [provider.name, asset_t, media_type, url])

    def on_post_service_spec_validation(self, provider, asset):
        self._register_call("on_post_service_spec_validation", [provider.name, str(asset._id)])

    def on_pre_service_spec_upgrade(self, asset, asset_t, service_spec):
        self._register_call("on_pre_service_spec_upgrade", [str(asset._id), asset_t, service_spec["id"]])

    def on_post_service_spec_upgrade(self, asset, asset_t, service_spec):
        self._register_call("on_post_service_spec_upgrade", [str(asset._id), asset_t, service_spec["id"]])

    def on_pre_product_offering_validation(self, asset, product_offering):
        self._register_call("on_pre_product_offering_validation", [str(asset._id), product_offering["name"]])

    def on_post_product_offering_validation(self, asset, product_offering):
        self._register_call("on_post_product_offering_validation", [str(asset._id), product_offering["name"]])


