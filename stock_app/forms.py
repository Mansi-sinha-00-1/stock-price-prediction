from django import forms

class StockForm(forms.Form):
    TICKER_CHOICES = [
        ('AAPL', 'Apple'),
        ('MSFT', 'Microsoft'),
        ('GOOGL', 'Alphabet'),
        ('AMZN', 'Amazon'),
        ('META', 'Meta'), 
        ('TSLA', 'Tesla'),
        ('NVDA', 'NVIDIA'),
        ('JPM', 'JPMorgan Chase'),
        ('V', 'Visa'),
        ('WMT', 'Walmart'),
    ]
    
    PERIOD_CHOICES = [
        ('1mo', '1 Month'),
        ('3mo', '3 Months'),
        ('6mo', '6 Months'),
        ('1y', '1 Year'),
        ('2y', '2 Years'),
        ('5y', '5 Years'),
        ('10y', '10 Years'),
    ]
    
    CHART_TYPE_CHOICES = [
        ('plotly', 'Interactive (Plotly)'),
        ('matplotlib', 'Static (Matplotlib)'),
    ]
    
    ticker = forms.CharField(
        label='Stock Ticker',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. AAPL, MSFT, GOOGL'
        })
    )
    
    period = forms.ChoiceField(
        label='Data Period',
        choices=PERIOD_CHOICES,
        initial='1y',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    forecast_days = forms.IntegerField(
        label='Forecast Days',
        initial=30,
        min_value=1,
        max_value=365,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    chart_type = forms.ChoiceField(
        label='Chart Type',
        choices=CHART_TYPE_CHOICES,
        initial='plotly',
        widget=forms.Select(attrs={'class': 'form-select'})
    )