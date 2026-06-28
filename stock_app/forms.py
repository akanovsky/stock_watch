from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class TickerForm(forms.Form):
    """Form for entering stock ticker symbol."""
    symbol = forms.CharField(
        max_length=10,
        required=True,
        label='Ticker Symbol',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., AAPL, MSFT, GOOGL',
            'autofocus': True
        })
    )


class UserRegistrationForm(UserCreationForm):
    """Form for user registration."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm Password'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })


class UserLoginForm(forms.Form):
    """Form for user login."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class PortfolioForm(forms.Form):
    """Form for creating or editing a portfolio."""
    name = forms.CharField(
        max_length=100,
        required=True,
        label='Portfolio Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., My Tech Stocks'
        })
    )
    description = forms.CharField(
        required=False,
        label='Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional description'
        })
    )


class PortfolioItemForm(forms.Form):
    """Form for adding a stock to a portfolio."""
    symbol = forms.CharField(
        max_length=10,
        required=True,
        label='Ticker Symbol',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., AAPL'
        })
    )
    quantity = forms.DecimalField(
        max_digits=15,
        decimal_places=4,
        min_value=0.0001,
        required=True,
        label='Quantity',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of shares',
            'step': '0.0001'
        })
    )
    purchase_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        required=True,
        label='Purchase Price',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Price per share',
            'step': '0.01'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove any inherited fields from other forms (e.g. password)
        for field_name in list(self.fields.keys()):
            if field_name not in ['symbol', 'quantity', 'purchase_price']:
                del self.fields[field_name]
