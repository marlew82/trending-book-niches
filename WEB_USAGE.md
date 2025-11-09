# Web Interface Usage Guide

Complete guide to using the Amazon Book Trends Analyzer web interface.

## Starting the Application

```bash
# 1. Make sure dependencies are installed
pip install -r requirements.txt

# 2. Generate sample data (if you haven't already)
python3 main.py generate-sample-data --months 12

# 3. Start the web server
python3 app.py
```

The application will start at **http://localhost:5000**

Access it in your web browser!

## Pages Overview

### 1. Dashboard (Homepage)

**URL:** `/` or `http://localhost:5000/`

The dashboard provides an at-a-glance view of your data:

- **Statistics Cards**: Shows total categories, books analyzed, months tracked, and date range
- **Quick Actions**: Buttons to navigate to trending categories, top books, or generate sample data
- **Trending Chart**: Interactive bar chart showing top trending categories
- **Category Browser**: Grid of all available categories with links to details

**Key Features:**
- Generate sample data directly from the dashboard
- See overall statistics
- Quick navigation to all sections
- Visual trending chart

### 2. Trending Categories

**URL:** `/trending`

Analyze which book categories are experiencing the most growth:

**Filters:**
- Start Month: Select the beginning of your analysis period
- End Month: Select the end of your analysis period
- Show Top: Choose how many categories to display (10, 20, or 50)

**Displays:**
- **Interactive Chart**: Bar chart showing trend scores for top categories
- **Detailed Table**: Comprehensive metrics including:
  - Rank (position in trending list)
  - Category name
  - Trend Score (composite metric)
  - Rank Improvement percentage
  - Book Count Growth percentage
  - Review Growth percentage
  - Number of books in category
  - Average price
  - Average rating
  - Action button to view category details

**Export Options:**
- Export to CSV for Excel analysis
- Export to JSON for programmatic use

### 3. Category Details

**URL:** `/category/<category-name>` (e.g., `/category/romance`)

Deep dive into a specific category's performance:

**Filters:**
- Start Month / End Month: Filter the timeline view
- Book Month: Select which month to show top books for

**Sections:**

#### Performance Timeline
- Dual-axis chart showing:
  - Book count over time (left axis)
  - Average category rank over time (right axis, inverted)
- Interactive hover details

#### Monthly Metrics Table
Shows for each month:
- Number of books
- Average sales rank
- Average category rank
- Average price
- Total reviews
- Average rating

#### Top Performing Books
For the selected month, shows:
- Book rankings
- Title and author
- Category rank
- Price
- Number of reviews
- Rating

#### Fastest Growing Books
Books with biggest rank improvements over the period:
- Rank improvement percentage
- Starting and ending ranks
- Review growth
- Current price and rating

### 4. Top Books

**URL:** `/books`

Browse the best-performing books across all categories:

**Filters:**
- Category: Select which category to analyze
- Month: Choose the month to view
- Show Top: Number of books to display (10, 20, or 50)

**Table Shows:**
- Rank position
- Book title
- Author name
- Category badge (clickable)
- Category rank
- Overall sales rank
- Price
- Review count
- Star rating with color-coded badge

**Category Browser:**
Grid of all categories for quick navigation

### 5. About

**URL:** `/about`

Learn about the tool and methodology:

**Sections:**
- Overview of the tool's purpose
- Key features explained
- Detailed trend score methodology
- Data collection approach
- Technology stack
- Getting started guide

## Using the API

The web application exposes RESTful API endpoints for integration:

### Get Overall Statistics

```bash
curl http://localhost:5000/api/stats
```

Returns:
```json
{
  "total_categories": 5,
  "total_books": 180,
  "months_tracked": 12,
  "date_range": {"start": "2024-12-14", "end": "2025-11-09"},
  "categories": ["romance", "self-help", ...],
  "months": ["2025-11", "2025-10", ...]
}
```

### Get Trending Categories

```bash
curl "http://localhost:5000/api/trending?start_month=2024-12&end_month=2025-11&limit=10"
```

Returns trending categories with all metrics.

### Get Category Timeline

```bash
curl "http://localhost:5000/api/category/romance/timeline?start_month=2024-12&end_month=2025-11"
```

Returns monthly data for the category.

### Get Top Books

```bash
curl "http://localhost:5000/api/category/romance/books?month=2025-11&limit=10"
```

Returns top performing books in the category for that month.

### Get Chart Data

```bash
curl "http://localhost:5000/api/chart/trending?start_month=2024-12&end_month=2025-11"
```

Returns Plotly-compatible JSON for rendering charts.

### Export Data

```bash
# CSV export
curl "http://localhost:5000/api/export/trending?start_month=2024-12&end_month=2025-11&format=csv" -o trending.csv

# JSON export
curl "http://localhost:5000/api/export/trending?start_month=2024-12&end_month=2025-11&format=json" -o trending.json
```

## Design Features

### Modern Minimal Interface

The web interface uses a custom-built minimal design with:

- **Clean Typography**: Inter font family for excellent readability
- **Subtle Shadows**: Layered depth without overwhelming visual noise
- **Professional Color Palette**: Primary blue (#2563eb), success green, warning orange
- **Smooth Transitions**: 300ms cubic-bezier animations
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Hover states and smooth interactions

### Color-Coded Badges

- **Success (Green)**: High ratings (4.5+), positive growth
- **Primary (Blue)**: Good performance, medium values
- **Warning (Orange)**: Moderate performance
- **Danger (Red)**: Negative trends or low rankings

### Interactive Charts

All charts are powered by Plotly and feature:
- Zoom and pan capabilities
- Hover details
- Legend toggling
- Responsive resizing
- Professional styling

## Tips for Best Experience

1. **Generate Sample Data First**: Use the "Generate Sample Data" button on the dashboard
2. **Use Date Filters**: Narrow down analysis to specific periods for clearer insights
3. **Compare Periods**: Try different date ranges to spot seasonal patterns
4. **Export for Analysis**: Use CSV export to analyze in Excel or Google Sheets
5. **Check Multiple Categories**: Compare different categories side-by-side
6. **Use the API**: Integrate with your own tools using the RESTful API

## Keyboard Shortcuts

- **Ctrl+F** / **Cmd+F**: Search within tables
- **Tab**: Navigate through form fields
- **Enter**: Submit filters

## Browser Compatibility

Works best in modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Deployment

### Local Development

```bash
python3 app.py
```

Default: http://localhost:5000

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or deploy to platforms like:
- **Heroku**: `web: gunicorn app:app`
- **Google Cloud Run**: Containerize with Docker
- **AWS Elastic Beanstalk**: Use Python platform
- **DigitalOcean App Platform**: Auto-detected Flask app

## Security Considerations

For production deployment:

1. **Change the secret key** in `app.py`
2. **Set DEBUG=False** in production
3. **Use HTTPS** with SSL certificates
4. **Implement authentication** if needed
5. **Rate limit** API endpoints
6. **Validate all inputs** (already implemented)

## Troubleshooting

### Server Won't Start

```bash
# Check if port 5000 is in use
lsof -i :5000

# Use a different port
python3 app.py --port 8080
```

### No Data Showing

1. Generate sample data: Click "Generate Sample Data" on dashboard
2. Or use CLI: `python3 main.py generate-sample-data --months 12`

### Charts Not Loading

1. Check browser console for errors
2. Ensure Plotly CDN is accessible
3. Try refreshing the page

### API Returns Empty Data

Check the date range - data may not exist for those months. Run:
```bash
curl http://localhost:5000/api/stats
```
To see available months.

## Support

For issues or questions:
1. Check the [README.md](README.md) for general setup
2. Review this guide for web-specific help
3. Examine browser console for errors
4. Check Flask server logs in terminal

---

Happy analyzing! 📊🌐
