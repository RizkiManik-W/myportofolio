from django.core.exceptions import ValidationError
from django.forms import ModelForm, NumberInput, TextInput, Textarea, URLInput
from django.utils.html import strip_tags

from main.models import Experience, Skill, Project

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

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "tech_stack", "project_url", "project_image_url"]
        labels = {
            "title": "Project title",
            "tech_stack": "Technologies used",
            "project_url": "Project URL",
            "project_image_url": "Image URL",
        }
        widgets = {
            "title": TextInput(
                attrs={"placeholder": "Portfolio Website"}
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Describe what your project does",
                    "rows": 4,
                }
            ),
            "tech_stack": TextInput(
                attrs={"placeholder": "Django, Python, JavaScript"}
            ),
            "project_url": URLInput(
                attrs={"placeholder": "https://github.com/username/project"}
            ),
            "project_image_url": URLInput(
                attrs={"placeholder": "https://example.com/project.png"}
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