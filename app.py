import csv
import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live HDD Equipment Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding: 20px; }
        .table-container { background: #white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .badge-source { font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <h2 class="mb-4">Live HDD Equipment Dashboard</h2>
        <div class="table-container bg-white">
            <table class="table table-hover align-middle">
                <thead class="table-dark">
                    <tr>
                        <th>Source</th>
                        <th>Equipment Title</th>
                        <th>Price</th>
                        <th>Listing Link</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in listings %}
                    <tr>
                        <td><span class="badge bg-primary badge-source">{{ row.Source }}</span></td>
                        <td>{{ row.Title }}</td>
                        <td><strong class="text-success">{{ row.Price }}</strong></td>
                        <td><a href="{{ row.URL }}" target="_blank" class="btn btn-outline-primary btn-sm">View Listing</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    listings = []
    if os.path.exists('all_listings.csv'):
        with open('all_listings.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                listings.append(row)
    return render_template_string(HTML_TEMPLATE, listings=listings)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
