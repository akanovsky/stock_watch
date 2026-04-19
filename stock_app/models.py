from django.db import models


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
    ticker = models.OneToOneField(Ticker, on_delete=models.CASCADE, related_name='favorite')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker.symbol} (Favorite)"
