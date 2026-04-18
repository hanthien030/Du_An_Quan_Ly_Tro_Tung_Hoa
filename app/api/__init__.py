from flask import Blueprint

def register_blueprints(app):
    from app.api.phong      import bp as phong_bp
    from app.api.khach_thue import bp as khach_bp
    from app.api.hop_dong   import bp as hopdong_bp
    from app.api.bang_gia   import bp as banggia_bp
    from app.api.thanh_toan import bp as thanhtoan_bp
    from app.api.hoa_don    import bp as hoadon_bp
    from app.api.thong_ke   import bp as thongke_bp

    app.register_blueprint(phong_bp,     url_prefix='/api/phong')
    app.register_blueprint(khach_bp,     url_prefix='/api/khach-thue')
    app.register_blueprint(hopdong_bp,   url_prefix='/api/hop-dong')
    app.register_blueprint(banggia_bp,   url_prefix='/api/bang-gia')
    app.register_blueprint(thanhtoan_bp, url_prefix='/api/thanh-toan')
    app.register_blueprint(hoadon_bp,    url_prefix='/api/hoa-don')
    app.register_blueprint(thongke_bp,   url_prefix='/api/thong-ke')
