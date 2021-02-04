import datetime

from .db import db


class Public(db.Model):
    """Public table class definition."""
    # pylint: disable=no-member
    __tablename__ = "public"
    issue = db.Column(db.Integer, primary_key=True)
    base_folder = db.Column(db.String(2048), nullable=False)
    public_folder = db.Column(db.String(2048), nullable=False)
    public_files = db.Column(db.String(2048), nullable=False)
    user = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, issue, base_folder, public_folder, public_files, user):
        self.issue = issue
        self.base_folder = base_folder
        self.public_folder = public_folder
        self.public_files = public_files
        self.user = user

    def __repr__(self):
        """Raw representation."""
        return (
            "<public(issue='{}', "
            "base_folder='{}', "
            "public_folder='{}', "
            "public_files='{}'>").format(
                self.issue, self.base_folder,
                self.public_folder, self.public_files)

    def get_dict(self):
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())

    def get_id(self):
        return self.issue

    @staticmethod
    def get_all_public_data():
        """Utility function to retrieve all sharings."""
        return Public.query.all()

    @staticmethod
    def get_public_data_for_issue(issue):
        """Utility function to retrieve the sharing for a specific issue id."""
        return Public.query.filter_by(issue=issue).first()

    @staticmethod
    def make_public(issue, base_link, public_folder, public_files, user):
        """Utility function to share a url to a redmine issue number."""
        public = Public.query.filter_by(issue=issue).first()
        if public:
            public.base_link = base_link
            public.public_folder = public_folder
            public.public_files = public_files
            public.timestamp = datetime.datetime.utcnow()
            public.user = user
        else:
            public = Public(issue=issue, base_folder=base_link, public_folder=public_folder, public_files=public_files, user=user)
            db.session.add(public)
        db.session.commit()
