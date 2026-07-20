import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

st.set_page_config(page_title="Manipal Hospitals - PDF Tools", layout="centered", page_icon="🏥")

st.title("🏥 Manipal Hospitals - PDF Operations Tool")
st.write("A 2-in-1 tool to **Stamp PDF Documents** and **Merge Multiple PDFs** seamlessly.")

tab1, tab2 = st.tabs(["📌 PDF Stamper", "🔗 PDF Merger"])

# ---------------------------------------------------------
# TAB 1: PDF STAMPER
# ---------------------------------------------------------
with tab1:
    st.subheader("Document Stamping")
    st.write("Upload a PDF document and a stamp image to apply the official Manipal Hospitals stamp.")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_pdf = st.file_uploader("1. Upload PDF Document", type=["pdf"], key="stamp_pdf")
    with col2:
        uploaded_stamp = st.file_uploader("2. Upload Stamp / Logo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="stamp_img")

    if uploaded_stamp:
        st.image(uploaded_stamp, caption="Selected Stamp Preview", width=160)

    position = st.selectbox("Select Stamp Position on PDF", ["Bottom Right", "Top Right", "Bottom Left", "Top Left"], key="stamp_pos")

    # Stamp dimensions (Increased size)
    stamp_width = 220
    stamp_height = 100

    if uploaded_pdf and uploaded_stamp:
        if st.button("🚀 Apply Stamp & Generate PDF", use_container_width=True, key="stamp_btn"):
            try:
                reader = PdfReader(uploaded_pdf)
                writer = PdfWriter()

                # Adjusted coordinates for standard letter/A4 (~ 612 x 792 pt) with larger stamp
                coords = {
                    "Bottom Right": (360, 30),
                    "Top Right": (360, 660),
                    "Bottom Left": (30, 30),
                    "Top Left": (30, 660)
                }
                x, y = coords[position]

                # Build Stamp Overlay Canvas
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=(612, 792))

                # Draw Larger Stamp Image
                stamp_img = ImageReader(io.BytesIO(uploaded_stamp.getvalue()))
                can.drawImage(stamp_img, x, y, width=stamp_width, height=stamp_height, mask='auto', preserveAspectRatio=True)

                can.save()
                packet.seek(0)

                overlay = PdfReader(packet).pages[0]

                # Merge overlay onto all pages
                for page in reader.pages:
                    page.merge_page(overlay)
                    writer.add_page(page)

                output_stream = io.BytesIO()
                writer.write(output_stream)
                output_stream.seek(0)

                st.success("✅ PDF Stamped Successfully!")
                st.download_button(
                    label="⬇️ Download Stamped PDF",
                    data=output_stream,
                    file_name=f"Stamped_{uploaded_pdf.name}",
                    mime="application/pdf",
                    use_container_width=True,
                    key="stamp_dl"
                )

            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")

# ---------------------------------------------------------
# TAB 2: PDF MERGER
# ---------------------------------------------------------
with tab2:
    st.subheader("PDF Merger")
    st.write("Upload multiple PDF files to combine them into a single document in sequence.")

    uploaded_pdfs = st.file_uploader("Upload PDFs to Merge", type=["pdf"], accept_multiple_files=True, key="merge_pdfs")

    if uploaded_pdfs and len(uploaded_pdfs) > 1:
        st.write(f"**Files selected to merge ({len(uploaded_pdfs)}):**")
        for idx, pdf in enumerate(uploaded_pdfs, 1):
            st.write(f"{idx}. {pdf.name}")

        if st.button("🔗 Merge PDFs", use_container_width=True, key="merge_btn"):
            try:
                merger_writer = PdfWriter()

                for pdf in uploaded_pdfs:
                    pdf_reader = PdfReader(pdf)
                    for page in pdf_reader.pages:
                        merger_writer.add_page(page)

                merged_output = io.BytesIO()
                merger_writer.write(merged_output)
                merged_output.seek(0)

                st.success("✅ PDFs Merged Successfully!")
                st.download_button(
                    label="⬇️ Download Merged PDF",
                    data=merged_output,
                    file_name="Manipal_Merged_Document.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="merge_dl"
                )

            except Exception as e:
                st.error(f"Error merging PDFs: {str(e)}")
    elif uploaded_pdfs and len(uploaded_pdfs) == 1:
        st.info("Please upload at least 2 PDF files to merge.")
