from string import punctuation

from wtforms import ValidationError


class SafeCharacters:
    def __init__(self, chars: set = None, message: str = None, field_name: str = "Field"):
        if not chars:
            chars = set(punctuation) - {".", "-", "_"}
        self.chars = chars
        if not message:
            message = f"{field_name} contains illegal characters."
        self.message = message

    def __call__(self, form, field):
        for char in field.data:
            if char in self.chars:
                raise ValidationError(self.message)
