from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class GeneExpression(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gene = db.Column(db.String(100), nullable=False)
    sample = db.Column(db.String(100), nullable=False)
    expression_value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<GeneExpression {self.gene} {self.sample}>'
