import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

st.set_page_config(page_title="Manipal Hospitals - PDF Tools", layout="centered", page_icon="🏥")

st.title("🏥 Manipal Hospitals - PDF Operations Tool")
st.write("A 4-in-1 suite for **Batch Stamping & Merging**, **Letterhead Overlay**, **PDF Merging**, and **Compressing**.")

tab1, tab2, tab3, tab4 = st.tabs(["📌 Batch Stamp & Merge", "📄 Letterhead Overlay", "🔗 PDF Merger", "🗜️ PDF Compressor"])

# ---------------------------------------------------------
# TAB 1: BATCH STAMPER & SIMULTANEOUS MERGER
# ---------------------------------------------------------
with tab1:
    st.subheader("Batch Stamp & Simultaneous Merge")
    st.write("Upload **multiple PDF documents** and a stamp image. The tool will stamp every file and automatically combine them into a single merged PDF!")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_pdfs = st.file_uploader("1. Upload Multiple PDFs", type=["pdf"], accept_multiple_files=True, key="batch_stamp_pdfs")
    with col2:
        uploaded_stamp = st.file_uploader("2. Upload Stamp / Logo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="batch_stamp_img")

    if uploaded_stamp:
        st.image(uploaded_stamp, caption="Selected Stamp Preview", width=160)

    position = st.selectbox("Select Stamp Position on PDFs", ["Bottom Right", "Top Right", "Bottom Left", "Top Left"], key="batch_stamp_pos")

    stamp_width = 220
    stamp_height = 100

    if uploaded_pdfs and uploaded_stamp:
        st.write(f"📁 **Selected {len(uploaded_pdfs)} PDF files to process:**")
        for idx, f in enumerate(uploaded_pdfs, 1):
            st.caption(f"{idx}. {f.name}")

        if st.button("🚀 Stamp All Files & Merge Simultaneously", use_container_width=True, key="batch_stamp_btn"):
            with st.spinner("Stamping and merging all documents..."):
                try:
                    stamp_bytes = uploaded_stamp.getvalue()

                    # Build overlay canvas
                    packet = io.BytesIO()
                    can = canvas.Canvas(packet, pagesize=(612, 792))
                    stamp_img = ImageReader(io.BytesIO(stamp_bytes))

                    coords = {
                        "Bottom Right": (360, 30),
                        "Top Right": (360, 660),
                        "Bottom Left": (30, 30),
                        "Top Left": (30, 660)
                    }
                    x, y = coords[position]

                    can.drawImage(stamp_img, x, y, width=stamp_width, height=stamp_height, mask='auto', preserveAspectRatio=True)
                    can.save()
                    packet.seek(0)

                    overlay = PdfReader(packet).pages[0]
                    merged_writer = PdfWriter()

                    # Loop through each PDF file: stamp every page and merge into single output
                    for pdf_file in uploaded_pdfs:
                        reader = PdfReader(io.BytesIO(pdf_file.getvalue()))
                        for page in reader.pages:
                            page.merge_page(overlay)
                            merged_writer.add_page(page)

                    merged_output = io.BytesIO()
                    merged_writer.write(merged_output)
                    merged_output.seek(0)

                    final_size = len(merged_output.getvalue()) / (1024 * 1024)

                    st.success(f"✅ Successfully stamped all {len(uploaded_pdfs)} files and merged them into 1 document!")
                    st.info(f"📊 **Final Merged File Size:** `{final_size:.2f} MB`")

                    st.download_button(
                        label="⬇️ Download Stamped & Merged PDF",
                        data=merged_output.getvalue(),
                        file_name="Stamped_and_Merged_Document.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="batch_stamp_dl"
                    )

                except Exception as e:
                    st.error(f"Error batch processing PDFs: {str(e)}")

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

    uploaded_pdfs_merger = st.file_uploader("Upload PDFs to Merge", type=["pdf"], accept_multiple_files=True, key="merge_pdfs")

    if uploaded_pdfs_merger and len(uploaded_pdfs_merger) > 1:
        st.write(f"**Files selected to merge ({len(uploaded_pdfs_merger)}):**")
        for idx, pdf in enumerate(uploaded_pdfs_merger, 1):
            st.write(f"{idx}. {pdf.name}")

        if st.button("🔗 Merge PDFs", use_container_width=True, key="merge_btn"):
            try:
                merger_writer = PdfWriter()

                for pdf in uploaded_pdfs_merger:
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
    elif uploaded_pdfs_merger and len(uploaded_pdfs_merger) == 1:
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
