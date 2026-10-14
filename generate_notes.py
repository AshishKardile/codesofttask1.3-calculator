import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to calculate total page count dynamically
    and render professional running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Page 1 is the cover page; do not draw header/footer
        if self._pageNumber == 1:
            return
        
        self.saveState()
        
        # Color palette
        dark_blue = colors.HexColor('#1A365D')
        charcoal = colors.HexColor('#2D3748')
        light_grey = colors.HexColor('#E2E8F0')
        
        # Draw Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(dark_blue)
        self.drawString(54, 752, "JAVA PROGRAMMING FOR BEGINNERS")
        self.setFont("Helvetica", 8)
        self.setFillColor(charcoal)
        self.drawRightString(558, 752, "COMPLETE CONCEPT NOTES & EXAMPLES")
        
        # Header Rule
        self.setStrokeColor(light_grey)
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)
        
        # Draw Footer Rule
        self.line(54, 52, 558, 52)
        
        # Draw Footer
        self.setFont("Helvetica-Oblique", 8)
        self.setFillColor(charcoal)
        self.drawString(54, 40, "Based on Apna College Java Tutorial by Shraddha Khapra")
        
        self.setFont("Helvetica", 8)
        self.drawRightString(558, 40, f"Page {self._pageNumber} of {page_count}")
        
        self.restoreState()


def escape_html(text):
    """Escapes XML-sensitive characters for ReportLab Paragraph compatibility."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def create_code_block(code_text, style_monospace):
    """
    Creates a stylized table containing code text, functioning as a code block.
    """
    escaped = escape_html(code_text.strip())
    # Format spaces and tabs for HTML representation
    formatted = escaped.replace("\n", "<br/>").replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;").replace("  ", "&nbsp;&nbsp;")
    p = Paragraph(formatted, style_monospace)
    
    t = Table([[p]], colWidths=[504])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#E2E8F0')),
        ('LINELEFT', (0,0), (-1,-1), 3.0, colors.HexColor('#3182CE')), # Blue left border accent
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    return t


def create_table(data_matrix, col_widths=None):
    """Creates a formatted table for tabular data representation."""
    t = Table(data_matrix, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')), # Primary blue header
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    # Alternating row background
    for i in range(1, len(data_matrix)):
        bg_color = colors.HexColor('#F7FAFC') if i % 2 == 1 else colors.HexColor('#FFFFFF')
        t.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), bg_color)]))
        
    return t


def build_pdf(filename="Java_Complete_Notes.pdf"):
    # Target path setup
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    style_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor('#1A365D'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    style_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#4A5568'),
        alignment=TA_CENTER,
        spaceAfter=25
    )
    
    style_metadata = ParagraphStyle(
        'CoverMetadata',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#718096'),
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    style_h1 = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8
    )

    style_body_bold = ParagraphStyle(
        'BodyTextCustomBold',
        parent=style_body,
        fontName='Helvetica-Bold'
    )
    
    style_bullet = ParagraphStyle(
        'BulletCustom',
        parent=style_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    style_mono = ParagraphStyle(
        'MonospaceBase',
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1A202C')
    )
    
    story = []

    # ==========================================
    # COVER PAGE
    # ==========================================
    story.append(Spacer(1, 100))
    story.append(Paragraph("JAVA PROGRAMMING", style_title))
    story.append(Paragraph("The Ultimate Concept Notes for Beginners", style_subtitle))
    
    # Modern accent divider line
    accent_bar = Table([['']], colWidths=[200], rowHeights=[4])
    accent_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#3182CE')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(accent_bar)
    story.append(Spacer(1, 40))
    
    # Details Box
    desc_p = Paragraph(
        "A highly detailed, elongated compilation of core Java programming topics. "
        "Each section includes comprehensive explanations, memory concepts, "
        "practical examples, code blocks, and a detailed walk-through of a mini-project. "
        "Designed to serve as a complete reference guide for beginners starting their software development journey.",
        ParagraphStyle('Desc', parent=style_body, alignment=TA_CENTER, fontSize=10, leading=15)
    )
    desc_table = Table([[desc_p]], colWidths=[400])
    desc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(desc_table)
    story.append(Spacer(1, 120))
    
    story.append(Paragraph("<b>Source Tutorial:</b> Java Tutorial for Beginners | Learn Java in 2 Hours (Apna College)", style_metadata))
    story.append(Paragraph("<b>Instructor:</b> Shraddha Khapra", style_metadata))
    story.append(Paragraph("<b>Compiled For:</b> Ashish Kardile", style_metadata))
    story.append(Paragraph("<b>Date of Compilation:</b> July 2026", style_metadata))
    story.append(PageBreak())

    # ==========================================
    # 1. INTRODUCTION & SETUP
    # ==========================================
    story.append(Paragraph("1. Introduction & Setup", style_h1))
    story.append(Paragraph(
        "<b>Java</b> is a high-level, class-based, object-oriented programming language designed to have as few implementation dependencies as possible. "
        "It follows the philosophy of <i>'Write Once, Run Anywhere' (WORA)</i>, meaning compiled Java code can run on all platforms that support Java without the need to recompile.",
        style_body
    ))
    
    story.append(Paragraph("<b>The Core Components: JDK, JRE, and JVM</b>", style_h2))
    story.append(Paragraph(
        "To understand how Java runs, we must distinguish between its three fundamental components:",
        style_body
    ))
    story.append(Paragraph("&bull; <b>JVM (Java Virtual Machine):</b> The engine that drives the Java code. It converts Java bytecode into machine language. The JVM is platform-dependent (different JVMs are built for Windows, macOS, Linux).", style_bullet))
    story.append(Paragraph("&bull; <b>JRE (Java Runtime Environment):</b> The environment in which Java programs run. It contains the JVM, class libraries, and other supporting files. It does not contain any development tools (like compilers).", style_bullet))
    story.append(Paragraph("&bull; <b>JDK (Java Development Kit):</b> A full-featured software development kit containing the JRE, along with tools like the compiler (<code>javac</code>), debugger, and archiver (<code>jar</code>).", style_bullet))
    
    story.append(Spacer(1, 4))
    # Relationship Table
    comp_data = [
        ["Component", "What it stands for", "What it contains", "Who uses it"],
        ["JVM", "Java Virtual Machine", "Execution Engine", "Runs the compiled bytecode"],
        ["JRE", "Java Runtime Environment", "JVM + Core Libraries", "End-users running Java apps"],
        ["JDK", "Java Development Kit", "JRE + Dev Tools (javac, etc.)", "Developers writing Java apps"]
    ]
    story.append(create_table(comp_data, col_widths=[70, 140, 160, 134]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Setting Up the Environment</b>", style_h2))
    story.append(Paragraph(
        "1. <b>Download JDK:</b> Install the standard Java Development Kit (e.g., JDK 11, 17, or 21) from Oracle or OpenJDK.<br/>"
        "2. <b>Environment Variables Configuration (Windows):</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&bull; Copy the path to the <code>bin</code> folder (e.g., <code>C:\\Program Files\\Java\\jdk-21\\bin</code>).<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&bull; Open <i>System Properties</i> -> <i>Environment Variables</i>.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&bull; Locate the <code>Path</code> variable in System Variables, edit it, and paste the path.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&bull; (Optional) Create a new system variable named <code>JAVA_HOME</code> with value pointing to the JDK root folder (without <code>bin</code>).<br/>"
        "3. <b>Verification:</b> Open the terminal (cmd/powershell) and run these commands to verify installation:",
        style_body
    ))
    story.append(create_code_block("java -version\njavac -version", style_mono))
    
    story.append(PageBreak())

    # ==========================================
    # 2. OUR FIRST PROGRAM & BASIC ANATOMY
    # ==========================================
    story.append(Paragraph("2. Our First Program & Basic Anatomy", style_h1))
    story.append(Paragraph(
        "Let's look at the standard template of a simple Java program that prints <code>\"Hello World\"</code>. Every single line of code in Java must reside inside a class.",
        style_body
    ))
    
    hello_code = """public class Main {
    public static void main(String[] args) {
        // Our first program
        System.out.println("Hello World");
    }
}"""
    story.append(create_code_block(hello_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Elaborating the Keywords:</b>", style_h2))
    story.append(Paragraph("&bull; <b><code>public</code>:</b> An access modifier. It makes the class or method accessible from anywhere in the project. The main class must be <code>public</code>.", style_bullet))
    story.append(Paragraph("&bull; <b><code>class Main</code>:</b> Declares a class named <code>Main</code>. In Java, the file name <b>must</b> match the name of the public class exactly. Thus, this file must be named <code>Main.java</code>.", style_bullet))
    story.append(Paragraph("&bull; <b><code>static</code>:</b> A keyword indicating that the method belongs to the class itself rather than an instance of the class. This allows the JVM to execute <code>main()</code> without creating an object of the class first.", style_bullet))
    story.append(Paragraph("&bull; <b><code>void</code>:</b> The return type of the method. <code>void</code> means the method does not return any value back to the caller.", style_bullet))
    story.append(Paragraph("&bull; <b><code>main</code>:</b> The starting point or entry point of the Java program. The JVM searches for this specific method signature to begin execution.", style_bullet))
    story.append(Paragraph("&bull; <b><code>String[] args</code>:</b> A parameter of type String array. It stores command-line arguments passed to the program during execution.", style_bullet))
    story.append(Paragraph("&bull; <b><code>System.out.println()</code>:</b> Used to output text. <code>System</code> is a built-in class, <code>out</code> is a static member representing the standard output stream, and <code>println</code> is a method that prints the content followed by a newline. To print without a newline, use <code>System.out.print()</code>.", style_bullet))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>Compilation & Execution Cycle:</b>", style_h2))
    story.append(Paragraph(
        "Java is both a compiled and interpreted language. Here are the terminal commands to run the code:",
        style_body
    ))
    comp_commands = """# 1. Compile: Generates Main.class (containing platform-independent bytecode)
javac Main.java

# 2. Run: The JVM executes the bytecode in Main.class
java Main"""
    story.append(create_code_block(comp_commands, style_mono))

    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>Comments in Java:</b>", style_h2))
    story.append(Paragraph(
        "Comments are non-executable lines used to document code. Java supports two types of comments:",
        style_body
    ))
    comments_code = """// This is a Single-line Comment

/*
   This is a Multi-line Comment.
   It can span multiple lines.
*/"""
    story.append(create_code_block(comments_code, style_mono))
    
    story.append(PageBreak())

    # ==========================================
    # 3. VARIABLES & DATA TYPES
    # ==========================================
    story.append(Paragraph("3. Variables & Data Types", style_h1))
    story.append(Paragraph(
        "A <b>Variable</b> is a container that stores data values during the execution of a Java program. "
        "Every variable in Java must have a declared data type. Java is a <i>statically-typed language</i>, meaning variable types are checked at compile-time and cannot change dynamically.",
        style_body
    ))
    
    var_code = """// Syntax: dataType variableName = value;
int age = 30;
String name = "Aman";
double salary = 85000.50;

// Variables can be updated later
age = 31;"""
    story.append(create_code_block(var_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>The Two Data Type Categories in Java:</b>", style_h2))
    story.append(Paragraph(
        "Java data types are divided into two main categories: <b>Primitive Types</b> and <b>Non-Primitive (Reference) Types</b>.",
        style_body
    ))
    
    story.append(Paragraph("<b>1. Primitive Data Types</b>", style_body_bold))
    story.append(Paragraph(
        "Primitive types are predefined by the language and represent simple, single values. There are exactly 8 primitive data types in Java:",
        style_body
    ))
    
    primitive_table_data = [
        ["Data Type", "Size", "Default Value", "Description / Value Range", "Example"],
        ["byte", "1 byte", "0", "Integers: -128 to 127", "byte age = 30;"],
        ["short", "2 bytes", "0", "Integers: -32,768 to 32,767", "short code = 450;"],
        ["int", "4 bytes", "0", "Integers: -2 Billion to 2 Billion (Default)", "int population = 150000;"],
        ["long", "8 bytes", "0L", "Large integers. Needs 'L' suffix", "long distance = 9876543210L;"],
        ["float", "4 bytes", "0.0f", "Single-precision decimal. Needs 'f' suffix", "float pi = 3.14f;"],
        ["double", "8 bytes", "0.0d", "Double-precision decimal (Default)", "double salary = 85000.50;"],
        ["char", "2 bytes", "'\\u0000'", "Single character in single quotes", "char grade = 'A';"],
        ["boolean", "1 bit", "false", "Logical values: true or false", "boolean isJavaFun = true;"]
    ]
    story.append(create_table(primitive_table_data, col_widths=[55, 45, 75, 204, 125]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2. Non-Primitive (Reference) Types</b>", style_body_bold))
    story.append(Paragraph(
        "Non-primitive data types refer to objects. They do not store the value itself, but rather a reference (memory address) to where the object resides in memory (specifically in the <i>Heap</i>). "
        "Examples include <b>Strings</b>, <b>Arrays</b>, <b>Classes</b>, and <b>Interfaces</b>.",
        style_body
    ))
    
    diff_table_data = [
        ["Feature", "Primitive Types", "Non-Primitive Types"],
        ["Memory Allocation", "Stored directly on the Stack", "Value on Heap, reference on Stack"],
        ["Size", "Fixed depending on the type (e.g., 4 bytes)", "Variable size (depends on object complexity)"],
        ["Methods", "Cannot call methods (no properties)", "Can call methods (e.g., string.length())"],
        ["Default Value", "Never null (has predefined defaults)", "Can be null (points to nothing)"]
    ]
    story.append(create_table(diff_table_data, col_widths=[110, 194, 200]))
    
    story.append(PageBreak())

    # ==========================================
    # 4. STRINGS IN JAVA
    # ==========================================
    story.append(Paragraph("4. Strings in Java", style_h1))
    story.append(Paragraph(
        "A <b>String</b> is a non-primitive data type that represents a sequence of characters. Strings are objects in Java, created using the <code>String</code> class.",
        style_body
    ))
    
    string_init = """// Initialization
String greeting = "Hello World";

// Concatenation
String firstName = "Aman";
String lastName = "Sharma";
String fullName = firstName + " " + lastName; // Aman Sharma"""
    story.append(create_code_block(string_init, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Essential String Methods</b>", style_h2))
    story.append(Paragraph(
        "Since Strings are objects, they come equipped with built-in methods. Let's look at the most common ones:",
        style_body
    ))
    
    string_methods = """String name = "Aman";

// 1. Length of string
System.out.println(name.length()); // Outputs: 4

// 2. Character at a specific index (0-based)
System.out.println(name.charAt(0)); // Outputs: A
System.out.println(name.charAt(3)); // Outputs: n

// 3. Replacing characters (returns a NEW string!)
String newName = name.replace('a', 'o');
System.out.println(newName); // Outputs: Amon (Note: replaces lower-case 'a')

// 4. Substring (extracting parts of string)
// syntax: substring(beginIndex, endIndex) -- endIndex is exclusive
String description = "Java Programming";
System.out.println(description.substring(0, 4)); // Outputs: Java
System.out.println(description.substring(5));    // Outputs: Programming (to end)"""
    story.append(create_code_block(string_methods, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Important Concept: String Immutability</b>", style_h2))
    story.append(Paragraph(
        "In Java, **Strings are immutable**. This means once a String object is created in memory, its value cannot be modified. "
        "Any operation that appears to modify a string (like <code>replace</code> or concatenation) actually creates a brand-new String object in the <b>String Constant Pool (SCP)</b> and returns its reference. The original string remains unchanged.",
        style_body
    ))
    
    immutability_ex = """String s1 = "Hello";
s1.concat(" World"); // Modifies s1? No!
System.out.println(s1); // Outputs: Hello

s1 = s1.concat(" World"); // Reassigning reference
System.out.println(s1); // Outputs: Hello World (s1 now points to a new object)"""
    story.append(create_code_block(immutability_ex, style_mono))
    
    story.append(PageBreak())

    # ==========================================
    # 5. ARRAYS IN JAVA
    # ==========================================
    story.append(Paragraph("5. Arrays in Java", style_h1))
    story.append(Paragraph(
        "An <b>Array</b> is a collection of variables of the same data type stored in contiguous memory locations. "
        "Arrays in Java have a **fixed size**, which must be specified when the array is created and cannot be changed later.",
        style_body
    ))
    
    array_code = """// Method 1: Declare and allocate memory
int[] marks = new int[3];
marks[0] = 97;
marks[1] = 98;
marks[2] = 95;

// Method 2: Inline initialization
int[] grades = { 90, 85, 88, 92 };"""
    story.append(create_code_block(array_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Array Properties & Utility Methods</b>", style_h2))
    story.append(Paragraph(
        "&bull; <b>Length Property:</b> The number of elements an array can hold is stored in its <code>length</code> property. Note that it is a property (no parentheses), unlike strings which use <code>length()</code> (a method).",
        style_bullet
    ))
    story.append(Paragraph("&bull; <b>Sorting:</b> Java provides the <code>java.util.Arrays</code> class containing utility methods. You can sort an array in ascending order using <code>Arrays.sort()</code>.", style_bullet))
    
    array_util_code = """import java.util.Arrays;

int[] marks = { 97, 95, 98 };
System.out.println(marks.length); // Outputs: 3

System.out.println(marks[0]); // Outputs: 97
Arrays.sort(marks); // Sorts array in-place to { 95, 97, 98 }
System.out.println(marks[0]); // Outputs: 95"""
    story.append(create_code_block(array_util_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Multidimensional Arrays</b>", style_h2))
    story.append(Paragraph(
        "Multidimensional arrays are arrays of arrays. The most common is a 2D array, which represents data in a grid (rows and columns).",
        style_body
    ))
    
    matrix_code = """// Declaring a 2D Array: 2 rows and 3 columns
int[][] finalMarks = new int[2][3];
finalMarks[0][0] = 97;
finalMarks[0][1] = 98;
finalMarks[0][2] = 95;

finalMarks[1][0] = 95;
finalMarks[1][1] = 92;
finalMarks[1][2] = 90;

// Inline 2D array initialization
int[][] matrix = { {1, 2, 3}, {4, 5, 6} };
System.out.println(matrix[1][2]); // Accesses row 1, column 2 -> Outputs: 6"""
    story.append(create_code_block(matrix_code, style_mono))
    
    story.append(PageBreak())

    # ==========================================
    # 6. TYPE CASTING & CONSTANTS
    # ==========================================
    story.append(Paragraph("6. Type Casting & Constants", style_h1))
    story.append(Paragraph(
        "<b>Type Casting</b> is the process of converting a value of one primitive data type into another. "
        "Java supports two types of casting: <b>Implicit (Widening) Casting</b> and <b>Explicit (Narrowing) Casting</b>.",
        style_body
    ))
    
    story.append(Paragraph("<b>1. Implicit Casting (Widening Conversion)</b>", style_body_bold))
    story.append(Paragraph(
        "Widening conversion happens automatically when passing a smaller data type to a larger data type size. "
        "There is no risk of data loss. The hierarchy is:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>byte</code> &rarr; <code>short</code> &rarr; <code>char</code> &rarr; <code>int</code> &rarr; <code>long</code> &rarr; <code>float</code> &rarr; <code>double</code>",
        style_body
    ))
    
    implicit_code = """int price = 100;
double finalPrice = price + 18.0; // int is implicitly cast to double
System.out.println(finalPrice);   // Outputs: 118.0"""
    story.append(create_code_block(implicit_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2. Explicit Casting (Narrowing Conversion)</b>", style_body_bold))
    story.append(Paragraph(
        "Narrowing conversion must be done manually by placing the target type in parentheses in front of the value. "
        "This is used when converting a larger type to a smaller type size, which can lead to data loss (e.g., truncating decimals).",
        style_body
    ))
    
    explicit_code = """double exactPrice = 100.99;
int roundedPrice = (int) exactPrice; // Manual cast, decimal part is truncated
System.out.println(roundedPrice);    // Outputs: 100 (0.99 is lost!)"""
    story.append(create_code_block(explicit_code, style_mono))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Constants in Java</b>", style_h2))
    story.append(Paragraph(
        "A <b>Constant</b> is a variable whose value cannot be changed once assigned. In Java, we define constants using the <code>final</code> keyword. "
        "By convention, constant variable names are written in UPPERCASE to distinguish them from regular variables.",
        style_body
    ))
    
    constants_code = """final float PI = 3.14159F;
// PI = 3.15F; // ERROR: cannot assign a value to final variable PI

final int MAX_USERS = 100;"""
    story.append(create_code_block(constants_code, style_mono))
    
    story.append(PageBreak())

    # ==========================================
    # 7. OPERATORS & MATH CLASS
    # ==========================================
    story.append(Paragraph("7. Operators & Math Class", style_h1))
    story.append(Paragraph(
        "Operators are symbols used to perform operations on variables and values. Java provides a wide range of operators.",
        style_body
    ))
    
    story.append(Paragraph("<b>1. Arithmetic Operators</b>", style_h2))
    story.append(Paragraph(
        "Used to perform basic mathematical operations: <code>+</code> (Addition), <code>-</code> (Subtraction), <code>*</code> (Multiplication), <code>/</code> (Division), <code>%</code> (Modulo - returns remainder).",
        style_body
    ))
    arith_code = """int a = 10, b = 3;
System.out.println(a / b); // Integer division: Outputs 3 (fractional part lost)
System.out.println(a % b); // Remainder: Outputs 1"""
    story.append(create_code_block(arith_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2. Unary Operators (Increment & Decrement)</b>", style_h2))
    story.append(Paragraph(
        "Increment (<code>++</code>) and Decrement (<code>--</code>) increase or decrease a value by 1. "
        "They behave differently depending on whether they are Prefix or Postfix:",
        style_body
    ))
    story.append(Paragraph("&bull; <b>Postfix (<code>i++</code>):</b> The current value is used in the expression first, and then incremented.", style_bullet))
    story.append(Paragraph("&bull; <b>Prefix (<code>++i</code>):</b> The value is incremented first, and then used in the expression.", style_bullet))
    
    unary_code = """int i = 1;
System.out.println(i++); // Outputs: 1 (i is printed, then becomes 2)
System.out.println(i);   // Outputs: 2

int j = 1;
System.out.println(++j); // Outputs: 2 (j becomes 2, then printed)"""
    story.append(create_code_block(unary_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>3. Logical & Comparison Operators</b>", style_h2))
    story.append(Paragraph(
        "&bull; <b>Comparison:</b> <code>==</code> (equal to), <code>!=</code> (not equal to), <code>&lt;</code>, <code>&gt;</code>, <code>&lt;=</code>, <code>&gt;=</code>.<br/>"
        "&bull; <b>Logical:</b> <code>&amp;&amp;</code> (AND - both true), <code>||</code> (OR - at least one true), <code>!</code> (NOT - reverses boolean).",
        style_body
    ))
    
    story.append(Paragraph("<b>The Math Class</b>", style_h2))
    story.append(Paragraph(
        "Java provides the <code>java.lang.Math</code> class to perform mathematical tasks. Key methods include:",
        style_body
    ))
    
    math_code = """// 1. Maximum / Minimum
System.out.println(Math.max(5, 10)); // Outputs: 10
System.out.println(Math.min(5, 10)); // Outputs: 5

// 2. Random value: Returns a double between 0.0 (inclusive) and 1.0 (exclusive)
System.out.println(Math.random()); 

// 3. Random integer between 0 and 99:
int randomInt = (int)(Math.random() * 100);"""
    story.append(create_code_block(math_code, style_mono))
    
    story.append(PageBreak())

    # ==========================================
    # 8. TAKING INPUT
    # ==========================================
    story.append(Paragraph("8. Taking Input", style_h1))
    story.append(Paragraph(
        "To take input from the user via the console, Java provides the <code>Scanner</code> class inside the <code>java.util</code> package. "
        "We must import this class, instantiate it with <code>System.in</code>, and then use its methods to read different data types.",
        style_body
    ))
    
    input_code = """import java.util.Scanner; // 1. Import Statement

public class InputExample {
    public static void main(String[] args) {
        // 2. Create Scanner Object
        Scanner sc = new Scanner(System.in);
        
        System.out.print("Enter your age: ");
        int age = sc.nextInt(); // Reads integer
        
        System.out.print("Enter your height (meters): ");
        float height = sc.nextFloat(); // Reads float
        
        System.out.print("Enter your name (single word): ");
        String firstName = sc.next(); // Reads a single token (stops at whitespace)
        
        sc.nextLine(); // Consume remaining newline character in buffer
        
        System.out.print("Enter your full bio: ");
        String bio = sc.nextLine(); // Reads complete line including spaces
        
        System.out.println("Hello " + firstName + ", Age: " + age);
        
        // 3. Good practice: Close the scanner when done to release resources
        sc.close();
    }
}"""
    story.append(create_code_block(input_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Scanner Methods Reference Table:</b>", style_h2))
    
    scanner_methods = [
        ["Method", "Return Type", "Description"],
        ["nextInt()", "int", "Scans the next token of the input as an int."],
        ["nextFloat()", "float", "Scans the next token of the input as a float."],
        ["nextDouble()", "double", "Scans the next token of the input as a double."],
        ["nextLong()", "long", "Scans the next token of the input as a long."],
        ["next()", "String", "Finds and returns the next complete token (word)."],
        ["nextLine()", "String", "Advances this scanner past the current line and returns it."]
    ]
    story.append(create_table(scanner_methods, col_widths=[100, 94, 310]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Warning:</b> When calling a numeric scanner method (like <code>nextInt()</code>) followed by <code>nextLine()</code>, "
        "the numeric method leaves a newline character (<code>\\n</code>) in the buffer. "
        "The subsequent <code>nextLine()</code> immediately consumes this newline and returns an empty string. "
        "To prevent this, always call an empty <code>sc.nextLine()</code> to clear the buffer before reading actual text.",
        ParagraphStyle('WarningStyle', parent=style_body, textColor=colors.HexColor('#9B2C2C'), backColor=colors.HexColor('#FFF5F5'), borderPadding=8, borderWidth=0.5, borderColor=colors.HexColor('#FEB2B2'))
    ))
    
    story.append(PageBreak())

    # ==========================================
    # 9. CONDITIONAL STATEMENTS
    # ==========================================
    story.append(Paragraph("9. Conditional Statements", style_h1))
    story.append(Paragraph(
        "Conditional statements are used to make decisions in code. They execute different blocks of code depending on whether a condition is true or false.",
        style_body
    ))
    
    story.append(Paragraph("<b>1. The If-Else Ladder</b>", style_h2))
    story.append(Paragraph(
        "Checks conditions sequentially. Once a condition is met, its corresponding block runs, and the rest of the ladder is skipped.",
        style_body
    ))
    
    ifelse_code = """int age = 18;

if (age >= 18) {
    System.out.println("You are an adult. You can vote.");
} else if (age > 12 && age < 18) {
    System.out.println("You are a teenager.");
} else {
    System.out.println("You are a child.");
}"""
    story.append(create_code_block(ifelse_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2. The Switch Statement</b>", style_h2))
    story.append(Paragraph(
        "Used when a variable is compared against multiple constant values (cases). "
        "It provides a cleaner structure than a long if-else ladder when dealing with single-variable equality checks.",
        style_body
    ))
    
    switch_code = """int day = 3;

switch (day) {
    case 1:
        System.out.println("Monday");
        break; // Exits switch block
    case 2:
        System.out.println("Tuesday");
        break;
    case 3:
        System.out.println("Wednesday"); // Executed
        break;
    default:
        System.out.println("Invalid day"); // Executed if no cases match
}"""
    story.append(create_code_block(switch_code, style_mono))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Important Rule about Switch:</b> Each case block should end with a <code>break</code> statement. "
        "If <code>break</code> is omitted, execution will 'fall through' to the subsequent cases and run their code too, "
        "regardless of whether the case conditions are met.",
        style_body
    ))
    
    story.append(PageBreak())

    # ==========================================
    # 10. LOOPS IN JAVA
    # ==========================================
    story.append(Paragraph("10. Loops in Java", style_h1))
    story.append(Paragraph(
        "Loops are used to execute a block of code repeatedly as long as a specified condition is met. "
        "Java has three primary types of loops: <code>for</code>, <code>while</code>, and <code>do-while</code>.",
        style_body
    ))
    
    story.append(Paragraph("<b>1. The For Loop</b>", style_h2))
    story.append(Paragraph(
        "Best used when you know in advance exactly how many times the loop should run.",
        style_body
    ))
    for_code = """// for (initialization; condition; update)
for (int i = 1; i <= 5; i++) {
    System.out.println("Count: " + i);
} // Prints numbers 1 to 5"""
    story.append(create_code_block(for_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2. The While Loop</b>", style_h2))
    story.append(Paragraph(
        "Best used when the number of iterations is not known beforehand, and depends on a dynamic condition.",
        style_body
    ))
    while_code = """int i = 1;
while (i <= 5) {
    System.out.println("Count: " + i);
    i++; // Don't forget to update the loop control variable!
}"""
    story.append(create_code_block(while_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>3. The Do-While Loop</b>", style_h2))
    story.append(Paragraph(
        "Similar to the while loop, but it evaluates its condition at the end. "
        "Consequently, a **do-while loop is guaranteed to execute at least once**, even if the condition is false on the first check.",
        style_body
    ))
    dowhile_code = """int i = 10;
do {
    System.out.println("This prints once even though i is not < 5");
    i++;
} while (i < 5);"""
    story.append(create_code_block(dowhile_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Loop Control Statements: Break & Continue</b>", style_h2))
    story.append(Paragraph("&bull; <b><code>break</code>:</b> Immediately terminates the entire loop and transfers execution to the statement following the loop.", style_bullet))
    story.append(Paragraph("&bull; <b><code>continue</code>:</b> Stops the current iteration of the loop, skips any remaining statements in the body, and immediately moves to the next iteration (evaluating the loop condition/update).", style_bullet))
    
    break_continue_code = """for (int i = 1; i <= 5; i++) {
    if (i == 3) {
        continue; // Skips printing 3
    }
    if (i == 5) {
        break; // Stops the loop entirely
    }
    System.out.println(i);
} // Output: 1, 2, 4"""
    story.append(create_code_block(break_continue_code, style_mono))
    
    story.append(PageBreak())

    # ==========================================
    # 11. EXCEPTION HANDLING
    # ==========================================
    story.append(Paragraph("11. Exception Handling", style_h1))
    story.append(Paragraph(
        "An <b>Exception</b> is an unwanted or unexpected event that occurs during runtime (program execution) "
        "and disrupts the normal flow of the program. "
        "Java provides <b>Exception Handling</b> using the <code>try-catch</code> mechanism to capture exceptions and handle them gracefully, preventing the application from crashing.",
        style_body
    ))
    
    story.append(Paragraph("<b>Anatomy of Try-Catch</b>", style_h2))
    story.append(Paragraph(
        "&bull; <b><code>try</code> block:</b> Contains code that might throw an exception.<br/>"
        "&bull; <b><code>catch</code> block:</b> Contains code to handle the exception if it occurs. You declare the exception type you want to catch.",
        style_body
    ))
    
    try_catch_code = """public class ExceptionExample {
    public static void main(String[] args) {
        int[] marks = { 97, 98, 95 };
        
        try {
            // Attempting to access index 5, which doesn't exist
            System.out.println(marks[5]); 
        } catch (ArrayIndexOutOfBoundsException e) {
            // Executed only if exception occurs
            System.out.println("Error: Index is invalid. " + e.getMessage());
        }
        
        // The program continues execution here instead of crashing!
        System.out.println("Program execution completed successfully.");
    }
}"""
    story.append(create_code_block(try_catch_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Common Exceptions in Java:</b>", style_h2))
    
    common_exceptions = [
        ["Exception Name", "Cause", "Example Scenario"],
        ["NullPointerException", "Attempting to call methods on a null reference", "String s = null; s.length();"],
        ["ArrayIndexOutOfBoundsException", "Accessing an invalid array index", "int[] a = new int[2]; a[5] = 1;"],
        ["ArithmeticException", "Invalid mathematical operation", "int division = 50 / 0;"],
        ["NumberFormatException", "Parsing a string to a number format improperly", "int x = Integer.parseInt(\"abc\");"]
    ]
    story.append(create_table(common_exceptions, col_widths=[180, 164, 160]))
    
    story.append(PageBreak())

    # ==========================================
    # 12. FUNCTIONS & METHODS
    # ==========================================
    story.append(Paragraph("12. Functions & Methods", style_h1))
    story.append(Paragraph(
        "A <b>Method</b> (commonly called a function) is a block of code that perform a specific task and only runs when it is called. "
        "Methods allow us to reuse code, modularize programs, and make code easier to read and maintain.",
        style_body
    ))
    
    story.append(Paragraph("<b>Method Declaration Syntax:</b>", style_h2))
    story.append(Paragraph(
        "<code>returnType methodName(parameterType parameterName) { ... }</code>",
        style_body
    ))
    
    method_code = """public class MethodsExample {
    
    // 1. Defining a static method that returns nothing (void)
    public static void printJava() {
        System.out.println("Hello Java!");
    }
    
    // 2. Defining a static method that takes arguments and returns a value (int)
    public static int sum(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        // Calling methods
        printJava(); // Outputs: Hello Java!
        
        int result = sum(5, 10);
        System.out.println("Sum is: " + result); // Outputs: Sum is: 15
    }
}"""
    story.append(create_code_block(method_code, style_mono))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Key Concepts in Methods:</b>", style_h2))
    story.append(Paragraph("&bull; <b>Parameters vs Arguments:</b> Parameters are the variables declared in the method definition (e.g., <code>int a, int b</code>). Arguments are the actual values passed during method invocation (e.g., <code>5, 10</code>).", style_bullet))
    story.append(Paragraph("&bull; <b>Return Value:</b> The <code>return</code> keyword is used to send a value back to the caller. The returned value's data type must match the declared return type of the method. If return type is <code>void</code>, the method doesn't return anything.", style_bullet))
    story.append(Paragraph("&bull; <b>Java Pass-by-Value:</b> Java passes arguments strictly <b>by value</b>. This means a copy of the argument value (or the copy of the memory address reference for objects) is passed. Modifying a primitive parameter inside a method does not change the original variable in the calling function.", style_bullet))
    
    story.append(PageBreak())

    # ==========================================
    # 13. MINI-PROJECT: GUESS THE NUMBER
    # ==========================================
    story.append(Paragraph("13. Mini-Project: Guess the Number Game", style_h1))
    story.append(Paragraph(
        "To practice variables, loops, conditional statements, taking inputs, and utilizing classes, "
        "here is the complete Java implementation of a mini-project: the <b>Guess the Number Game</b>.",
        style_body
    ))
    
    story.append(Paragraph("<b>Game Logic & Flow:</b>", style_h2))
    story.append(Paragraph("1. The program generates a random target number between 1 and 100.", style_bullet))
    story.append(Paragraph("2. The game enters a loop, repeatedly prompting the user to guess the number.", style_bullet))
    story.append(Paragraph("3. If the user's guess is higher than the target, the program prints <i>\"Your number is too large\"</i>.", style_bullet))
    story.append(Paragraph("4. If the user's guess is lower, the program prints <i>\"Your number is too small\"</i>.", style_bullet))
    story.append(Paragraph("5. If the user guesses correctly, the program prints a success message and exits the loop.", style_bullet))
    story.append(Paragraph("6. (Extra Feature): The loop also tracks the number of attempts and terminates if the user inputs a negative number (to exit early).", style_bullet))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>Complete Annotated Code:</b>", style_h2))
    
    project_code = """import java.util.Scanner;

public class MiniProject {
    public static void main(String[] args) {
        // 1. Create a Scanner object for user input
        Scanner sc = new Scanner(System.in);
        
        // 2. Generate a random target number between 1 and 100
        // Math.random() returns [0.0, 1.0) -> * 100 gives [0.0, 100.0)
        // Casting to int gives [0, 99] -> Adding 1 gives [1, 100]
        int targetNumber = (int)(Math.random() * 100) + 1;
        int userGuess = 0;
        int attemptsCount = 0;
        
        System.out.println("=== Welcome to the Guessing Game! ===");
        System.out.println("I have chosen a number between 1 and 100.");
        System.out.println("Can you guess it? (Enter a negative number to quit)");
        
        // 3. Play game in a loop
        do {
            System.out.print("Enter your guess: ");
            userGuess = sc.nextInt();
            attemptsCount++;
            
            // Check for exit condition
            if (userGuess < 0) {
                System.out.println("You chose to quit the game.");
                System.out.println("The correct number was: " + targetNumber);
                break;
            }
            
            // Compare guess with target
            if (userGuess == targetNumber) {
                System.out.println("CONGRATULATIONS!!! You guessed it right!");
                System.out.println("Total attempts: " + attemptsCount);
                break;
            } else if (userGuess > targetNumber) {
                System.out.println("Your number is too large. Try again!");
            } else {
                System.out.println("Your number is too small. Try again!");
            }
            
        } while (userGuess >= 0);
        
        System.out.println("=== Thank you for playing! ===");
        sc.close(); // Clean up scanner resources
    }
}"""
    story.append(create_code_block(project_code, style_mono))
    
    # Render the PDF
    doc.build(story, canvasmaker=NumberedCanvas)


if __name__ == "__main__":
    build_pdf()
    print("PDF generation completed successfully.")
