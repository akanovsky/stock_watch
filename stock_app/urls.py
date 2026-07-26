from django.urls import path
from .views import HomeView, StockDetailView, AddFavoriteView, RemoveFavoriteView, ToggleFavoriteView
from .views import RegisterView, LoginView, LogoutView
from .views import PortfolioListView, PortfolioCreateView, PortfolioDetailView
from .views import PortfolioUpdateView, PortfolioDeleteView, PortfolioItemDeleteView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('stock/<str:ticker>/', StockDetailView.as_view(), name='stock_detail'),
    path('favorite/add/<str:ticker>/', AddFavoriteView.as_view(), name='add_favorite'),
    path('favorite/remove/<str:ticker>/', RemoveFavoriteView.as_view(), name='remove_favorite'),
    path('api/toggle-favorite/<str:ticker>/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    # Authentication URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # Portfolio URLs
    path('portfolios/', PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolios/create/', PortfolioCreateView.as_view(), name='portfolio_create'),
    path('portfolios/<int:pk>/', PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('portfolios/<int:pk>/edit/', PortfolioUpdateView.as_view(), name='portfolio_edit'),
    path('portfolios/<int:pk>/delete/', PortfolioDeleteView.as_view(), name='portfolio_delete'),
    path('portfolios/<int:pk>/items/<int:item_pk>/delete/', PortfolioItemDeleteView.as_view(), name='portfolio_item_delete'),
]
