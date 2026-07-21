import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

st.set_page_config(page_title="Manipal Hospitals - PDF Tools", layout="centered", page_icon="🏥")

st.title("🏥 Manipal Hospitals - PDF Operations Tool")
st.write("A 3-in-1 tool to **Stamp PDF Documents**, **Merge PDFs**, and **Compress PDF File Sizes** safely.")

tab1, tab2, tab3 = st.tabs(["📌 PDF Stamper", "🔗 PDF Merger", "🗜️ PDF Compressor"])

# ---------------------------------------------------------
# HELPER: Ultra-Safe Stream Compression Engine
# ---------------------------------------------------------
def safe_compress_pdf(input_bytes):
    reader = PdfReader(io.BytesIO(input_bytes))
    writer = PdfWriter()

    # 1. First add all pages to writer
    for page in reader.pages:
        writer.add_page(page)

    # 2. Compress streams on writer pages cleanly
    for page in writer.pages:
        try:
            page.compress_content_streams()
        except Exception:
            pass  # Fallback gracefully if a specific page stream is already compressed/encrypted

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()

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
    auto_compress_stamp = st.checkbox("🗜️ Enable Auto-Compression (Optimizes output file size)", value=True, key="stamp_compress_check")

    stamp_width = 220
    stamp_height = 100

    if uploaded_pdf and uploaded_stamp:
        if st.button("🚀 Apply Stamp & Generate PDF", use_container_width=True, key="stamp_btn"):
            try:
                reader = PdfReader(uploaded_pdf)
                writer = PdfWriter()

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
                
                final_bytes = output_stream.getvalue()
                
                if auto_compress_stamp:
                    final_bytes = safe_compress_pdf(final_bytes)

                orig_size = len(uploaded_pdf.getvalue()) / (1024 * 1024)
                final_size = len(final_bytes) / (1024 * 1024)

                st.success("✅ PDF Stamped Successfully!")
                st.info(f"📊 **File Size:** `{final_size:.2f} MB` (Original: `{orig_size:.2f} MB`)")

                st.download_button(
                    label="⬇️ Download Stamped PDF",
                    data=final_bytes,
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
    auto_compress_merge = st.checkbox("🗜️ Auto-compress merged output", value=True, key="merge_compress_check")

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

                final_bytes = merged_output.getvalue()
                
                if auto_compress_merge:
                    final_bytes = safe_compress_pdf(final_bytes)

                final_size = len(final_bytes) / (1024 * 1024)

                st.success("✅ PDFs Merged Successfully!")
                st.info(f"📊 **Final Size:** `{final_size:.2f} MB`")

                st.download_button(
                    label="⬇️ Download Merged PDF",
                    data=final_bytes,
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
# TAB 3: STANDALONE PDF COMPRESSOR
# ---------------------------------------------------------
with tab3:
    st.subheader("PDF Compressor")
    st.write("Upload any heavy PDF file to compress its streams and remove redundant metadata without quality loss.")

    compress_file = st.file_uploader("Upload Heavy PDF to Compress", type=["pdf"], key="comp_only_pdf")

    if compress_file:
        orig_mb = len(compress_file.getvalue()) / (1024 * 1024)
        st.info(f"📁 **Original File Size:** `{orig_mb:.2f} MB`")

        if st.button("🗜️ Compress PDF Now", use_container_width=True, key="comp_btn"):
            try:
                compressed_bytes = safe_compress_pdf(compress_file.getvalue())
                new_mb = len(compressed_bytes) / (1024 * 1024)
                savings = max(0, ((orig_mb - new_mb) / orig_mb) * 100) if orig_mb > 0 else 0

                st.success(f"✅ PDF Compression Complete! Reduced by **{savings:.1f}%**")
                st.info(f"📉 **New Size:** `{new_mb:.2f} MB` (Original was `{orig_mb:.2f} MB`)")

                st.download_button(
                    label="⬇️ Download Compressed PDF",
                    data=compressed_bytes,
                    file_name=f"Compressed_{compress_file.name}",
                    mime="application/pdf",
                    use_container_width=True,
                    key="comp_dl"
                )
            except Exception as e:
                st.error(f"Error compressing PDF: {str(e)}")
