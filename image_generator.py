import geometry_operations

class ImageGenerator:
    BORDER_PX = 50
    FONT_SIZE = 54
    def __init__(self, pathfinder):
        self.pathfinder = pathfinder

    @staticmethod
    def __pad_dimensions(x, y):
        return x + 2*ImageGenerator.BORDER_PX, y + 2*ImageGenerator.BORDER_PX

    @staticmethod
    def __pad_points(points, padding):
        def pad_point(point, padding):
            x, y = point
            return (x + padding, y + padding)

        return [pad_point(point, padding) for point in points]

    @staticmethod
    def __render_image_normalized(path, boundaries, size):
        from PIL import Image, ImageDraw, ImageFont
        image = Image.new("RGB", size, '#FFFFFF')
        draw = ImageDraw.Draw(image)

        draw.polygon(boundaries, '#999999')
        font = ImageFont.truetype('arial.ttf', ImageGenerator.FONT_SIZE)

        if len(path) > 1:
            for index, segment in enumerate(geometry_operations.calculate_perimeters(path)[:-1]):
                draw.line(segment, '#000000')
                draw.text(segment[0], str(index+1), fill='#FF0000', font=font)

        return image

    @staticmethod
    def __normalize_and_pad(path, boundaries, size):
        (smallest_x, smallest_y), (largest_x, largest_y) = \
        geometry_operations.get_bounding_box(boundaries + path)

        dx = largest_x - smallest_x
        dy = largest_y - smallest_y
        x_pixels, y_pixels = size

        def normalize_points(points):
            def normalize_point(point):
                x = float(point[0] - smallest_x)
                y = float(point[1] - smallest_y)
                return ((x/dx) * x_pixels, (y/dy) * y_pixels)

            return [normalize_point(point) for point in points]

        path = normalize_points(path)
        boundaries = normalize_points(boundaries)

        return ImageGenerator.__pad_points(path, ImageGenerator.BORDER_PX), \
               ImageGenerator.__pad_points(boundaries, ImageGenerator.BORDER_PX)

    def create_image(self, filename, size = None):

        def get_base_size():
            if size:
                return size
            else: 
                image_x = 1024
                image_y = int(1024 * geometry_operations.compute_ratio(\
                    self.pathfinder.boundaries))
                return image_x, image_y

        def get_padded_size():
            image_x, image_y = get_base_size()
            return ImageGenerator.__pad_dimensions(image_x, image_y)

        path, boundaries = ImageGenerator.__normalize_and_pad(self.pathfinder.get_path(),
                self.pathfinder.boundaries, get_base_size())
        image = ImageGenerator.__render_image_normalized(path, boundaries, get_padded_size())
        image.save(filename, 'jpeg')
