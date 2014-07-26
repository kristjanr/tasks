import re

from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from django.forms.models import BaseInlineFormSet


class CustomInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CustomInlineFormSet, self).__init__(*args, **kwargs)
        self.regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def need_to_validate(self):
        return '_preview' in self.request.POST

    def clean(self):
        super(CustomInlineFormSet, self).clean()
        if self.need_to_validate():
            for form in self.forms:
                summary_pitch = form.cleaned_data['summary_pitch']
                validation_errors = []
                min_summary_length = 140
                if len(summary_pitch) < min_summary_length:
                    validation_errors.append(ValidationError("Summary pitch length needs to be at least %d characters. You have %d." % (min_summary_length, len(summary_pitch))))
                body = form.cleaned_data['body']
                min_body_length = 280
                if len(body) < min_body_length:
                    validation_errors.append(ValidationError("Body length needs to be at least %d characters. You have %d." % (min_body_length, len(body))))
                conclusion = form.cleaned_data['conclusion']
                min_conclusion_length = 140
                if len(conclusion) < min_conclusion_length:
                    validation_errors.append(ValidationError("Conclusion length needs to be at least %d characters. You have %d." % (min_conclusion_length, len(conclusion))))
                references = form.cleaned_data['references']
                if not self.regex.search(force_text(references)):
                    validation_errors.append(ValidationError("Reference needs to be a valid URL address."))
                video = form.cleaned_data['video']
                if not self.regex.search(force_text(video)):
                    validation_errors.append(ValidationError("Video needs to be a valid URL address."))
                raise ValidationError(validation_errors)
