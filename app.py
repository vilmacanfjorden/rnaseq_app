from flask import Flask, render_template, request, send_file
from models import db, GeneExpression
import pandas as pd
import plotly.express as px
import plotly.io as pio
import io

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def get_data(gene_name=None):
    with app.app_context():
        if gene_name:
            data = GeneExpression.query.filter_by(gene=gene_name).all()
        else:
            data = GeneExpression.query.all()

        df = pd.DataFrame([(d.gene, d.sample, d.expression_value) for d in data],
                          columns=['gene', 'sample', 'expression_value'])
        return df

def create_plot(df, color_queries):
    gene = ''.join(df["gene"].unique())
    color_map = {query: color for query, color in color_queries.items()}
    default_color = 'grey'

    def get_color(sample_name):
        for query, color in color_map.items():
            if query in sample_name:
                return color
        return default_color

    df['color'] = df['sample'].apply(get_color)
    sample_order = df['sample'].unique().tolist()
    df['sample'] = pd.Categorical(df['sample'], categories=sample_order, ordered=True)

    fig = px.bar(df, x='sample', y='expression_value',
                 title=f'Gene Expression Values in {gene}',
                 labels={'sample': 'Sample', 'expression_value': 'Expression Value'},
                 color='color',
                 color_discrete_map={color: color for color in df['color'].unique()})

    fig.update_layout(
        xaxis_title='Sample',
        yaxis_title='Expression Value',
        xaxis_tickangle=-45,
        xaxis_categoryorder='array',
        xaxis_categoryarray=sample_order,
        font=dict(family="Calibri, sans-serif"),
        title_font=dict(size=24),
        title={'x':0.14,'y':0.93},
        width= 1200,
        height=800
    )

    color_to_query = {v: k for k, v in color_map.items()}
    for trace in fig.data:
        if hasattr(trace, 'marker') and hasattr(trace.marker, 'color'):
            color = trace.marker.color
            query = color_to_query.get(color, color)
            trace.name = query

    fig.update_layout(
        legend=dict(
            title='Gene Queries',
            x=1,
            y=1,
            traceorder='normal')
    )

    plot_html = pio.to_html(fig, full_html=False)
    return fig, plot_html

@app.route('/', methods=['GET', 'POST'])
def index():
    gene_info = None
    plot_html = None
    color_queries = []
    gene_name = request.form.get('gene_name', '')

    if request.method == 'POST':
        color_queries = []
        for key in request.form:
            if key.startswith('query_'):
                index = key.split('_')[1]
                query = request.form.get(f'query_{index}')
                color = request.form.get(f'color_{index}')
                if query and color:
                    color_queries.append({'index': index, 'query': query, 'color': color})

        color_queries_dict = {q['query']: q['color'] for q in color_queries}

        if gene_name:
            gene_info = GeneExpression.query.filter_by(gene=gene_name).all()
            df = get_data(gene_name)
            fig, plot_html = create_plot(df, color_queries_dict)

    return render_template('index.html', gene_info=gene_info, plot_html=plot_html, color_queries=color_queries, gene_name=gene_name)

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    gene_name = request.form.get('gene_name', '')
    color_queries = []
    for key in request.form:
        if key.startswith('query_'):
            index = key.split('_')[1]
            query = request.form.get(f'query_{index}')
            color = request.form.get(f'color_{index}')
            if query and color:
                color_queries.append({'index': index, 'query': query, 'color': color})

    color_queries_dict = {q['query']: q['color'] for q in color_queries}

    df = get_data(gene_name)
    fig, _ = create_plot(df, color_queries_dict)

    # Convert the plot to a PDF file
    pdf_buffer = io.BytesIO()
    fig.write_image(pdf_buffer, format='pdf')
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, mimetype='application/pdf', download_name=f'{gene_name}_gene_expression_plot.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
