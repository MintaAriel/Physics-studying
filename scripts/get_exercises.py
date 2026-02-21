from PIL import Image, ImageDraw, ImageFont
import os
import fitz
import pandas as pd
import sqlite3
from pathlib import Path
import gradio as gr

script_dir = Path(__file__).parent
project_root = script_dir.parent

def join_images_horizontally(image_paths, output_path='joined_horizontal.jpg'):
    """Join images horizontally (side by side)."""
    images = [Image.open(img) for img in image_paths]

    # Get dimensions
    widths, heights = zip(*(img.size for img in images))
    total_width = sum(widths)
    max_height = max(heights)

    # Create new image
    new_image = Image.new('RGB', (total_width, max_height))

    # Paste images
    x_offset = 0
    for img in images:
        new_image.paste(img, (x_offset, 0))
        x_offset += img.width

    # Save result
    new_image.save(output_path)
    return new_image


def join_images_vertically(
        image_paths,
        output_path='joined_vertical.jpg',
        top_text=None,
        text_box_height=100,  # Altura fija para la caja de texto
        text_color=(0, 0, 0),
        background_color=(255, 255, 255),
        font_size=40,
        font_path=None  # Ruta opcional a un archivo de fuente .ttf
):
    """
    Join images vertically with optional text box at the top.

    Args:
        image_paths: Lista de rutas a imágenes
        output_path: Ruta para guardar la imagen resultante
        top_text: Texto a mostrar en la parte superior
        text_box_height: Altura fija de la caja de texto en píxeles
        text_color: Color del texto (RGB)
        background_color: Color de fondo de la caja (RGB)
        font_size: Tamaño de la fuente (solo si se usa una fuente .ttf)
        font_path: Ruta a un archivo .ttf para la fuente
    """
    images = [Image.open(img) for img in image_paths]

    # Get dimensions of all images
    widths, heights = zip(*(img.size for img in images))
    max_width = max(widths)
    total_images_height = sum(heights)

    # Calculate total height including text box
    total_height = total_images_height + (text_box_height if top_text else 0)

    # Create new image
    new_image = Image.new('RGB', (max_width, total_height), background_color)

    # Draw text if provided
    y_offset = 0
    if top_text and text_box_height > 0:
        # Create drawing context
        draw = ImageDraw.Draw(new_image)

        # Load font (try user-specified, then system fonts, then default)
        font = None
        if font_path and os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = None

        # Try common system fonts if no custom font
        if not font:
            system_fonts = [
                "arial.ttf", "Arial.ttf",
                "DejaVuSans.ttf", "LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/System/Library/Fonts/Helvetica.ttc"
            ]
            for font_name in system_fonts:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                    break
                except:
                    continue

        # Fallback to default if no TrueType font found
        if not font:
            font = ImageFont.load_default()
            print("⚠️  Using default bitmap font (font_size ignored). For proper font scaling, provide a .ttf file.")

        # Calculate text position (centered)
        text_bbox = draw.textbbox((0, 0), top_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]

        # Center text horizontally and vertically within the text box
        text_x = (max_width - text_width) // 2
        text_y = (text_box_height - (text_bbox[3] - text_bbox[1])) // 2

        # Draw the text
        draw.text((text_x, text_y), top_text, fill=text_color, font=font)

        # Update y_offset to start below the text box
        y_offset = text_box_height

    # Paste all images
    for img in images:
        # Center each image horizontally if narrower than max_width
        x_offset = (max_width - img.width) // 2
        new_image.paste(img, (x_offset, y_offset))
        y_offset += img.height

    # Save result
    new_image.save(output_path)
    # print(f"✅ Image saved to: {output_path}")
    # print(f"   Total size: {max_width}x{total_height}px")
    # print(f"   Text box: {'Yes' if top_text else 'No'} ({text_box_height}px)" if top_text else "   Text box: No")

    return new_image



def extract_region_two_corners(pdf_path, page_num, corner1, corner2, output_path, zoom=2.0):
    """
    Extract rectangular region using two opposite corners.

    Args:
        corner1: (x, y) - e.g., (103.5, 219.5) top-left or bottom-left
        corner2: (x, y) - e.g., (109.0, 229.0) bottom-right or top-right
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    # PyMuPDF automatically handles the order - it finds min/max
    rect = fitz.Rect(corner1[0], corner1[1], corner2[0], corner2[1])

    # Create transformation matrix for zoom
    mat = fitz.Matrix(zoom, zoom)

    # Get pixmap of the region
    pix = page.get_pixmap(matrix=mat, clip=rect)

    # Save to file
    pix.save(output_path)
    # print(f"Image saved to: {output_path}")
    # print(f"Extracted region: {rect}")

    doc.close()
    return pix



notebook1_json = os.path.join(project_root, 'data', 'json', 'pages_sem_2_fixed.json')
chertov_json = os.path.join(project_root, 'data', 'json', 'Chertov_final.json')
chertov_idx_json = os.path.join(project_root, 'data', 'json', 'Chertov_index.json')


df_notebook = pd.read_json(notebook1_json,  dtype={'exercise_num': str})
df_book = pd.read_json(chertov_json)
df_book_idx = pd.read_json(chertov_idx_json)

df_book_idx.columns = ['number', 'unit', 'subunit']
df_notebook[['unit', 'subunit']] = df_notebook['exercise_num'].str.split('.', expand=True)
df_book[['unit', 'subunit']] = df_book['exercise'].str.extract(r'(\d+)\.(\d+)')



seminar_path = os.path.join(project_root, 'data', 'notebooks', 'Физика 2 семестр_2.pdf')
Chertov_path = os.path.join(project_root, 'data', 'books', 'Chertov.pdf')


chertov = df_notebook[ df_notebook['Book'] == 'Chertov']




# Construct the full path to the folder you to remove
temp_path = os.path.join(project_root, "test", "temp_images")

os.makedirs(temp_path, exist_ok=True)

try:
    os.makedirs(temp_path)
except:
    print('folder already exists')

def get_exercise(number):
    for filename in os.listdir(temp_path):
        try:
            file_path = os.path.join(temp_path, filename)
            os.unlink(file_path)
        except:
            pass

    numbers = number.split('.')
    unit, subunit = numbers[0], numbers[1]
    exer_df = chertov[(chertov['unit'] == unit) & (chertov['subunit'] == subunit) ]
    exer_book_df = df_book[(df_book['unit'] == unit) & (df_book['subunit'] == subunit) ]
    results = len(exer_df)
    results_book = len(exer_book_df)
    if results > 0 and results_book > 0 :
        index_book = df_book_idx.iloc[int(unit)-1]
        image_text = f"{index_book['number']}-{index_book['subunit']}:{index_book['unit']}"
        for i in range(results):
            row = exer_df.iloc[i]
            extract_region_two_corners(
                pdf_path=seminar_path,
                page_num=int(row['page']),  # Page 1 (0-indexed)
                corner1=(30, row['pdf_points'][0]-10),
                corner2=(560, row['pdf_points'][1]),
                output_path= os.path.join(temp_path,  f"z{unit}-{subunit}_{i}.png"),
                zoom=3.0  # Higher zoom for better quality
            )
        for i in range(results_book):
            row = exer_book_df.iloc[i]
            extract_region_two_corners(
                pdf_path=Chertov_path,
                page_num=int(row['page']),  # Page 1 (0-indexed)
                corner1=(0, row['points'][0]-5),
                corner2=(560, row['points'][1]),
                output_path=os.path.join(temp_path,f"b{unit}-{subunit}_{i}.png"),
                zoom=4  # Higher zoom for better quality
            )

        images_exer = os.listdir(temp_path)
        images_exer = sorted(images_exer)
        images_path = [os.path.join(temp_path, i) for i in images_exer]


        join_images_vertically(
            image_paths=images_path,
            output_path= os.path.join(temp_path, f'{unit}_{subunit}.jpg'),
            top_text=image_text,
            text_box_height=80,
            text_color=(255, 0, 0),  # Texto rojo
            background_color=(240, 240, 240),  # Fondo gris claro

        )
        for image in images_path:
            os.remove(image)
    elif results == 0 :
        print(f'There is no exercise {number} in your notebook')

    elif results_book == 0:
        print(f'There is no exercise {number} in Chertov')

    image_path = os.path.join(temp_path, f'{unit}_{subunit}.jpg')
    return image_path


def log_request(exercise_number, feedback=None):
    conn = sqlite3.connect(os.path.join(project_root, 'data',"exercise_history.db"))
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO requests (exercise_number, feedback)
        VALUES (?, ?)
    """, (exercise_number, feedback))

    conn.commit()
    conn.close()

units = sorted(chertov['unit'].astype(int).unique())

unit_map = {
    str(unit): sorted(
        chertov[chertov['unit'] == str(unit)]['subunit']
        .astype(int)
        .tolist()
    )
    for unit in units
}






# ---------- STATE ----------
current_unit = gr.State()
current_exercise = gr.State()

# ---------- FUNCTIONS ----------

def select_unit(unit):
    subunits = unit_map[str(unit)]
    subunit_labels = [f"{unit}.{sub}" for sub in subunits]

    return (
        gr.update(choices=subunit_labels, visible=True),
        None
    )


def load_exercise_from_dropdown(ex_number):
    image_path = get_exercise(ex_number)
    log_request(ex_number)
    try:
        return Image.open(image_path)
    except Exception as e:
        pass

def submit_feedback(ex_number, feedback):
    log_request(ex_number, feedback)
    return f"Stored feedback '{feedback}' for {ex_number}"



# ---------- UI ----------

with gr.Blocks() as demo:
    gr.Markdown("## Physics Exercise Explorer")

    # UNIT SELECTION
    gr.Markdown("### Select Unit")
    unit_buttons = []

    with gr.Row():
        for unit in units:
            btn = gr.Button(f"Unit {unit}")
            unit_buttons.append(btn)

    # SUBUNIT DROPDOWN (initially hidden)
    subunit_dropdown = gr.Dropdown(
        choices=[],
        label="Select Exercise",
        visible=False
    )

    image_output = gr.Image(type="filepath", height=600)

    # FEEDBACK
    gr.Markdown("### Feedback")
    feedback_radio = gr.Radio(
        choices=["good", "normal", "bad"],
        label="Rate this exercise"
    )

    feedback_button = gr.Button("Submit Feedback")
    status_text = gr.Markdown()

    # ---------- INTERACTIONS ----------

    for i, unit in enumerate(units):
        unit_buttons[i].click(
            fn=lambda u=str(unit): select_unit(u),
            outputs=[subunit_dropdown, image_output]
        )

    subunit_dropdown.change(
        fn=load_exercise_from_dropdown,
        inputs=subunit_dropdown,
        outputs=image_output
    )

    feedback_button.click(
        fn=submit_feedback,
        inputs=[subunit_dropdown, feedback_radio],
        outputs=status_text
    )

demo.launch()