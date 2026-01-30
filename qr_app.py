#!/usr/bin/env python3
"""
QR Code Generator Web App
Streamlit interface for non-technical users
Bilingual: English and Hungarian
"""

import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.base import QRModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw
import io

# Language dictionary
TRANSLATIONS = {
    'en': {
        'title': 'QR Code Generator',
        'subtitle': 'Generate stylish QR codes with circular dots',
        'url_label': 'Enter URL',
        'url_placeholder': '24.hu',
        'filename_label': 'Filename',
        'generate_button': 'Generate QR Code',
        'error_empty': '⚠️ Please enter a URL',
        'generating': 'Generating...',
        'success': '✅ Success!',
        'preview_title': 'Preview',
        'download_title': 'Download',
        'download_png': '📥 PNG',
        'download_svg': '📥 SVG',
        'qr_url_label': 'URL:',
        'instructions_title': 'How to use',
        'instructions': """
**Quick Guide:**
1. Enter your URL (e.g., `24.hu`)
2. Click Generate
3. Download PNG or SVG

**Tips:**
- Shorter URLs = cleaner QR codes
- Modern phones read URLs without https://
- Test before printing
        """,
        'footer': 'Made by AR | DBS'
    },
    'hu': {
        'title': 'QR Kód Generátor',
        'subtitle': 'Készíts stílusos QR kódokat',
        'url_label': 'URL megadása',
        'url_placeholder': '24.hu',
        'filename_label': 'Fájlnév',
        'generate_button': 'QR Kód Létrehozása',
        'error_empty': '⚠️ Kérlek adj meg egy URL-t',
        'generating': 'Generálás...',
        'success': '✅ Kész!',
        'preview_title': 'Előnézet',
        'download_title': 'Letöltés',
        'download_png': '📥 PNG',
        'download_svg': '📥 SVG',
        'qr_url_label': 'URL:',
        'instructions_title': 'Használat',
        'instructions': """
**Gyors útmutató:**
1. Írd be az URL-t (pl.: `24.hu`)
2. Kattints a Generálás gombra
3. Töltsd le PNG vagy SVG formátumban

**Tippek:**
- Rövidebb URL = tisztább QR kód
- Modern telefonok https:// nélkül is felismerik
- Nyomtatás előtt teszteld
        """,
        'footer': 'Készítette: AR | DBS'
    }
}

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
    
    outer_r = 3.5 * module_size
    draw.ellipse([center_x - outer_r, center_y - outer_r, center_x + outer_r, center_y + outer_r], fill='black')
    
    middle_r = 2.5 * module_size
    draw.ellipse([center_x - middle_r, center_y - middle_r, center_x + middle_r, center_y + middle_r], fill='white')
    
    inner_r = 1.5 * module_size
    draw.ellipse([center_x - inner_r, center_y - inner_r, center_x + inner_r, center_y + inner_r], fill='black')

def replace_position_markers(img, box_size, border):
    """Replace square position markers with circular ones"""
    draw = ImageDraw.Draw(img)
    module_size = box_size
    offset = border * box_size
    marker_size = 7 * module_size
    
    img_size = img.size[0]
    qr_size = (img_size - 2 * offset) // module_size
    top_right_x = offset + (qr_size - 7) * module_size
    bottom_left_y = offset + (qr_size - 7) * module_size
    
    draw.rectangle([offset, offset, offset + marker_size, offset + marker_size], fill='white')
    draw.rectangle([top_right_x, offset, top_right_x + marker_size, offset + marker_size], fill='white')
    draw.rectangle([offset, bottom_left_y, offset + marker_size, bottom_left_y + marker_size], fill='white')
    
    draw_circular_position_marker(draw, offset, offset, module_size)
    draw_circular_position_marker(draw, top_right_x, offset, module_size)
    draw_circular_position_marker(draw, offset, bottom_left_y, module_size)
    
    return img

def create_qr_code(url):
    """Generate QR code with circular dots"""
    box_size = 40
    border = 4
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(url.strip())
    qr.make(fit=True)
    
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=CircleAllModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=(0, 0, 0))
    )
    
    img = replace_position_markers(img, box_size, border)
    img = img.resize((1000, 1000), Image.Resampling.LANCZOS)
    
    return img, qr, url.strip()

def draw_svg_position_marker(svg_elements, x, y, module_size):
    """Add SVG elements for circular position marker"""
    center_x = x + 3.5 * module_size
    center_y = y + 3.5 * module_size
    
    outer_r = 3.5 * module_size
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{outer_r}" fill="black"/>')
    
    middle_r = 2.5 * module_size
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{middle_r}" fill="white"/>')
    
    inner_r = 1.5 * module_size
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{inner_r}" fill="black"/>')

def create_svg(url):
    """Generate SVG QR code with circular dots"""
    box_size = 40
    border = 4
    size = 1000
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(url.strip())
    qr.make(fit=True)
    
    matrix = qr.get_matrix()
    module_count = len(matrix)
    
    module_size = size / (module_count + 2 * border)
    offset = border * module_size
    radius = module_size * 0.42
    
    svg_elements = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="white"/>'
    ]
    
    def is_position_marker(row, col):
        if 0 <= row < 7 and 0 <= col < 7:
            return True
        if 0 <= row < 7 and module_count - 7 <= col < module_count:
            return True
        if module_count - 7 <= row < module_count and 0 <= col < 7:
            return True
        return False
    
    for row in range(module_count):
        for col in range(module_count):
            if is_position_marker(row, col):
                continue
            
            if matrix[row][col]:
                cx = offset + col * module_size + module_size / 2
                cy = offset + row * module_size + module_size / 2
                svg_elements.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="black"/>')
    
    draw_svg_position_marker(svg_elements, offset, offset, module_size)
    draw_svg_position_marker(svg_elements, offset + (module_count - 7) * module_size, offset, module_size)
    draw_svg_position_marker(svg_elements, offset, offset + (module_count - 7) * module_size, module_size)
    
    svg_elements.append('</svg>')
    
    return '\n'.join(svg_elements)

def main():
    st.set_page_config(
        page_title="QR Code Generator",
        page_icon="🎯",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    t = TRANSLATIONS[st.session_state.language]
    
    # Minimal custom CSS
    st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .controls-row {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-bottom: 30px;
    }
    .flag-button {
        font-size: 28px;
        cursor: pointer;
        user-select: none;
        transition: transform 0.2s;
    }
    .flag-button:hover {
        transform: scale(1.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with language switch
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.title(f"🎯 {t['title']}")
        st.caption(t['subtitle'])
    
    with col2:
        st.write("")  # Spacing
        current_flag = "🇭🇺" if st.session_state.language == 'hu' else "🇬🇧"
        if st.button(current_flag, key="lang", help="Switch language", use_container_width=True):
            st.session_state.language = 'hu' if st.session_state.language == 'en' else 'en'
            st.rerun()
    
    st.divider()
    
    # Input section
    url = st.text_input(
        t['url_label'],
        placeholder=t['url_placeholder'],
        label_visibility="visible"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        filename = st.text_input(
            t['filename_label'],
            value="qr_code",
            label_visibility="visible"
        )
    
    # Generate button
    if st.button(t['generate_button'], type="primary", use_container_width=True):
        if not url:
            st.error(t['error_empty'])
        else:
            with st.spinner(t['generating']):
                try:
                    img, qr, normalized_url = create_qr_code(url)
                    svg_content = create_svg(url)
                    
                    st.success(t['success'])
                    st.divider()
                    
                    # Preview
                    st.subheader(t['preview_title'])
                    st.image(img, use_container_width=True)
                    
                    # Download buttons
                    st.subheader(t['download_title'])
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        buf = io.BytesIO()
                        img.save(buf, format='PNG')
                        st.download_button(
                            label=t['download_png'],
                            data=buf.getvalue(),
                            file_name=f"{filename}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.download_button(
                            label=t['download_svg'],
                            data=svg_content,
                            file_name=f"{filename}.svg",
                            mime="image/svg+xml",
                            use_container_width=True
                        )
                    
                    st.divider()
                    st.caption(f"{t['qr_url_label']} `{normalized_url}`")
                    
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    
    # Instructions
    st.divider()
    with st.expander(t['instructions_title']):
        st.markdown(t['instructions'])
    
    # Footer
    st.divider()
    st.caption(f"<center>{t['footer']}</center>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()