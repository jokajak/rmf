from django.db import models

# Create your models here.
class ControlFamily(models.Model):
    """A NIST 800-53 Control Family

    A Control Family has a set of controls underneath it.
    """
    control_family_id = models.CharField(max_length=2, unique=True,
                                         null=False, blank=False)
    title = models.CharField(max_length=200, unique=True, null=False,
                             blank=False)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('control_family_id',)

class Overlay(models.Model):
    """A control selection overlay

    An Overlay is used to augment the controls selected by the RMF framewark.
    It defines additional information about controls and is a collection of
    controls.
    """
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)

class Control(models.Model):
    """A NIST 800-53 Control

    Each control is part of a control family.
    The security control structure consists of the following components:
    (i) a control section;
    (ii) a supplemental guidance section;
    (iii) a control enhancements section;
    (iv) a references section; and
    (v) a priority and baseline allocation section.

    At this time, baseline allocation is not populated
    """
    control_family = models.ForeignKey(ControlFamily)
    overlays = models.ManyToManyField(Overlay, blank=True, null=True,
                                      through='OverlayControlSupplement')
    control_id = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    control = models.TextField()
    supplemental_guidance = models.TextField()
    references = models.CharField(max_length=255, null=True, blank=True)
    related_controls = models.ManyToManyField('self', symmetrical=False,
                                              null=True, blank=True,
                                              related_name='related+')
    priority = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return '%s-%s %s' % (self.control_family.control_family_id,
                          self.control_id, self.title)

    class Meta:
        ordering = ('control_id',)
        unique_together = ('control_family', 'control_id')

class ControlEnhancement(models.Model):
    """A NIST 800-53 Control Enhancement

    From NIST 800-53:
    The security control enhancements section provides statements of
    security capability to: (i) add functionality/specificity to a
    control; and/or (ii) increase the strength of a control. In both
    cases, control enhancements are used in information systems and
    environments of operation requiring greater protection than
    provided by the base control due to the potential adverse
    organizational impacts or when organizations seek additions to the
    base control functionality/specificity based on organizational
    assessments of risk. Security control enhancements are numbered
    sequentially within each control so that the enhancements can be
    easily identified when selected to supplement the base control.
    Each security control enhancement has a short subtitle to indicate
    the intended security capability provided by the control
    enhancement. In the AU-3 example, if the first control enhancement
    is selected, the control designation becomes AU-3 (1). The
    numerical designation of a control enhancement is used only to
    identify the particular enhancement within the control. The
    designation is not indicative of either the strength of the
    control enhancement or any hierarchical relationship among the
    enhancements. Control enhancements are not intended to be
    selected independently (i.e., if a control enhancement is selected,
    then the corresponding base security control must also be
    selected). This intent is reflected in the baseline specifications
    in Appendix D and in the baseline allocation section under each
    control in Appendix F.
    """
    enhancement_id = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    control = models.ForeignKey(Control)
    supplemental_guidance = models.TextField()
    related_controls = models.ManyToManyField(Control,
                                              related_name='related_controls+',
                                              null=True,blank=True)

    def __unicode__(self):
        return '%s(%s) %s' % (self.control, self.enhancement_id, self.title)

class OverlayControlSupplement(models.Model):
    """Supplemental information for controls in overlays"""
    supplemental_text = models.TextField()
    overlay = models.ForeignKey(Overlay)
    control = models.ForeignKey(Control)

class ImplementationText(models.Model):
    """Implementation details for a control

    This class is configured this way to support querying through django.
    This class won't be viewable directly and instead is just a deduplication
    technique.

    TODO:
    When using this class, figure out a way to break the link across multiple
    controls.
    """
    implementation = models.TextField()
    controls = models.ManyToManyField(Control, null=True, blank=True)
    control_enhancements = models.ManyToManyField(ControlEnhancement,
                                                 null=True, blank=True)
    def __unicode__(self):
        if self.controls.count() == 1:
            return '%s implementation' % (self.controls.all()[0])
        if self.control_enhancements.count() == 1:
            return '%s implementation' % (self.control_enhancements.all()[0])
        if self.controls.count() > 1 or self.control_enhancements.count() > 1:
            return 'Multiple controls met by this implementation'
        return 'No controls met'

#    def clean(self):
#        if self.control or self.control_enhancement:
#            return
#        # Require at least one control or control enhancement
#        if not self.control and not self.control_enhancement:
#            raise ValidationError('Implementations must be associated with a control')

class Product(models.Model):
    """Collection of implementations

    This class represents a product which must be assessed under the NIST
    800-53.  The product will have implementation details for each control
    that is selected.
    """
    implementations = models.ManyToManyField(ImplementationText, null=True,
                                             blank=True)
    overlays = models.ManyToManyField(Overlay, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)