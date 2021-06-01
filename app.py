#!/usr/bin/python
#!/usr/bin/python3
#!/usr/bin/env python
#!/usr/bin/env python3

# -*- coding: utf8 -*-
#                      :- 
# date                 :-
# author               :- Md Jabed Ali(jabed)

import os
import subprocess
import urllib.request
import time
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from pdf2docx import parse
from docx2pdf import convert
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2 import PdfFileMerger
import pdfplumber
import fitz
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTFigure, LTTextBox
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
from pdf2image import convert_from_path, convert_from_bytes

text_ = ""

def convert_pdf_to_html(path):
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0 #is for all
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str


UPLOAD_FOLDER = 'static/uploads/'
convert_folder = 'static/convert/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['convert_folder'] = convert_folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['pdf'])
ALLOWED_EXTENSIONS_ = set(['docx', 'doc'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
def allowed_file_(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_
	
@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No pdf selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		print(file.filename)
		filename = file.filename #secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
		print('upload_pdf filename: ' + filename)
		flash('Pdf successfully uploaded and previewed below')
		return render_template('upload.html', filename=filename)
	else:
		flash('Allowed image types are -> pdf')
		return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route("/convert" , methods=['GET', 'POST'])
def test():
	select = request.form.get('select')
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No pdf selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		print(file.filename)
		filename = file.filename #secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
		print('upload_pdf filename: ' + filename)
		pdf_file = app.config['UPLOAD_FOLDER'] + file.filename
		docx_file = app.config['convert_folder'] + str(file.filename).replace('.pdf', '.docx')
		docx_file_nm = docx_file.split('/')[-1]
		text_file = app.config['convert_folder'] + str(file.filename).replace('.pdf', '.txt')
		text_file_nm = text_file.split('/')[-1]
		html_file = app.config['convert_folder'] + str(file.filename).replace('.pdf', '.html')
		html_file_nm = html_file.split('/')[-1]
		flash('Pdf successfully uploaded')
		
		pdf_file_ = 'pdf2txt.py ' + pdf_file + ' -o ' + docx_file
		if request.form.get('select') == 'word':
		  #parse(pdf_file, docx_file)
		  subprocess.call(pdf_file_, shell=True)
		if request.form.get('select') == 'txt':
		  with fitz.open(pdf_file) as doc:
		      text = ""
		      for page in doc:
		          text += page.getText()
		  with open(text_file, 'w') as f:
		      f.write(text)
		if request.form.get('select') == 'html':
		   html_string = convert_pdf_to_html(pdf_file)
		   with open(html_file, 'w') as f:
		       f.write(str(html_string)) 
		images_nm = []
		if request.form.get('select') == 'img':
		  images = convert_from_path(pdf_file)
		  for i in range(len(images)):
		      images[i].save( app.config['convert_folder'] + file.filename +' page '+ str(i) +'.jpg', 'JPEG')
		      images_nm.append(file.filename +' page '+ str(i) +'.jpg')
		  
		return render_template('convert.html', select_=select, filename=filename, docx_file_nm=docx_file_nm, text_file_nm=text_file_nm, html_file_nm=html_file_nm,images_nm=images_nm)
	else:
		flash('Allowed image types are -> pdf')
		return redirect(request.url)
	return(str(select)) 
    
@app.route('/convert_pdf_docx/<docx_file_nm>')
def convert_pdf_docx(docx_file_nm):
	return redirect(url_for('static', filename='convert/' + docx_file_nm), code=301)
	

@app.route('/convert_pdf_txt/<text_file_nm>')
def convert_pdf_txt(text_file_nm):
	return redirect(url_for('static', filename='convert/' + text_file_nm), code=301)

@app.route('/convert_pdf_html/<html_file_nm>')
def convert_pdf_html(html_file_nm):
	return redirect(url_for('static', filename='convert/' + html_file_nm), code=301)

@app.route('/convert_pdf_img/<images_nm>')
#@app.route('/convert_pdf_img/<>')
def convert_pdf_img(images_nm):
	return redirect(url_for('static', filename='convert/' + images_nm), code=301)

@app.route("/convert_docx" , methods=['GET', 'POST'])
def convert_docx():
	select = request.form.get('select')
	print (select)
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	print (file.filename)
	if file.filename == '':
		flash('No docx selected for uploading')
		return redirect(request.url)
	if file and allowed_file_(file.filename):
		print(file.filename)
		filename = file.filename #secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
		print('upload_pdocx filename: ' + filename)
		docx_file = app.config['UPLOAD_FOLDER'] + file.filename
		docx_file_ = app.config['convert_folder'] + str(file.filename).replace('.docx', '.pdf')
		docx_file_nm = docx_file.split('/')[-1]
		print (docx_file,docx_file_,docx_file_nm)
		convert(docx_file,docx_file_)
		  
		return render_template('convert.html', select_=select, filename=filename, docx_file_nm=docx_file_nm, text_file_nm=text_file_nm, html_file_nm=html_file_nm,images_nm=images_nm)
	else:
		flash('Allowed image types are -> docx')
		return redirect(request.url)
	return(str(select)) 
    

@app.route("/split" , methods=['GET', 'POST'])
def split():
	pageno = request.form.get('pageno')

	print (pageno)
	start_ = pageno
	end_ = pageno
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No pdf selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		
		filename = file.filename #secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
		print('upload_pdf filename: ' + filename)
		pdf_file = app.config['UPLOAD_FOLDER'] + file.filename
		if ',' in pageno:
		   pageno = pageno.split(',')
		   start_ = str(pageno[0])
		   end_ = str(pageno[1])
		   
		if '-' in pageno:
		   pageno = pageno.split('-')
		   start_ = str(pageno[0])
		   end_ = str(pageno[1])
		   
		if pdf_file:
		   pdf_pages = PdfFileReader(open(pdf_file, 'rb'))
		   pdf_pages = pdf_pages.numPages
		   if int(start_)>pdf_pages:
		      flash('Page no cannot exceed total number of pages ')
		   if int(end_)>pdf_pages:
		      flash('Page no cannot exceed total number of pages ')	
		      
		pdfs = {pdf_file: ({'start': int(start_), 'end': int(end_)},)}  
		for pdf, segments in pdfs.items():
		    pdf_reader = PdfFileReader(open(pdf, 'rb'))
		    pdf = pdf.split('/')[-1]
		    for segment in segments:
		        pdf_writer = PdfFileWriter()
		        start_page = segment['start']
		        end_page = segment['end']
		        for page_num in range(start_page - 1, end_page):
		            pdf_writer.addPage(pdf_reader.getPage(page_num))
		        output_filename = f'{pdf}_{start_page}_page_{end_page}.pdf'
		        print(output_filename)
		        with open(app.config['convert_folder'] + output_filename,'wb') as f:
		            pdf_writer.write(f)
		
				            		            
		return render_template('split.html', output_filename=output_filename)
	else:
		flash('Allowed image types are -> pdf')
		return redirect(request.url)
	return(str(select)) 

@app.route('/split_pdf/<output_filename>')
#@app.route('/convert_pdf_img/<>')
def split_pdf(output_filename):
	return redirect(url_for('static', filename='convert/' + output_filename), code=301)

@app.route("/append" , methods=['GET', 'POST'])
def append():
    uploaded_files = request.files.getlist("files")
    filenames = []
    pdfs = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            a = str(os.path.join(app.config['UPLOAD_FOLDER'])) + filename
            print (os.path.join(app.config['UPLOAD_FOLDER']))
            filenames.append(filename)
            pdfs.append(a)
    append_ = PdfFileMerger()
    for pdf in pdfs:
        append_.append(pdf)
    pdf_write = app.config['convert_folder']+ time.strftime("%m.%d.%y %H:%M", time.localtime()) + ' converted.pdf'
    append_file_nm = pdf_write.split('/')[-1]
    print (append_file_nm)
    append_.write(pdf_write)
    append_.close()
    
    return render_template('append.html', append_file_nm=append_file_nm)

@app.route('/append_pdf/<append_file_nm>')
def append_pdf(append_file_nm):
	return redirect(url_for('static', filename='convert/' + append_file_nm), code=301)
	
if __name__ == "__main__":
    app.run(debug=True)
