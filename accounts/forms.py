from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter First Name','class':'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Enter Last Name','class':'form-control'}))
    phone_number = forms.CharField(widget=forms.NumberInput(attrs={'placeholder':'Enter Phone Number','class':'form-control'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder':'Enter Email','class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter Password','class':'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter Password','class':'form-control'}))
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            print('IAMHERE')
            raise forms.ValidationError(
                'Password Does Not Match!'
            )
        

    # #add class:form-control to all fields
    # def __init__(self,*args,**kwargs):
    #     super(RegistrationForm,self).__init__(*args,**kwargs)
    #     for field in self.fields:
    #         self.fields[field].widget.attrs['class']= 'form-control'