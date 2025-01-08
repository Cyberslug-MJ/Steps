from . import views 
from django.urls import path 

urlpatterns = [
    path('api/register',views.register,name='register'),
    path('api/login',views.login,name='login'),
    path('api/logout',views.logout,name='logout'),
    path('api/refresh',views.CookieTokenRefreshView.as_view(),name='refresh'),
    path('api/transactions',views.TransactionsList,name='transactions-list'),
    path('api/transactions/<int:pk>/',views.TransactionsDetail,name='transactions-detail'),
    path('api/verify-mail',views.VerifyMail,name='verify-mail'),
    path('api/create-tenant',views.create_tenant,name='create-tenant'),
    path('',views.home,name='home'),
]