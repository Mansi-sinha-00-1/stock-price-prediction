from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import StockForm
from .utils import process_stock_data
import base64
 
def index(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker'].upper()
            period = form.cleaned_data['period']
            forecast_days = form.cleaned_data['forecast_days']
            chart_type = form.cleaned_data['chart_type']

            # Save to session for later use
            request.session['ticker'] = ticker
            request.session['period'] = period
            request.session['forecast_days'] = forecast_days
            request.session['chart_type'] = chart_type

            return redirect('stock_app:results')
    else:
        form = StockForm()

    return render(request, 'stock_app/index.html', {'form': form})


def results(request):
    # Check required session data
    required_keys = ['ticker', 'period', 'forecast_days', 'chart_type']
    if not all(k in request.session for k in required_keys):
        return redirect('index')

    ticker = request.session['ticker']
    period = request.session['period']
    forecast_days = request.session['forecast_days']
    chart_type = request.session['chart_type']

    # ✅ FIXED: UNPACK 4 VALUES
    df, _, chart, error = process_stock_data(ticker, period, forecast_days, chart_type)

    if error:
        return render(request, 'stock_app/results.html', {
            'error': error,
            'ticker': ticker
        })

    # Save CSV to session for download
    csv_data = df.to_csv(index=True)
    request.session['csv_data'] = csv_data

    context = {
        'ticker': ticker,
        'period': period,
        'forecast_days': forecast_days,
        'chart_type': chart_type,
        'chart': chart,
        'csv_data': csv_data,
        'has_data': not df.empty,
    }

    return render(request, 'stock_app/results.html', context)


def download_csv(request):
    csv_data = request.session.get('csv_data')
    ticker = request.session.get('ticker', 'stock_data')

    if not csv_data:
        return redirect('index')

    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{ticker}_data.csv"'
    return response


def download_chart(request):
    # Ensure session has the same keys
    required_keys = ['ticker', 'period', 'forecast_days']
    if not all(k in request.session for k in required_keys):
        return redirect('index')

    ticker = request.session['ticker']
    period = request.session['period']
    forecast_days = request.session['forecast_days']

    # Always use Matplotlib for download (more stable for binary files)
    df, _, chart_base64, error = process_stock_data(ticker, period, forecast_days, chart_type='matplotlib')

    if error or df is None:
        return redirect('index')

    # Decode base64 to bytes
    chart_bytes = base64.b64decode(chart_base64)

    response = HttpResponse(chart_bytes, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{ticker}_chart.png"'
    return response
