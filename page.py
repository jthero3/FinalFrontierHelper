import os
import sys

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

# Define button labels
BUTTON_LABELS = ["Center_Primary", "Center_Secondary", "Edge_Primary", "Edge_Secondary"]
TOGGLE_LABELS = ["Hatching", "Bevel", "Medal"]

CENTER_PRIMARY = (117, 100, 88)
CENTER_SECONDARY = (200, 167, 152)
EDGE_PRIMARY = (61, 45, 72)
EDGE_SECONDARY = (214, 207, 224)

ORDERED_COLORS = [
    CENTER_PRIMARY,
    CENTER_SECONDARY,
    EDGE_PRIMARY,
    EDGE_SECONDARY,
]

# Define paths and opacities for each layer in display order (excluding Base)
LAYER_PATHS = {
    "Hatching": {"path": "./Images/Single/hatching_single.png", "opacity": 0.2},
    "Bevel": {"path": "./Images/Single/bevel_single.png", "opacity": 1.0},
    "Medal": {"path": "./Images/Single/medal_single.png", "opacity": 1.0},
}

FILE_NAMES = [
    "Atmosphere.png",
    "DeepAtmosphere.png",
    "EvaGround.png",
    "EvaOrbit.png",
    "EvaSpace.png",
    "FirstAtmosphere.png",
    "FirstEvaGround.png",
    "FirstEvaOrbit.png",
    "FirstEvaSpace.png",
    "FirstLanding.png",
    "FirstOrbitCapsule.png",
    "FirstOrbitCapsuleDocked.png",
    "FirstPlantFlag.png",
    "FirstRover.png",
    "Landing.png",
    "OrbitCapsule.png",
    "OrbitCapsuleDocked.png",
    "PlantFlag.png",
    "Rover.png",
    "SphereOfInfluence.png",
]

TILE_SIZE = (120, 32)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Final Frontier Helper")

        # Create the main layout
        main_layout = QVBoxLayout()

        # Create and style the label above the tabs
        self.tab1_label = QLabel("Final Frontier Helper")
        self.tab1_label.setStyleSheet("font-size: 20px;")
        main_layout.addWidget(self.tab1_label)

        self.tabs = QTabWidget()
        self.tabs.setFixedSize(450, 280)

        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()

        # Create a horizontal layout for "Body Name" input and toggles
        body_name_toggle_layout = QHBoxLayout()

        # Add "Body Name:" label and input field
        body_name_label = QLabel("Body Name:")
        body_name_toggle_layout.addWidget(body_name_label)

        self.body_name_input = QLineEdit()  # Text input field
        self.body_name_input.setPlaceholderText("Enter body name")
        self.body_name_input.textChanged.connect(
            self.update_tab_title
        )  # Connect text change
        body_name_toggle_layout.addWidget(self.body_name_input)

        # Create toggle buttons for each layer
        self.layer_toggles = {}
        for label in TOGGLE_LABELS:
            toggle_button = QCheckBox(label)
            toggle_button.stateChanged.connect(self.update_layers)
            body_name_toggle_layout.addWidget(toggle_button)
            self.layer_toggles[label] = toggle_button

        # Add the combined layout above the main image view in tab1
        self.tab1_layout.addLayout(body_name_toggle_layout)

        # Create a QGraphicsScene to manage multiple images
        self.scene = QGraphicsScene()

        # Create a QGraphicsView to display the scene
        self.graphics_view = QGraphicsView(self.scene)

        # Load and set the resized main image
        self.image_path = "./Images/Single/color_single.png"
        self.main_pixmap = QPixmap(self.image_path).scaled(396, 106)
        self.original_pixmap = (
            self.main_pixmap.copy()
        )  # Keep a backup of the original image
        self.main_item = QGraphicsPixmapItem(self.main_pixmap)
        self.scene.addItem(self.main_item)
        self.color_updated_image = self.original_pixmap.toImage()

        # Add the graphics view to tab1 layout
        self.tab1_layout.addWidget(self.graphics_view)

        # Create a horizontal layout for the color buttons
        button_layout = QHBoxLayout()
        self.buttons = []
        for label in BUTTON_LABELS:
            button = QPushButton(label)
            button.clicked.connect(self.open_color_dialog)
            button.setProperty("label", label)
            button_layout.addWidget(button)
            self.buttons.append(button)

        # Add the button layout to the main layout of tab1
        self.tab1_layout.addLayout(button_layout)

        # Set the layout for tab1
        self.tab1.setLayout(self.tab1_layout)

        # Set initial tab title with default "Untitled"
        self.tabs.addTab(self.tab1, "Medal Creator: Untitled")

        # Add the tabs to the main layout
        main_layout.addWidget(self.tabs)

        # Create a label and image preview for the combined images, initially hidden
        self.lower_label = QLabel("Final Medals: ")
        self.lower_label.setStyleSheet("font-size: 18px;")
        self.lower_label.setVisible(False)  # Initially hidden
        main_layout.addWidget(self.lower_label)

        self.lower_image_preview = QLabel()
        lower_pixmap = QPixmap("./Images/Combined/medals.png").scaled(400, 126)
        self.lower_image_preview.setPixmap(lower_pixmap)
        self.lower_image_preview.setVisible(False)  # Initially hidden
        main_layout.addWidget(self.lower_image_preview)

        # Add a placeholder for the grid of medals, initially hidden
        self.medal_grid_preview = QLabel()
        self.medal_grid_preview.setVisible(False)  # Initially hidden
        main_layout.addWidget(self.medal_grid_preview)

        # Add a "Create Medals!" button below the preview image
        self.create_medals_button = QPushButton("Create Medals!")
        self.create_medals_button.clicked.connect(self.create_medals_action)
        main_layout.addWidget(self.create_medals_button)

        # Add a "Finished Creating!" button below the preview image
        self.finished_creating_button = QPushButton("Finished Creating!")
        self.finished_creating_button.clicked.connect(self.on_finished_creating)
        self.finished_creating_button.setVisible(False)  # Initially hidden
        main_layout.addWidget(self.finished_creating_button)

        # Track custom colors chosen for each section
        self.custom_colors = {}

        # Create a central widget and set the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Adjust the size of the window to fit the contents
        self.adjustSize()

        # Adjust the size of the window to fit the contents
        self.tabs.setFixedSize(500, 300)

        # Adjust the tabs to fit their contents
        self.tabs.adjustSize()

    def update_tab_title(self):
        # Update the tab title based on the text input
        body_name = self.body_name_input.text() or "Untitled"
        body_name = body_name.replace(" ", "_")
        self.tabs.setTabText(0, f"Medal Creator: {body_name}")

    def open_color_dialog(self):
        button = self.sender()
        color = QColorDialog.getColor()

        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()};")
            label = button.property("label")
            index = BUTTON_LABELS.index(label)
            self.custom_colors[ORDERED_COLORS[index]] = color  # Track color changes

            self.apply_color_changes()

    def apply_color_changes(self):
        # Start by restoring the original image to apply new colors
        self.color_updated_image = self.original_pixmap.toImage()

        # Apply color changes to the base image
        for old_color, new_color in self.custom_colors.items():
            color_to_replace = QColor(*old_color)
            for x in range(self.color_updated_image.width()):
                for y in range(self.color_updated_image.height()):
                    if self.color_updated_image.pixelColor(x, y) == color_to_replace:
                        self.color_updated_image.setPixelColor(x, y, new_color)

        # Apply layers on top of the color-modified image
        self.update_layers()  # Ensure layers are added to the updated base

    def update_layers(self):
        # Start with the base color-updated image to preserve color options
        final_image = self.color_updated_image.copy()

        # Create a QPainter to add the selected layers
        painter = QPainter(final_image)

        for label, toggle_button in self.layer_toggles.items():
            if toggle_button.isChecked():
                # Get the layer path and opacity
                layer_info = LAYER_PATHS[label]
                layer_pixmap = QPixmap(layer_info["path"]).scaled(
                    final_image.width(), final_image.height()
                )

                # Set opacity and draw the layer on top of the color-updated image
                painter.setOpacity(layer_info["opacity"])
                painter.drawPixmap(0, 0, layer_pixmap)

        painter.end()

        # Update the main item in the scene with the color-updated and layered image
        self.main_item.setPixmap(QPixmap.fromImage(final_image))

    def create_medals_action(self):
        # Create a new image to hold the main image with applied layers
        image_width = self.main_pixmap.width()
        image_height = self.main_pixmap.height()

        # Create a new blank image to draw the main image with layers
        combined_image = QImage(image_width, image_height, QImage.Format.Format_ARGB32)
        combined_image.fill(QColor(255, 255, 255, 0))

        # Create a QPainter to draw on the combined image
        painter = QPainter(combined_image)

        # Draw the main image
        painter.drawPixmap(0, 0, self.main_item.pixmap())

        bevel_pixmap = QPixmap(LAYER_PATHS["Bevel"]["path"]).scaled(
            image_width, image_height
        )
        painter.setOpacity(LAYER_PATHS["Bevel"]["opacity"])
        painter.drawPixmap(0, 0, bevel_pixmap)

        hatching_pixmap = QPixmap(LAYER_PATHS["Hatching"]["path"]).scaled(
            image_width, image_height
        )
        painter.setOpacity(LAYER_PATHS["Hatching"]["opacity"])
        painter.drawPixmap(0, 0, hatching_pixmap)

        painter.end()

        # Now create a grid with the combined image
        grid_width = 5
        grid_height = 4

        # Create a new blank image for the grid
        grid_image = QImage(
            image_width * grid_width,
            image_height * grid_height,
            QImage.Format.Format_ARGB32,
        )
        grid_image.fill(QColor(255, 255, 255, 0))  # Fill with transparent background

        # Create a QPainter for the grid image
        grid_painter = QPainter(grid_image)

        # Place the combined image in the grid
        for x in range(grid_width):
            for y in range(grid_height):
                grid_painter.drawPixmap(
                    x * image_width, y * image_height, QPixmap.fromImage(combined_image)
                )

        grid_painter.end()

        # Load the bottom image and scale it to the same size as the grid image
        bottom_image_path = "./Images/Combined/medals.png"  # Path to the bottom image
        bottom_image = QPixmap(bottom_image_path)  # Keep original size first

        # Resize grid image to the same size as bottom image
        grid_image = grid_image.scaled(
            bottom_image.size(), Qt.AspectRatioMode.KeepAspectRatio
        )

        # Create a new image for layering the grid below the bottom image
        final_combined_image = QImage(bottom_image.size(), QImage.Format.Format_ARGB32)
        final_combined_image.fill(
            QColor(255, 255, 255, 0)
        )  # Fill with transparent background

        # Create a painter for the final combined image
        final_painter = QPainter(final_combined_image)

        # Draw the gridded image first
        final_painter.drawImage(0, 0, grid_image)

        # Draw the bottom image on top
        final_painter.drawPixmap(0, 0, bottom_image)

        final_painter.end()  # Finalize the painter

        # Set the final combined image to the lower image preview
        self.lower_image_preview.setPixmap(QPixmap.fromImage(final_combined_image))

        # Show the lower label, image, and grid preview
        self.lower_label.setVisible(True)  # Show the label
        self.lower_image_preview.setVisible(True)  # Show the image
        self.finished_creating_button.setVisible(True)  # Initially hidden
        self.tabs.setFixedSize(600, 300)

    def on_finished_creating(self):
        # Get the body name from the input field, or use "Untitled" if empty
        body_name = self.body_name_input.text() or "Untitled"
        body_name = body_name.replace(" ", "_")

        # Create the directory path in the main directory
        directory_path = os.path.join(
            os.getcwd(), body_name
        )  # Folder in main directory

        # Check if the directory already exists, and create it if it doesn't
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Folder '{directory_path}' created successfully.")
        else:
            print(f"Folder '{directory_path}' already exists.")

        # Use the final combined image instead of the bottom image
        final_combined_image = (
            self.lower_image_preview.pixmap().toImage()
        )  # Get the image from the lower image preview

        # Calculate number of tiles based on TILE_SIZE and FILE_NAMES length
        tile_width, tile_height = TILE_SIZE
        rows = final_combined_image.height() // tile_height
        cols = final_combined_image.width() // tile_width

        # Ensure we have enough tiles based on FILE_NAMES
        assert (
            len(FILE_NAMES) <= rows * cols
        ), "Not enough tiles in the image for the provided file names."

        # Loop through the FILE_NAMES and save each tile
        index = 0
        for row in range(rows):
            for col in range(cols):
                if index >= len(FILE_NAMES):
                    break  # Stop if there are more tiles than file names

                # Crop a tile from the final combined image
                tile_rect = QRect(
                    col * tile_width, row * tile_height, tile_width, tile_height
                )
                tile_pixmap = QPixmap.fromImage(
                    final_combined_image.copy(tile_rect)
                )  # Use the final combined image

                # Save the tile with the corresponding file name in the new folder
                tile_path = os.path.join(directory_path, FILE_NAMES[index])
                tile_pixmap.save(tile_path, "PNG")
                print(f"Saved tile as '{tile_path}'")

                index += 1

        print("All tiles saved successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
