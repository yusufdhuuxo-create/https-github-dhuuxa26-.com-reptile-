# Activation Code Manager

A beautiful, feature-rich activation code management system built with Python Flask.

## Overview

This application allows you to:
- **Generate** unique activation codes with customizable options
- **Validate** codes and track their usage
- **Manage** all codes with filtering and status tracking
- **View statistics** on code usage and performance

## Tech Stack

- **Backend**: Python 3.11 with Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: Jinja2 templates with modern CSS
- **Server**: Gunicorn (production) / Flask dev server (development)

## Project Structure

```
/
├── app.py                 # Main Flask application with all routes and models
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template with navigation and styles
│   ├── index.html         # Home page
│   ├── generate.html      # Code generation page
│   ├── validate.html      # Code validation page
│   ├── codes.html         # All codes list with filtering
│   └── statistics.html    # Statistics dashboard
├── static/                # Static files (if needed)
├── pyproject.toml         # Python dependencies
└── replit.md              # This file
```

## Features

### Code Generation
- Generate 1-100 codes at once
- Add custom prefix (e.g., PROMO-XXXX-XXXX)
- Set batch names for organization
- Configure uses per code
- Set expiration dates

### Code Validation
- Validate codes with instant feedback
- Track user who activated the code
- Automatic usage counting
- Expiration checking

### Code Management
- View all codes with pagination
- Filter by status (All, Valid, Used, Inactive)
- Toggle code activation status
- Delete codes
- Copy codes to clipboard

### Statistics Dashboard
- Total, active, used, inactive counts
- Today's activity tracking
- Usage rate calculation
- Recent codes and activations

## API Endpoints

- `GET /` - Home page
- `GET/POST /generate` - Generate activation codes
- `GET/POST /validate` - Validate and activate codes
- `GET /codes` - View all codes
- `GET /statistics` - View statistics
- `POST /api/code/<id>/toggle` - Toggle code active status
- `POST /api/code/<id>/delete` - Delete a code
- `POST /api/validate` - API endpoint for code validation

## Running the Application

The application runs on port 5000 with:
```bash
python app.py
```

For production, use:
```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

## Database

Uses PostgreSQL via the `DATABASE_URL` environment variable. Tables are automatically created on startup.

## Recent Changes

- 2024-12-06: Created activation code management system with Python Flask
- Implemented code generation with secure random algorithm
- Added validation system with usage tracking
- Built beautiful responsive UI with modern CSS
- Added statistics dashboard
