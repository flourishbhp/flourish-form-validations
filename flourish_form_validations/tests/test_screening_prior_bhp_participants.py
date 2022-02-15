from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_constants.constants import NO, OTHER, NOT_APPLICABLE, YES

from ..form_validators.screening_prior_bhp_participants_form_validator import \
    ScreeningPriorBhpParticipantsFormValidator


@tag('screening_prior')
class TestScreeningPriorBhpParticipantsForm(TestCase):

    def test_participation(self):
        """
        Raise an error if the mother is alive but the child is
        """

        cleaned_data = {
            'mother_alive': NO,
            'flourish_participation': None
        }

        form_validator = ScreeningPriorBhpParticipantsFormValidator(
            cleaned_data=cleaned_data
        )

        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_child_alive(self):
        """
        Raise an error if mother and florish participation is specified but the child is no longer alive
        """

        cleaned_data = {
            'mother_alive': NOT_APPLICABLE,
            'child_alive': NO,
            'flourish_participation': NOT_APPLICABLE
        }

        form_validator = ScreeningPriorBhpParticipantsFormValidator(
            cleaned_data=cleaned_data
        )

        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('reasons')
    def test_reason_not_to_participate(self):
        """
        Raise an error if flourish participation is set to no and there is no reason provided
        """

        cleaned_data = {
            'flourish_participation': NO,
            'reason_not_to_participate': None,
        }

        form_validator = ScreeningPriorBhpParticipantsFormValidator(
            cleaned_data=cleaned_data
        )

        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('other_field')
    def test_reason_not_to_participate_other(self):
        """
        Raise an error if reason no to participate is set to other but the other field is
        empty
        """

        cleaned_data = {
            'reason_not_to_participate': OTHER,
            'reason_not_to_participate_other': 'Blah blah',
        }

        form_validator = ScreeningPriorBhpParticipantsFormValidator(
            cleaned_data=cleaned_data
        )

        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
