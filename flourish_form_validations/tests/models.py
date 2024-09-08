from django.db import models
from django.db.models.deletion import PROTECT
from django_crypto_fields.fields import IdentityField
from edc_base.model_mixins import BaseUuidModel, ListModelMixin
from edc_base.utils import get_utcnow
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin


class ListModel(ListModelMixin, BaseUuidModel):
    pass


class CaregiverLocator(BaseUuidModel):
    subject_identifier = models.CharField(max_length=50)

    screening_identifier = models.CharField(max_length=50)

    report_datetime = models.DateTimeField(
        null=True,
        blank=True)

    may_call = models.CharField(
        max_length=3)

    may_visit_home = models.CharField(
        max_length=3)


class SubjectConsent(UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    gender = models.CharField(max_length=25)

    is_literate = models.CharField(max_length=25,
                                   blank=True,
                                   null=True)

    witness_name = models.CharField(max_length=25,
                                    blank=True,
                                    null=True)

    dob = models.DateField()

    first_name = models.CharField(max_length=25, blank=True, null=True)

    last_name = models.CharField(max_length=25, blank=True, null=True)

    initials = models.CharField(max_length=25, blank=True, null=True)

    is_dob_estimated = models.CharField(max_length=50, blank=True, null=True)

    citizen = models.CharField(max_length=25, blank=True, null=True)

    identity = models.CharField(max_length=25, blank=True, null=True)

    confirm_identity = models.CharField(max_length=25, blank=True, null=True)

    consent_datetime = models.DateTimeField()

    version = models.CharField(
        max_length=10,
        editable=False)


class TbAdolConsent(BaseUuidModel):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    initials = models.CharField(max_length=50, blank=True, null=True)
    is_literate = models.CharField(max_length=50, blank=True, null=True)
    dob = models.CharField(max_length=50, blank=True, null=True)
    is_dob_estimated = models.CharField(max_length=50, blank=True, null=True)
    citizen = models.CharField(max_length=50, blank=True, null=True)
    identity = models.CharField(max_length=50, blank=True, null=True)
    confirm_identity = models.CharField(max_length=50, blank=True, null=True)


class ScreeningPregWomen(UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):
    screening_identifier = models.CharField(max_length=50)

    mother_alive = models.CharField(max_length=50)


class MaternalDelivery(UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)


class AntenatalEnrollment(BaseUuidModel):
    subject_identifier = models.CharField(max_length=50)

    report_datetime = models.DateTimeField(
        null=True,
        blank=True)

    last_period_date = models.DateField(
        null=True,
        blank=True)

    current_hiv_status = models.CharField(
        max_length=15,
        null=True,
        blank=True)

    week32_test = models.CharField(
        max_length=15,
        null=True,
        blank=True)

    week32_test_date = models.DateField(
        null=True,
        blank=True)

    enrollment_hiv_status = models.CharField(
        max_length=15,
        null=True,
        blank=True)

    evidence_hiv_status = models.CharField(
        max_length=15,
        null=True,
        blank=True)

    week32_result = models.CharField(
        max_length=15,
        null=True,
        blank=True)

    rapid_test_done = models.CharField(
        max_length=15,
        null=True,
        blank=True)

    rapid_test_result = models.CharField(
        max_length=15,
        null=True,
        blank=True)

    rapid_test_date = models.DateField(
        null=True,
        blank=True)


class OnSchedule(BaseUuidModel):
    subject_identifier = models.CharField(
        max_length=50)
    schedule_name = models.CharField(max_length=25, blank=True, null=True)

    child_subject_identifier = models.CharField(
        max_length=50)


class Schedule(BaseUuidModel):
    subject_identifier = models.CharField(
        max_length=50)

    child_subject_identifier = models.CharField(
        max_length=50, blank=True, null=True)

    schedule_name = models.CharField(max_length=25, blank=True, null=True)

    onschedule_model = models.CharField(max_length=25, blank=True, null=True)


class Appointment(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    appt_datetime = models.DateTimeField(default=get_utcnow)

    visit_code = models.CharField(max_length=25)

    visit_code_sequence = models.IntegerField(default=0)

    visit_instance = models.CharField(max_length=25)

    visit_schedule_name = models.CharField(max_length=25)

    @classmethod
    def related_visit_model_attr(cls):
        return 'maternalvisit'


class MaternalVisit(BaseUuidModel):
    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25)

    visit_code = models.CharField(max_length=25)

    visit_code_sequence = models.IntegerField(default=0)

    schedule_name = models.CharField(max_length=25, null=True)

    schedule = models.ForeignKey(Schedule, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        default=get_utcnow)

    def save(self, *args, **kwargs):
        self.visit_code = self.appointment.visit_code
        self.subject_identifier = self.appointment.subject_identifier
        super().save(*args, **kwargs)


class MaternalArvDuringPreg(models.Model):
    took_arv = models.CharField(
        choices=YES_NO,
        max_length=10)

    maternal_visit = models.OneToOneField(MaternalVisit, on_delete=PROTECT)

    art_start_date = models.DateField(
        null=True,
        blank=False)


class MaternalArv(models.Model):
    maternal_arv_durg_preg = models.ForeignKey(MaternalArvDuringPreg, on_delete=PROTECT)

    arv_code = models.CharField(
        verbose_name="ARV code",
        max_length=35)

    start_date = models.DateField(
        null=True,
        blank=False)

    stop_date = models.DateField(
        null=True,
        blank=True)


class BirthFeedingVaccine(models.Model):
    child_visit = models.OneToOneField(MaternalVisit, on_delete=PROTECT)
    report_datetime = models.DateTimeField(
        default=get_utcnow)
    breastfeed_start_dt = models.DateField(
        null=True,
        blank=True)


class ArvsPrePregnancy(models.Model):
    maternal_visit = models.ForeignKey(MaternalVisit, on_delete=PROTECT)

    preg_on_art = models.CharField(max_length=25, choices=YES_NO_NA)

    art_start_date = models.DateField(
        blank=True,
        null=True)


class RegisteredSubject(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    relative_identifier = models.CharField(
        max_length=36,
        null=True,
        blank=True)


class UltraSound(models.Model):
    maternal_visit = models.OneToOneField(MaternalVisit, on_delete=PROTECT)

    ga_confirmed = models.IntegerField()


class MaternalDataset(BaseUuidModel):
    screening_identifier = models.CharField(max_length=36)

    study_child_identifier = models.CharField(max_length=36)

    study_maternal_identifier = models.CharField(max_length=36)

    delivdt = models.DateField()


class ChildDataset(BaseUuidModel):
    study_child_identifier = models.CharField(max_length=36)

    dob = models.DateField(
        null=True,
        blank=True)

    infant_sex = models.CharField(max_length=7)


class FlourishConsentVersion(models.Model):
    screening_identifier = models.CharField(max_length=25)

    version = models.CharField(max_length=3)

    report_datetime = models.DateTimeField(
        null=True,
        blank=True)


class OffStudy(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)


class CaregiverContact(BaseUuidModel):
    consent_model = SubjectConsent

    report_datetime = models.DateField(
        null=True,
        blank=True)

    contact_type = models.CharField(max_length=7)

    contact_datetime = models.DateField(
        null=True,
        blank=True)

    call_reason = models.CharField(max_length=7)

    call_reason_other = models.CharField(max_length=7)

    contact_success = models.CharField(max_length=7)

    contact_comment = models.CharField(max_length=7)

    call_rescheduled = models.CharField(max_length=7)

    reason_rescheduled = models.CharField(max_length=7)


class ScreeningPriorBhpParticipants(BaseUuidModel):
    screening_identifier = models.CharField(max_length=7)

    report_datetime = models.DateTimeField()

    study_maternal_identifier = models.CharField(max_length=7)

    child_alive = models.CharField(max_length=7)

    mother_alive = models.CharField(max_length=7)

    flourish_participation = models.CharField(max_length=7)

    reason_not_to_participate = models.CharField(max_length=7)

    ineligibility = models.TextField(
        max_length=150, )

    is_eligible = models.BooleanField(
        default=False,
        editable=False)

    # is updated via signal once subject is consented
    is_consented = models.BooleanField(
        default=False,
        editable=False)


class CaregiverChildConsent(BaseUuidModel):
    subject_consent = models.ForeignKey(
        SubjectConsent,
        on_delete=models.PROTECT)

    subject_identifier = models.CharField(max_length=25)

    child_dob = models.DateField(null=True)

    preg_enroll = models.BooleanField(null=True)

    consent_datetime = models.DateTimeField()


class CaregiverOnSchedule(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    schedule_name = models.CharField(max_length=25)

    child_subject_identifier = models.CharField(max_length=25)


class ReceivedTrainingOnFeedingList(ListModelMixin, BaseUuidModel):
    pass


class ChildAssent(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    consent_datetime = models.DateTimeField()

    dob = models.DateField()

    identity = IdentityField(
        verbose_name='Identity number',
        null=True, blank=True)

    version = models.CharField(
        max_length=10,
        editable=False)


class MestitisActions(ListModelMixin, BaseUuidModel):
    pass
