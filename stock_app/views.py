from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import TickerForm, UserRegistrationForm, UserLoginForm, PortfolioForm, PortfolioItemForm
from .models import Ticker, Favorite, Portfolio, PortfolioItem
from .services.indicators import analyze_stock
from .services.yfinance_service import get_current_low_high, get_full_monthly_history


class HomeView(View):
    """Home page with ticker input form and favorites list."""

    def _get_favorites(self, request, with_analysis=False):
        """Fetch favorites for the user, optionally with technical analysis."""
        favorites = []
        if request.user.is_authenticated:
            favorite_qs = Favorite.objects.select_related('ticker').filter(user=request.user)
            for fav in favorite_qs:
                analysis = None
                if with_analysis:
                    try:
                        analysis = analyze_stock(fav.ticker.symbol)
                    except Exception:
                        analysis = None
                favorites.append({
                    'favorite': fav,
                    'analysis': analysis,
                })
        return favorites

    def get(self, request):
        form = TickerForm()
        favorites = self._get_favorites(request, with_analysis=False)
        return render(request, 'stock_app/home.html', {
            'form': form,
            'favorites': favorites,
            'show_refresh': True,
            'user': request.user
        })

    def post(self, request):
        # Refresh favorites analysis
        if request.POST.get('refresh_favorites'):
            favorites = self._get_favorites(request, with_analysis=True)
            return render(request, 'stock_app/home.html', {
                'form': TickerForm(),
                'favorites': favorites,
                'show_refresh': True,
                'user': request.user
            })

        form = TickerForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol'].upper()
            return redirect('stock_detail', ticker=symbol)
        favorites = self._get_favorites(request, with_analysis=False)
        return render(request, 'stock_app/home.html', {
            'form': form,
            'favorites': favorites,
            'show_refresh': True,
            'user': request.user
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

            # Check if this ticker is in current user's favorites
            if request.user.is_authenticated:
                try:
                    ticker_obj = Ticker.objects.get(symbol=ticker.upper())
                    is_favorite = Favorite.objects.filter(user=request.user, ticker=ticker_obj).exists()
                except Ticker.DoesNotExist:
                    is_favorite = False
            else:
                is_favorite = False

            # Prepare quick-add form for authenticated users
            add_form = None
            user_portfolios = []
            if request.user.is_authenticated:
                from .services.yfinance_service import get_current_low_high
                try:
                    current_data = get_current_low_high(ticker.upper())
                    last_price = current_data.get('close') or analysis.get('current_price')
                except Exception:
                    last_price = analysis.get('current_price')
                add_form = PortfolioItemForm(initial={
                    'symbol': ticker.upper(),
                    'purchase_price': last_price
                })
                user_portfolios = Portfolio.objects.filter(user=request.user)

            context = {
                'analysis': analysis,
                'history': history,  # Full month history, most recent first
                'is_favorite': is_favorite,
                'user': request.user,
                'add_form': add_form,
                'user_portfolios': user_portfolios
            }
            return render(request, 'stock_app/detail.html', context)
        except ValueError as e:
            form = TickerForm()
            error_message = str(e)
            if request.user.is_authenticated:
                favorites = Favorite.objects.select_related('ticker').filter(user=request.user)
            else:
                favorites = []
            return render(request, 'stock_app/home.html', {
                'form': form,
                'error': error_message,
                'favorites': favorites,
                'user': request.user
            })

    def post(self, request, ticker):
        """Handle quick-add stock to portfolio from detail page."""
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to manage portfolios.')
            return redirect('login')

        form = PortfolioItemForm(request.POST)
        portfolio_id = request.POST.get('portfolio')
        if form.is_valid() and portfolio_id:
            portfolio = get_object_or_404(Portfolio, pk=portfolio_id, user=request.user)
            symbol = form.cleaned_data['symbol'].upper()
            ticker_obj, _ = Ticker.objects.get_or_create(symbol=symbol)
            item, created = PortfolioItem.objects.get_or_create(
                portfolio=portfolio,
                ticker=ticker_obj,
                defaults={
                    'quantity': form.cleaned_data['quantity'],
                    'purchase_price': form.cleaned_data['purchase_price']
                }
            )
            if not created:
                item.quantity = form.cleaned_data['quantity']
                item.purchase_price = form.cleaned_data['purchase_price']
                item.save()
                messages.success(request, f'{symbol} updated in {portfolio.name}.')
            else:
                messages.success(request, f'{symbol} added to {portfolio.name}.')
        else:
            errors = form.errors.as_text() if not form.is_valid() else 'portfolio missing'
            messages.error(request, f'Please select a portfolio and enter valid quantity/price. {errors}')
        return redirect('stock_detail', ticker=ticker.upper())


@method_decorator(login_required, name='dispatch')
class AddFavoriteView(View):
    """Add a ticker to favorites."""

    def post(self, request, ticker):
        ticker_obj, created = Ticker.objects.get_or_create(symbol=ticker.upper())
        favorite, created = Favorite.objects.get_or_create(user=request.user, ticker=ticker_obj)
        
        if created:
            messages.success(request, f'{ticker.upper()} added to favorites.')
        else:
            messages.info(request, f'{ticker.upper()} is already in favorites.')
        
        return redirect('stock_detail', ticker=ticker.upper())


@method_decorator(login_required, name='dispatch')
class RemoveFavoriteView(View):
    """Remove a ticker from favorites."""

    def post(self, request, ticker):
        try:
            ticker_obj = Ticker.objects.get(symbol=ticker.upper())
            favorite = Favorite.objects.get(user=request.user, ticker=ticker_obj)
            favorite.delete()
            messages.success(request, f'{ticker.upper()} removed from favorites.')
        except (Ticker.DoesNotExist, Favorite.DoesNotExist):
            messages.warning(request, f'{ticker.upper()} was not found in favorites.')
        
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class ToggleFavoriteView(View):
    """AJAX endpoint to toggle favorite status."""

    def post(self, request, ticker):
        ticker_upper = ticker.upper()
        try:
            ticker_obj = Ticker.objects.get(symbol=ticker_upper)
            try:
                favorite = Favorite.objects.get(user=request.user, ticker=ticker_obj)
                favorite.delete()
                is_favorite = False
                message = f'{ticker_upper} removed from favorites.'
            except Favorite.DoesNotExist:
                Favorite.objects.create(user=request.user, ticker=ticker_obj)
                is_favorite = True
                message = f'{ticker_upper} added to favorites.'
        except Ticker.DoesNotExist:
            ticker_obj = Ticker.objects.create(symbol=ticker_upper)
            Favorite.objects.create(user=request.user, ticker=ticker_obj)
            is_favorite = True
            message = f'{ticker_upper} added to favorites.'

        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })


class RegisterView(View):
    """User registration view."""

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'stock_app/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}! You are now logged in.')
            return redirect('home')
        return render(request, 'stock_app/register.html', {'form': form})


class LoginView(View):
    """User login view."""

    def get(self, request):
        form = UserLoginForm()
        return render(request, 'stock_app/login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Logged in as {user.username}.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        return render(request, 'stock_app/login.html', {'form': form})


class LogoutView(View):
    """User logout view."""

    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class PortfolioListView(View):
    """List all portfolios for the current user."""

    def get(self, request):
        portfolios = Portfolio.objects.filter(user=request.user).prefetch_related('items__ticker')
        return render(request, 'stock_app/portfolio_list.html', {
            'portfolios': portfolios
        })


@method_decorator(login_required, name='dispatch')
class PortfolioCreateView(View):
    """Create a new portfolio."""

    def get(self, request):
        form = PortfolioForm()
        return render(request, 'stock_app/portfolio_form.html', {'form': form, 'action': 'Create'})

    def post(self, request):
        form = PortfolioForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Portfolio.objects.filter(user=request.user, name=name).exists():
                form.add_error('name', 'You already have a portfolio with this name.')
            else:
                Portfolio.objects.create(
                    user=request.user,
                    name=name,
                    description=form.cleaned_data['description']
                )
                messages.success(request, f'Portfolio "{name}" created.')
                return redirect('portfolio_list')
        return render(request, 'stock_app/portfolio_form.html', {'form': form, 'action': 'Create'})


@method_decorator(login_required, name='dispatch')
class PortfolioDetailView(View):
    """Show portfolio details and allow adding stocks."""

    def get(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        form = PortfolioItemForm()
        return render(request, 'stock_app/portfolio_detail.html', {
            'portfolio': portfolio,
            'form': form
        })

    def post(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        form = PortfolioItemForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol'].upper()
            ticker_obj, _ = Ticker.objects.get_or_create(symbol=symbol)
            item, created = PortfolioItem.objects.get_or_create(
                portfolio=portfolio,
                ticker=ticker_obj,
                defaults={
                    'quantity': form.cleaned_data['quantity'],
                    'purchase_price': form.cleaned_data['purchase_price']
                }
            )
            if not created:
                item.quantity = form.cleaned_data['quantity']
                item.purchase_price = form.cleaned_data['purchase_price']
                item.save()
                messages.success(request, f'{symbol} updated in portfolio.')
            else:
                messages.success(request, f'{symbol} added to portfolio.')
            return redirect('portfolio_detail', pk=pk)
        return render(request, 'stock_app/portfolio_detail.html', {
            'portfolio': portfolio,
            'form': form
        })


@method_decorator(login_required, name='dispatch')
class PortfolioDeleteView(View):
    """Delete a portfolio."""

    def post(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        name = portfolio.name
        portfolio.delete()
        messages.success(request, f'Portfolio "{name}" deleted.')
        return redirect('portfolio_list')


@method_decorator(login_required, name='dispatch')
class PortfolioUpdateView(View):
    """Edit portfolio name and description."""

    def get(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        form = PortfolioForm(initial={
            'name': portfolio.name,
            'description': portfolio.description
        })
        return render(request, 'stock_app/portfolio_form.html', {
            'form': form,
            'portfolio': portfolio,
            'action': 'Edit'
        })

    def post(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        form = PortfolioForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if name != portfolio.name and Portfolio.objects.filter(user=request.user, name=name).exists():
                form.add_error('name', 'You already have a portfolio with this name.')
            else:
                portfolio.name = name
                portfolio.description = form.cleaned_data['description']
                portfolio.save()
                messages.success(request, f'Portfolio "{name}" updated.')
                return redirect('portfolio_detail', pk=pk)
        return render(request, 'stock_app/portfolio_form.html', {
            'form': form,
            'portfolio': portfolio,
            'action': 'Edit'
        })


@method_decorator(login_required, name='dispatch')
class PortfolioItemDeleteView(View):
    """Remove a stock from a portfolio."""

    def post(self, request, pk, item_pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        item = get_object_or_404(PortfolioItem, pk=item_pk, portfolio=portfolio)
        symbol = item.ticker.symbol
        item.delete()
        messages.success(request, f'{symbol} removed from portfolio.')
        return redirect('portfolio_detail', pk=pk)
