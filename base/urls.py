from django.urls import path
from . import views

urlpatterns = [

    #ex: homepage
    path('', views.home, name = 'home'),

    #ex: room
    path('room/<int:pk>/', views.room, name='room'),

    #ex: registerpage
    path('sign-up/', views.registerPage, name='registerpage'),

    #ex: loginpage
    path('sign-in/', views.loginPage, name='loginpage'),

    #ex: logout
    path('sign-out/', views.logoutPage, name='logoutpage'),

    #CRUD OPERTIONS ROOM
    #ex: create-room
    path('create-room/', views.createRoom, name='create-room'),
    #ex: update-room
    path('update-room/<int:pk>/', views.updateRoom, name="update-room"),
    #ex: delete-room
    path('delete-room/<int:pk>/', views.deleteRoom, name = "delete-room"),


    #CRUD OPERATIONS MESSAGE
    path('create-message/<int:pk>/', views.createMessage, name='create-message'),
    path('delete-message/<int:pk>/', views.deleteMessage, name= 'delete-message'),
    path('update-message/<int:pk>/', views.editMessage, name = 'edit-message'),

    #ACTIVATE ACCOUNT
    path('activate/<uid64>/<token>/', views.activateAccount, name='activate' )

]