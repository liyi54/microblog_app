from config import Config
from datetime import datetime, timedelta
from app import db, create_app
import unittest
from app.models import User, Post

class TestConfig(Config):
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hash(self):
        u = User(username='bailey', email='bailey@email.com')
        u.set_password('everything')
        self.assertFalse(u.check_password('power'))
        self.assertTrue(u.check_password('everything'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(60), 'https://gravatar.com/avatar/d4c74594d841139328695756648b6bd6?d=identicon&s=60')

    def test_follow(self):
        u1 = User(username='maya', email='maya@email.com')
        u2 = User(username='todd', email='todd@email.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'todd')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'maya')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_following_posts(self):
        u1 = User(username='todd', email='todd@email.com')
        u2 = User(username='maya', email='maya@email.com')
        u3 = User(username='bailey', email='bailey@email.com')
        u4 = User(username='john', email='john@email.com')
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.utcnow()
        p1 = Post(body="I love sweet things", author=u1, timestamp=now + timedelta(seconds=2))
        p2 = Post(body="My baby give me ginger", author=u2, timestamp=now + timedelta(seconds=4))
        p3 = Post(body="Need to go on a vacation", author=u3, timestamp=now + timedelta(seconds=3))
        p4 = Post(body="What is the state of COVID-19?", author=u4, timestamp=now + timedelta(seconds=5))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u3)
        u2.follow(u4)
        u2.follow(u3)
        u3.follow(u1)
        u4.follow(u3)
        u4.follow(u1)
        db.session.commit()

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()

        self.assertEqual(f1, [p3, p1])  # The list are to be ordered based on the most recent posts
        self.assertEqual(f2, [p4, p2, p3])
        self.assertEqual(f3, [p3, p1])
        self.assertEqual(f4, [p4, p3, p1])


if __name__ == '__main__':
    unittest.main(verbosity=2)

