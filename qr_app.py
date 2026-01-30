#!/usr/bin/env python3
"""
QR Code Generator Web App
Streamlit interface for non-technical users
Bilingual: English and Hungarian
Supports both elegant circular and classic square styles
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
        'generate_button': 'Generate QR Codes',
        'error_empty': '⚠️ Please enter a URL',
        'generating': 'Generating your QR codes...',
        'success': '✅ QR codes generated successfully!',
        'preview_title': '### Preview',
        'elegant_title': '#### Elegant Style (Circular Dots)',
        'classic_title': '#### Classic Style (Square)',
        'download_title': '### Download',
        'download_elegant_png': '📥 Elegant PNG',
        'download_elegant_svg': '📥 Elegant SVG',
        'download_classic_png': '📥 Classic PNG',
        'download_classic_svg': '📥 Classic SVG',
        'qr_url_label': '**QR Code URL:**',
        'qr_info': '💡 QR Code Version: {version} | Modules: {size}x{size}',
        'instructions_title': 'ℹ️ How to use',
        'instructions': """
        1. **Enter the URL** you want to encode (e.g., `24.hu`)
        2. **Optional:** Change the filename if you want
        3. Click **Generate QR Codes**
        4. Preview both styles
        5. Download your preferred format (PNG or SVG) in either style
        
        **Styles:**
        - **Elegant:** Circular dots with rounded position markers (modern look)
        - **Classic:** Traditional square modules (maximum compatibility)
        
        **Tips:**
        - For cleaner QR codes, use short URLs without https:// (e.g., `24.hu`)
        - Modern phones will recognize domains automatically
        - Test the QR code with your phone camera before printing
        - Use PNG for general use (1000x1000 pixels)
        - Use SVG for high-quality print and infinite scaling
        - Shorter URLs create simpler, less "busy" QR codes
        """,
        'footer': 'Made by AR | DBS for easy QR code generation'
    },
    'hu': {
        'title': '🎯 QR Kód Generátor',
        'subtitle': 'Készíts stílusos QR kódokat kör alakú pontokkal névjegykártyákhoz és marketing anyagokhoz',
        'url_label': 'Add meg az URL-t:',
        'url_placeholder': '24.hu',
        'url_help': 'Írd be az URL-t (a https:// elhagyható, a modern telefonok felismerik)',
        'filename_label': 'Fájlnév (opcionális):',
        'filename_help': 'A QR kód fájl neve (kiterjesztés nélkül)',
        'generate_button': 'QR Kódok Létrehozása',
        'error_empty': '⚠️ Kérlek adj meg egy URL-t',
        'generating': 'QR kódok generálása...',
        'success': '✅ QR kódok sikeresen létrehozva!',
        'preview_title': '### Előnézet',
        'elegant_title': '#### Elegáns Stílus (Kör alakú pontok)',
        'classic_title': '#### Klasszikus Stílus (Négyzet)',
        'download_title': '### Letöltés',
        'download_elegant_png': '📥 Elegáns PNG',
        'download_elegant_svg': '📥 Elegáns SVG',
        'download_classic_png': '📥 Klasszikus PNG',
        'download_classic_svg': '📥 Klasszikus SVG',
        'qr_url_label': '**QR Kód URL:**',
        'qr_info': '💡 QR Kód Verzió: {version} | Modulok: {size}x{size}',
        'instructions_title': 'ℹ️ Használati útmutató',
        'instructions': """
        1. **Írd be az URL-t** amit kódolni szeretnél (pl.: `24.hu`)
        2. **Opcionális:** Módosítsd a fájlnevet ha szeretnéd
        3. Kattints a **QR Kódok Létrehozása** gombra
        4. Nézd meg mindkét stílust az előnézetben
        5. Töltsd le a választott formátumot (PNG vagy SVG) bármelyik stílusban
        
        **Stílusok:**
        - **Elegáns:** Kör alakú pontok kerek pozíció jelzőkkel (modern megjelenés)
        - **Klasszikus:** Hagyományos négyzet modulok (maximális kompatibilitás)
        
        **Tippek:**
        - Tisztább QR kódokhoz használj rövid URL-t https:// nélkül (pl.: `24.hu`)
        - A modern telefonok automatikusan felismerik a domain neveket
        - Nyomtatás előtt teszteld le a QR kódot a telefonod kamerájával
        - Használd a PNG-t általános célra (1000x1000 pixel)
        - Használd az SVG-t nyomtatáshoz és végtelen méretezéshez
        - A rövidebb URL-ek egyszerűbb, kevésbé zsúfolt QR kódokat eredményeznek
        """,
        'footer': 'Készítette: AR | DBS egyszerű QR kód generáláshoz'
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

def create_qr_code_elegant(url):
    """Generate elegant QR code with circular dots"""
    box_size = 40
    border = 4
    
    url = normalize_url(url)
    
    qr = qrcode.QRCode(
        version=None,
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

def create_qr_code_classic(url):
    """Generate classic QR code with square modules"""
    box_size = 40
    border = 4
    
    url = normalize_url(url)
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    # Classic style - standard square modules
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((1000, 1000), Image.Resampling.LANCZOS)
    
    return img, qr, url

def create_svg_elegant(url):
    """Generate elegant SVG QR code with circular dots"""
    box_size = 40
    border = 4
    size = 1000
    
    url = normalize_url(url)
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(url)
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
    
    # Draw ALL data modules as circles first
    for row in range(module_count):
        for col in range(module_count):
            if matrix[row][col]:
                cx = offset + col * module_size + module_size / 2
                cy = offset + row * module_size + module_size / 2
                svg_elements.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="black"/>')
    
    # Cover position marker areas with LARGER white rectangles (8x8 to include separator)
    marker_clear_size = 8 * module_size
    
    # Top-left - clear 8x8 area
    svg_elements.append(f'<rect x="{offset}" y="{offset}" width="{marker_clear_size}" height="{marker_clear_size}" fill="white"/>')
    
    # Top-right - clear 8x8 area
    x_tr_clear = offset + (module_count - 8) * module_size
    svg_elements.append(f'<rect x="{x_tr_clear}" y="{offset}" width="{marker_clear_size}" height="{marker_clear_size}" fill="white"/>')
    
    # Bottom-left - clear 8x8 area
    y_bl_clear = offset + (module_count - 8) * module_size
    svg_elements.append(f'<rect x="{offset}" y="{y_bl_clear}" width="{marker_clear_size}" height="{marker_clear_size}" fill="white"/>')
    
    # Draw the circular position markers (centered in 7x7 grid)
    # Top-left
    center_x = offset + 3.5 * module_size
    center_y = offset + 3.5 * module_size
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{3.5 * module_size}" fill="black"/>')
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{2.5 * module_size}" fill="white"/>')
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{1.5 * module_size}" fill="black"/>')
    
    # Top-right
    center_x = offset + (module_count - 7) * module_size + 3.5 * module_size
    center_y = offset + 3.5 * module_size
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{3.5 * module_size}" fill="black"/>')
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{2.5 * module_size}" fill="white"/>')
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{1.5 * module_size}" fill="black"/>')
    
    # Bottom-left
    center_x = offset + 3.5 * module_size
    center_y = offset + (module_count - 7) * module_size + 3.5 * module_size
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{3.5 * module_size}" fill="black"/>')
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{2.5 * module_size}" fill="white"/>')
    svg_elements.append(f'<circle cx="{center_x}" cy="{center_y}" r="{1.5 * module_size}" fill="black"/>')
    
    svg_elements.append('</svg>')
    
    return '\n'.join(svg_elements)

def create_svg_classic(url):
    """Generate classic SVG QR code with square modules"""
    box_size = 40
    border = 4
    size = 1000
    
    url = normalize_url(url)
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    matrix = qr.get_matrix()
    module_count = len(matrix)
    
    module_size = size / (module_count + 2 * border)
    offset = border * module_size
    
    svg_elements = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="white"/>'
    ]
    
    for row in range(module_count):
        for col in range(module_count):
            if matrix[row][col]:
                x = offset + col * module_size
                y = offset + row * module_size
                svg_elements.append(f'<rect x="{x}" y="{y}" width="{module_size}" height="{module_size}" fill="black"/>')
    
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
    
    # Get current language translations
    t = TRANSLATIONS[st.session_state.language]
    
    # Language switcher - positioned to the left, before title
    current_flag = "🇭🇺" if st.session_state.language == 'hu' else "🇬🇧"
    if st.button(current_flag, key="lang_switch", help="Switch language"):
        st.session_state.language = 'hu' if st.session_state.language == 'en' else 'en'
        st.rerun()
    
    # Title and subtitle
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
                    # Generate both styles
                    img_elegant, qr_elegant, normalized_url = create_qr_code_elegant(url)
                    svg_elegant = create_svg_elegant(url)
                    
                    img_classic, qr_classic, _ = create_qr_code_classic(url)
                    svg_classic = create_svg_classic(url)
                    
                    # Display preview
                    st.success(t['success'])
                    st.markdown("---")
                    st.markdown(t['preview_title'])
                    
                    # Show both styles side by side
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(t['elegant_title'])
                        st.image(img_elegant, use_container_width=True)
                    
                    with col2:
                        st.markdown(t['classic_title'])
                        st.image(img_classic, use_container_width=True)
                    
                    # Download buttons
                    st.markdown("---")
                    st.markdown(t['download_title'])
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    # Elegant PNG
                    with col1:
                        buf = io.BytesIO()
                        img_elegant.save(buf, format='PNG')
                        st.download_button(
                            label=t['download_elegant_png'],
                            data=buf.getvalue(),
                            file_name=f"{filename}_elegant.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    # Elegant SVG
                    with col2:
                        st.download_button(
                            label=t['download_elegant_svg'],
                            data=svg_elegant,
                            file_name=f"{filename}_elegant.svg",
                            mime="image/svg+xml",
                            use_container_width=True
                        )
                    
                    # Classic PNG
                    with col3:
                        buf = io.BytesIO()
                        img_classic.save(buf, format='PNG')
                        st.download_button(
                            label=t['download_classic_png'],
                            data=buf.getvalue(),
                            file_name=f"{filename}_classic.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    # Classic SVG
                    with col4:
                        st.download_button(
                            label=t['download_classic_svg'],
                            data=svg_classic,
                            file_name=f"{filename}_classic.svg",
                            mime="image/svg+xml",
                            use_container_width=True
                        )
                    
                    # Show URL for verification
                    st.markdown("---")
                    st.markdown(f"{t['qr_url_label']} `{normalized_url}`")
                    st.info(t['qr_info'].format(version=qr_elegant.version, size=len(qr_elegant.get_matrix())))
                    
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