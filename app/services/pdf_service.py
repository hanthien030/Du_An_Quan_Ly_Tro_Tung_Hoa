from datetime import date
from io import BytesIO
from pathlib import Path

from flask import current_app, render_template


def _format_currency(value):
    return f"{int(round(float(value or 0))):,}".replace(",", ".") + " đ"


def _build_pdf_context(hoa_don):
    hd = hoa_don.to_dict()
    hd.update(
        {
            'so_dien': hoa_don.thanh_toan.so_dien,
            'so_nuoc': hoa_don.thanh_toan.so_nuoc,
            'snapshot_don_gia_dien': float(hoa_don.snapshot_don_gia_dien or 0),
            'snapshot_don_gia_nuoc': float(hoa_don.snapshot_don_gia_nuoc or 0),
            'snapshot_gia_phong': float(hoa_don.snapshot_gia_phong or 0),
            'ghi_chu': hoa_don.thanh_toan.ghi_chu,
            'status_label': 'Đã thanh toán' if hoa_don.thanh_toan.trang_thai == 'da_tt' else 'Chưa thanh toán',
            'formatted_ngay_tao': hoa_don.ngay_tao.strftime('%d/%m/%Y') if hoa_don.ngay_tao else date.today().strftime('%d/%m/%Y'),
        }
    )
    return hd


def _find_font(candidates):
    for font_path in candidates:
        if Path(font_path).exists():
            return font_path
    return None


def _wrap_text(draw, text, font, max_width):
    words = str(text or '').split()
    if not words:
        return ['']

    lines = []
    current = words[0]
    for word in words[1:]:
        trial = f'{current} {word}'
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _draw_right_text(draw, text, font, x_right, y, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    draw.text((x_right - width, y), text, font=font, fill=fill)


def _build_image_fallback_pdf(hd):
    from PIL import Image, ImageDraw, ImageFont

    regular_font_path = _find_font(
        [
            r'C:\Windows\Fonts\arial.ttf',
            r'C:\Windows\Fonts\tahoma.ttf',
            r'C:\Windows\Fonts\segoeui.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
        ]
    )
    bold_font_path = _find_font(
        [
            r'C:\Windows\Fonts\arialbd.ttf',
            r'C:\Windows\Fonts\tahomabd.ttf',
            r'C:\Windows\Fonts\segoeuib.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
        ]
    ) or regular_font_path

    if regular_font_path:
        font_small = ImageFont.truetype(regular_font_path, 22)
        font_regular = ImageFont.truetype(regular_font_path, 26)
        font_medium = ImageFont.truetype(regular_font_path, 30)
        font_bold = ImageFont.truetype(bold_font_path, 30)
        font_title = ImageFont.truetype(bold_font_path, 48)
        font_total = ImageFont.truetype(bold_font_path, 36)
    else:
        font_small = font_regular = font_medium = font_bold = font_title = font_total = ImageFont.load_default()

    image = Image.new('RGB', (1240, 1754), 'white')
    draw = ImageDraw.Draw(image)

    navy = '#19324a'
    blue = '#2f6fed'
    slate = '#4b5563'
    soft = '#f4f7fb'
    border = '#d6dde8'
    total_bg = '#eef4ff'
    success_bg = '#e7f8ee'
    warning_bg = '#fff5e5'
    success_fg = '#0f7b41'
    warning_fg = '#9a6700'

    margin = 80
    content_width = image.width - (margin * 2)

    draw.rounded_rectangle((margin, 70, margin + content_width, 250), radius=28, fill=navy)
    draw.text((margin + 45, 105), 'NHÀ TRỌ BÌNH DÂN', font=font_medium, fill='white')
    draw.text((margin + 45, 150), 'Hóa đơn tiền phòng', font=font_title, fill='white')
    draw.text((margin + 45, 210), f'Kỳ thanh toán {hd["thang"]}/{hd["nam"]}', font=font_medium, fill='#d9e4f7')

    badge_fill = success_bg if hd['trang_thai'] == 'da_tt' else warning_bg
    badge_text = success_fg if hd['trang_thai'] == 'da_tt' else warning_fg
    badge_box = (margin + content_width - 290, 105, margin + content_width - 40, 165)
    draw.rounded_rectangle(badge_box, radius=18, fill=badge_fill)
    draw.text((badge_box[0] + 24, badge_box[1] + 15), hd['status_label'], font=font_regular, fill=badge_text)

    info_top = 305
    info_bottom = 520
    draw.rounded_rectangle((margin, info_top, margin + content_width, info_bottom), radius=24, fill=soft, outline=border, width=2)

    left_x = margin + 40
    right_x = margin + (content_width // 2) + 20
    rows = [
        ('Phòng', f'Phòng {hd["so_phong"]}', left_x, info_top + 34),
        ('Khách thuê', hd['ho_ten'], left_x, info_top + 120),
        ('Ngày tạo', hd['formatted_ngay_tao'], right_x, info_top + 34),
        ('Chỉ số', f'{hd["so_dien"]} kWh • {hd["so_nuoc"]} m³', right_x, info_top + 120),
    ]
    for label, value, x_pos, y_pos in rows:
        draw.text((x_pos, y_pos), label, font=font_small, fill=slate)
        draw.text((x_pos, y_pos + 34), str(value), font=font_bold, fill=navy)

    table_top = 575
    row_height = 92
    table_left = margin
    table_right = margin + content_width

    draw.rounded_rectangle((table_left, table_top, table_right, table_top + 78), radius=18, fill=blue)
    columns = [table_left + 28, table_left + 470, table_left + 700, table_right - 30]
    headers = ['Khoản mục', 'Số lượng', 'Đơn giá', 'Thành tiền']
    for idx, header in enumerate(headers):
        if idx == 3:
            _draw_right_text(draw, header, font_bold, columns[idx], table_top + 22, 'white')
        else:
            draw.text((columns[idx], table_top + 22), header, font=font_bold, fill='white')

    line_y = table_top + 96
    items = [
        ('Tiền phòng', '1 tháng', _format_currency(hd['snapshot_gia_phong']), _format_currency(hd['tien_phong'])),
        ('Tiền điện', f'{hd["so_dien"]} kWh', f'{_format_currency(hd["snapshot_don_gia_dien"])} / kWh', _format_currency(hd['tien_dien'])),
        ('Tiền nước', f'{hd["so_nuoc"]} m³', f'{_format_currency(hd["snapshot_don_gia_nuoc"])} / m³', _format_currency(hd['tien_nuoc'])),
        ('Phí dịch vụ', 'Wifi + Vệ sinh + Gửi xe', '—', _format_currency(hd['phi_dich_vu'])),
    ]
    for idx, (title, quantity, unit_price, amount) in enumerate(items):
        row_top = line_y + idx * row_height
        row_bottom = row_top + row_height - 8
        if idx % 2 == 0:
            draw.rounded_rectangle((table_left, row_top - 8, table_right, row_bottom), radius=12, fill='#fbfdff')
        draw.text((columns[0], row_top + 16), title, font=font_bold, fill=navy)
        qty_lines = _wrap_text(draw, quantity, font_regular, 210)
        for line_idx, line in enumerate(qty_lines):
            draw.text((columns[1], row_top + 16 + line_idx * 28), line, font=font_regular, fill=slate)
        unit_lines = _wrap_text(draw, unit_price, font_regular, 210)
        for line_idx, line in enumerate(unit_lines):
            draw.text((columns[2], row_top + 16 + line_idx * 28), line, font=font_regular, fill=slate)
        _draw_right_text(draw, amount, font_bold, columns[3], row_top + 16, navy)
        draw.line((table_left + 12, row_bottom + 8, table_right - 12, row_bottom + 8), fill=border, width=1)

    total_top = line_y + len(items) * row_height + 26
    draw.rounded_rectangle((table_left, total_top, table_right, total_top + 120), radius=22, fill=total_bg, outline=border, width=2)
    draw.text((table_left + 30, total_top + 34), 'TỔNG CỘNG', font=font_total, fill=navy)
    _draw_right_text(draw, _format_currency(hd['tong_tien']), font_total, table_right - 28, total_top + 32, blue)

    footer_top = total_top + 170
    draw.text((margin, footer_top), 'Ghi chú', font=font_medium, fill=navy)
    note_lines = _wrap_text(draw, hd['ghi_chu'] or 'Không có', font_regular, content_width - 60)
    note_box_bottom = footer_top + 60 + max(1, len(note_lines)) * 34 + 28
    draw.rounded_rectangle((margin, footer_top + 42, table_right, note_box_bottom), radius=20, fill='white', outline=border, width=2)
    for idx, line in enumerate(note_lines):
        draw.text((margin + 24, footer_top + 66 + idx * 34), line, font=font_regular, fill=slate)

    sign_top = note_box_bottom + 90
    draw.text((margin + 110, sign_top), 'Người thuê', font=font_medium, fill=navy)
    draw.text((table_right - 270, sign_top), 'Chủ nhà trọ', font=font_medium, fill=navy)
    draw.line((margin + 40, sign_top + 130, margin + 310, sign_top + 130), fill=slate, width=2)
    draw.line((table_right - 330, sign_top + 130, table_right - 40, sign_top + 130), fill=slate, width=2)

    buffer = BytesIO()
    image.save(buffer, format='PDF', resolution=150.0)
    return buffer.getvalue()


def _build_text_fallback_pdf(lines):
    content_lines = ['BT', '/F1 12 Tf', '50 780 Td']
    for index, line in enumerate(lines):
        escaped = str(line).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        if index == 0:
            content_lines.append(f'({escaped}) Tj')
        else:
            content_lines.append('0 -18 Td')
            content_lines.append(f'({escaped}) Tj')
    content_lines.append('ET')

    content = '\n'.join(content_lines).encode('latin-1', errors='replace')
    objects = [
        b'1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj',
        b'2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj',
        b'3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj',
        b'4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj',
        f'5 0 obj << /Length {len(content)} >> stream\n'.encode('latin-1') + content + b'\nendstream endobj',
    ]

    pdf = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj + b'\n')

    xref_pos = len(pdf)
    pdf.extend(f'xref\n0 {len(objects) + 1}\n'.encode('latin-1'))
    pdf.extend(b'0000000000 65535 f \n')
    for offset in offsets[1:]:
        pdf.extend(f'{offset:010d} 00000 n \n'.encode('latin-1'))
    pdf.extend(
        (
            f'trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n'
            f'startxref\n{xref_pos}\n%%EOF'
        ).encode('latin-1')
    )
    return bytes(pdf)


def generate_pdf_bytes(hoa_don):
    hd = _build_pdf_context(hoa_don)

    try:
        from weasyprint import HTML

        html = render_template('pdf/hoa_don_pdf.html', hd=hd)
        return HTML(string=html, base_url=current_app.root_path).write_pdf()
    except Exception as exc:
        current_app.logger.warning('Falling back to non-WeasyPrint invoice PDF: %s', exc, exc_info=True)
        try:
            return _build_image_fallback_pdf(hd)
        except Exception as image_exc:
            current_app.logger.warning('Image-based PDF fallback failed: %s', image_exc, exc_info=True)
            lines = [
                'HOA DON TIEN PHONG',
                f'Phong: {hd["so_phong"]}',
                f'Khach: {hd["ho_ten"]}',
                f'Ky: {hd["thang"]}/{hd["nam"]}',
                f'Tong cong: {int(hd["tong_tien"]):,} VND',
                f'Ngay tao: {hd["ngay_tao"] or date.today().isoformat()}',
                'Fallback text PDF was used because richer rendering was unavailable.',
            ]
            return _build_text_fallback_pdf(lines)
