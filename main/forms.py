from django.forms import ModelForm, NumberInput, TextInput, Textarea

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