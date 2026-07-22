import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

st.set_page_config(page_title="Manipal Hospitals - PDF Tools", layout="centered", page_icon="🏥")

st.title("🏥 Manipal Hospitals - PDF Operations Tool")
st.write("A 4-in-1 suite for **Stamping**, **Merging**, **Compressing**, and **Applying Letterheads** to PDF documents.")

tab1, tab2, tab3, tab4 = st.tabs(["📌 PDF Stamper", "📄 Letterhead Overlay", "🔗 PDF Merger", "🗜️ PDF Compressor"])

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

    stamp_width = 220
    stamp_height = 100

    if uploaded_pdf and uploaded_stamp:
        if st.button("🚀 Apply Stamp & Generate PDF", use_container_width=True, key="stamp_btn"):
            try:
                pdf_bytes = uploaded_pdf.getvalue()
                stamp_bytes = uploaded_stamp.getvalue()

                reader = PdfReader(io.BytesIO(pdf_bytes))
                writer = PdfWriter()

                coords = {
                    "Bottom Right": (360, 30),
                    "Top Right": (360, 660),
                    "Bottom Left": (30, 30),
                    "Top Left": (30, 660)
                }
                x, y = coords[position]

                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=(612, 792))
                stamp_img = ImageReader(io.BytesIO(stamp_bytes))
                can.drawImage(stamp_img, x, y, width=stamp_width, height=stamp_height, mask='auto', preserveAspectRatio=True)
                can.save()
                packet.seek(0)

                overlay = PdfReader(packet).pages[0]

                for page in reader.pages:
                    page.merge_page(overlay)
                    writer.add_page(page)

                output_stream = io.BytesIO()
                writer.write(output_stream)
                output_stream.seek(0)

                st.success("✅ PDF Stamped Successfully!")
                st.download_button(
                    label="⬇️ Download Stamped PDF",
                    data=output_stream.getvalue(),
                    file_name=f"Stamped_{uploaded_pdf.name}",
                    mime="application/pdf",
                    use_container_width=True,
                    key="stamp_dl"
                )

            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")

# ---------------------------------------------------------
# TAB 2: LETTERHEAD OVERLAY
# ---------------------------------------------------------
with tab2:
    st.subheader("Letterhead Document Print")
    st.write("Overlay plain document content onto an official Manipal Hospitals Letterhead template PDF.")

    col1, col2 = st.columns(2)
    with col1:
        letterhead_pdf = st.file_uploader("1. Upload Letterhead Template (PDF)", type=["pdf"], key="lh_template")
    with col2:
        content_pdf = st.file_uploader("2. Upload Content PDF", type=["pdf"], key="lh_content")

    if letterhead_pdf and content_pdf:
        if st.button("📄 Apply Content to Letterhead", use_container_width=True, key="lh_btn"):
            with st.spinner("Processing document onto letterhead..."):
                try:
                    letterhead_bytes = letterhead_pdf.getvalue()
                    content_bytes = content_pdf.getvalue()

                    content_reader = PdfReader(io.BytesIO(content_bytes))
                    writer = PdfWriter()

                    for content_page in content_reader.pages:
                        bg_reader = PdfReader(io.BytesIO(letterhead_bytes))
                        bg_page = bg_reader.pages[0]
                        bg_page.merge_page(content_page)
                        writer.add_page(bg_page)

                    lh_output = io.BytesIO()
                    writer.write(lh_output)
                    lh_output.seek(0)

                    st.success("✅ Document Printed onto Letterhead Successfully!")
                    st.download_button(
                        label="⬇️ Download Letterhead PDF",
                        data=lh_output.getvalue(),
                        file_name=f"Letterhead_{content_pdf.name}",
                        mime="application/pdf",
                        use_container_width=True,
                        key="lh_dl"
                    )

                except Exception as e:
                    st.error(f"Error merging with Letterhead: {str(e)}")

# ---------------------------------------------------------
# TAB 3: PDF MERGER
# ---------------------------------------------------------
with tab3:
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
                    pdf_reader = PdfReader(io.BytesIO(pdf.getvalue()))
                    for page in pdf_reader.pages:
                        merger_writer.add_page(page)

                merged_output = io.BytesIO()
                merger_writer.write(merged_output)
                merged_output.seek(0)

                st.success("✅ PDFs Merged Successfully!")
                st.download_button(
                    label="⬇️ Download Merged PDF",
                    data=merged_output.getvalue(),
                    file_name="Manipal_Merged_Document.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="merge_dl"
                )

            except Exception as e:
                st.error(f"Error merging PDFs: {str(e)}")
    elif uploaded_pdfs and len(uploaded_pdfs) == 1:
        st.info("Please upload at least 2 PDF files to merge.")

# ---------------------------------------------------------
# TAB 4: STANDALONE PDF COMPRESSOR
# ---------------------------------------------------------
with tab4:
    st.subheader("PDF Compressor")
    st.write("Upload any heavy PDF file to compress its content streams and optimize file size.")

    compress_file = st.file_uploader("Upload Heavy PDF to Compress", type=["pdf"], key="comp_only_pdf")

    if compress_file:
        orig_mb = len(compress_file.getvalue()) / (1024 * 1024)
        st.info(f"📁 **Original File Size:** `{orig_mb:.2f} MB`")

        if st.button("🗜️ Compress PDF Now", use_container_width=True, key="comp_btn"):
            try:
                reader = PdfReader(io.BytesIO(compress_file.getvalue()))
                writer = PdfWriter()

                for page in reader.pages:
                    writer.add_page(page)

                for page in writer.pages:
                    try:
                        page.compress_content_streams()
                    except Exception:
                        pass

                output = io.BytesIO()
                writer.write(output)
                output.seek(0)

                new_mb = len(output.getvalue()) / (1024 * 1024)
                savings = max(0, ((orig_mb - new_mb) / orig_mb) * 100) if orig_mb > 0 else 0

                st.success(f"✅ PDF Compression Complete! Reduced by **{savings:.1f}%**")
                st.info(f"📉 **New Size:** `{new_mb:.2f} MB` (Original was `{orig_mb:.2f} MB`)")

                st.download_button(
                    label="⬇️ Download Compressed PDF",
                    data=output.getvalue(),
                    file_name=f"Compressed_{compress_file.name}",
                    mime="application/pdf",
                    use_container_width=True,
                    key="comp_dl"
                )
            except Exception as e:
                st.error(f"Error compressing PDF: {str(e)}")
