import csv
import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Equipment Aggregator Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-light">
    <div class="container py-5">
        <h2 class="mb-4">Live HDD Equipment Dashboard</h2>
        <div class="card shadow-sm">
            <div class="card-body">
                <table class="table table-hover align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>Source</th>
                            <th>Equipment Title</th>
                            <th>Listing Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in listings %}
                        <tr>
                            <td><span class="badge bg-primary">{{ item.Source }}</span></td>
                            <td>{{ item.Title }}</td>
                            <td><a href="{{ item.URL }}" target="_blank" class="btn btn-sm btn-outline-primary">View Listing</a></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    listings = []
    if os.path.exists("all_listings.csv"):
        with open("all_listings.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            listings = list(reader)
    return render_template_string(HTML_TEMPLATE, listings=listings)


if __name__ == "__main__":
    app.run(port=5000, debug=True)