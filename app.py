#!/usr/bin/env python3
 
# export FLASK_APP=app.py
# export FLASK_DEBUG=1
# flask run

from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from flask import flash
from flask import redirect
from flask import send_from_directory
from PIL import Image                           # Image()
from resizeimage import resizeimage             # resize_width()
from werkzeug import secure_filename            # secure_filemane()
from flask_wtf import FlaskForm                 # FlaskForm
from flask_wtf.file import FileField            # FileField()
from flask_wtf.file import FileRequired         # FileRequired()
from wtforms.validators import ValidationError  # ValidationError()
import imghdr                                   # what()
import os                                       # join(), listdir()

app = Flask(__name__)

# App config
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024                         # 16Mb max per upload
app.config['ALLOWED_EXTENSIONS'] = ('bmp', 'gif', 'png', 'jpg', 'jpeg')     # Allowed file extensions to be uploaded
app.config['UPLOAD_DIR'] = 'uploads/'                                       # Upload directory
app.config['THUMBN_DIR'] = 'thumbnails/'                                    # Thumbnails directory
app.config['THUMBN_SIZE'] = [300, 300]                                      # Thumbnails size in px
app.secret_key = '1RK+3588rZaM081C/c6fhTIvNOzb1L9K9nP0ojX3O7b7wJjAz5/I7EICH3m+/530/sW7iotaUK4R'




# Custom validator
# Check that the file is a real image,
# Check that the file has a valid image extension
def validate_file(alwd_ext):

    def _validate_file(form, field):

        # Raise a ValidationError if the image is not
        # a real image. Ex: random file with image extension
        if not imghdr.what(field.data) in alwd_ext:
            message = "File must be an image !"
            raise ValidationError(message)
            return _validate_file

        # Raise a ValidationError if the image extension is not
        # listed in app.config['ALLOWED_EXTENSIONS']
        if not field.data.filename.rsplit('.')[-1].lower() in app.config['ALLOWED_EXTENSIONS']:
            message = "File must have a valid image extension !"
            raise ValidationError(message)
            return _validate_file

    return _validate_file


# Image form declaration
class ImageForm(FlaskForm):

    image = FileField('image', validators=[
        FileRequired(),
        validate_file(app.config['ALLOWED_EXTENSIONS'])
    ])



# Main page
@app.route("/index/", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def main():

    # List if images in the upload folder
    images = [ img for img in os.listdir(app.config['UPLOAD_DIR']) 
        if 
        (
            check_filetype(os.path.join(app.config['UPLOAD_DIR'], img)) and 
            img.rsplit('.')[-1].lower() in app.config['ALLOWED_EXTENSIONS']
        )
    ]

    # Create a second list, same as 'images' but with the thumbnail name
    # Ex: ['a-thumb.jpg', 'b-thumb.jpg', ...]
    thumbnails = [add_thumb(item) for item in images]

    # Create a bounded dictionnary from images and thumbnails
    dictionnary = dict(zip(images, thumbnails))

    # Initialize ImageForm()
    form = ImageForm()


    if request.method == 'POST':

        # Form is submitted
        if form.validate_on_submit():
            f = form.image.data
            filename = secure_filename(f.filename)

            # If an image with the same name is already uploaded,
            # add an incremental counter before the '.extension'
            # Ex: filename-001.png, filename-002.png, ...
            if filename in images:
                filename = increment_filename(filename, images)
                    
            print("f: " + str(f))
            print("filename: " + str(filename))
            print("save path: " + os.path.join(app.config['UPLOAD_DIR'],  filename))

            # Save image in upload folder
            f.save(os.path.join(
                app.config['UPLOAD_DIR'], 
                filename
            ))

            # Create the thumbnail from uploaded image and save it to thumbnails folder
            create_thumbnail(str(filename))

            # Inform user the file is uploaded
            flash(u'File successfully uploaded', 'success')
            return redirect(request.url)



    # If a cookie is set with the name "theme",
    # get this cookie
    if request.cookies.get("theme"):
        theme = request.cookies.get("theme")
    else:
        # Default is 'flatty'  
        theme = "flatty"

    # Prepare response
    response = make_response(render_template('index.html',
        dictionnary=dictionnary,
        form=form,
        theme=theme))
    
    # Set the 'theme' cookie
    response.set_cookie('theme', theme)


    # Display the index for GET or POST requests
    return response


@app.route('/uploads/<filename>')
def upload_file(filename):
    return send_from_directory(app.config['UPLOAD_DIR'],
                               filename)

@app.route('/thumbnails/<filename>')
def thumbn_file(filename):
    return send_from_directory("thumbnails/",
                               filename)

if __name__ == "__main__":
    app.run()


# Return true if the type is truly an image,  
# and not a random file with an image  
# extension 
def check_filetype(file): 
    return imghdr.what(file) in app.config['ALLOWED_EXTENSIONS'] 


# Add an incremental counter before the '.extension'
# Ex: filename-001.png, filename-002.png, ...
def increment_filename(filename, images):
    basename = filename.rsplit('.')[-2] + "-"
    extension = "." + filename.rsplit('.')[-1]
    i = 1
    while filename in images:
        filename = basename + str("{0:0=3d}".format(i)) + extension
        i = i + 1

    return filename


# Add '-thumb' to a filename juste before the .extension
# Ex: a.jpg --> a-thumb.jpg
def add_thumb(filename):
    basename = '.'.join(filename.rsplit('.')[:-1]) + "-thumb"
    extension = "." + filename.rsplit('.')[-1]
    return basename + extension


# Create and save a thumbnail of an image
def create_thumbnail(filename):
    thumbnail = app.config['THUMBN_DIR'] + add_thumb(filename)

    with open(app.config['UPLOAD_DIR'] + filename, 'rb') as f:
        img = Image.open(f)
        img = resizeimage.resize_cover(img, app.config['THUMBN_SIZE'])
        img.save(thumbnail, img.format)


