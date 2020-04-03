"""
Config file for Gunicorn
"""

bind = "0.0.0.0:5000"
access_logfile = "/dev/stdout"
error_logfile = "/dev/stderr"
