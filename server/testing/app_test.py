import flask

from app import app
from models import Article, User

app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'

class TestApp:
    '''Flask API in app.py'''

    def test_member_endpoints_require_login(self):
        '''returns a useful unauthorized response for both member endpoints.'''
        with app.test_client() as client:
            for path in ('/members_only_articles', '/members_only_articles/1'):
                response = client.get(path)
                assert response.status_code == 401
                assert response.get_json()['error']

    def test_login_session_and_logout(self):
        '''restores a logged-in user and rejects the session after logout.'''
        with app.test_client() as client:
            assert client.get('/check_session').status_code == 401

            user = User.query.first()
            response = client.post('/login', json={'username': user.username})
            assert response.status_code == 200
            assert response.get_json()['username'] == user.username
            assert client.get('/check_session').get_json()['id'] == user.id

            client.delete('/logout')
            assert client.get('/check_session').status_code == 401
    
    def test_can_only_access_member_only_while_logged_in(self):
        '''allows logged in users to access member-only article index at /members_only_articles.'''
        with app.test_client() as client:
            
            client.get('/clear')

            user = User.query.first()
            client.post('/login', json={
                'username': user.username
            })

            response = client.get('/members_only_articles')
            assert(response.status_code == 200)

            client.delete('/logout')

            response = client.get('/members_only_articles')
            assert(response.status_code == 401)

    def test_member_only_articles_shows_member_only_articles(self):
        '''only shows member-only articles at /members_only_articles.'''
        with app.test_client() as client:
            
            client.get('/clear')

            user = User.query.first()
            client.post('/login', json={
                'username': user.username
            })

            response_json = client.get('/members_only_articles').get_json()
            for article in response_json:
                assert article['is_member_only'] == True

    def test_can_only_access_member_only_article_while_logged_in(self):
        '''allows logged in users to access full member-only articles at /members_only_articles/<int:id>.'''
        with app.test_client() as client:
            
            client.get('/clear')

            user = User.query.first()
            client.post('/login', json={
                'username': user.username
            })

            article_id = Article.query.with_entities(Article.id).first()[0]

            response = client.get(f'/members_only_articles/{article_id}')
            assert(response.status_code == 200)

            client.delete('/logout')

            response = client.get(f'/members_only_articles/{article_id}')
            assert(response.status_code == 401)
