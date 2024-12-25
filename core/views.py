import easyocr
import re
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

def home(request):


    return render(request, 'core/home.html')



def extract_phone_numbers(image_path):
    try:
        reader = easyocr.Reader(['en'])
        results = reader.readtext(image_path)
        
        # Extract all text from the image
        lines = [result[1] for result in results]
        text = ' '.join(lines)
        
        # Enhanced pattern for WhatsApp numbers
        patterns = [
            r'\+\d{1,3}\s*\(\d{3}\)\s*\d{3}[-\s]?\d{4}',  
            r'\+\d{1,3}\s*\d{5}\s*\d{5}',                  
            r'\+\d{1,3}\s*\d{10}',                         
            r'\+\d{1,3}\s*\d{2}\s*\d{3}\s*\d{4}'          
        ]
        
        combined_pattern = '|'.join(patterns)
        phone_numbers = re.findall(combined_pattern, text)
        cleaned_numbers = [re.sub(r'[-\s()]', '', number) for number in phone_numbers]
        unique_numbers = list(dict.fromkeys(cleaned_numbers))
        
        return unique_numbers
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return []

def upload_screenshot(request):
    if request.method == 'POST' and request.FILES.get('whatsapp_image'):
        image = request.FILES['whatsapp_image']
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if image.content_type not in allowed_types:
            return render(request, 'core/upload.html', {
                'error': 'Please upload only JPEG or PNG images.'
            })
            
        # Check file size
        if image.size > 5 * 1024 * 1024:
            return render(request, 'core/upload.html', {
                'error': 'File size should be less than 5MB.'
            })

        try:
            # Delete existing images
            for filename in os.listdir(os.path.join(settings.MEDIA_ROOT, 'whatsapp_screenshots')):
                file_path = os.path.join(settings.MEDIA_ROOT, 'whatsapp_screenshots', filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

            fs = FileSystemStorage()
            filename = 'whatsapp-image.' + image.name.split('.')[-1]
            saved_path = fs.save(f'whatsapp_screenshots/{filename}', image)
            
            # Get full path of saved image
            full_path = os.path.join(settings.MEDIA_ROOT, saved_path)
            
            # Extract phone numbers
            phone_numbers = extract_phone_numbers(full_path)
            
            if phone_numbers:
                return render(request, 'core/results.html', {
                    'phone_numbers': phone_numbers,
                    'count': len(phone_numbers)
                })
            else:
                return render(request, 'core/upload.html', {
                    'error': 'No phone numbers found in the image.'
                })

        except Exception as e:
            return render(request, 'core/upload.html', {
                'error': f'An error occurred: {str(e)}'
            })

    return render(request, 'core/upload.html')

