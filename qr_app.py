#!/usr/bin/env python3
"""
QR Code Generator Web App
Streamlit interface for non-technical users
"""

import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.base import QRModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw
import io

class CircleAllModuleDrawer(QRModuleDrawer):
    """Custom drawer that makes ALL modules circular"""
    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.imgDraw = ImageDraw.Draw(self.img._img)
    
    def drawrect(self, box, is_active):
        if not is_active:
            return
        
        x, y = box[0][0], box[0][1]
        size = box[1][0] - box[0][0]
        radius = size / 2
        center_x = x + radius
        center_y = y + radius
        circle_radius = radius * 0.85
        
        self.imgDraw.ellipse(
            [center_x - circle_radius, center_y - circle_radius,
             center_x + circle_radius, center_y + circle_radius],
            fill=self.img.paint_color
        )

def draw_circular_position_marker(draw, x, y, module_size):
    """Draw circular position detection pattern"""
    center_x = x + 3.5 * module_size
    center_y = y + 3.5 * module_size
    
    # Outer circle
    outer_r = 3.5 * module_size
    draw.ellipse(
        [center_x - outer_r, center_y - outer_r,
         center_x + outer_r, center_y + outer_r],
        fill='black'
    )
    
    # Middle white circle
    middle_r = 2.5 * module_size
    draw.ellipse(
        [center_x - middle_r, center_y - middle_r,
         center_x + middle_r, center_y + middle_r],
        fill='white'
    )
    
    # Inner black circle
    inner_r = 1.5 * module_size
    draw.ellipse(
        [center_x - inner_r, center_y - inner_r,
         center_x + inner_r, center_y + inner_r],
        fill='black'
    )

def replace_position_markers(img, box_size, border):
    """Replace square position markers with circular ones"""
    draw = ImageDraw.Draw(img)
    module_size = box_size
    offset = border * box_size
    marker_size = 7 * module_size
    
    # Calculate QR size
    img_size = img.size[0]
    qr_size = (img_size - 2 * offset) // module_size
    top_right_x = offset + (qr_size - 7) * module_size
    bottom_left_y = offset + (qr_size - 7) * module_size
    
    # Clear position marker areas
    draw.rectangle([offset, offset, offset + marker_size, offset + marker_size], fill='white')
    draw.rectangle([top_right_x, offset, top_right_x + marker_size, offset + marker_size], fill='white')
    draw.rectangle([offset, bottom_left_y, offset + marker_size, bottom_left_y + marker_size], fill='white')
    
    # Draw circular markers
    draw_circular_position_marker(draw, offset, offset, module_size)
    draw_circular_position_marker(draw, top_right_x, offset, module_size)
    draw_circular_position_marker(draw, offset, bottom_left_y, module_size)
    
    return img

def create_qr_code(url):
    """Generate QR code with circular dots"""
    box_size = 40
    border = 4
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=CircleAllModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(0, 0, 0))
    )
    
    img = replace_position_markers(img, box_size, border)
    img = img.resize((1000, 1000), Image.Resampling.LANCZOS)
    
    return img

def main():
    st.set_page_config(
        page_title="QR Code Generator",
        page_icon="🎯",
        layout="centered"
    )
    
    st.title("🎯 QR Code Generator")
    st.markdown("Generate stylish QR codes with circular dots for business cards and marketing materials")
    
    # Input section
    st.markdown("---")
    url = st.text_input(
        "Enter the URL:",
        placeholder="https://example.com",
        help="Enter the full URL including https://"
    )
    
    filename = st.text_input(
        "Filename (optional):",
        value="qr_code",
        help="Name for your QR code file (without extension)"
    )
    
    # Generate button
    if st.button("Generate QR Code", type="primary", use_container_width=True):
        if not url:
            st.error("⚠️ Please enter a URL")
        else:
            with st.spinner("Generating your QR code..."):
                try:
                    # Generate QR code
                    img = create_qr_code(url)
                    
                    # Display preview
                    st.success("✅ QR code generated successfully!")
                    st.markdown("---")
                    st.markdown("### Preview")
                    st.image(img, caption="Your QR Code", use_container_width=True)
                    
                    # Download buttons
                    st.markdown("### Download")
                    col1, col2 = st.columns(2)
                    
                    # PNG download
                    with col1:
                        buf = io.BytesIO()
                        img.save(buf, format='PNG')
                        png_data = buf.getvalue()
                        
                        st.download_button(
                            label="📥 Download PNG",
                            data=png_data,
                            file_name=f"{filename}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    # SVG info (would need potrace or conversion library)
                    with col2:
                        st.info("💡 SVG export coming soon")
                    
                    # Show URL for verification
                    st.markdown("---")
                    st.markdown(f"**QR Code URL:** `{url}`")
                    
                except Exception as e:
                    st.error(f"❌ Error generating QR code: {str(e)}")
    
    # Instructions
    st.markdown("---")
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Enter the URL** you want to encode (e.g., your website, product page, etc.)
        2. **Optional:** Change the filename if you want
        3. Click **Generate QR Code**
        4. Preview your QR code
        5. Click **Download PNG** to save it
        
        **Tips:**
        - Always include `https://` in your URL
        - Test the QR code with your phone camera before printing
        - QR codes are 1000x1000 pixels, perfect for print
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
        "Made with ❤️ for easy QR code generation"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()