"""
Configuration settings for the AutoCAD MCP Server
"""
import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # AutoCAD configuration
    AUTOCAD_APPLICATION_NAME = "AutoCAD.Application"
    AUTOCAD_TIMEOUT = 30  # seconds
    MAX_AUTOCAD_INSTANCES = 5
    
    # Server configuration
    HOST = os.environ.get('HOST') or '127.0.0.1'
    PORT = int(os.environ.get('PORT') or 5000)
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'autocad_mcp.log'
    
    # Drawing defaults
    DEFAULT_LAYER_COLOR = 7  # White
    DEFAULT_LINE_TYPE = "Continuous"
    DEFAULT_LINE_WEIGHT = 0.25
    DEFAULT_TEXT_HEIGHT = 2.5
    
    # Building code defaults
    MIN_DOOR_WIDTH = 32  # inches
    MIN_WINDOW_WIDTH = 24  # inches
    MIN_ROOM_AREA = 70  # square feet
    MAX_WALL_HEIGHT = 12  # feet

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> Config:
    """Get configuration based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])