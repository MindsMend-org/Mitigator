# render_weights.py

# watch it learn in real-time

import moderngl
import numpy as np
from PIL import Image
import glfw

# Initialize GLFW
if not glfw.init():
    print("Could not initialize GLFW")
    exit(999)
else:
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(800, 600, "Weight Renderer", None, None)
    if not window:
        glfw.terminate()
        print("Could not create GLFW window")
        exit(999)

        # Make the window's context current
    glfw.make_context_current(window)

    # Initialize ModernGL
    ctx = moderngl.create_context()

def matrix_to_image(weight_matrix):
    # Normalize the matrix to the 0-255 range for image representation
    normalized_matrix = (weight_matrix - np.min(weight_matrix)) / (np.max(weight_matrix) - np.min(weight_matrix))
    image_data = (normalized_matrix * 255).astype(np.uint8)

    # Create an image from the normalized data
    image = Image.fromarray(image_data, 'L')  # 'L' mode is for grayscale
    return image

class WeightRenderer:
    def __init__(self, width, height):
        # Initialize ModernGL context
        self.ctx = moderngl.create_standalone_context()

        # Create the texture
        self.texture = self.ctx.texture((width, height), 3)

        # Vertex data for a quad
        vertices = np.array([
            -1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 1.0,
        ], dtype='f4')

        # Create the vertex buffer
        vertex_buffer = self.ctx.buffer(vertices.tobytes())
        # Create a shader program
        program = self.ctx.program(
            vertex_shader='''
                       #version 330
                       in vec2 in_vert;
                       in vec2 in_text;
                       out vec2 v_text;
                       void main() {
                           gl_Position = vec4(in_vert, 0.0, 1.0);
                           v_text = in_text;
                       }
                   ''',
            fragment_shader='''
                       #version 330
                       uniform sampler2D Texture;
                       in vec2 v_text;
                       out vec4 f_color;
                       void main() {
                           f_color = texture(Texture, v_text);
                       }
                   '''
        )

        # Create the vertex array object
        self.vao = self.ctx.vertex_array(
            program,
            [(vertex_buffer, '2f 2f', 'in_vert', 'in_text')]
        )

        # Create a frame-buffer to render to
        self.fbo = self.ctx.framebuffer(color_attachments=[self.ctx.texture((width, height), 4)])

        # Define a simple quad to render the texture on
        self.quad = self.ctx.buffer(np.array([
            -1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, 1.0, 1.0, 1.0
        ], dtype='f4'))

    def update(self, weight_matrix, GPU_MODE=False, TEST=False):
        if TEST:
            print(f'\r-Testing Display Neuron with image.-')
            #weight_matrix = loadimage
        if GPU_MODE:
            if weight_matrix is not None:
                # Normalize weight matrix to be in the range [0, 1]
                weight_matrix_normalized = (weight_matrix - weight_matrix.min()) / (weight_matrix.max() - weight_matrix.min())

                # Update texture with the weight matrix
                texture = self.ctx.texture(weight_matrix_normalized.shape, 1, weight_matrix_normalized.tobytes())
                texture.use()

                # Render the quad with the weight texture
                self.fbo.use()
                self.vao.render(moderngl.TRIANGLE_STRIP)
        else:
            if not glfw.window_should_close(window):
                # Convert the weight matrix to an image
                image = Image.fromarray((weight_matrix * 255).astype(np.uint8))  # Convert to 8-bit per channel
                if image.mode != 'RGB':
                    image = image.convert('RGB')  # Convert to RGB if necessary

                # Resize the image to match the texture size
                resized_image = image.resize(self.texture.size)

                # Convert the resized image to raw data
                raw_image_data = resized_image.tobytes()

                # Ensure the size of data matches what ModernGL expects
                expected_size = self.texture.width * self.texture.height * 3  # For RGB format
                if len(raw_image_data) != expected_size:
                    print(f"Data size mismatch: {len(raw_image_data)} != {expected_size}")
                else:
                    self.texture.write(raw_image_data)

                    # Swap front and back buffers
                    glfw.swap_buffers(window)

                    # Poll for and process events
                    glfw.poll_events()
            else:
                glfw.terminate()

    def save_render(self, file_path):
        # Save the rendered image to a file
        image = Image.frombytes('RGB', self.fbo.size, self.fbo.read(components=3))
        image.save(file_path)