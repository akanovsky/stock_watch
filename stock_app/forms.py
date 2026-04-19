from django import forms


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
