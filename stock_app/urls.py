from django.urls import path
from .views import HomeView, StockDetailView, AddFavoriteView, RemoveFavoriteView, ToggleFavoriteView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('stock/<str:ticker>/', StockDetailView.as_view(), name='stock_detail'),
    path('favorite/add/<str:ticker>/', AddFavoriteView.as_view(), name='add_favorite'),
    path('favorite/remove/<str:ticker>/', RemoveFavoriteView.as_view(), name='remove_favorite'),
    path('api/toggle-favorite/<str:ticker>/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
]
