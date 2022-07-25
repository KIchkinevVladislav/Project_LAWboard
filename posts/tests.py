from urllib.parse import urljoin

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User, Follow, Comment


class PostPageTest(TestCase):

    def setUp(self):
        self.authorized_client = Client()
        self.unauthorized_client = Client()

        # create a test user
        self.user = User.objects.create_user(
            username='test_user',
            email='test@user.com',
            password='test_user_123456'
        )

        # create test group
        self.group = Group.objects.create(
            title='test group',
            slug='test_group',
            description='test description')

        # create authorized/unauthorized user
        self.authorized_client.force_login(self.user)
        self.unauthorized_client.logout()

        self.text = 'Text test!'
        self.edit = 'Changed text'

    def tearDown(self):
        User.objects.filter(
            username='test_user',
            email='test@user.com',
            password='test_user_123456'
        ).delete()
        Post.objects.filter(
            text='Test post',
            group=self.group,
            author=self.user
        ).delete()


    def check_post_content(self, url, user, group, text, new_text):
        """
        Checks post content, author and group name
        """
        self.authorized_client.get(url)
        self.assertEqual(user, self.user)
        self.assertEqual(group, self.group)
        self.assertEqual(text, self.text)
        self.assertEqual(new_text, self.edit)

    def urls(self):
        """
        Collects url of pages for testing
        """
        urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post',
                    kwargs={'username': self.user.username, 'post_id': 1}),
            reverse('group', kwargs={'slug': self.group.slug})]
        return urls

      
    def test_new_post_authorized_user(self):
        """
        Authorized user can new post.
        """
        response = self.authorized_client.get('new_post')
        self.assertEqual(response.status_code, 404)
        response = self.authorized_client.post(
            reverse('new_post'),
            data={'text': self.text, 'group': self.group.id},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), 1)
        self.check_post_content(
            'new', self.user, self.group, self.text, self.edit)

    def test_new_post_unauthorized_user(self):
        """
        An unauthorized visitor cannot post a post (redirects to the login page).
        """
        response = self.unauthorized_client.post(
            reverse('new_post'),
            data={'text': self.text, 'group': self.group.id},
            follow=True
        )
        # since it is impossible to add query parameters to reverse,
        # we will collect url
        url = urljoin(reverse('login'), '?next=/new/')
        self.assertRedirects(response, url)
        self.assertEqual(Post.objects.count(), 0)

    def test_new_post_location(self):
        """
        After the post is published, a new post appears on the main page
        of the site (index), on the user's personal page (profile),
        and on a separate post page (post).
        """    
        self.authorized_client.post(
            reverse('new_post'),
            data={'text': self.text, 'group': self.group.id},
            follow=True
        )

        for url in self.urls():
            with self.subTest(url=url):
                self.check_post_content(url, self.user, self.group, self.text, self.edit)

    def test_edit_post(self):
        """
        An authorized user can edit his post and its content will change on all linked pages.
        """
        post = Post.objects.create(text=self.text, group=self.group, author=self.user, )
        self.authorized_client.post(
                reverse('post_edit',
                        kwargs={'username': post.author,
                                'post_id': post.id}),
                data={'text': self.edit,
                    'group': post.group.id, }, follow=True)

        for url in self.urls():
            with self.subTest(url=url):
                self.check_post_content(url, self.user, self.group, self.text, self.edit)

    def test_error_404(self):
        """
        Check whether the server returns the 404 code if the page is not found.
        """
        response = self.authorized_client.get('/some_url/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')

    def test_image_on_page(self):
        """
        Checks that the image post is displayed correctly on the main page,
        profile page, group page, and post page.
        """                                  
        post = Post.objects.create(text='Post with image',
                                group=self.group,
                                author=self.user)
        
        with open ('media/posts/Capture001.png', 'rb') as img:
            response = self.authorized_client.post(
                reverse('post_edit',
                        kwargs={'username': self.user.username,
                                'post_id': post.id}),
                data={'text': 'Post with image',
                    'image': img}, follow=True)

        for url in self.urls():
            with self.subTest(url=url):
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<img')

    def test_non_image(self):
        """
        Check the protection against downloading files in non-graphic formats
        """
        with open('posts/urls.py') as file:
            response = self.authorized_client.post(
                reverse('new_post'), {'text': 'test_text', 'image': file}, follow=True)
            self.assertNotContains(response, 'test_id')

    def test_cache(self):
        """
        Checks whether the cache is working correctly.
        """
        with self.assertNumQueries(3):
            response = self.authorized_client.get(reverse('index'))
            self.assertEqual(response.status_code, 200)
            response = self.authorized_client.get(reverse('index'))
            self.assertEqual(response.status_code, 200)
    
    def test_check_follow_auth(self):
        """
        Checks whether an authorized user can subscribe to others.
        """
        follower = User.objects.create_user(username='follower', password='12345')
        self.authorized_client.post(reverse(
            'profile_follow', kwargs={'username': follower.username, }))
        follow = Follow.objects.first()
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(follow.author, follower)
        self.assertEqual(follow.user, self.user)

    def test_check_follow_non_unauth(self):
        """
        Checks whether an unauthorized user can't subscribe to others.
        """
        follower = User.objects.create_user(username='follower', password='12345')
        self.unauthorized_client.post(
            reverse('profile_follow',
                    kwargs={'username': follower.username}))
        self.assertEqual(follower.following.count(), 0)

    def test_auth_user_can_comment(self):
        """
        An authorized user can comment on posts.
        """

        self.author = User.objects.create(username='Wan', password='123456')
        self.post = Post.objects.create(text='Test post!', author=self.author)
        response = self.authorized_client.post(
            reverse('add_comment',
                    kwargs={'username': self.author,
                            'post_id': self.post.id}),
            data={'text': 'Test comment',
                  'author': self.user}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.comment = Comment.objects.last()
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.comment.text, 'Test comment')

    def test_non_auth_user_can_comment(self):
        """
        An unauthorized user can't comment on posts.
        """
        self.author = User.objects.create(username='Wan', password='123456')
        self.post = Post.objects.create(text='Test post!', author=self.user)
        response = self.unauthorized_client.post(
            reverse('add_comment',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}),
            data={'text': 'Test comment',
                  'author': self.user.id,
                  'post': self.post.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)