# Test Images

Place your test disaster images in this directory for testing the system.

## Supported Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## Image Types for Testing

### Fire Disasters
- Wildfire images
- Building fires
- Smoke plumes

### Flood Disasters
- Flooded streets
- River overflow
- Coastal flooding

### Structural Damage
- Earthquake damage
- Building collapse
- Infrastructure damage

### Casualty Detection
- Images with people in disaster scenarios
- Emergency situations

## Usage

```bash
# Test with a fire image
python run.py test test_images/wildfire.jpg --coordinates "34.0522,-118.2437"

# Test with flood image
python run.py test test_images/flood.jpg --coordinates "29.7604,-95.3698"
```

## Sample Images

You can download sample disaster images from:
- NASA Earth Observatory
- USGS Disaster Images
- Emergency Management Agencies
- News Media (with proper attribution)

**Note**: Ensure you have proper rights to use any images for testing purposes.