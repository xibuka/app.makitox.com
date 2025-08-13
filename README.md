# Makitox - Premium Mobile App Showcase

Premium static website showcasing innovative mobile applications with glassmorphism design.

## 🌟 Features

- **Premium Design**: Glassmorphism aesthetic with dark theme
- **Responsive Layout**: Mobile-first design using TailwindCSS  
- **App Showcase**: Featured mobile applications with detailed pages
- **Contact Forms**: JavaScript validation and form handling
- **SEO Optimized**: Meta tags and Open Graph properties

## 🚀 Featured App

### Mirai Alert
Revolutionary alarm clock that learns your sleep patterns and wakes you at the optimal time for better mornings.

**📱 Available Now**: [Download on App Store](https://apps.apple.com/us/app/mirai-alert/id6748834235)

## 📁 Project Structure

```
makitox/
├── index.html              # Homepage with app showcase
├── app-miraialarm.html     # Mirai Alert product page
├── support.html            # Support & contact page
├── privacy.html            # Privacy policy
├── /assets
│   ├── /images            # App screenshots and assets
│   └── /icons             # Icon files
├── /css
│   └── tailwind.css       # Custom TailwindCSS utilities
├── /js
│   └── form-handler.js    # Contact form validation
└── /components            # Future HTML components
```

## 🎨 Design System

- **Colors**: Dark theme (#0f172a, #1e293b) with orange accents (#f97316)
- **Typography**: Inter font family with clear hierarchy
- **Effects**: Glassmorphism cards with backdrop blur
- **Spacing**: Generous padding for premium feel
- **Animations**: Subtle hover effects and transitions

## 🖥️ Local Development

### Simple HTTP Server
```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000

# Node.js (if you have http-server installed)
npx http-server
```

### VS Code Live Server
1. Install "Live Server" extension
2. Right-click `index.html` → "Open with Live Server"

### Access
- **Website**: http://localhost:8000
- **App Page**: http://localhost:8000/app-miraialarm.html
- **Support**: http://localhost:8000/support.html

## 📱 Mobile Applications

### Current Apps
- **Mirai Alert** - Smart alarm clock with sleep pattern learning

### Coming Soon  
- Additional productivity and lifestyle apps
- Enhanced features and integrations

## 🌐 Deployment

### Static Hosting Platforms
- **Netlify**: Drag & drop deployment
- **Vercel**: Git-based deployment  
- **GitHub Pages**: Direct from repository
- **Surge.sh**: Simple command-line deployment

### Traditional Web Hosting
- Upload all files to web server root directory
- Ensure proper MIME types for CSS/JS files
- Configure redirects if needed for clean URLs

## 🔧 Customization

### Adding New Apps
1. Create new HTML page: `app-newapp.html`
2. Add app card to `index.html` in Featured Apps section
3. Update navigation and footer links
4. Add new images to `assets/images/`

### Styling Changes
- Main styles: `css/tailwind.css`
- Inline styles: Within `<style>` tags in HTML files
- Color scheme: Update CSS custom properties

### Form Configuration
- Form handling: `js/form-handler.js`
- Add validation rules for new form fields
- Update success/error messages

## 📞 Support

For technical support or questions:
- Visit: [makitox.com/support](https://makitox.com/support)
- Contact form available on support page

## 📄 License

© 2024 Makitox. All rights reserved.

---

**Built with modern web technologies for premium mobile app showcase.**