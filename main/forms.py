from django.core.exceptions import ValidationError
from django.forms import ModelForm, NumberInput, TextInput, Textarea
from django.utils.html import strip_tags

from main.models import Experience, Skill


class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = [
            "title",
            "description",
            "category",
            "proficiency",
            "order",
        ]
        labels = {
            "title": "Skill name",
            "description": "Description",
            "category": "Category",
            "proficiency": "Proficiency",
            "order": "Display order",
        }
        widgets = {
            "title": TextInput(
                attrs={"placeholder": "Python"}
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Describe this skill",
                    "rows": 4,
                }
            ),
            "proficiency": TextInput(
                attrs={"placeholder": "Advanced"}
            ),
            "order": NumberInput(
                attrs={"min": 1}
            ),
        }


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
        ]
        labels = {
            "title": "Experience title",
            "description": "Description",
            "category": "Category",
            "thumbnail": "Thumbnail URL",
        }
        widgets = {
            "title": TextInput(
                attrs={"placeholder": "Assistant Lecturer"}
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Describe your responsibilities",
                    "rows": 4,
                }
            ),
            "thumbnail": TextInput(
                attrs={"placeholder": "https://example.com/image.jpg"}
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Enter a title without HTML tags.")
        return title

    def clean_description(self):
        description = strip_tags(self.cleaned_data["description"]).strip()
        if not description:
            raise ValidationError("Enter a description without HTML tags.")
        return description
