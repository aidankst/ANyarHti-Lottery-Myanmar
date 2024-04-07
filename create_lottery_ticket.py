from flask import Flask, current_app
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

def create_lottery_ticket():
    with app.app_context():  # Push an application context
        template_path = os.path.join(current_app.root_path, 'static', 'images', 'ticket_compressed.jpg')
        roboto_regular = os.path.join(current_app.root_path, 'static', 'Roboto-Bold.ttf')
        myanmar_font = os.path.join(current_app.root_path, 'static', 'myanmar_font_bold.ttf')
        
        starting_number = 100001
        total_tickets = 100000
        
        # Load template and fonts once
        template_image = Image.open(template_path)
        font_large = ImageFont.truetype(roboto_regular, size=60)
        font_myanmar = ImageFont.truetype(myanmar_font, size=40)
        
        folder_count = total_tickets // 1000  # Use integer division
        
        for folder_num in range(0, folder_count):
            # folder_path = os.path.join(current_app.root_path, 'static', f'tickets/folder_{folder_num}')
            folder_path = f'/Users/sithukaung/Desktop/Tickets/folder_{folder_num}'
            os.makedirs(folder_path, exist_ok=True)  # Create the directory for the folder
            
            for ticket_count in range(1000):  # Generate 1000 tickets per folder
                ticket_number = starting_number
                
                # Work on a copy of the template for each ticket
                current_image = template_image.copy()
                draw = ImageDraw.Draw(current_image)
                
                details = [
                    {'text': str(ticket_number), 'position': (820, 55), 'font': font_large},
                    {'text': '၆', 'position': (477, 45), 'font': font_myanmar},
                ]
                
                for detail in details:
                    draw.text(detail['position'], detail['text'], fill='black', font=detail['font'])
                
                save_path = os.path.join(folder_path, f'{ticket_count}_{ticket_number}.jpg')
                current_image.save(save_path)  # Save the ticket
                starting_number += 1
            

if __name__ == '__main__':
    with app.app_context():
        create_lottery_ticket()
