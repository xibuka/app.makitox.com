# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Makitox is a premium static website showcasing a suite of mobile applications. The site features glassmorphism design, responsive layout, and is built with vanilla HTML, CSS (TailwindCSS), and JavaScript.

## Project Structure

```
makitox/
├── index.html                # Homepage with app showcase
├── app-future-alarm.html     # Future Alarm product page
├── support.html              # Support page with contact form
├── privacy.html              # Privacy policy page
├── /assets
│   ├── /images              # Product images and mockups
│   └── /icons               # Optional icons/SVG
├── /css
│   └── tailwind.css         # Custom Tailwind utilities
├── /js
│   └── form-handler.js      # Contact form validation
└── /components              # Reserved for future HTML snippets
```

## Development Setup

This is a static website that requires no build process:

1. **Local Development**: Open `index.html` in a web browser or use a simple HTTP server
2. **Live Server**: Use VS Code Live Server extension or run `python -m http.server 8000`
3. **Images**: Replace placeholder image files in `assets/images/` with actual Unsplash images

## Key Features

- **Glassmorphism Design**: Semi-transparent cards with backdrop blur effects
- **Responsive Layout**: Mobile-first design using TailwindCSS utilities
- **Contact Form**: JavaScript validation in `js/form-handler.js`
- **Expandable Structure**: Ready for additional app cards and product pages
- **Premium Feel**: Dark theme with orange accent colors

## Technology Stack

- **Framework**: Static HTML/CSS/JS (no build tools)
- **Styling**: TailwindCSS CDN + custom utilities in `css/tailwind.css`
- **Fonts**: Inter font family from Google Fonts
- **Icons**: Inline SVG icons (Heroicons style)
- **Form Handling**: Vanilla JavaScript with validation

## Image Requirements

Replace these placeholder images with actual content:
- `hero-phones.jpg` (1200x800px) - Phone mockups for hero section
- `future-alarm-icon.jpg` (256x256px) - App icon
- `future-alarm-preview.jpg` (600x1200px) - Phone screenshot
- `app-interface-mockup.jpg` (800x600px) - Interface preview
- `testimonial-1/2/3.jpg` (128x128px) - User profile photos

## Design Guidelines

- **Colors**: Dark background (#0f172a, #1e293b) with orange accents (#f97316)
- **Typography**: Inter font with clear hierarchy
- **Spacing**: Generous padding and margins for premium feel
- **Effects**: Subtle animations and hover states
- **Accessibility**: Focus states and semantic HTML

## Form Configuration

The contact form in `support.html` includes:
- Real-time validation
- XSS protection
- Simulated submission (replace with actual backend)
- Success/error feedback
- Analytics hooks for tracking

## Future Expansion

To add new apps:
1. Create new product page (e.g., `app-new-product.html`)
2. Add product card to `index.html` in the Featured Apps section
3. Update navigation and footer links
4. Add new images to `assets/images/`