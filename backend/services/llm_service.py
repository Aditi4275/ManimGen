"""
LLM Service for generating Manim code using OpenRouter API.
"""
import httpx
import re
import json
from typing import Optional

from config import get_settings
from .code_validator import validate_manim_code

settings = get_settings()

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Mock code templates for demo mode (when no API key is set)
MOCK_CODE_TEMPLATES = {
    "circle": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        self.play(Create(circle))
        self.wait(0.5)
        self.play(circle.animate.scale(1.5))
        self.play(circle.animate.shift(RIGHT * 2))
        self.play(circle.animate.shift(LEFT * 2))
        self.wait(1)
''',
    "square": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        square = Square(color=RED, fill_opacity=0.5)
        self.play(Create(square))
        self.wait(0.5)
        self.play(Rotate(square, PI/2))
        self.play(square.animate.scale(0.5))
        self.wait(1)
''',
    "triangle": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        triangle = Triangle(color=GREEN, fill_opacity=0.5)
        self.play(Create(triangle))
        self.wait(0.5)
        self.play(Rotate(triangle, PI))
        self.play(triangle.animate.scale(1.5))
        self.wait(1)
''',
    "transform": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5)
        triangle = Triangle(color=GREEN, fill_opacity=0.5)
        
        self.play(Create(circle))
        self.wait(0.5)
        self.play(Transform(circle, square))
        self.wait(0.5)
        self.play(Transform(circle, triangle))
        self.wait(1)
''',
    "pythagorean": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Title
        title = Text("Pythagorean Theorem", font_size=36, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Create right triangle
        triangle = Polygon(
            ORIGIN, RIGHT * 3, RIGHT * 3 + UP * 2,
            color=WHITE, fill_opacity=0.3
        ).shift(LEFT * 1.5 + DOWN * 0.5)
        
        self.play(Create(triangle))
        self.wait(0.5)
        
        # Labels
        a_label = MathTex("a").next_to(triangle, DOWN)
        b_label = MathTex("b").next_to(triangle, RIGHT)
        c_label = MathTex("c").move_to(triangle.get_center() + UP * 0.5 + LEFT * 0.5)
        
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait(0.5)
        
        # Formula
        formula = MathTex("a^2 + b^2 = c^2", font_size=48)
        formula.to_edge(DOWN)
        self.play(Write(formula))
        self.wait(2)
''',
    "sort": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Title
        title = Text("Bubble Sort", font_size=36, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Create bars
        values = [4, 2, 5, 1, 3]
        bars = VGroup()
        for i, val in enumerate(values):
            bar = Rectangle(width=0.6, height=val * 0.5, fill_opacity=0.7, color=BLUE)
            bar.move_to(RIGHT * (i - 2) * 0.8)
            bars.add(bar)
        
        self.play(Create(bars))
        self.wait(0.5)
        
        # Animate one swap
        self.play(
            bars[0].animate.set_color(RED),
            bars[1].animate.set_color(RED)
        )
        self.play(
            bars[0].animate.shift(RIGHT * 0.8),
            bars[1].animate.shift(LEFT * 0.8)
        )
        self.play(
            bars[0].animate.set_color(BLUE),
            bars[1].animate.set_color(BLUE)
        )
        self.wait(1)
''',
    "client_server": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Client
        client_box = Rectangle(width=2, height=1.2, color=BLUE, fill_opacity=0.3)
        client_label = Text("Client", font_size=24).move_to(client_box)
        client = VGroup(client_box, client_label).shift(LEFT * 4)
        
        # Server
        server_box = Rectangle(width=2, height=1.2, color=GREEN, fill_opacity=0.3)
        server_label = Text("Server", font_size=24).move_to(server_box)
        server = VGroup(server_box, server_label)
        
        # Database
        db_box = Rectangle(width=2, height=1.2, color=PURPLE, fill_opacity=0.3)
        db_label = Text("Database", font_size=20).move_to(db_box)
        db = VGroup(db_box, db_label).shift(RIGHT * 4)
        
        self.play(Create(client), Create(server), Create(db))
        self.wait(0.5)
        
        # Request arrow
        arrow1 = Arrow(client.get_right(), server.get_left(), color=YELLOW)
        req_label = Text("Request", font_size=16, color=YELLOW).next_to(arrow1, UP)
        self.play(GrowArrow(arrow1), Write(req_label))
        self.wait(0.3)
        
        # Query arrow
        arrow2 = Arrow(server.get_right(), db.get_left(), color=ORANGE)
        self.play(GrowArrow(arrow2))
        self.wait(0.3)
        
        # Response arrows
        arrow3 = Arrow(db.get_left(), server.get_right(), color=TEAL).shift(DOWN * 0.3)
        arrow4 = Arrow(server.get_left(), client.get_right(), color=TEAL).shift(DOWN * 0.3)
        resp_label = Text("Response", font_size=16, color=TEAL).next_to(arrow4, DOWN)
        self.play(GrowArrow(arrow3))
        self.play(GrowArrow(arrow4), Write(resp_label))
        self.wait(1)
''',
    "neural_network": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Neural Network", font_size=36, color=YELLOW).to_edge(UP)
        self.play(Write(title))
        
        # Create layers
        layers = []
        layer_sizes = [3, 4, 4, 2]  # Input, hidden, hidden, output
        
        for l, size in enumerate(layer_sizes):
            layer = VGroup()
            for i in range(size):
                neuron = Circle(radius=0.2, color=BLUE, fill_opacity=0.5)
                neuron.move_to(RIGHT * (l - 1.5) * 2 + UP * (i - (size-1)/2) * 0.8)
                layer.add(neuron)
            layers.append(layer)
        
        all_neurons = VGroup(*[n for layer in layers for n in layer])
        self.play(Create(all_neurons))
        self.wait(0.5)
        
        # Animate activation flowing through
        for layer in layers:
            self.play(*[n.animate.set_color(GREEN) for n in layer], run_time=0.5)
        self.wait(1)
''',
    "formula": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Mathematical Formulas", font_size=36, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        # Quadratic formula
        quad = MathTex(r"x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}")
        quad.shift(UP)
        
        # Euler's identity
        euler = MathTex(r"e^{i\\pi} + 1 = 0")
        
        # Pythagorean
        pyth = MathTex(r"a^2 + b^2 = c^2")
        pyth.shift(DOWN)
        
        self.play(Write(quad))
        self.wait(0.5)
        self.play(Write(euler))
        self.wait(0.5)
        self.play(Write(pyth))
        self.wait(2)
''',
    "default": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Welcome text
        title = Text("Manim Animation", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        
        # Transform to shapes
        self.play(title.animate.scale(0.5).to_edge(UP))
        
        # Create shapes
        circle = Circle(color=RED, fill_opacity=0.5).shift(LEFT * 2)
        square = Square(color=GREEN, fill_opacity=0.5)
        triangle = Triangle(color=BLUE, fill_opacity=0.5).shift(RIGHT * 2)
        
        shapes = VGroup(circle, square, triangle)
        self.play(Create(shapes))
        self.wait(0.5)
        
        # Animate
        self.play(Rotate(shapes, PI/4))
        self.play(shapes.animate.shift(UP))
        self.play(shapes.animate.shift(DOWN))
        self.wait(1)
'''
}

def get_mock_code(prompt: str) -> str:
    """Return mock code based on prompt keywords."""
    prompt_lower = prompt.lower()
    
    # Check for specific keywords
    if "pythagorean" in prompt_lower or "theorem" in prompt_lower:
        return MOCK_CODE_TEMPLATES["pythagorean"]
    elif "sort" in prompt_lower or "bubble" in prompt_lower or "algorithm" in prompt_lower:
        return MOCK_CODE_TEMPLATES["sort"]
    elif "client" in prompt_lower or "server" in prompt_lower or "database" in prompt_lower or "request" in prompt_lower:
        return MOCK_CODE_TEMPLATES["client_server"]
    elif "neural" in prompt_lower or "network" in prompt_lower or "ai" in prompt_lower or "machine learning" in prompt_lower:
        return MOCK_CODE_TEMPLATES["neural_network"]
    elif "formula" in prompt_lower or "equation" in prompt_lower or "quadratic" in prompt_lower or "euler" in prompt_lower:
        return MOCK_CODE_TEMPLATES["formula"]
    elif "transform" in prompt_lower or "morph" in prompt_lower or "change" in prompt_lower:
        return MOCK_CODE_TEMPLATES["transform"]
    elif "triangle" in prompt_lower:
        return MOCK_CODE_TEMPLATES["triangle"]
    elif "circle" in prompt_lower:
        return MOCK_CODE_TEMPLATES["circle"]
    elif "square" in prompt_lower or "rectangle" in prompt_lower:
        return MOCK_CODE_TEMPLATES["square"]
    
    return MOCK_CODE_TEMPLATES["default"]


# Multi-scene templates for creating 30-second videos (5-6 scenes @ ~5 seconds each)
MULTI_SCENE_TEMPLATES = {
    "intro": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Intro scene with title
        title = Text("{title}", font_size=56, color=BLUE)
        subtitle = Text("{subtitle}", font_size=28, color=GRAY).next_to(title, DOWN)
        
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))
        self.wait(0.5)
''',
    "concept1": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # First concept visualization
        header = Text("Step 1", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        shape = Circle(color=BLUE, fill_opacity=0.6)
        label = Text("Core Concept", font_size=24).next_to(shape, DOWN)
        
        self.play(Create(shape))
        self.play(Write(label))
        self.wait(0.5)
        self.play(shape.animate.scale(1.3))
        self.wait(1)
        self.play(FadeOut(shape), FadeOut(label), FadeOut(header))
''',
    "concept2": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Second concept - transformation
        header = Text("Step 2", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5)
        triangle = Triangle(color=GREEN, fill_opacity=0.5)
        
        self.play(Create(circle))
        self.wait(0.3)
        self.play(Transform(circle, square))
        self.wait(0.3)
        self.play(Transform(circle, triangle))
        self.wait(0.5)
        self.play(FadeOut(circle), FadeOut(header))
''',
    "concept3": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Third concept - movement and grouping
        header = Text("Step 3", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        shapes = VGroup(
            Circle(color=RED, fill_opacity=0.5).shift(LEFT * 2),
            Square(color=GREEN, fill_opacity=0.5),
            Triangle(color=BLUE, fill_opacity=0.5).shift(RIGHT * 2)
        )
        
        self.play(Create(shapes))
        self.wait(0.3)
        self.play(Rotate(shapes, PI/2))
        self.play(shapes.animate.arrange(DOWN))
        self.wait(0.5)
        self.play(FadeOut(shapes), FadeOut(header))
''',
    "diagram": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Diagram scene with connections
        header = Text("Architecture", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        # Create boxes
        box1 = VGroup(
            Rectangle(width=1.8, height=1, color=BLUE, fill_opacity=0.3),
            Text("A", font_size=20)
        ).shift(LEFT * 3)
        
        box2 = VGroup(
            Rectangle(width=1.8, height=1, color=GREEN, fill_opacity=0.3),
            Text("B", font_size=20)
        )
        
        box3 = VGroup(
            Rectangle(width=1.8, height=1, color=PURPLE, fill_opacity=0.3),
            Text("C", font_size=20)
        ).shift(RIGHT * 3)
        
        self.play(Create(box1), Create(box2), Create(box3))
        
        arrow1 = Arrow(box1.get_right(), box2.get_left(), color=YELLOW)
        arrow2 = Arrow(box2.get_right(), box3.get_left(), color=YELLOW)
        
        self.play(GrowArrow(arrow1), GrowArrow(arrow2))
        self.wait(1.5)
        self.play(FadeOut(VGroup(box1, box2, box3, arrow1, arrow2, header)))
''',
    "summary": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Summary/conclusion scene
        header = Text("Summary", font_size=36, color=YELLOW)
        header.to_edge(UP)
        self.play(Write(header))
        
        points = VGroup(
            Text("✓ Concept 1: Visualization", font_size=24, color=GREEN),
            Text("✓ Concept 2: Transformation", font_size=24, color=GREEN),
            Text("✓ Concept 3: Animation", font_size=24, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        
        for point in points:
            self.play(Write(point), run_time=0.6)
            self.wait(0.3)
        
        self.wait(1)
        self.play(FadeOut(points), FadeOut(header))
''',
    "outro": '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Outro with thank you
        thanks = Text("Thank You!", font_size=56, color=BLUE)
        
        self.play(Write(thanks))
        self.wait(0.5)
        
        # Animate with colors
        self.play(thanks.animate.set_color(RED))
        self.play(thanks.animate.set_color(GREEN))
        self.play(thanks.animate.set_color(BLUE))
        
        self.wait(1)
        self.play(FadeOut(thanks))
'''
}


def split_topic_into_scenes(prompt: str) -> list:
    """
    Intelligently split a topic/prompt into logical scene parts.
    Returns list of (scene_title, scene_description) tuples.
    """
    prompt_lower = prompt.lower()
    
    # Common topic patterns and their scene breakdowns
    if "sort" in prompt_lower or "bubble" in prompt_lower:
        return [
            ("Introduction", "Title: Bubble Sort Algorithm - How it works"),
            ("Unsorted Array", "Show initial unsorted array of numbers"),
            ("Compare & Swap", "Demonstrate comparing adjacent elements and swapping"),
            ("Multiple Passes", "Show multiple passes through the array"),
            ("Sorted Result", "Show final sorted array with summary")
        ]
    
    elif "binary search" in prompt_lower or "search" in prompt_lower:
        return [
            ("Introduction", "Title: Binary Search - Efficient searching"),
            ("Sorted Array", "Show a sorted array we'll search in"),
            ("Find Middle", "Highlight the middle element"),
            ("Compare & Narrow", "Compare target with middle, narrow search range"),
            ("Found Target", "Show successful search with complexity O(log n)")
        ]
    
    elif "neural" in prompt_lower or "network" in prompt_lower or "deep learning" in prompt_lower:
        return [
            ("Introduction", "Title: Neural Networks Explained"),
            ("Input Layer", "Show input neurons receiving data"),
            ("Hidden Layers", "Visualize hidden layer processing"),
            ("Weights & Connections", "Animate data flowing through connections"),
            ("Output Layer", "Show final output and prediction")
        ]
    
    elif "pythagorean" in prompt_lower or "theorem" in prompt_lower:
        return [
            ("Introduction", "Title: The Pythagorean Theorem"),
            ("Right Triangle", "Draw a right triangle with sides a, b, c"),
            ("Squares on Sides", "Draw squares on each side of the triangle"),
            ("Area Comparison", "Show a² + b² = c² visually"),
            ("Formula", "Display the famous equation")
        ]
    
    elif "client" in prompt_lower or "server" in prompt_lower or "api" in prompt_lower:
        return [
            ("Introduction", "Title: Client-Server Architecture"),
            ("The Client", "Show client making a request"),
            ("The Server", "Server receives and processes request"),
            ("Database Query", "Server queries the database"),
            ("Response Flow", "Data flows back to client")
        ]
    
    elif "recursion" in prompt_lower or "fibonacci" in prompt_lower:
        return [
            ("Introduction", "Title: Recursion & Fibonacci"),
            ("Base Case", "Show the base case F(0)=0, F(1)=1"),
            ("Recursive Call", "Visualize function calling itself"),
            ("Call Stack", "Show the call stack building up"),
            ("Result", "Show final computed value")
        ]
    
    elif "tree" in prompt_lower or "binary tree" in prompt_lower:
        return [
            ("Introduction", "Title: Binary Tree Data Structure"),
            ("Root Node", "Create and show the root node"),
            ("Adding Children", "Add left and right children"),
            ("Tree Traversal", "Show in-order, pre-order traversal"),
            ("Complete Tree", "Display the full tree structure")
        ]
    
    elif "stack" in prompt_lower or "queue" in prompt_lower:
        return [
            ("Introduction", f"Title: {'Stack (LIFO)' if 'stack' in prompt_lower else 'Queue (FIFO)'} Data Structure"),
            ("Empty Structure", "Show empty stack/queue"),
            ("Push/Enqueue", "Add elements to the structure"),
            ("Pop/Dequeue", "Remove elements showing order"),
            ("Use Cases", "Show common applications")
        ]
    
    elif "graph" in prompt_lower or "bfs" in prompt_lower or "dfs" in prompt_lower:
        return [
            ("Introduction", "Title: Graph Traversal Algorithms"),
            ("Create Graph", "Show nodes and edges"),
            ("Start Node", "Highlight the starting node"),
            ("Traversal Steps", "Animate visiting each node"),
            ("Visited All", "Show complete traversal path")
        ]
    
    elif "array" in prompt_lower or "list" in prompt_lower:
        return [
            ("Introduction", "Title: Arrays and Lists"),
            ("Create Array", "Show array with indices"),
            ("Access Element", "Highlight accessing by index O(1)"),
            ("Insert/Delete", "Show insert and delete operations"),
            ("Summary", "Compare time complexities")
        ]
    
    else:
        # Generic topic splitting - extract key concepts from prompt
        words = [w for w in prompt.split() if len(w) > 3 and w.lower() not in ['the', 'and', 'for', 'with', 'how', 'what', 'why', 'show', 'explain', 'create', 'make', 'visualize', 'animate', 'demonstrate']]
        topic = " ".join(words[:4]).title() if words else "Animation"
        
        return [
            ("Introduction", f"Title: {topic}"),
            ("Core Concept", f"Explain the main idea of {topic}"),
            ("Visualization", f"Visual demonstration of {topic}"),
            ("Details", f"Additional details and examples"),
            ("Summary", f"Recap of {topic} with key points")
        ]


def generate_scene_code_for_part(scene_title: str, scene_description: str, scene_index: int, total_scenes: int) -> str:
    """
    Generate Manim code for a specific scene part.
    Creates unique animations based on the scene's role in the video.
    """
    title_clean = scene_title.replace("'", "\\'").replace('"', '\\"')
    desc_clean = scene_description.replace("'", "\\'").replace('"', '\\"')
    
    # Different templates based on scene position and type
    if scene_index == 0:  # Intro
        # Extract title from description
        if "Title:" in scene_description:
            main_title = scene_description.split("Title:")[-1].strip()
        else:
            main_title = scene_title
        
        return f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Intro scene
        title = Text("{main_title}", font_size=48, color=BLUE)
        
        self.play(Write(title), run_time=1.5)
        self.wait(1)
        
        # Animate title
        self.play(title.animate.scale(0.7).to_edge(UP))
        
        subtitle = Text("Let's explore step by step", font_size=24, color=GRAY)
        subtitle.next_to(title, DOWN)
        self.play(FadeIn(subtitle))
        self.wait(1.5)
        
        self.play(FadeOut(title), FadeOut(subtitle))
'''
    
    elif scene_index == total_scenes - 1:  # Outro/Summary
        return f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Summary scene
        header = Text("Summary", font_size=42, color=YELLOW)
        header.to_edge(UP)
        self.play(Write(header))
        
        points = VGroup(
            Text("✓ Concept introduced", font_size=26, color=GREEN),
            Text("✓ Steps demonstrated", font_size=26, color=GREEN),
            Text("✓ Visual explanation", font_size=26, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        
        for point in points:
            self.play(Write(point), run_time=0.5)
            self.wait(0.2)
        
        self.wait(1)
        
        thanks = Text("Thanks for watching!", font_size=36, color=BLUE)
        thanks.next_to(points, DOWN, buff=0.8)
        self.play(Write(thanks))
        self.wait(1.5)
'''
    
    elif "array" in scene_description.lower() or "unsorted" in scene_description.lower():
        return f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # {scene_title}: Array visualization
        header = Text("{title_clean}", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        # Create array boxes
        values = [64, 34, 25, 12, 22]
        boxes = VGroup()
        for i, val in enumerate(values):
            box = VGroup(
                Square(side_length=0.8, color=BLUE, fill_opacity=0.3),
                Text(str(val), font_size=20)
            )
            box.move_to(RIGHT * (i - 2) * 1.0)
            boxes.add(box)
        
        self.play(Create(boxes))
        self.wait(0.5)
        
        # Highlight each element
        for box in boxes:
            self.play(box[0].animate.set_color(GREEN), run_time=0.3)
            self.play(box[0].animate.set_color(BLUE), run_time=0.3)
        
        self.wait(1)
        self.play(FadeOut(boxes), FadeOut(header))
'''
    
    elif "compare" in scene_description.lower() or "swap" in scene_description.lower():
        return f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # {scene_title}: Compare and Swap
        header = Text("{title_clean}", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        # Two elements to compare
        box1 = VGroup(
            Square(side_length=1, color=RED, fill_opacity=0.5),
            Text("5", font_size=28)
        ).shift(LEFT * 1.5)
        
        box2 = VGroup(
            Square(side_length=1, color=RED, fill_opacity=0.5),
            Text("3", font_size=28)
        ).shift(RIGHT * 1.5)
        
        self.play(Create(box1), Create(box2))
        self.wait(0.3)
        
        # Compare arrow
        compare = Text("5 > 3 → Swap!", font_size=24, color=WHITE)
        compare.shift(DOWN * 1.5)
        self.play(Write(compare))
        self.wait(0.5)
        
        # Swap animation
        self.play(
            box1.animate.shift(RIGHT * 3),
            box2.animate.shift(LEFT * 3),
            run_time=1
        )
        
        self.play(box1[0].animate.set_color(GREEN), box2[0].animate.set_color(GREEN))
        self.wait(1)
        self.play(FadeOut(VGroup(box1, box2, compare, header)))
'''
    
    elif "node" in scene_description.lower() or "layer" in scene_description.lower():
        return f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # {scene_title}: Node/Layer visualization
        header = Text("{title_clean}", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        # Create nodes in a layer
        nodes = VGroup()
        for i in range(4):
            node = Circle(radius=0.3, color=BLUE, fill_opacity=0.6)
            node.shift(UP * (i - 1.5) * 0.9)
            nodes.add(node)
        
        self.play(Create(nodes))
        self.wait(0.3)
        
        # Activate nodes one by one
        for node in nodes:
            self.play(node.animate.set_color(GREEN), run_time=0.3)
        
        label = Text("Active Layer", font_size=24, color=WHITE).shift(DOWN * 2)
        self.play(Write(label))
        self.wait(1)
        self.play(FadeOut(VGroup(nodes, label, header)))
'''
    
    elif "triangle" in scene_description.lower() or "geometry" in scene_description.lower():
        return f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # {scene_title}: Geometry
        header = Text("{title_clean}", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        # Right triangle
        triangle = Polygon(
            ORIGIN, RIGHT * 3, RIGHT * 3 + UP * 2,
            color=WHITE, fill_opacity=0.2
        ).shift(DOWN * 0.5)
        
        self.play(Create(triangle))
        
        # Label sides
        a = Text("a", font_size=24, color=RED).next_to(triangle, DOWN)
        b = Text("b", font_size=24, color=GREEN).next_to(triangle, RIGHT)
        c = Text("c", font_size=24, color=BLUE).move_to(triangle.get_center() + UP*0.5 + LEFT*0.5)
        
        self.play(Write(a), Write(b), Write(c))
        self.wait(1.5)
        self.play(FadeOut(VGroup(triangle, a, b, c, header)))
'''
    
    elif "flow" in scene_description.lower() or "request" in scene_description.lower() or "response" in scene_description.lower():
        return f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # {scene_title}: Data flow
        header = Text("{title_clean}", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        # Source and destination
        source = VGroup(
            Rectangle(width=1.5, height=1, color=BLUE, fill_opacity=0.4),
            Text("Source", font_size=18)
        ).shift(LEFT * 3)
        
        dest = VGroup(
            Rectangle(width=1.5, height=1, color=GREEN, fill_opacity=0.4),
            Text("Dest", font_size=18)
        ).shift(RIGHT * 3)
        
        self.play(Create(source), Create(dest))
        
        # Animated arrow/data flow
        arrow = Arrow(source.get_right(), dest.get_left(), color=YELLOW)
        data = Dot(color=RED).move_to(source.get_right())
        
        self.play(GrowArrow(arrow))
        self.play(data.animate.move_to(dest.get_left()), run_time=1.5)
        self.play(FadeOut(data))
        
        self.wait(0.5)
        self.play(FadeOut(VGroup(source, dest, arrow, header)))
'''
    
    else:
        # Default scene with shapes and animation
        colors = ["BLUE", "RED", "GREEN", "PURPLE", "ORANGE"]
        color = colors[scene_index % len(colors)]
        
        return f'''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # {scene_title}
        header = Text("{title_clean}", font_size=32, color=YELLOW).to_edge(UP)
        self.play(Write(header))
        
        # Main content
        main_text = Text("{desc_clean[:50]}...", font_size=24) if len("{desc_clean}") > 50 else Text("{desc_clean}", font_size=24)
        main_text.shift(UP * 0.5)
        self.play(Write(main_text))
        
        # Decorative shapes
        shapes = VGroup(
            Circle(radius=0.5, color={color}, fill_opacity=0.5).shift(LEFT * 2 + DOWN),
            Square(side_length=0.8, color={color}, fill_opacity=0.5).shift(DOWN),
            Triangle(color={color}, fill_opacity=0.5).scale(0.5).shift(RIGHT * 2 + DOWN)
        )
        
        self.play(Create(shapes))
        self.wait(0.3)
        self.play(Rotate(shapes, PI/4))
        self.wait(1)
        self.play(FadeOut(VGroup(header, main_text, shapes)))
'''


def get_multi_scene_codes(prompt: str, num_scenes: int = 5) -> list:
    """
    Generate multiple scene codes from a single prompt.
    Intelligently splits the topic into logical parts and generates unique code for each.
    
    Args:
        prompt: User's description of the animation topic
        num_scenes: Number of scenes to generate (default 5)
    
    Returns:
        List of tuples: [(scene_prompt, scene_code), ...]
    """
    # Split the topic into logical scene parts
    scene_parts = split_topic_into_scenes(prompt)[:num_scenes]
    
    # Generate code for each scene
    scenes = []
    for i, (title, description) in enumerate(scene_parts):
        code = generate_scene_code_for_part(title, description, i, len(scene_parts))
        scenes.append((title, code))
    
    return scenes


SYSTEM_PROMPT = """You are an expert Manim animation code generator. Your task is to generate Python code using the Manim library (Community Edition) to create mathematical and technical animations.

## Rules:
1. Always start with `from manim import *`
2. Create a single Scene class that inherits from `Scene`
3. The class name should be `GeneratedScene`
4. Implement the `construct` method with all animations
5. Use `self.play()` for all animations
6. Keep animations concise (under 15 seconds total)
7. Use descriptive variable names
8. Add appropriate `self.wait()` calls between animations
9. Use colors from Manim's color palette (RED, BLUE, GREEN, YELLOW, WHITE, etc.)
10. For text, use `Text()` or `MathTex()` for mathematical expressions

## Output Format:
Return ONLY the Python code, no explanations, no markdown code blocks.
The code must be valid and executable.

## Example Output:
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        self.play(Create(circle))
        self.wait(1)
        
        square = Square(color=RED)
        self.play(Transform(circle, square))
        self.wait(1)
"""

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Create a circle that moves to the right"
    },
    {
        "role": "assistant",
        "content": """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        circle = Circle(color=BLUE, fill_opacity=0.5)
        self.play(Create(circle))
        self.wait(0.5)
        self.play(circle.animate.shift(RIGHT * 3))
        self.wait(1)
"""
    },
    {
        "role": "user",
        "content": "Show two boxes labeled 'Client' and 'Server' with an arrow between them"
    },
    {
        "role": "assistant",
        "content": """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Create boxes
        client_box = Rectangle(width=2, height=1, color=BLUE)
        client_label = Text("Client", font_size=24).move_to(client_box)
        client = VGroup(client_box, client_label).shift(LEFT * 3)
        
        server_box = Rectangle(width=2, height=1, color=GREEN)
        server_label = Text("Server", font_size=24).move_to(server_box)
        server = VGroup(server_box, server_label).shift(RIGHT * 3)
        
        # Create arrow
        arrow = Arrow(client.get_right(), server.get_left(), color=YELLOW)
        
        # Animate
        self.play(Create(client))
        self.play(Create(server))
        self.wait(0.5)
        self.play(GrowArrow(arrow))
        self.wait(1)
"""
    },
    {
        "role": "user",
        "content": "Display the quadratic formula with animation"
    },
    {
        "role": "assistant",
        "content": """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("The Quadratic Formula", font_size=36, color=YELLOW)
        title.to_edge(UP)
        
        formula = MathTex(
            r"x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
            font_size=48
        )
        
        self.play(Write(title))
        self.wait(0.5)
        self.play(Write(formula))
        self.wait(2)
"""
    }
]


def extract_code(response_text: str) -> str:
    """Extract Python code from LLM response."""
    # Try to find code blocks
    code_block_pattern = r"```(?:python)?\s*(.*?)```"
    matches = re.findall(code_block_pattern, response_text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # If no code blocks, assume the entire response is code
    return response_text.strip()


async def generate_manim_code(prompt: str, max_retries: int = 2) -> str:
    """
    Generate Manim code from a text prompt using OpenRouter API.
    Falls back to mock code if API key is not configured.
    
    Args:
        prompt: User's description of the animation
        max_retries: Number of retry attempts if generation fails
    
    Returns:
        Valid Manim Python code
    """
    # Check if API key is configured (not empty and not placeholder)
    api_key = settings.openrouter_api_key
    if not api_key or api_key == "your_openrouter_api_key_here" or api_key.startswith("your_"):
        # Use mock mode for demo/testing
        print(f"[MOCK MODE] No API key configured, using mock code for prompt: {prompt[:50]}...")
        return get_mock_code(prompt)
    
    # Build messages with few-shot examples
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *FEW_SHOT_EXAMPLES,
        {"role": "user", "content": prompt}
    ]
    
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.frontend_url,
        "X-Title": "MotionScript"
    }
    
    last_error = None
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for attempt in range(max_retries + 1):
            try:
                response = await client.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json={
                        "model": settings.openrouter_model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    raise Exception(f"OpenRouter API error: {error_data.get('error', {}).get('message', response.text)}")
                
                data = response.json()
                generated_text = data["choices"][0]["message"]["content"]
                generated_code = extract_code(generated_text)
                
                # Validate the generated code
                is_valid, error_message = validate_manim_code(generated_code)
                
                if is_valid:
                    return generated_code
                
                # If invalid, add error context and retry
                if attempt < max_retries:
                    messages.append({"role": "assistant", "content": generated_text})
                    messages.append({
                        "role": "user", 
                        "content": f"The previous code had an error: {error_message}\nPlease fix it and generate valid Manim code."
                    })
                else:
                    last_error = error_message
                    
            except httpx.TimeoutException:
                last_error = "Request timed out"
                if attempt == max_retries:
                    raise Exception(f"Failed to generate Manim code: {last_error}")
            except Exception as e:
                last_error = str(e)
                if attempt == max_retries:
                    raise Exception(f"Failed to generate Manim code: {last_error}")
    
    raise Exception(f"Failed to generate valid Manim code after {max_retries + 1} attempts: {last_error}")
