from django import forms

from .models import Server


class ServerForm(forms.ModelForm):

    class Meta:

        model = Server

        fields = [
            "name",
            "hostname",
            "ip_address",
            "operating_system",
            "ssh_username",
            "ssh_port",
            "pem_file",
            "application_name",
            "environment",
            "enabled",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Application Server 01"
                }
            ),

            "hostname": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "server01.company.com"
                }
            ),

            "ip_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "10.10.10.100"
                }
            ),

            "operating_system": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "ssh_username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ec2-user"
                }
            ),

            "ssh_port": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "application_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "My Application"
                }
            ),

            "environment": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "PROD"
                }
            ),

            "pem_file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }

class KPIExcelUploadForm(forms.Form):

    excel_file = forms.FileField(
        label="KPI Excel File",
        required=True
    )        