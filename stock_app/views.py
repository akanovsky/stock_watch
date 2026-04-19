from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from .forms import TickerForm
from .models import Ticker, Favorite
from .services.indicators import analyze_stock
from .services.yfinance_service import get_current_low_high, get_full_monthly_history


class HomeView(View):
    """Home page with ticker input form and favorites list."""

    def get(self, request):
        form = TickerForm()
        # Get all favorites
        favorites = Favorite.objects.select_related('ticker').all()
        return render(request, 'stock_app/home.html', {
            'form': form,
            'favorites': favorites
        })

    def post(self, request):
        form = TickerForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol'].upper()
            return redirect('stock_detail', ticker=symbol)
        favorites = Favorite.objects.select_related('ticker').all()
        return render(request, 'stock_app/home.html', {
            'form': form,
            'favorites': favorites
        })


class StockDetailView(View):
    """Stock detail page with technical analysis."""

    def get(self, request, ticker):
        try:
            # Get analysis data
            analysis = analyze_stock(ticker)

            # Get full history for display (sorted by date descending - most recent first)
            history = get_full_monthly_history(ticker)
            history.reverse()  # Reverse to show most recent first in table

            # Check if this ticker is in favorites
            try:
                ticker_obj = Ticker.objects.get(symbol=ticker.upper())
                is_favorite = Favorite.objects.filter(ticker=ticker_obj).exists()
            except Ticker.DoesNotExist:
                is_favorite = False

            context = {
                'analysis': analysis,
                'history': history,  # Full month history, most recent first
                'is_favorite': is_favorite,
            }
            return render(request, 'stock_app/detail.html', context)
        except ValueError as e:
            form = TickerForm()
            error_message = str(e)
            favorites = Favorite.objects.select_related('ticker').all()
            return render(request, 'stock_app/home.html', {
                'form': form,
                'error': error_message,
                'favorites': favorites
            })


class AddFavoriteView(View):
    """Add a ticker to favorites."""

    def post(self, request, ticker):
        ticker_obj, created = Ticker.objects.get_or_create(symbol=ticker.upper())
        favorite, created = Favorite.objects.get_or_create(ticker=ticker_obj)
        
        if created:
            messages.success(request, f'{ticker.upper()} added to favorites.')
        else:
            messages.info(request, f'{ticker.upper()} is already in favorites.')
        
        return redirect('stock_detail', ticker=ticker.upper())


class RemoveFavoriteView(View):
    """Remove a ticker from favorites."""

    def post(self, request, ticker):
        try:
            ticker_obj = Ticker.objects.get(symbol=ticker.upper())
            favorite = Favorite.objects.get(ticker=ticker_obj)
            favorite.delete()
            messages.success(request, f'{ticker.upper()} removed from favorites.')
        except (Ticker.DoesNotExist, Favorite.DoesNotExist):
            messages.warning(request, f'{ticker.upper()} was not found in favorites.')
        
        return redirect('home')


class ToggleFavoriteView(View):
    """AJAX endpoint to toggle favorite status."""

    def post(self, request, ticker):
        ticker_upper = ticker.upper()
        try:
            ticker_obj = Ticker.objects.get(symbol=ticker_upper)
            try:
                favorite = Favorite.objects.get(ticker=ticker_obj)
                favorite.delete()
                is_favorite = False
                message = f'{ticker_upper} removed from favorites.'
            except Favorite.DoesNotExist:
                Favorite.objects.create(ticker=ticker_obj)
                is_favorite = True
                message = f'{ticker_upper} added to favorites.'
        except Ticker.DoesNotExist:
            ticker_obj = Ticker.objects.create(symbol=ticker_upper)
            Favorite.objects.create(ticker=ticker_obj)
            is_favorite = True
            message = f'{ticker_upper} added to favorites.'

        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })
