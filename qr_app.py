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
import xml.etree.ElementTree as ET

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
    
    return img, qr

def draw_svg_position_marker(svg_elements, x, y, module_size):
    """Add SVG elements for circular position marker"""
    center_x = x + 3.5 * module_size
    center_y = y + 3.5 * module_size
    
    # Outer circle
    outer_r = 3.5 * module_size
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{outer_r}" fill="black"/>')
    
    # Middle white circle
    middle_r = 2.5 * module_size
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{middle_r}" fill="white"/>')
    
    # Inner black circle
    inner_r = 1.5 * module_size
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{inner_r}" fill="black"/>')

def create_svg(url):
    """Generate SVG QR code with circular dots"""
    box_size = 40
    border = 4
    size = 1000
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    matrix = qr.get_matrix()
    module_count = len(matrix)
    
    # Calculate scaling
    module_size = size / (module_count + 2 * border)
    offset = border * module_size
    radius = module_size * 0.42
    
    # Start SVG
    svg_elements = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="white"/>'
    ]
    
    # Function to check if position is in a position marker
    def is_position_marker(row, col):
        if 0 <= row < 7 and 0 <= col < 7:
            return True
        if 0 <= row < 7 and module_count - 7 <= col < module_count:
            return True
        if module_count - 7 <= row < module_count and 0 <= col < 7:
            return True
        return False
    
    # Draw data modules as circles
    for row in range(module_count):
        for col in range(module_count):
            if is_position_marker(row, col):
                continue
            
            if matrix[row][col]:
                cx = offset + col * module_size + module_size / 2
                cy = offset + row * module_size + module_size / 2
                svg_elements.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="black"/>')
    
    # Draw circular position markers
    draw_svg_position_marker(svg_elements, offset, offset, module_size)  # Top-left
    draw_svg_position_marker(svg_elements, offset + (module_count - 7) * module_size, offset, module_size)  # Top-right
    draw_svg_position_marker(svg_elements, offset, offset + (module_count - 7) * module_size, module_size)  # Bottom-left
    
    svg_elements.append('</svg>')
    
    return '\n'.join(svg_elements)

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
                    img, qr = create_qr_code(url)
                    svg_content = create_svg(url)
                    
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
                    
                    # SVG download
                    with col2:
                        st.download_button(
                            label="📥 Download SVG",
                            data=svg_content,
                            file_name=f"{filename}.svg",
                            mime="image/svg+xml",
                            use_container_width=True
                        )
                    
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
        5. Click **Download PNG** for raster graphics or **Download SVG** for vector graphics
        
        **Tips:**
        - Always include `https://` in your URL
        - Test the QR code with your phone camera before printing
        - Use PNG for general use (1000x1000 pixels)
        - Use SVG for high-quality print and scaling
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
        "Made by AR | DBS for easy QR code generation"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()