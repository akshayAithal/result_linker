import datetime

from .db import db


class Process(db.Model):
    """Process table class definition."""
    # pylint: disable=no-member
    __tablename__ = "process"
    key = db.Column(db.String(255), primary_key=True)
    process = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    cancel_flag = db.Column(db.Integer)
    #total_mem = db.Column(db.Float)

    def __init__(self, key, process):
        self.key = key
        self.process = process
        self.timestamp = datetime.datetime.utcnow()
        self.cancel = 0
        #self.total_mem = 0.0

    def __repr__(self):
        """Raw representation."""
        return (
            "<Process(key='{}', "
            "process='{}', "
            "timestamp='{}'>").format(
                self.key, self.process, self.timestamp)


    @staticmethod
    def get_all_process_data():
        """Utility function to retrieve all sharings."""
        return Process.query.all()

    @staticmethod
    def get_process(key):
        """Utility function to retrieve the sharing for a specific issue id."""
        return Process.query.filter_by(key=key).first()

    @staticmethod
    def get_process_progress(key):
        """Utility function to retrieve the sharing for a specific issue id."""
        if not key or not len(key):
            return 0
        process = Process.query.filter_by(key=key).first()
        if process:
            return process.process
        else:
            return 0

    @staticmethod
    def set_process_progress(key, progress):
        """Utility function to share a url to a redmine issue number."""
        if not key or not len(key):
            return 
        process = Process.query.filter_by(key=key).first()
        if process:
            process.key = key
            process.process = progress
        else:
            process = Process(key=key, process=progress)
            db.session.add(process)
        db.session.commit()

    @staticmethod
    def is_process_valid(key):
        if not key or not len(key):
            return False
        process = Process.query.filter_by(key=key).first()
        if process:
            return True
        else:
            return False

    @staticmethod
    def delete_process(key):
        """To delete the process"""
        if not key or not len(key):
            return 
        process = Process.query.filter_by(key=key).first()
        db.session.delete(process)
        db.session.commit()  

    @staticmethod
    def cancel_process(key):
        """To delete the process"""
        if not key or not len(key):
            return 
        process = Process.query.filter_by(key=key).first()
        process.cancel_flag = 1
        db.session.commit() 

    @staticmethod
    def check_for_cancel(key):
        """To delete the process"""
        if not key or not len(key):
            return 
        process = Process.query.filter_by(key=key).first()
        return process.cancel_flag

    #@staticmethod
    #def add_memory


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

async def clear_out_old_process():
    current_time = datetime.datetime.utcnow()
    processes = Process.query.all()
    for process in processes:
        difference =  process.timestamp - current_time
        #if process.process == 100:
        #    Process.delete_process(process.key)
        if difference.days > 2:
            Process.delete_process(process.key)
