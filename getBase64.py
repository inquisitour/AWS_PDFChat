import base64

# Path to your PDF file
pdf_file_path = "./deepLearning.pdf"
# Path to save the encoded string
output_file_path = "./encoded_pdf.txt"

# Read and encode the PDF file
with open(pdf_file_path, "rb") as pdf_file:
    encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')

# Save the encoded string to a text file
with open(output_file_path, "w") as text_file:
    text_file.write(encoded_string)

print(f"Base64 encoded string saved to {output_file_path}")
