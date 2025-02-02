import os
import requests
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Allowed extensions for uploaded files
ALLOWED_EXTENSIONS = {'m3u', 'txt'}

# Check if the file is an allowed type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Route to handle file upload or URL input
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('uploads', filename))
            links = parse_file(os.path.join('uploads', filename))
            dead_links = check_links(links)
            return render_template_string(results_page(dead_links))
        
        # OR if the user submits links directly
        urls = request.form.get('urls')
        if urls:
            links = urls.split('\n')
            dead_links = check_links(links)
            return render_template_string(results_page(dead_links))
        
    return render_template_string(index_page)

# Parse the M3U file and extract the URLs
def parse_file(file_path):
    links = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('http'):
                links.append(line.strip())
    return links

# Check each link from the list and return the dead links
def check_links(links):
    dead_links = []
    for link in links:
        if not check_url(link):
            dead_links.append(link)
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
    <form method="post" enctype="multipart/form-data">
        <label for="file">Upload M3U File:</label>
        <input type="file" name="file" id="file"><br><br>
        <label for="urls">Or Enter URLs (One per line):</label><br>
        <textarea name="urls" rows="10" cols="30"></textarea><br><br>
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
