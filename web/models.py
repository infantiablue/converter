from datetime import datetime
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
# initalize DB instance
db = SQLAlchemy()


class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    admin = db.Column(db.Boolean())
    pwdhash = db.Column(db.String())
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    video = db.relationship('Video', backref='user', lazy=True)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_admin(self):
        return self.admin


class Oauth(db.Model, OAuthConsumerMixin):
    __tablename__ = 'oauth'
    __table_args__ = {'extend_existing': True}
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)


class Video(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey(User.id))
    video_id = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    @staticmethod
    def limit_history_videos(user_id, num=50):
        videos = Video.query.filter_by(
            user_id=user_id).order_by(Video.created_at.desc()).all()
        if len(videos) > num:
            db.session.delete(videos[-1])
            db.session.commit()
            return videos[-1].id
        else:
            return False
