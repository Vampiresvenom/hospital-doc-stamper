import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime

st.set_page_config(page_title="Hospital Document Stamper", layout="centered", page_icon="🏥")

st.title("🏥 Hospital Document Stamping Tool")
st.write("Upload a scanned or digital PDF to automatically apply your hospital logo/stamp and timestamp.")

st.info("💡 **Note:** You can use your hospital logo image right now for testing. Once the official stamp is approved, simply upload the new stamp image here!")

# 1. File Uploaders
col1, col2 = st.columns(2)

with col1:
    uploaded_pdf = st.file_uploader("1. Upload PDF Document", type=["pdf"])

with col2:
    uploaded_stamp = st.file_uploader("2. Upload Hospital Logo / Stamp (PNG/JPG)", type=["png", "jpg", "jpeg"])

# 2. Options & Preview
if uploaded_stamp:
    st.image(uploaded_stamp, caption="Selected Logo/Stamp Preview", width=120)

position = st.selectbox("Select Stamp Position on PDF", ["Bottom Right", "Top Right", "Bottom Left", "Top Left"])

if uploaded_pdf and uploaded_stamp:
    if st.button("🚀 Apply Stamp & Generate PDF", use_container_width=True):
        try:
            reader = PdfReader(uploaded_pdf)
            writer = PdfWriter()

            # Coordinates for standard letter/A4 (~ 612 x 792 pt)
            coords = {
                "Bottom Right": (430, 40),
                "Top Right": (430, 680),
                "Bottom Left": (40, 40),
                "Top Left": (40, 680)
            }
            x, y = coords[position]

            # Build Stamp Overlay Canvas
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(612, 792))

            # FIX: Wrap BytesIO stream in ImageReader
            stamp_img = ImageReader(io.BytesIO(uploaded_stamp.getvalue()))
            can.drawImage(stamp_img, x, y, width=130, height=60, mask='auto', preserveAspectRatio=True)

            # Add Live Timestamp Text
            now_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")
            can.setFont("Helvetica-Bold", 8)
            can.drawString(x, y - 10, f"STAMPED: {now_str}")

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
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
