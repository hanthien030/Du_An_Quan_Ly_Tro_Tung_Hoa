from datetime import date

from flask import render_template


def _escape_pdf_text(value):
    return str(value).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def _build_fallback_pdf(lines):
    content_lines = ['BT', '/F1 12 Tf', '50 780 Td']
    for index, line in enumerate(lines):
        if index == 0:
            content_lines.append(f'({_escape_pdf_text(line)}) Tj')
        else:
            content_lines.append('0 -18 Td')
            content_lines.append(f'({_escape_pdf_text(line)}) Tj')
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
    hd = hoa_don.to_dict()
    hd.update(
        {
            'so_dien': hoa_don.thanh_toan.so_dien,
            'so_nuoc': hoa_don.thanh_toan.so_nuoc,
            'snapshot_don_gia_dien': float(hoa_don.snapshot_don_gia_dien or 0),
            'snapshot_don_gia_nuoc': float(hoa_don.snapshot_don_gia_nuoc or 0),
            'snapshot_gia_phong': float(hoa_don.snapshot_gia_phong or 0),
            'ghi_chu': hoa_don.thanh_toan.ghi_chu,
        }
    )

    try:
        from weasyprint import HTML

        html = render_template('pdf/hoa_don_pdf.html', hd=hd)
        return HTML(string=html).write_pdf()
    except Exception:
        lines = [
            'HOA DON TIEN PHONG',
            f'Phong: {hd["so_phong"]}',
            f'Khach: {hd["ho_ten"]}',
            f'Ky: {hd["thang"]}/{hd["nam"]}',
            f'Tong cong: {int(hd["tong_tien"]):,} VND',
            f'Ngay tao: {hd["ngay_tao"] or date.today().isoformat()}',
            'Fallback PDF generated because HTML to PDF rendering was unavailable.',
        ]
        return _build_fallback_pdf(lines)
