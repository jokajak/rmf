from django.contrib import admin

# Register your models here.
from sctm import models
from sctm.models import ControlFamily, Control, Overlay, ControlEnhancement
from sctm.models import Implementation, Product

admin.site.register(ControlFamily)
admin.site.register(Control)
admin.site.register(ControlEnhancement)
admin.site.register(Overlay)
admin.site.register(ImplementationText)
admin.site.register(Product)