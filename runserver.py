#!/usr/bin/env python
"""
Runs the Flask server.
"""
from miridan import app
app.run(debug=True, host='0.0.0.0')
