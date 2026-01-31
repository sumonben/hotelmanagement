# Carousel Implementation Guide

## Overview
The carousel system allows you to display beautiful, rotating slides on the homepage with customizable content, images, and call-to-action buttons.

## Models

### Carousel
- **hotel**: OneToOneField to Hotel - Links carousel to a specific hotel
- **is_active**: Boolean - Enable/disable the carousel
- **created_at**: DateTime - Creation timestamp
- **updated_at**: DateTime - Last update timestamp

**Methods:**
- `get_active_slides()` - Returns all active carousel slides ordered by display order

### CarouselSlide
- **carousel**: ForeignKey to Carousel - Links slide to parent carousel
- **title**: CharField - Main slide title (max 200 characters)
- **subtitle**: CharField - Secondary text (max 300 characters, optional)
- **description**: TextField - Extended description (optional)
- **image**: ImageField - Slide background image (required)
- **button_text**: CharField - CTA button text (max 50 chars, default: "View Rooms")
- **button_url**: CharField - CTA button URL (max 200 chars, optional)
- **is_active**: Boolean - Show/hide slide
- **order**: IntegerField - Display order (lower numbers appear first)
- **created_at**: DateTime - Creation timestamp
- **updated_at**: DateTime - Last update timestamp

## Setup Instructions

### 1. Apply Migrations
Run the migration to create the carousel tables:

```bash
python manage.py migrate hotel
```

### 2. Initialize Carousel (Optional)
Use the management command to create a carousel with sample slides:

```bash
python manage.py init_carousel
```

This will:
- Create a Carousel for your default hotel
- Add 3 sample carousel slides
- Note: You'll need to upload actual images via Django admin

### 3. Add Carousel Slides via Admin

1. Go to Django Admin: `/admin/`
2. Navigate to **Carousels** section
3. Click on your hotel's carousel
4. Add slides using the inline form
5. For each slide, configure:
   - Title
   - Subtitle (optional)
   - Description (optional)
   - Image (upload or select)
   - Button text (default: "View Rooms")
   - Button URL (optional - defaults to hotel detail page)
   - Order (1, 2, 3... for display sequence)
   - Is Active (check to display)

## Usage in Templates

The carousel is automatically displayed on the homepage (`hotel/home.html`) if:
1. A carousel exists for the hotel
2. The carousel is marked as active
3. At least one slide is active

The template includes:
- Auto-rotating slides (5-second interval)
- Navigation indicators (dots at bottom)
- Previous/Next buttons
- Responsive design for mobile/tablet/desktop
- Smooth animations and transitions

## Features

### Slide Customization
- **Image**: Upload high-quality images (recommended: 1920x500px or larger)
- **Text Overlay**: Title, subtitle, and description with responsive sizing
- **CTA Button**: Customizable button text and URL
- **Order**: Drag-and-drop or manual ordering in admin

### Carousel Features
- **Auto-rotate**: Slides automatically change every 5 seconds
- **Manual Navigation**: Users can click previous/next buttons
- **Indicators**: Click dots to jump to specific slides
- **Responsive**: Automatically adjusts for mobile/tablet/desktop
- **Accessible**: Keyboard navigation support via Bootstrap carousel

### Styling
- Gradient overlay for text readability
- Fade-in animation on slide content
- Hover effects on buttons
- Smooth transitions between slides
- Shadow and border-radius for polish

## Mobile Responsiveness

The carousel adapts to different screen sizes:

**Desktop (>768px):**
- Image height: 500px
- Title font size: 3.5rem
- Button padding: 0.75rem 2.5rem

**Mobile (<768px):**
- Image height: 300px
- Title font size: 2rem
- Button padding: 0.5rem 1.5rem
- Subtitle font size: 1.1rem

## Image Recommendations

**Dimensions:** 1920x500px (3.84:1 aspect ratio) or similar
**Format:** JPG or PNG
**Size:** Compress to <500KB for fast loading
**Quality:** High-quality images for professional appearance

## Best Practices

1. **Keep Text Short:**
   - Title: 2-5 words maximum
   - Subtitle: 5-10 words
   - Use concise, compelling copy

2. **Image Quality:**
   - Use professional, high-quality images
   - Ensure text is readable with the overlay
   - Maintain consistent image style across slides

3. **Call-to-Action:**
   - Use action-oriented button text: "Book Now", "View Rooms", "Learn More"
   - Point to relevant URLs

4. **Order:**
   - Put most important slides first
   - Test the sequence for flow and storytelling

5. **Timing:**
   - 5-second auto-rotate is good for most cases
   - Users can manually navigate anytime

## Customization

### Change Auto-Rotate Interval
In `hotel/home.html`, modify the carousel HTML:

```html
<div id="hotelCarousel" class="carousel slide" data-bs-ride="carousel" data-bs-interval="8000">
```

Change `data-bs-interval="5000"` to your desired milliseconds (e.g., 8000 = 8 seconds)

### Modify Slide Animations
Edit the CSS in `home.html` under the `<style>` tag:

```css
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);  /* Increase for more movement */
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

### Adjust Colors/Styling
Modify the `.carousel-*` CSS classes in `home.html`

## Admin Interface

The carousel admin provides:

### Carousel Admin
- **List View**: Shows all carousels with hotel name, active status, slide count
- **Edit View**: Toggle active status, manage slides with inline editor
- **Inline Slides**: Add/edit multiple slides directly from carousel page

### CarouselSlide Admin
- **List View**: Shows all slides with title, carousel, order, active status
- **Search**: Find slides by title, carousel, or hotel
- **Filter**: Filter by hotel, active status, or created date
- **Ordering**: Default sort by carousel and order field

## Troubleshooting

### Carousel Not Showing
- Check if carousel is marked as active in admin
- Verify at least one slide is marked as active
- Ensure the hotel is the DEFAULT_HOTEL_ID

### Slides Not Appearing
- Confirm slides are marked as active (`is_active = True`)
- Check that images are uploaded and accessible
- Verify carousel is active

### Images Not Loading
- Check image file permissions
- Ensure images are in `media/carousel/` folder
- Verify image format and size

### Text Not Readable
- Increase the overlay darkness (modify `background` in `.carousel-caption`)
- Change text color or add text shadow
- Use lighter/simpler background images

## Advanced: Custom Carousel Template

To create a custom carousel template, create `hotel/includes/carousel.html`:

```django
{% if carousel_slides %}
<div id="hotelCarousel" class="carousel slide" data-bs-ride="carousel">
    <!-- Your custom carousel HTML -->
</div>
{% endif %}
```

Then include it in `home.html`:
```django
{% include 'hotel/includes/carousel.html' %}
```

## References

- Bootstrap Carousel: https://getbootstrap.com/docs/5.3/components/carousel/
- Django File Upload: https://docs.djangoproject.com/en/stable/topics/files/
- ImageField: https://docs.djangoproject.com/en/stable/ref/models/fields/#imagefield

## Support

For issues:
1. Check Django admin carousel/slide settings
2. Verify migrations are applied
3. Check browser console for JavaScript errors
4. Review Django logs for server-side errors
