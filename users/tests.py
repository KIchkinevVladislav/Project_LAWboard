from django.test import TestCase, Client
from django.urls import reverse

class TestProfileUserCreate(TestCase):
    
    #Проверка создания страницы пользователя при его регистрации
    
    def test_profile(self):
        
        self.client.post(reverse('signup'),
                         {'username': 'test_profile',
                          'email': 'testmail@gmail.com',
                          'password1': 'password_test',
                          'password2': 'password_test'}
                         )
        response = self.client.get(
            reverse ('profile', kwargs={'username': 'test_profile'}))
        self.assertEqual(response.status_code, 200)

       


      
