from flask import Blueprint, render_template

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
@web_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@web_bp.route('/phong')
def phong_index():
    return render_template('phong/index.html')


@web_bp.route('/khach-thue')
def khach_thue_index():
    return render_template('khach_thue/index.html')


@web_bp.route('/hop-dong')
def hop_dong_index():
    return render_template('hop_dong/index.html')


@web_bp.route('/bang-gia')
def bang_gia_index():
    return render_template('bang_gia/index.html')


@web_bp.route('/thanh-toan')
def thanh_toan_index():
    return render_template('thanh_toan/index.html')


@web_bp.route('/hoa-don')
def hoa_don_index():
    return render_template('hoa_don/index.html')


@web_bp.route('/thong-ke')
def thong_ke_index():
    return render_template('thong_ke/index.html')
