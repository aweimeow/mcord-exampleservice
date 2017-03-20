# models.py -  ExampleService Models

from core.models import Service, TenantWithContainer, Image
from django.db import models, transaction

MCORD_KIND = "My Example Service"

SERVICE_NAME = 'exampleservice'
SERVICE_NAME_VERBOSE = 'Example Service'
SERVICE_NAME_VERBOSE_PLURAL = 'Example Services'
TENANT_NAME_VERBOSE = 'Example Tenant'
TENANT_NAME_VERBOSE_PLURAL = 'Example Tenants'

class ExampleService(Service):

    KIND = SERVICE_NAME

    class Meta:
        app_label = SERVICE_NAME
        verbose_name = SERVICE_NAME_VERBOSE

    service_message = models.CharField(max_length=254, help_text="Service Message to Display")

class ExampleTenant(TenantWithContainer):

    KIND = SERVICE_NAME

    class Meta:
        verbose_name = TENANT_NAME_VERBOSE

    tenant_message = models.CharField(max_length=254, help_text="Tenant Message to Display")
    image_name = models.CharField(max_length=254, help_text="Name of VM image")
    default_attributes = {"s5s8_pgw_tag": 300, "image_name": "trusty-server-multi-nic"}

    def __init__(self, *args, **kwargs):
        exampleservice = ExampleService.get_service_objects().all()
        if exampleservice:
            self._meta.get_field('provider_service').default = exampleservice[0].id
        super(ExampleTenant, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(ExampleTenant, self).save(*args, **kwargs)
        model_policy_exampletenant(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_container()
        super(ExampleTenant, self).delete(*args, **kwargs)

    @property
    def image(self):
        img = self.image_name.strip()
        if img.lower() != 'default':
            return Image.objects.get(name=img)
        else:
            return super(ExampleTenant, self).image

    @property
    def s5s8_pgw_tag(self):
        return self.get_attribute(
            "s5s8_pgw_tag",
            self.default_attributes['s5s8_pgw_tag'])

    def get_slice(self):
        if not self.provider_service.slices.count():
            raise XOSConfigurationError("The service has no slices")
        slice = self.provider_service.slices.all()[0]
        return slice

    def make_instance(self):
        slice = self.provider_service.slices.all()[0]
        flavors = Flavor.objects.filter(name=slice.default_flavor)

        if not flavors:
            raise XOSConfigurationError("No default flavor")

        slice = self.provider_service.slices.all()[0]

        if slice.default_isolation == "container_vm":
            (node, parent) = ContainerVmScheduler(slice).pick()
        else:
            (node, parent) = LeastLoadedNodeScheduler(slice).pick()

        instance = Instance(slice = slice,
                        node = node,
                        image = self.image,
                        creator = self.creator,
                        deployment = node.site_deployment.deployment,
                        flavor = flavors[0],
                        isolation = slice.default_isolation,
                        parent = parent)
        self.save_instance(instance)

        return instance

    def save_instance(self, instance):
        with transaction.atomic():
            if instance.isolation in ["vm"]:
                if self.image_name == 'trusty-server-multi-nic':
                    lan_network = self.get_lan_network(instance, "wan_network")
                    port = self.find_or_make_port(instance,lan_network)
                    port.set_parameter("neutron_port_ip", "102.0.0.8")
                    port.save()

    def find_or_make_port(self, instance, network, **kwargs):
        port = Port.objects.filter(instance=instance, network=network)
        if port:
            port = port[0]
            print "port already exist", port[0]
        else:
            port = Port(instance=instance, network=network, **kwargs)
            print "NETWORK", network, "MAKE_PORT", port
            port.save()
        return port

    def manage_container(self):
        from core.models import Instance, Flavor
        
        if self.deleted:
            return

        slice = self.get_slice()
        if slice.default_isolution in ["container_vm", "container"]
            super(ExampleTenant, self).manage_container()
            return

        if not self.s5s8_pgw_tag:
            raise XOSConfigurationError("S5S8_PGW_TAG is missed")

        if self.instance:
            # We're good, No need to create an instance
            return

        instance = self.make_instance()
        self.instance = instance
        super(TenantWithContainer, self).save()
    
    

def model_policy_exampletenant(pk):
    with transaction.atomic():
        tenant = ExampleTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        tenant = tenant[0]
        tenant.manage_container()

