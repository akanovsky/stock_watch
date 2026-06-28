from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User


class Ticker(models.Model):
    """Stores ticker symbols entered by users."""
    symbol = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol


class StockData(models.Model):
    """Cached stock data with OHLCV prices."""
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name='data')
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        ordering = ['-date']
        unique_together = ['ticker', 'date']

    def __str__(self):
        return f"{self.ticker.symbol} - {self.date}"


class Favorite(models.Model):
    """Stores favorite tickers for quick access."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', null=True, blank=True)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'ticker']

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.ticker.symbol}"
        return f"Anonymous - {self.ticker.symbol}"


class Portfolio(models.Model):
    """User portfolio for grouping stock holdings."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @property
    def total_value(self):
        """Calculate total current value of all holdings."""
        return sum(item.current_value for item in self.items.all())

    @property
    def total_invested(self):
        """Calculate total amount invested."""
        return sum(item.total_cost for item in self.items.all())

    @property
    def total_profit_loss(self):
        """Calculate total profit/loss."""
        return self.total_value - self.total_invested


class PortfolioItem(models.Model):
    """Individual stock holding within a portfolio."""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='items')
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['portfolio', 'ticker']

    def __str__(self):
        return f"{self.portfolio.name} - {self.ticker.symbol}"

    @property
    def total_cost(self):
        """Total purchase cost."""
        return self.quantity * self.purchase_price

    @property
    def current_price(self):
        """Get current market price."""
        try:
            from .services.yfinance_service import get_current_low_high
            data = get_current_low_high(self.ticker.symbol)
            return data.get('close', self.purchase_price)
        except Exception:
            return self.purchase_price

    @property
    def current_value(self):
        """Current market value of holding."""
        price = self.current_price
        if isinstance(price, float):
            price = Decimal(str(price))
        return self.quantity * price

    @property
    def profit_loss(self):
        """Profit/loss on this holding."""
        return self.current_value - self.total_cost
