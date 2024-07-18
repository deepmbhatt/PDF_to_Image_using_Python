import streamlit as st
import fitz  # PyMuPDF
import io
import os
from zipfile import ZipFile

# Function to convert images to a ZIP file and return its path
def images_to_zip(images, zip_name="images.zip"):
    with ZipFile(zip_name, 'w') as zipf:
        for i, img in enumerate(images):
            img_name = f"page_{i+1}.png"
            img_data = img.getvalue()
            zipf.writestr(img_name, img_data)
    return zip_name

st.title('PDF to Image Converter')

# Upload PDF file
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save uploaded file to disk
    with open("temp_pdf_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Open the saved PDF file
    pdffile = "temp_pdf_file.pdf"
    doc = fitz.open(pdffile)
    zoom = 4  # Zoom factor for image conversion
    mat = fitz.Matrix(zoom, zoom)

    images = []  # List to store images

    # Convert each page of the PDF to an image
    for i in range(len(doc)):
        page = doc.load_page(i)  # Load the current page
        pix = page.get_pixmap(matrix=mat)  # Render page to an image
        img_byte_arr = io.BytesIO(pix.tobytes("png"))  # Convert image to byte array
        images.append(img_byte_arr)  # Add image to list

    # Input for selecting page number
    page_number = st.number_input("Enter page number to download", min_value=1, max_value=len(doc), step=1)
    selected_page_img = images[page_number-1].getvalue()
    # Button to download the selected page
    st.download_button(label="Download Selected Page", data=selected_page_img, file_name=f"page_{page_number}.png", mime="image/png")
    
    # Button to download all pages as a ZIP file
    if st.button("Download All Pages"):
        zip_name = images_to_zip(images)  # Convert all images to a ZIP file
        with open(zip_name, "rb") as f:
            st.download_button(label="Download All Pages as ZIP", data=f, file_name=zip_name, mime="application/zip")
        os.remove(zip_name)  # Clean up the ZIP file after downloading

    # Display each image below the buttons
    for i, img_byte_arr in enumerate(images):
        st.image(img_byte_arr.getvalue(), caption=f"Page {i+1}")

    # Button to clean up and close the application
    if st.button("Done"):
        doc.close()  # Close the PDF document
        os.remove("temp_pdf_file.pdf")  # Remove the temporary saved PDF file