"""
Flask web application for Amazon Book Trends Analyzer
"""
from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

from analyzer import TrendAnalyzer
from scraper import AmazonScraper
from database import BookDatabase
from config import EXPORTS_DIR, AMAZON_CATEGORIES


app = Flask(__name__)
app.config['SECRET_KEY'] = 'amazon-book-trends-analyzer-secret-key'
app.json_encoder = PlotlyJSONEncoder

# Initialize components
analyzer = TrendAnalyzer()
scraper = AmazonScraper()
db = BookDatabase()


@app.route('/')
def index():
    """Home page - Dashboard"""
    return render_template('index.html')


@app.route('/trending')
def trending():
    """Trending categories page"""
    return render_template('trending.html')


@app.route('/category/<category_name>')
def category_detail(category_name):
    """Category detail page"""
    return render_template('category.html', category=category_name)


@app.route('/books')
def books():
    """Top books page"""
    return render_template('books.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


# API Endpoints

@app.route('/api/stats')
def api_stats():
    """Get overall statistics"""
    categories = db.get_all_categories()
    min_date, max_date = db.get_date_range()
    months = analyzer.get_available_months()

    # Get total book count
    monthly_data = db.get_monthly_snapshots()
    total_books = 0
    if not monthly_data.empty:
        total_books = monthly_data['book_count'].sum()

    return jsonify({
        'total_categories': len(categories),
        'total_books': int(total_books),
        'months_tracked': len(months),
        'date_range': {
            'start': min_date,
            'end': max_date
        },
        'categories': categories,
        'months': months
    })


@app.route('/api/trending')
def api_trending():
    """Get trending categories"""
    start_month = request.args.get('start_month')
    end_month = request.args.get('end_month')
    limit = int(request.args.get('limit', 20))

    # Use default months if not provided
    months = analyzer.get_available_months()
    if not start_month and len(months) >= 2:
        start_month = months[-1]
        end_month = months[0]

    if not start_month or not end_month:
        return jsonify({'error': 'No data available'}), 400

    trending = analyzer.get_trending_categories(start_month, end_month, min_books=1)

    if trending.empty:
        return jsonify({'data': [], 'start_month': start_month, 'end_month': end_month})

    # Convert to records
    trending_data = trending.head(limit).to_dict('records')

    return jsonify({
        'data': trending_data,
        'start_month': start_month,
        'end_month': end_month
    })


@app.route('/api/category/<category_name>/timeline')
def api_category_timeline(category_name):
    """Get category timeline data"""
    start_month = request.args.get('start_month')
    end_month = request.args.get('end_month')

    timeline = analyzer.get_category_timeline(category_name, start_month, end_month)

    if timeline.empty:
        return jsonify({'error': 'No data available'}), 404

    return jsonify({
        'data': timeline.to_dict('records')
    })


@app.route('/api/category/<category_name>/books')
def api_category_books(category_name):
    """Get top books in category"""
    month = request.args.get('month')
    limit = int(request.args.get('limit', 10))

    # Use latest month if not provided
    if not month:
        months = analyzer.get_available_months()
        if months:
            month = months[0]
        else:
            return jsonify({'error': 'No data available'}), 400

    books = analyzer.get_top_books_in_category(category_name, month, limit)

    if books.empty:
        return jsonify({'data': [], 'month': month})

    return jsonify({
        'data': books.to_dict('records'),
        'month': month
    })


@app.route('/api/category/<category_name>/growing')
def api_category_growing(category_name):
    """Get fastest growing books in category"""
    start_month = request.args.get('start_month')
    end_month = request.args.get('end_month')
    limit = int(request.args.get('limit', 10))

    # Use default months if not provided
    months = analyzer.get_available_months()
    if not start_month and len(months) >= 2:
        start_month = months[-1]
        end_month = months[0]

    if not start_month or not end_month:
        return jsonify({'error': 'No data available'}), 400

    growing = analyzer.get_fastest_growing_books(category_name, start_month, end_month, limit)

    if growing.empty:
        return jsonify({'data': [], 'start_month': start_month, 'end_month': end_month})

    return jsonify({
        'data': growing.to_dict('records'),
        'start_month': start_month,
        'end_month': end_month
    })


@app.route('/api/chart/trending')
def api_chart_trending():
    """Generate trending chart data"""
    start_month = request.args.get('start_month')
    end_month = request.args.get('end_month')

    # Use default months if not provided
    months = analyzer.get_available_months()
    if not start_month and len(months) >= 2:
        start_month = months[-1]
        end_month = months[0]

    trending = analyzer.get_trending_categories(start_month, end_month, min_books=1)

    if trending.empty:
        return jsonify({'data': []})

    # Top 10 for chart
    trending = trending.head(10)

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=trending['category'],
            y=trending['trend_score'] * 100,
            marker_color='rgb(55, 83, 109)',
            text=[f"{val:.1f}%" for val in trending['trend_score'] * 100],
            textposition='auto',
        )
    ])

    fig.update_layout(
        title='Top Trending Categories',
        xaxis_title='Category',
        yaxis_title='Trend Score (%)',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=100),
        xaxis={'tickangle': -45}
    )

    return jsonify(json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)))


@app.route('/api/chart/category/<category_name>/timeline')
def api_chart_category_timeline(category_name):
    """Generate category timeline chart"""
    start_month = request.args.get('start_month')
    end_month = request.args.get('end_month')

    timeline = analyzer.get_category_timeline(category_name, start_month, end_month)

    if timeline.empty:
        return jsonify({'error': 'No data available'}), 404

    # Create multi-line chart
    fig = go.Figure()

    # Book count
    fig.add_trace(go.Scatter(
        x=timeline['month'],
        y=timeline['book_count'],
        name='Book Count',
        mode='lines+markers',
        line=dict(color='rgb(55, 83, 109)', width=2),
        yaxis='y'
    ))

    # Average rank (inverted - lower is better)
    fig.add_trace(go.Scatter(
        x=timeline['month'],
        y=timeline['avg_category_rank'],
        name='Avg Rank',
        mode='lines+markers',
        line=dict(color='rgb(26, 118, 255)', width=2),
        yaxis='y2'
    ))

    fig.update_layout(
        title=f'{category_name.replace("-", " ").title()} - Timeline',
        xaxis_title='Month',
        yaxis=dict(
            title='Book Count',
            titlefont=dict(color='rgb(55, 83, 109)'),
            tickfont=dict(color='rgb(55, 83, 109)')
        ),
        yaxis2=dict(
            title='Average Rank',
            titlefont=dict(color='rgb(26, 118, 255)'),
            tickfont=dict(color='rgb(26, 118, 255)'),
            anchor='x',
            overlaying='y',
            side='right',
            autorange='reversed'  # Lower rank is better
        ),
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )

    return jsonify(json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)))


@app.route('/api/export/trending')
def api_export_trending():
    """Export trending data as CSV"""
    start_month = request.args.get('start_month')
    end_month = request.args.get('end_month')
    format_type = request.args.get('format', 'csv')

    months = analyzer.get_available_months()
    if not start_month and len(months) >= 2:
        start_month = months[-1]
        end_month = months[0]

    trending = analyzer.get_trending_categories(start_month, end_month, min_books=1)

    if trending.empty:
        return jsonify({'error': 'No data available'}), 404

    # Export to file
    filename = f'trending_{start_month}_{end_month}.{format_type}'
    filepath = EXPORTS_DIR / filename

    if format_type == 'csv':
        trending.to_csv(filepath, index=False)
    else:  # json
        trending.to_json(filepath, orient='records', indent=2)

    return send_file(filepath, as_attachment=True, download_name=filename)


@app.route('/api/generate-sample-data')
def api_generate_sample_data():
    """Generate sample data (for demo purposes)"""
    months = int(request.args.get('months', 12))

    try:
        scraper.generate_sample_historical_data(months)
        return jsonify({'success': True, 'message': f'Generated {months} months of sample data'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Error handlers

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
