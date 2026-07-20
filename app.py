import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from PIL import Image

st.set_page_config(page_title="Manipal Hospitals - PDF Tools", layout="centered", page_icon="🏥")

st.title("🏥 Manipal Hospitals - PDF Operations Tool")
st.write("A 3-in-1 tool to **Stamp PDF Documents**, **Merge PDFs**, and **Auto-Compress Files under 2 MB** seamlessly.")

tab1, tab2, tab3 = st.tabs(["📌 PDF Stamper", "🔗 PDF Merger", "🗜️ PDF Compressor"])

# ---------------------------------------------------------
# HELPER: Target Size Compressor (Forces under 2 MB)
# ---------------------------------------------------------
def compress_pdf_under_2mb(input_bytes, max_mb=2.0):
    max_bytes = max_mb * 1024 * 1024
    reader = PdfReader(io.BytesIO(input_bytes))
    
    # Pass 1: Lossless Stream Compression
    writer = PdfWriter()
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    writer.add_metadata({})
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    
    # If already under 2 MB, return losslessly compressed version
    if len(output.getvalue()) <= max_bytes:
        return output.getvalue(), "Lossless Compression"
    
    # Pass 2: Adaptive Compression if Pass 1 is still > 2 MB
    quality = 75
    while quality >= 25:
        writer_img = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams()
            for img_obj in page.images:
                try:
                    img = Image.open(io.BytesIO(img_obj.data))
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
                    img_obj.replace(img_byte_arr.getvalue())
                except Exception:
                    pass
            writer_img.add_page(page)
        
        out_img = io.BytesIO()
        writer_img.write(out_img)
        out_img.seek(0)
        
        if len(out_img.getvalue()) <= max_bytes or quality == 25:
            return out_img.getvalue(), f"Smart Compression (Quality: {quality}%)"
            
        quality -= 15
        
    return output.getvalue(), "Maximum Reduction Reached"

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
    auto_2mb_stamp = st.checkbox("⚡ Auto-compress output file under 2 MB (TPA Upload Ready)", value=True, key="stamp_2mb_check")

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
                method_used = "Standard"

                if auto_2mb_stamp and len(final_bytes) > 2 * 1024 * 1024:
                    final_bytes, method_used = compress_pdf_under_2mb(final_bytes, max_mb=2.0)

                orig_size = len(uploaded_pdf.getvalue()) / (1024 * 1024)
                final_size = len(final_bytes) / (1024 * 1024)

                st.success("✅ PDF Stamped Successfully!")
                
                if final_size <= 2.0:
                    st.info(f"🎯 **File Size Target Met:** `{final_size:.2f} MB` (Under 2 MB Limit) | Mode: `{method_used}`")
                else:
                    st.warning(f"⚠️ **Final Size:** `{final_size:.2f} MB` (Original: `{orig_size:.2f} MB`)")

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
    auto_2mb_merge = st.checkbox("⚡ Auto-compress merged output under 2 MB (TPA Upload Ready)", value=True, key="merge_2mb_check")

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
                method_used = "Standard"

                if auto_2mb_merge and len(final_bytes) > 2 * 1024 * 1024:
                    final_bytes, method_used = compress_pdf_under_2mb(final_bytes, max_mb=2.0)

                final_size = len(final_bytes) / (1024 * 1024)

                st.success("✅ PDFs Merged Successfully!")
                if final_size <= 2.0:
                    st.info(f"🎯 **File Size Target Met:** `{final_size:.2f} MB` (Under 2 MB Limit) | Mode: `{method_used}`")
                else:
                    st.warning(f"⚠️ **Final Size:** `{final_size:.2f} MB`")

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
# TAB 3: STANDALONE PDF COMPRESSOR (TARGET < 2 MB)
# ---------------------------------------------------------
with tab3:
    st.subheader("Auto PDF Compressor (Target: < 2 MB)")
    st.write("Upload any heavy PDF file (claims, medical records, invoices) to compress it under 2 MB.")

    compress_file = st.file_uploader("Upload Heavy PDF to Compress", type=["pdf"], key="comp_only_pdf")

    if compress_file:
        orig_mb = len(compress_file.getvalue()) / (1024 * 1024)
        st.info(f"📁 **Original File Size:** `{orig_mb:.2f} MB`")

        if st.button("🗜️ Compress Under 2 MB Now", use_container_width=True, key="comp_btn"):
            try:
                compressed_bytes, method = compress_pdf_under_2mb(compress_file.getvalue(), max_mb=2.0)
                new_mb = len(compressed_bytes) / (1024 * 1024)
                savings = max(0, ((orig_mb - new_mb) / orig_mb) * 100) if orig_mb > 0 else 0

                st.success(f"✅ PDF Compression Complete! Reduced by **{savings:.1f}%**")
                
                if new_mb <= 2.0:
                    st.info(f"🎯 **Target Met:** `{new_mb:.2f} MB` (Successfully compressed under 2.0 MB threshold)")
                else:
                    st.warning(f"📉 **Compressed Size:** `{new_mb:.2f} MB` (Maximum safe compression reached)")

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
