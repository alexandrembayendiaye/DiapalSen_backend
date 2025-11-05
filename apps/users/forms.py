from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

Utilisateur = get_user_model()


class UtilisateurCreationForm(forms.ModelForm):
    """
    Formulaire de création d'utilisateur compatible Django 5.
    """

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = Utilisateur
        fields = (
            "email",
            "first_name",
            "last_name",
            "date_de_naissance",
            "numero_telephone",
            "adresse",
            "ville",
            "type_utilisateur",
            "photo_profil",
        )

    def clean_password2(self):
        pwd1 = self.cleaned_data.get("password1")
        pwd2 = self.cleaned_data.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        return pwd2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UtilisateurChangeForm(forms.ModelForm):
    """
    Formulaire de modification d'utilisateur compatible Django 5.
    """

    class Meta:
        model = Utilisateur
        fields = (
            "email",
            "first_name",
            "last_name",
            "date_de_naissance",
            "numero_telephone",
            "adresse",
            "ville",
            "type_utilisateur",
            "photo_profil",
            "is_active",
            "is_staff",
            "is_superuser",
        )
