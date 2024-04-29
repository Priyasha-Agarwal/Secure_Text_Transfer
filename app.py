import os
import os.path
from flask import Flask, request, redirect, url_for, render_template, session, send_from_directory, send_file, flash
from werkzeug.utils import secure_filename
from flask import redirect, url_for
import DH
import pickle
import random

UPLOAD_FOLDER = './media/text-files/'
UPLOAD_KEY = './media/public-keys/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

app = Flask(__name__, static_folder='static')



# app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Replace this with your own secret key


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/contact_us')
def contact():
    return render_template('contact_us.html')

@app.route('/register')
def call_page_register_user():
    return render_template('register.html')

@app.route('/home')
def back_home():
    return render_template('index.html')

@app.route('/upload-file')
def call_page_upload():
    return render_template('upload.html')

# @app.route('/upload-file', methods=['POST'])
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             flash('No selected file')
#             return 'NO FILE SELECTED'
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return 'File uploaded successfully'
#         return 'Invalid File Format !'
#     else:
#         return 'Method not allowed', 405

@app.route('/filenames')
def download_f():
    file_list = os.listdir(UPLOAD_FOLDER)
    length = len(file_list)
    if not file_list:
        return render_template('filenames.html', msg='No files found in directory', length=length, files=[])
    else:
        return render_template('filenames.html', msg='', files=file_list, length=length)
    




@app.route('/retrieve/file/<path:filename>')
def download_file(filename):
    return send_from_directory('media/text-files', filename, as_attachment=True)

@app.route('/generate-key')
def generate_key():
    random_key = generate_random_key(16)
    return render_template('key-display.html', random_key=random_key)

@app.route('/public-key-directory/retrieve/key/<username>', methods=['GET'])
def download_public_key(username):
    key_filename = f"./media/public-keys/{username}-PublicKey.pem"
    
    if os.path.isfile(key_filename):
        return send_file(key_filename, attachment_filename=f"{username}-PublicKey.pem", as_attachment=True)
    else:
        return render_template('error.html', msg='Public key not found')

# @app.route('/public-key-list')
# def public_key_list():
#     # Example data for demonstration, replace with actual data retrieval
#     directory = [('username1', 'uploader1'), ('username2', 'uploader2')]
#     length = len(directory)
#     return render_template('public_key_list.html', msg='', directory=directory, length=length)

@app.route('/public-key-list')
def public_key_list():
    # Example data for demonstration, replace with actual data retrieval
    directory = [('username1', 'uploader1'), ('username2', 'uploader2')]
    length = len(directory)
    return render_template('public-key-list.html', msg='', directory=directory, length=length)



@app.route('/public-key-directory/')
def downloads_pk():
    username = []
    if os.path.isfile("./media/database/database_1.pickle"):
        with open("./media/database/database_1.pickle", "rb") as pickleObj:
            username = pickle.load(pickleObj)

    length = len(username)

    if length == 0:
        return render_template('public-key-list.html', msg='Aww snap! No public key found in the database')
    else:
        return render_template('public-key-list.html', msg='', length=length, directory=username)

@app.route('/register-new-user', methods=['POST'])
def register_new_user():
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['first-name']
        secondname = request.form['last-name']
        pin = random.randint(1, 128) % 64
        privatekey = DH.generate_private_key(pin)
        
        with open("./media/database/database.pickle", "rb") as pickleObj:
            privatekeylist = pickle.load(pickleObj)
        with open("./media/database/database_1.pickle", "rb") as pickleObj:
            usernamelist = pickle.load(pickleObj)

        if username in usernamelist:
            return render_template('register.html', name='Username already exists')
        
        privatekeylist.append(str(privatekey))
        usernamelist.append(username)
        
        with open("./media/database/database.pickle", "wb") as pickleObj:
            pickle.dump(privatekeylist, pickleObj)
        with open("./media/database/database_1.pickle", "wb") as pickleObj:
            pickle.dump(usernamelist, pickleObj)

        filename = f"{UPLOAD_KEY}{username}-{secondname.upper()}{firstname.lower()}-PublicKey.pem"
        publickey = DH.generate_public_key(privatekey)
        with open(filename, "w") as fileObject:
            fileObject.write(str(publickey))
        
        return render_template('key-display.html', privatekey=str(privatekey))
    else:
        return 'Method not allowed', 405
    
from flask import redirect

@app.route('/upload-file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return 'NO FILE SELECTED'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('post_upload'))  # Corrected the redirection
        return 'Invalid File Format !'
    else:
        return 'Method not allowed', 405

@app.route('/post-upload')
def post_upload():
    return render_template('post-upload.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)

