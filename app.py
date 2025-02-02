import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Function to check if the URL is accessible
def check_url(url):
    try:
        response = requests.head(url, timeout=5)  # Using HEAD to minimize load
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

# Route to handle form submission
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get M3U data entered in the textarea
        m3u_data = request.form.get('m3u')
        if m3u_data:
            # Parse the M3U data and extract the URLs
            links = parse_m3u(m3u_data)
            # Check each link
            dead_links = check_links(links)
            return render_template_string(results_page(dead_links))
        
    return render_template_string(index_page)

# Parse the M3U content and extract stream URLs
def parse_m3u(m3u_data):
    lines = m3u_data.split('\n')
    links = []
    
    # Iterate over lines to find URLs after #EXTINF lines
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
            # Next line after #EXTINF contains the URL
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url.startswith('http'):
                    links.append(url)
    return links

# Check each link from the list and return the dead links
def check_links(links):
    dead_links = []
    for link in links:
        if not check_url(link.strip()):  # Strip any leading/trailing spaces
            dead_links.append(link.strip())
    return dead_links

# HTML content for the main page (index)
index_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream Validator</title>
</head>
<body>
    <h1>Validate M3U Streams</h1>
    <p>Paste your M3U playlist below:</p>
    <form method="post">
        <textarea name="m3u" rows="10" cols="50"></textarea><br><br>
        <button type="submit">Validate</button>
    </form>
</body>
</html>
'''

# HTML content for the results page
def results_page(dead_links):
    if dead_links:
        dead_links_html = ''.join(f'<li>{link}</li>' for link in dead_links)
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Validation Results</title>
        </head>
        <body>
            <h1>Validation Results</h1>
            <h3>Dead Links:</h3>
            <ul>
                {dead_links_html}
            </ul>
            <br><br>
            <a href="/">Check Another</a>
        </body>
        </html>
        '''
    else:
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Validation Results</title>
        </head>
        <body>
            <h1>Validation Results</h1>
            <p>All links are up!</p>
            <br><br>
            <a href="/">Check Another</a>
        </body>
        </html>
        '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
