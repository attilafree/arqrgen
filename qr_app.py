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
        'title': '🎯 QR Code Generator',
        'subtitle': 'Generate stylish QR codes with circular dots for business cards and marketing materials',
        'url_label': 'Enter the URL:',
        'url_placeholder': '24.hu',
        'url_help': 'Enter your URL (you can include https:// for compatibility, but it\'s not required)',
        'filename_label': 'Filename (optional):',
        'filename_help': 'Name for your QR code file (without extension)',
        'generate_button': 'Generate QR Code',
        'error_empty': '⚠️ Please enter a URL',
        'generating': 'Generating your QR code...',
        'success': '✅ QR code generated successfully!',
        'preview_title': '### Preview',
        'download_title': '### Download',
        'download_png': '📥 Download PNG',
        'download_svg': '📥 Download SVG',
        'qr_url_label': '**QR Code URL:**',
        'qr_info': '💡 QR Code Version: {version} | Modules: {size}x{size}',
        'instructions_title': 'ℹ️ How to use',
        'instructions': """
        1. **Enter the URL** you want to encode (e.g., `24.hu`)
        2. **Optional:** Change the filename if you want
        3. Click **Generate QR Code**
        4. Preview your QR code
        5. Click **Download PNG** for raster graphics or **Download SVG** for vector graphics
        
        **Tips:**
        - For cleaner QR codes, use short URLs without https:// (e.g., `24.hu`)
        - Modern phones will recognize domains automatically
        - Test the QR code with your phone camera before printing
        - Use PNG for general use (1000x1000 pixels)
        - Use SVG for high-quality print and infinite scaling
        - Shorter URLs create simpler, less "busy" QR codes
        """,
        'footer': 'Made by AR for easy QR code generation',
        'language_label': 'Language / Nyelv'
    },
    'hu': {
        'title': '🎯 QR Kód Generátor',
        'subtitle': 'Készíts stílusos QR kódokat kör alakú pontokkal névjegykártyákhoz és marketing anyagokhoz',
        'url_label': 'Add meg az URL-t:',
        'url_placeholder': '24.hu',
        'url_help': 'Írd be az URL-t (a https:// elhagyható, a modern telefonok felismerik)',
        'filename_label': 'Fájlnév (opcionális):',
        'filename_help': 'A QR kód fájl neve (kiterjesztés nélkül)',
        'generate_button': 'QR Kód Létrehozása',
        'error_empty': '⚠️ Kérlek adj meg egy URL-t',
        'generating': 'QR kód generálása...',
        'success': '✅ QR kód sikeresen létrehozva!',
        'preview_title': '### Előnézet',
        'download_title': '### Letöltés',
        'download_png': '📥 PNG Letöltése',
        'download_svg': '📥 SVG Letöltése',
        'qr_url_label': '**QR Kód URL:**',
        'qr_info': '💡 QR Kód Verzió: {version} | Modulok: {size}x{size}',
        'instructions_title': 'ℹ️ Használati útmutató',
        'instructions': """
        1. **Írd be az URL-t** amit kódolni szeretnél (pl.: `24.hu`)
        2. **Opcionális:** Módosítsd a fájlnevet ha szeretnéd
        3. Kattints a **QR Kód Létrehozása** gombra
        4. Nézd meg az előnézetet
        5. Kattints a **PNG Letöltése** vagy **SVG Letöltése** gombra
        
        **Tippek:**
        - Tisztább QR kódokhoz használj rövid URL-t https:// nélkül (pl.: `24.hu`)
        - A modern telefonok automatikusan felismerik a domain neveket
        - Nyomtatás előtt teszteld le a QR kódot a telefonod kamerájával
        - Használd a PNG-t általános célra (1000x1000 pixel)
        - Használd az SVG-t nyomtatáshoz és végtelen méretezéshez
        - A rövidebb URL-ek egyszerűbb, kevésbé zsúfolt QR kódokat eredményeznek
        """,
        'footer': 'Készítette: AR egyszerű QR kód generáláshoz',
        'language_label': 'Language / Nyelv'
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

def normalize_url(url):
    """Clean up the URL but don't force https://"""
    return url.strip()

def create_qr_code(url):
    """Generate QR code with circular dots"""
    box_size = 40
    border = 4
    
    # Normalize URL
    url = normalize_url(url)
    
    qr = qrcode.QRCode(
        version=None,  # Auto-size
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
    
    return img, qr, url

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
    
    # Normalize URL
    url = normalize_url(url)
    
    qr = qrcode.QRCode(
        version=None,  # Auto-size
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
    
    # Initialize language in session state
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    # Language selector in sidebar for easy access
    with st.sidebar:
        st.markdown("### 🌐 Language / Nyelv")
        lang_option = st.radio(
            "",
            options=['en', 'hu'],
            format_func=lambda x: '🇬🇧 English' if x == 'en' else '🇭🇺 Magyar',
            index=0 if st.session_state.language == 'en' else 1,
            key='lang_selector'
        )
        if lang_option != st.session_state.language:
            st.session_state.language = lang_option
            st.rerun()
    
    # Get current language translations
    t = TRANSLATIONS[st.session_state.language]
    
    st.title(t['title'])
    st.markdown(t['subtitle'])
    
    # Input section
    st.markdown("---")
    url = st.text_input(
        t['url_label'],
        placeholder=t['url_placeholder'],
        help=t['url_help']
    )
    
    filename = st.text_input(
        t['filename_label'],
        value="qr_code",
        help=t['filename_help']
    )
    
    # Generate button
    if st.button(t['generate_button'], type="primary", use_container_width=True):
        if not url:
            st.error(t['error_empty'])
        else:
            with st.spinner(t['generating']):
                try:
                    # Generate QR code
                    img, qr, normalized_url = create_qr_code(url)
                    svg_content = create_svg(url)
                    
                    # Display preview
                    st.success(t['success'])
                    st.markdown("---")
                    st.markdown(t['preview_title'])
                    st.image(img, caption="QR Code", use_container_width=True)
                    
                    # Download buttons
                    st.markdown(t['download_title'])
                    col1, col2 = st.columns(2)
                    
                    # PNG download
                    with col1:
                        buf = io.BytesIO()
                        img.save(buf, format='PNG')
                        png_data = buf.getvalue()
                        
                        st.download_button(
                            label=t['download_png'],
                            data=png_data,
                            file_name=f"{filename}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    # SVG download
                    with col2:
                        st.download_button(
                            label=t['download_svg'],
                            data=svg_content,
                            file_name=f"{filename}.svg",
                            mime="image/svg+xml",
                            use_container_width=True
                        )
                    
                    # Show URL for verification
                    st.markdown("---")
                    st.markdown(f"{t['qr_url_label']} `{normalized_url}`")
                    st.info(t['qr_info'].format(version=qr.version, size=len(qr.get_matrix())))
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Instructions
    st.markdown("---")
    with st.expander(t['instructions_title']):
        st.markdown(t['instructions'])
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9em;'>"
        f"{t['footer']}"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()