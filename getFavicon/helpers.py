from PIL import Image
from io import BytesIO

def detect_image_format_and_size(image_data):
    try:
        with Image.open(BytesIO(image_data)) as img:
            format = img.format
            width, height = img.size
            return format, width, height
    except IOError:
        return None, None, None

def find_best_favicon(favicons, size):
    format_priority = ['ico', 'png', 'jpg', 'jpeg']
    best_favicon = None
    best_format_index = len(format_priority)

    for favicon in favicons:
        if size is not None:
            if size == "small" and favicon['width'] > 32:
                continue
            elif size == "medium" and (favicon['width'] <= 32 or favicon['width'] > 96):
                continue
            elif size == "large" and favicon['width'] <= 96:
                continue

        if favicon['format'] in format_priority:
            format_index = format_priority.index(favicon['format'])
            if format_index < best_format_index:
                best_favicon = favicon
                best_format_index = format_index
    return best_favicon

def prepare_response(data, size, all):
    if all=='true' and data:
        unique_urls = set()
        data_without_duplicates = []
        for item in data:
            print(item)
            url = item["url"]
            if url not in unique_urls:
                data_without_duplicates.append(item)
                unique_urls.add(url)
        return {
        "response": data_without_duplicates,
        "status": 200
        }
    elif all != 'true' and data:
        best_favicon = find_best_favicon(data, size)
        if best_favicon:
            return {"response": best_favicon, "status":200}
        else:
            return {"response":"No favicons matching the current parameters were located","status": 404}
    else:
            return {"response":"No favicons matching the current parameters were located","status": 404}
