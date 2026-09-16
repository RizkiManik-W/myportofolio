from django.forms import ModelForm, TextInput, Textarea, NumberInput

from main.models import Skill


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