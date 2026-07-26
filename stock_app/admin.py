from django.contrib import admin

from .models import Ticker, StockData, Favorite, Portfolio, PortfolioItem


@admin.register(Ticker)
class TickerAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'created_at')
    search_fields = ('symbol',)


@admin.register(StockData)
class StockDataAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'date', 'open_price', 'high', 'low', 'close', 'volume')
    list_filter = ('ticker', 'date')
    search_fields = ('ticker__symbol',)
    date_hierarchy = 'date'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'added_at')
    list_filter = ('user', 'ticker')
    search_fields = ('user__username', 'ticker__symbol')


class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 1
    autocomplete_fields = ('ticker',)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at')
    search_fields = ('user__username', 'name')
    inlines = (PortfolioItemInline,)


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'ticker', 'quantity', 'purchase_price', 'purchase_date')
    list_filter = ('portfolio', 'ticker')
    search_fields = ('portfolio__name', 'ticker__symbol')
    autocomplete_fields = ('portfolio', 'ticker')
