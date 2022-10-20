from edc_form_validators import FormValidator
from .crf_form_validator import FormValidatorMixin


class TbKnowledgeFormValidator(FormValidatorMixin, FormValidator):

    def clean(self):

        self.m2m_other_specify(
            m2m_field='tb_knowledge_medium')
