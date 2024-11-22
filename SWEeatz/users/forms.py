from django import forms
from .models import Student, Reward

class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        exclude = ['user']
        fields = '__all__'
        labels = {
            'student_id':'Student ID',
            'name': 'Name',
            'school': 'School',
            'graduation_year': 'Graduation Year',
            'major': 'Primary Major',
            'major2': 'Second Major (If Applicable)',
            'profile_picture': 'Profile Picture',
        }

        widgets = {
            'student_id': forms.NumberInput(
                attrs= {'placeholder': 'e.g 1234567', 'class':'form-control'}),
            'name': forms.TextInput(
                attrs={'placeholder': 'e.g. Baldwin', 'class': 'form-control'}),
            'school': forms.Select(
                attrs={'placeholder': 'e.g Boston College', 'class': 'form-control'}),
            'graduation_year': forms.Select(
                attrs={'class': 'form-control'}),
            'major': forms.Select(
                attrs={'class': 'form-control'}),
            'major2': forms.Select(
                attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(
                attrs={'class': 'form-control'}),

        }

class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ['title', 'description', 'points_required', 'available_from', 'available_until']