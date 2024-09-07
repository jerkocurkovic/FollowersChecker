from flask import Flask, render_template, request
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt'}

# Check if extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Initialize variables
    usernames = []
    name_found = False
    
    for line in lines:
        line = line.strip()
        if line.startswith("Slika profila ") or line.startswith("Profile picture "):
            # Skip lines that start with "Slika profila" or "Profile picture"
            name_found = False
            continue
        elif not name_found:
            # Collect usernames from lines
            usernames.append(line)
            name_found = True
    
    # Write the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        for username in usernames:
            file.write(f"{username}\n")
    return output_file


# Followers check function
def followers_check(file1_path, file2_path):
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        set1 = set(file1.read().splitlines())
        set2 = set(file2.read().splitlines())

    unique_lines = [line for line in set1 if line not in set2]
    return unique_lines


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file1' not in request.files or 'file2' not in request.files:
            return render_template('index.html', result=[])

        file1 = request.files['file1']
        file2 = request.files['file2']

        if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
            file1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            file2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
            
            file1.save(file1_path)
            file2.save(file2_path)

            file1_path = process_file(file1_path, file1_path)
            file2_path = process_file(file2_path, file2_path)

            result = followers_check(file1_path, file2_path)
            return render_template('index.html', result=result)

    return render_template('index.html', result=[])

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
