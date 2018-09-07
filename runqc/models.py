from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from runqc import db

db = get_db()

class BaseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False,, default=datetime.now)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '{} ({})'.format(self.id, self.name)


class RunInfo(BaseModel):
    run_folder = db.Column(db.String(100), nullable=False)
    qc_folder = db.Column(db.String(200), nullable=False)
    gt_project = db.Column(db.String(50), nullable=False)
    seq_protocol = db.Column(db.String(25), nullable=False)
    sample_count = db.Column(db.Integer, nullable=False)
    fastq_count = db.Column(db.Integer, nullable=False)
    date_reported = db.Column(db.DateTime, nullable=False) # format recd: 2018/07/24 11:12:31
    qc_report_file = db.Column(db.String(100), nullable=False,
                                   default='{{gt_project}}_QCreport.csv')
    run_metrics_file = db.Column(db.String(100), nullable=False,
                                     default='Run_Metric_Summary_{{gt_project}}.csv')

    def __repr__(self):
        return '{} ({}), {} samples'.format(self.name, self.project, self.samples)


class RunQC(BaseModel):
    run_id = db.Column(db.Integer, db.ForeignKey('runinfo.id'), nullable=False)
    qc_report = db.Column(db.String(100), nullable=False,
                          db.ForeignKey('runinfo.qc_report_file'))
    read_count_xls = db.Column(db.String(100), nullable=False,
                               default="{{run_folder}}_Samples_Read_Count.xls")
    read_dist_img = db.Corumn(db.String(100), nullable=False,
                              default="{{run_folder}}_LANE-001_Read_Distributions.png")


class RunMetrics(BaseModel):
    run_id = db.Column(db.Integer, db.ForeignKey('runinfo.id'), nullable=False)
    metrics_filename = db.Column(db.String(100), nullable=False,
                                     db.ForeignKey('runinfo.run_metrics_file'))


class RunPipelineResults(BaseModel):
    run_id = db.Column(db.Integer, db.ForeignKey('runinfo.id'), nullable=False)
    # reads_lost_<process_1,2,...> = db.Column(db.Integer, nullable=True)

