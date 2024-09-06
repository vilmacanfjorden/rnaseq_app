import pandas as pd
from models import db, GeneExpression
from flask import Flask

def load_files(file_paths):
    # Create a Flask application instance
    app = Flask(__name__)

    # Configure the Flask app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    # Push an application context
    with app.app_context():
        for file_path in file_paths:
            # Read the file into a pandas DataFrame
            with app.app_context():
                df = pd.read_csv(file_path, sep='\t', header=0)

                # Iterate over the rows in the DataFrame
                for _, row in df.iterrows():
                    gene = row["gene"]

                    # Iterate over the columns (excluding the gene column)
                    for sample, value in row[1:].items():
                        # Create a new GeneExpression object
                        gene_expression = GeneExpression(
                            gene=gene,
                            sample=sample,
                            expression_value=value
                        )
                        # Add the object to the session
                        db.session.add(gene_expression)

                # Commit the session to save the data
                db.session.commit()

if __name__ == "__main__":
    file_paths = [
        "231201_mls-402_normalized_counts.txt",
        "231201_mls-avory_normalized_counts.txt",
        "231202_mls-1765_normalized_counts.txt",
        "231204_ews-6647_normalized_counts.txt",
        "231204_ews-tc_normalized_counts.txt",
        "231204_ht1080-fd_normalized_counts.txt",
        "231204_ht1080-wt_normalized_counts.txt"
        # Add more file paths as needed
    ]
    load_files(file_paths)
