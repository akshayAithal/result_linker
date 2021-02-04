import datetime

from .db import db

from result_linker.logger import logger

class Share(db.Model):
    """Shared table class definition."""
    # pylint: disable=no-member
    __tablename__ = "sharings"
    identifier = db.Column(db.String(30), primary_key=True)
    issue = db.Column(db.Integer, nullable=True)
    user = db.Column(db.String(500), nullable=True)
    root_folder = db.Column(db.String(2048), default="")
    shared_files = db.Column(db.String(2048), default="")
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expire_at = db.Column(db.DateTime)
    revision = db.Column(db.Integer, default=0)
    option = db.Column(db.String(50), default="public_same_revision")

    def __init__(self, issue,  user, shared_files, revision, option,root_folder="", expiry_day=None ):
        import random
        not_found = True
        import string
        id_ = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(30))
        while not_found:
            if Share.query.filter_by(identifier=id_).first():
                id_ = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(30))
            else:
                not_found = False
        self.user = user
        if issue == "":
            self.issue = 0
        else:
            self.issue = issue
        self.root_folder = root_folder
        self.identifier = id_
        if revision:
            self.revision = revision
        else:
            self.revision = None
        self.shared_files = shared_files
        if expiry_day:
            self.expire_at =  datetime.datetime.utcnow() + timedelta(days=int(expiry_day))
        else:
            self.expire_at = datetime.date(9999, 12, 4)
        self.option = option

    def __repr__(self):
        """Raw representation."""
        return (
            "<Shared(issue='{}', "
            "user='{}', "
            "timestamp='{}'>").format(
                self.issue, 
                self.user, self.timestamp)

    def get_dict(self):
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())

    def get_id(self):
        return self.identifier
    
    def set_selected_file(self, selected_file_list):
        selected_file_str="||".join(str(x) for x in selected_file_list)
        self.shared_files = selected_file_str
        db.session.commit()
    
    def get_selected_files(self):
        selected_file_str = self.shared_files
        selected_files = []
        if selected_file_str:
            selected_files = selected_file_str.split("||")
        return selected_files

    @staticmethod
    def get_all_shared_data():
        """Utility function to retrieve all sharings."""
        return Share.query.all()

    @staticmethod
    def get_shared_link_for(issue):
        """Utility function to retrieve the sharing for a specific issue id."""
        return Share.query.filter_by(issue=issue).first()

    @staticmethod
    def share(issue, user, shared_files, revision, option, root_folder, expiry_day=None):
        """Utility function to share a url to a redmine issue number."""
        shared = Share(issue, user, shared_files, revision, option, root_folder, expiry_day)
        id_ = shared.identifier
        db.session.add(shared)
        db.session.commit()
        return id_

    @staticmethod
    def check_valid_id(id_):
        """Utility function to retrieve the sharing for a specific issue id."""
        shareObj = Share.query.filter_by(identifier=id_).first()
        err_msg = ""
        now = datetime.datetime.utcnow()
        if shareObj:
            if shareObj.expire_at >= now:
                pass
            else:
                shareObj = None
                err_msg = "Link Expired"
        else:
            logger.error("No Object with that id")
            err_msg = "Incorrect Url"
        return shareObj, err_msg
