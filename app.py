import sys
import json
import re
import os
import math
from collections import defaultdict
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QMessageBox, 
                               QComboBox, QProgressBar, QFileDialog, QDockWidget,
                               QTextBrowser, QMenu, QDialog, QSplitter, QFormLayout, 
                               QLineEdit, QTextEdit, QAbstractItemView, QTreeWidget, 
                               QTreeWidgetItem, QStackedWidget, QFrame)
from PySide6.QtCore import Qt, QPointF, Signal, QTimer, QRectF
from PySide6.QtGui import QFont, QColor, QPen, QBrush, QPainter, QAction, QKeySequence, QTextDocument
from PySide6.QtTextToSpeech import QTextToSpeech

# Optional: AI Math Engine
try:
    import sympy
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

# --- Theorem Definitions ---
THEOREM_DEFINITIONS = {
    "Given": "Information provided in the problem statement.",
    "Definition of Midpoint": "A point that divides a segment into two congruent segments.",
    "Definition of Angle Bisector": "A ray that divides an angle into two congruent angles.",
    "Definition of Complementary Angles": "Two angles whose measures sum to 90 degrees.",
    "Definition of Supplementary Angles": "Two angles whose measures sum to 180 degrees.",
    "Definition of Congruent Segments": "Segments that have the same length.",
    "Definition of Congruent Angles": "Angles that have the same measure.",
    "Definition of Perpendicular Lines": "Lines that intersect to form a 90 degree right angle.",
    "Definition of Parallel Lines": "Lines in the same plane that never intersect.",
    "Definition of Isosceles Triangle": "A triangle with at least two congruent sides.",
    "Definition of Parallelogram": "A quadrilateral with two pairs of parallel sides.",
    "Distance Formula": "The distance between (x1,y1) and (x2,y2) is sqrt((x2-x1)^2 + (y2-y1)^2).",
    "Slope Formula": "The slope of a line through (x1,y1) and (x2,y2) is (y2-y1)/(x2-x1).",
    "Segment Addition Postulate": "If B is between A and C, then AB + BC = AC.",
    "Angle Addition Postulate": "If D is in the interior of ∠ABC, then m∠ABD + m∠DBC = m∠ABC.",
    "Linear Pair Postulate": "If two angles form a linear pair, then they are supplementary.",
    "Vertical Angles Theorem": "If two angles are vertical angles, then they are congruent.",
    "Corresponding Angles Postulate": "If two parallel lines are cut by a transversal, then corresponding angles are congruent.",
    "Alternate Interior Angles Theorem": "If two parallel lines are cut by a transversal, then alternate interior angles are congruent.",
    "Isosceles Triangle Theorem": "If two sides of a triangle are congruent, then the angles opposite them are congruent.",
    "Angle Sum Theorem": "The sum of the measures of the interior angles of a triangle is 180 degrees.",
    "Combine Like Terms": "Simplifying an expression by adding/subtracting terms with the same variable parts.",
    "Transitive Property of Equality": "If a = b and b = c, then a = c.",
    "Substitution Property": "If a = b, then a can be substituted for b in any equation.",
    "Addition Property of Equality": "If a = b, then a + c = b + c.",
    "Subtraction Property of Equality": "If a = b, then a - c = b - c.",
    "Division Property of Equality": "If a = b, then a / c = b / c.",
    "SSS Congruence Postulate": "If three sides of one triangle are congruent to three sides of another, the triangles are congruent.",
    "ASA Congruence Postulate": "If two angles and the included side of one triangle are congruent to two angles and the included side of another, the triangles are congruent.",
    "CPCTC": "Corresponding Parts of Congruent Triangles are Congruent."
}

STANDARD_REASONS = list(THEOREM_DEFINITIONS.keys())

DEFAULT_PROBLEMS = [
    {
        "category": "1. Lines & Angles",
        "title": "Vertical Angles Theorem",
        "given": "Lines AB and CD intersect at point E.",
        "to_prove": "∠AEC ≅ ∠DEB",
        "given_steps": [("Lines AB and CD intersect at E", "Given")],
        "graphics_data": {
            "points": {"A": (0, -150), "B": (0, 150), "C": (-150, 0), "D": (150, 0), "E": (0, 0)},
            "lines": [("A", "B"), ("C", "D")]
        },
        "correct_steps": [
            ("∠AEC and ∠AED are supplementary", "Linear Pair Postulate"),
            ("∠DEB and ∠AED are supplementary", "Linear Pair Postulate"),
            ("m∠AEC + m∠AED = 180", "Definition of Supplementary Angles"),
            ("m∠DEB + m∠AED = 180", "Definition of Supplementary Angles"),
            ("m∠AEC + m∠AED = m∠DEB + m∠AED", "Substitution Property"),
            ("m∠AEC = m∠DEB", "Subtraction Property of Equality"),
            ("∠AEC ≅ ∠DEB", "Definition of Congruent Angles")
        ]
    },
    {
        "category": "1. Lines & Angles",
        "title": "Right Angle Formation",
        "given": "Line AB ⊥ Line CD at E.",
        "to_prove": "∠AEC = 90°",
        "given_steps": [("AB ⊥ CD", "Given")],
        "graphics_data": {
            "points": {"A": (0, -150), "B": (0, 150), "C": (-150, 0), "D": (150, 0), "E": (0, 0)},
            "lines": [("A", "B"), ("C", "D")],
            "right_angles": [("A", "E", "C"), ("C", "E", "B"), ("B", "E", "D"), ("D", "E", "A")]
        },
        "correct_steps": [
            ("AB ⊥ CD", "Given"),
            ("∠AEC is a right angle", "Definition of Perpendicular Lines"),
            ("m∠AEC = 90", "Definition of Right Angles")
        ]
    },
    {
        "category": "2. Segments & Midpoints",
        "title": "Segment Addition Postulate",
        "given": "Point B is between points A and C.",
        "to_prove": "AB + BC = AC",
        "given_steps": [("B is between A and C", "Given")],
        "graphics_data": {"points": {"A": (-150, 0), "B": (0, 0), "C": (150, 0)}, "lines": [("A", "C")]},
        "correct_steps": [("AB + BC = AC", "Segment Addition Postulate")]
    },
    {
        "category": "3. Triangles & Congruence",
        "title": "Isosceles Triangle Theorem",
        "given": "In △ABC, AB ≅ AC.",
        "to_prove": "∠B ≅ ∠C",
        "given_steps": [("AB ≅ AC", "Given")],
        "graphics_data": {
            "points": {"A": (0, -150), "B": (-120, 100), "C": (120, 100)},
            "lines": [("A", "B"), ("B", "C"), ("A", "C")],
            "tick_marks": [("A", "B"), ("A", "C")]
        },
        "correct_steps": [
            ("AB ≅ AC", "Given"),
            ("∠B ≅ ∠C", "Isosceles Triangle Theorem")
        ]
    },
    {
        "category": "4. Quadrilaterals & Polygons",
        "title": "Parallelogram Diagonals",
        "given": "ABCD is a parallelogram. AB ≅ CD. Diagonals intersect at E.",
        "to_prove": "AE ≅ CE",
        "given_steps": [
            ("ABCD is a parallelogram", "Given"), 
            ("AB ≅ CD", "Given"),
            ("AB ∥ CD", "Definition of Parallelogram")
        ],
        "graphics_data": {
            "points": {"A": (-120, -60), "B": (120, -60), "C": (60, 80), "D": (-60, 80), "E": (0, 10)},
            "lines": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("A", "C"), ("B", "D")]
        },
        "correct_steps": [
            ("∠BAE ≅ ∠DCE", "Alternate Interior Angles Theorem"),
            ("∠ABE ≅ ∠CDE", "Alternate Interior Angles Theorem"),
            ("△ABE ≅ △CDE", "ASA Congruence Postulate"),
            ("AE ≅ CE", "CPCTC")
        ]
    },
    {
        "category": "5. Algebra in Geometry",
        "title": "Supplementary Angles Algebra",
        "given": "∠1 and ∠2 are supplementary. m∠1 = 2x + 10, m∠2 = 3x + 20",
        "to_prove": "x = 30",
        "given_steps": [
            ("∠1 and ∠2 are supplementary", "Given"),
            ("m∠1 = 2x + 10", "Given"),
            ("m∠2 = 3x + 20", "Given")
        ],
        "graphics_data": {
            "points": {"A": (-150, 0), "B": (150, 0), "C": (0, 0), "D": (0, 150)},
            "lines": [("A", "B"), ("C", "D")],
            "text_labels": [("C", "D", "m∠1 = 2x+10"), ("C", "B", "m∠2 = 3x+20")],
            "angle_numbers": [("A", "C", "D", 1), ("D", "C", "B", 2)]
        },
        "correct_steps": [
            ("m∠1 + m∠2 = 180", "Definition of Supplementary Angles"),
            ("2x + 10 + 3x + 20 = 180", "Substitution Property"),
            ("5x + 30 = 180", "Combine Like Terms"),
            ("5x = 150", "Subtraction Property of Equality"),
            ("x = 30", "Division Property of Equality")
        ]
    },
    {
        "category": "6. Coordinate Geometry",
        "title": "Distance Formula Proof",
        "given": "A = (1, 2), B = (4, 6). Let AB be the distance between them.",
        "to_prove": "AB = 5",
        "given_steps": [
            ("A = (1, 2)", "Given"),
            ("B = (4, 6)", "Given")
        ],
        "graphics_data": {
            "show_grid": True,
            "points": {"A": (100, -200), "B": (400, -600)}, 
            "lines": [("A", "B")],
            "text_labels": [("A", "B", "sqrt( (4-1)^2 + (6-2)^2 ) = 5")]
        },
        "correct_steps": [
            ("AB = sqrt( (x2-x1)^2 + (y2-y1)^2 )", "Distance Formula"),
            ("AB = sqrt( (4-1)^2 + (6-2)^2 )", "Substitution Property"),
            ("AB = sqrt( 3^2 + 4^2 )", "Subtraction Property of Equality"),
            ("AB = sqrt( 9 + 16 )", "Definition of Exponents"),
            ("AB = sqrt( 25 )", "Addition Property of Equality"),
            ("AB = 5", "Definition of Square Root")
        ]
    }
]

SAVE_FILE = "geometry_progress_v14.json"

# --- AI Math Verification Logic ---
def prep_expr_for_sympy(s):
    s = s.replace("m∠", "mAngle_").replace("∠", "Angle_").replace("△", "Triangle_")
    s = s.replace("≅", "==").replace("°", "")
    s = s.replace("^", "**") 
    return s

def math_equiv(u_expr, c_expr):
    if not HAS_SYMPY:
        return u_expr == c_expr
    try:
        u = prep_expr_for_sympy(u_expr)
        c = prep_expr_for_sympy(c_expr)
        if "=" in u and "=" in c:
            u_lhs, u_rhs = u.split("=")
            c_lhs, c_rhs = c.split("=")
            expr_u = sympy.sympify(u_lhs) - sympy.sympify(u_rhs)
            expr_c = sympy.sympify(c_lhs) - sympy.sympify(c_rhs)
            return sympy.simplify(expr_u - expr_c) == 0
    except Exception:
        pass
    return u_expr == c_expr


class GeometryDiagram(QWidget):
    point_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.data = None
        self.highlighted_points = set()
        self.highlighted_segments = set()
        self.highlighted_angles = set()
        self.setMinimumSize(400, 400)
        self.setMouseTracking(True)
        self.dragging_point = None
        self.mouse_down_pos = None

    def load_data(self, data):
        self.data = data
        self.clear_highlights()

    def clear_highlights(self):
        self.highlighted_points = set()
        self.highlighted_segments = set()
        self.highlighted_angles = set()
        self.update()

    def set_highlights_from_text(self, text):
        self.highlighted_points = set()
        self.highlighted_segments = set()
        self.highlighted_angles = set()
        if not self.data or not text:
            self.update()
            return

        angles = re.findall(r'(?:∠|<)([A-Z0-9]{1,3})', text)
        for ang in angles:
            if len(ang) == 3:
                self.highlighted_angles.add(ang)
                for p in ang:
                    if p in self.data["points"]: self.highlighted_points.add(p)

        segments = re.findall(r'(?<!\w)([A-Z]{2})(?!\w)', text)
        for seg in segments:
            p1, p2 = seg[0], seg[1]
            if p1 in self.data["points"] and p2 in self.data["points"]:
                self.highlighted_segments.add((p1, p2))
                self.highlighted_points.add(p1)
                self.highlighted_points.add(p2)

        singles = re.findall(r'(?<!\w)([A-Z])(?!\w)', text)
        for p in singles:
            if p in self.data["points"]: self.highlighted_points.add(p)

        self.update()

    def calculate_angle(self, p_end1, p_vertex, p_end2):
        v1 = (p_end1[0] - p_vertex[0], p_end1[1] - p_vertex[1])
        v2 = (p_end2[0] - p_vertex[0], p_end2[1] - p_vertex[1])
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        m1 = math.hypot(*v1)
        m2 = math.hypot(*v2)
        if m1 == 0 or m2 == 0: return 0
        cos_theta = max(-1, min(1, dot / (m1 * m2)))
        return math.degrees(math.acos(cos_theta))

    def draw_tick_mark(self, painter, p1, p2):
        mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length == 0: return
        nx, ny = -dy / length, dx / length
        tick_len = 8
        x1, y1 = mid_x + nx * tick_len, mid_y + ny * tick_len
        x2, y2 = mid_x - nx * tick_len, mid_y - ny * tick_len
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def draw_right_angle(self, painter, p_end1, p_vertex, p_end2):
        v1 = (p_end1[0] - p_vertex[0], p_end1[1] - p_vertex[1])
        v2 = (p_end2[0] - p_vertex[0], p_end2[1] - p_vertex[1])
        m1 = math.hypot(*v1)
        m2 = math.hypot(*v2)
        if m1 == 0 or m2 == 0: return
        u1, u2 = (v1[0]/m1, v1[1]/m1), (v2[0]/m2, v2[1]/m2)
        size = 15
        p1 = QPointF(p_vertex[0] + u1[0]*size, p_vertex[1] + u1[1]*size)
        p2 = QPointF(p_vertex[0] + u2[0]*size, p_vertex[1] + u2[1]*size)
        p3 = QPointF(p_vertex[0] + (u1[0]+u2[0])*size, p_vertex[1] + (u1[1]+u2[1])*size)
        painter.drawLine(p1, p3)
        painter.drawLine(p2, p3)

    def paintEvent(self, event):
        if not self.data: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(QPointF(self.width() / 2, self.height() / 2))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)

        if self.data.get("show_grid", False):
            painter.setPen(QPen(QColor("#ecf0f1"), 1))
            w, h = int(self.width()/2), int(self.height()/2)
            for x in range(-w, w, 50):
                painter.drawLine(QPointF(x, -h), QPointF(x, h))
            for y in range(-h, h, 50):
                painter.drawLine(QPointF(-w, y), QPointF(w, y))
            painter.setPen(QPen(QColor("#7f8c8d"), 2))
            painter.drawLine(QPointF(-w, 0), QPointF(w, 0))
            painter.drawLine(QPointF(0, -h), QPointF(0, h))

        for p1_name, p2_name in self.data["lines"]:
            p1 = self.data["points"][p1_name]
            p2 = self.data["points"][p2_name]
            if (p1_name, p2_name) in self.highlighted_segments or (p2_name, p1_name) in self.highlighted_segments:
                painter.setPen(QPen(QColor("#e74c3c"), 3))
            else:
                painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawLine(QPointF(*p1), QPointF(*p2))

        painter.setPen(QPen(QColor("#2ecc71"), 2))
        for seg in self.data.get("tick_marks", []):
            p1, p2 = seg[0], seg[1]
            if p1 in self.data["points"] and p2 in self.data["points"]:
                self.draw_tick_mark(painter, self.data["points"][p1], self.data["points"][p2])

        painter.setPen(QPen(QColor("#f1c40f"), 2))
        for ang in self.data.get("right_angles", []):
            p_end1, p_vertex, p_end2 = ang[0], ang[1], ang[2]
            if all(p in self.data["points"] for p in ang):
                self.draw_right_angle(painter, self.data["points"][p_end1], self.data["points"][p_vertex], self.data["points"][p_end2])

        painter.setPen(QColor("#9b59b6"))
        for lbl in self.data.get("text_labels", []):
            p1, p2, text = lbl[0], lbl[1], lbl[2]
            if p1 in self.data["points"] and p2 in self.data["points"]:
                mid_x = (self.data["points"][p1][0] + self.data["points"][p2][0]) / 2
                mid_y = (self.data["points"][p1][1] + self.data["points"][p2][1]) / 2
                painter.drawText(QPointF(mid_x - 20, mid_y - 5), text)

        painter.setPen(QPen(QColor("#3498db"), 2))
        for ang in self.data.get("angle_numbers", []):
            p_end1, p_vertex, p_end2, num = ang[0], ang[1], ang[2], ang[3]
            if all(p in self.data["points"] for p in [p_end1, p_vertex, p_end2]):
                v = self.data["points"][p_vertex]
                e1 = self.data["points"][p_end1]
                e2 = self.data["points"][p_end2]
                ang1 = math.atan2(e1[1] - v[1], e1[0] - v[0])
                ang2 = math.atan2(e2[1] - v[1], e2[0] - v[0])
                deg1, deg2 = math.degrees(ang1), math.degrees(ang2)
                if abs(deg1 - deg2) > 180:
                    if deg1 < deg2: deg1 += 360
                    else: deg2 += 360
                start, span = min(deg1, deg2), abs(deg1 - deg2)
                painter.drawArc(QRectF(v[0]-30, v[1]-30, 60, 60), int(start * 16), int(span * 16))
                
                mid_deg = math.radians(start + span/2)
                txt_x = v[0] + math.cos(mid_deg) * 45
                txt_y = v[1] - math.sin(mid_deg) * 45
                painter.drawText(QPointF(txt_x-5, txt_y+5), str(num))

        painter.setPen(QPen(QColor("#e74c3c"), 3))
        for ang_name in self.highlighted_angles:
            if len(ang_name) == 3:
                p_end1, p_vertex, p_end2 = ang_name[0], ang_name[1], ang_name[2]
                if all(p in self.data["points"] for p in ang_name):
                    v = self.data["points"][p_vertex]
                    e1 = self.data["points"][p_end1]
                    e2 = self.data["points"][p_end2]
                    ang1 = math.atan2(e1[1] - v[1], e1[0] - v[0])
                    ang2 = math.atan2(e2[1] - v[1], e2[0] - v[0])
                    deg1, deg2 = math.degrees(ang1), math.degrees(ang2)
                    if abs(deg1 - deg2) > 180:
                        if deg1 < deg2: deg1 += 360
                        else: deg2 += 360
                    start, span = min(deg1, deg2), abs(deg1 - deg2)
                    painter.drawArc(QRectF(v[0]-30, v[1]-30, 60, 60), int(start * 16), int(span * 16))

        for name, (x, y) in self.data["points"].items():
            if name in self.highlighted_points:
                painter.setBrush(QBrush(QColor("#e74c3c")))
                painter.setPen(QPen(QColor("#e74c3c")))
                painter.drawEllipse(QPointF(x, y), 7, 7)
            else:
                painter.setBrush(QBrush(Qt.GlobalColor.black))
                painter.setPen(QPen(Qt.GlobalColor.black))
                painter.drawEllipse(QPointF(x, y), 5, 5)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(QPointF(x + 10, y - 10), name)

    def mousePressEvent(self, event):
        if not self.data: return
        click_pos = event.position() - QPointF(self.width() / 2, self.height() / 2)
        for name, (x, y) in self.data["points"].items():
            if (click_pos - QPointF(x, y)).manhattanLength() < 15:
                self.dragging_point = name
                self.mouse_down_pos = event.position()
                break

    def mouseMoveEvent(self, event):
        if self.dragging_point and self.data:
            new_pos = event.position() - QPointF(self.width() / 2, self.height() / 2)
            new_pos.setX(max(-self.width()/2 + 20, min(self.width()/2 - 20, new_pos.x())))
            new_pos.setY(max(-self.height()/2 + 20, min(self.height()/2 - 20, new_pos.y())))
            self.data["points"][self.dragging_point] = (new_pos.x(), new_pos.y())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging_point and self.mouse_down_pos:
            if (event.position() - self.mouse_down_pos).manhattanLength() < 5:
                self.point_clicked.emit(self.dragging_point)
        self.dragging_point = None
        self.mouse_down_pos = None


class ProofTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDropIndicatorShown(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current = self.currentRow()
            current_col = self.currentColumn()
            if current_col == 0:
                self.setCurrentCell(current, 1)
                if self.cellWidget(current, 1):
                    self.cellWidget(current, 1).setFocus()
                    self.cellWidget(current, 1).lineEdit().selectAll()
            elif current_col == 1:
                self.main_window.add_step()
                self.setCurrentCell(self.rowCount() - 1, 0)
                self.editItem(self.item(self.rowCount() - 1, 0))
        else:
            super().keyPressEvent(event)

    def dropEvent(self, event):
        target_row = self.indexAt(event.pos()).row()
        if target_row == -1: target_row = self.rowCount() - 1
        source_row = self.currentRow()
        if source_row == target_row or source_row == -1: return
        self.main_window.snapshot_table()
        
        src_stmt = self.item(source_row, 0).text() if self.item(source_row, 0) else ""
        src_rsn_combo = self.cellWidget(source_row, 1)
        src_rsn = src_rsn_combo.currentText() if src_rsn_combo else ""
        
        tgt_stmt = self.item(target_row, 0).text() if self.item(target_row, 0) else ""
        tgt_rsn_combo = self.cellWidget(target_row, 1)
        tgt_rsn = tgt_rsn_combo.currentText() if tgt_rsn_combo else ""

        self.item(source_row, 0).setText(tgt_stmt)
        src_rsn_combo.setEditText(tgt_rsn)
        self.item(target_row, 0).setText(src_stmt)
        tgt_rsn_combo.setEditText(src_rsn)
        
        self.main_window.update_row_status(source_row)
        self.main_window.update_row_status(target_row)
        event.accept()


class CustomProblemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Custom Problem")
        self.resize(500, 600)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.cat_input = QLineEdit("Custom Category")
        self.title_input = QLineEdit("Custom Problem")
        self.given_input = QLineEdit("Point B is between A and C.")
        self.prove_input = QLineEdit("AB + BC = AC")
        self.points_input = QTextEdit("A:(-150, 0)\nB:(0, 0)\nC:(150, 0)")
        self.lines_input = QTextEdit("A-C")
        self.steps_input = QTextEdit("B is between A and C|Given\nAB + BC = AC|Segment Addition Postulate")
        
        form.addRow("Category:", self.cat_input)
        form.addRow("Title:", self.title_input)
        form.addRow("Given:", self.given_input)
        form.addRow("To Prove:", self.prove_input)
        form.addRow("Points (Name:X,Y):", self.points_input)
        form.addRow("Lines (P1-P2):", self.lines_input)
        form.addRow("Correct Steps (Stmt|Reason):", self.steps_input)
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        btn_create = QPushButton("Create")
        btn_create.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_create)
        layout.addLayout(btn_layout)

    def get_problem_data(self):
        points = {}
        for line in self.points_input.toPlainText().split('\n'):
            line = line.strip()
            if ":" in line:
                name, coords = line.split(":")
                x, y = coords.split(",")
                points[name.strip()] = (int(x.strip()), int(y.strip()))
                
        lines = []
        for line in self.lines_input.toPlainText().split('\n'):
            line = line.strip()
            if "-" in line:
                p1, p2 = line.split("-")
                lines.append((p1.strip(), p2.strip()))
                
        steps = []
        for line in self.steps_input.toPlainText().split('\n'):
            line = line.strip()
            if "|" in line:
                stmt, rsn = line.split("|")
                steps.append((stmt.strip(), rsn.strip()))
                
        given_steps = [steps[0]] if steps else [("Given", "Given")]
                
        return {
            "category": self.cat_input.text(),
            "title": self.title_input.text(),
            "given": self.given_input.text(),
            "to_prove": self.prove_input.text(),
            "given_steps": given_steps,
            "graphics_data": {"points": points, "lines": lines},
            "correct_steps": steps
        }


class StatsDialog(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Learning Analytics & Achievements")
        self.resize(450, 400)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("<h2>🏆 Achievements</h2>"))
        achievements = stats.get("achievements", {})
        all_achievements = ["First Steps", "Speed Demon", "Flawless", "Master"]
        for ach in all_achievements:
            unlocked = achievements.get(ach, False)
            color = "#27ae60" if unlocked else "#bdc3c7"
            symbol = "✅" if unlocked else "🔒"
            lbl = QLabel(f"{symbol} <b>{ach}</b>")
            lbl.setStyleSheet(f"font-size: 14px; padding: 5px; color: {color};")
            layout.addWidget(lbl)
            
        layout.addWidget(QLabel("<h2>📊 Mistake Breakdown</h2>"))
        if not stats or not stats.get("mistakes"):
            layout.addWidget(QLabel("No mistakes recorded yet. Perfect work!"))
        else:
            mistakes = stats["mistakes"]
            for reason, count in sorted(mistakes.items(), key=lambda item: item[1], reverse=True):
                lbl = QLabel(f"• {reason}: <b>{count} mistakes</b>")
                lbl.setStyleSheet("font-size: 14px; padding: 2px;")
                layout.addWidget(lbl)
                
        layout.addStretch()
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


class DashboardWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Geometric Proofs Tutor")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Intelligent Tutoring System")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: gray;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(40)
        
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        
        self.progress_label = QLabel("0% Complete")
        self.progress_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(self.progress_label)
        
        self.time_label = QLabel("0m Spent")
        self.time_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(self.time_label)
        
        self.ach_label = QLabel("0/4 Achievements")
        self.ach_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.ach_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(self.ach_label)
        
        layout.addWidget(stats_frame)
        layout.addSpacing(40)
        
        self.continue_btn = QPushButton("➡️ Continue Learning")
        self.continue_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.continue_btn.setMinimumHeight(50)
        self.continue_btn.clicked.connect(lambda: main_window.stack.setCurrentIndex(1))
        layout.addWidget(self.continue_btn)
        
        layout.addStretch()


class GeometryProofApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geometric Proofs Tutor - V14")
        self.resize(1400, 850)
        self.current_problem_index = 0
        self.hints_used = 0
        self.mistakes_this_proof = 0
        self.completed_proofs = set()
        self.bookmarked_proofs = set()
        self.is_dark_mode = False
        self.saved_tables = {}
        self.stats = {"mistakes": {}, "achievements": {}}
        self.best_times = {}
        self.scratchpad_text = ""
        self.problems = DEFAULT_PROBLEMS.copy()
        self.learning_mode = "Normal" # Normal, Fill Reasons, Fill Statements
        
        self.undo_stack = []
        self.redo_stack = []
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_seconds = 0
        self.timer_running = False
        
        self.solution_timer = QTimer(self)
        self.solution_step = 0
        
        self.tts = QTextToSpeech(self)
        
        self.init_ui()
        self.init_shortcuts()
        self.load_state()
        self.load_problem()
        self.start_timer()

    def apply_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet("""
                QMainWindow, QDockWidget, QDialog { background-color: #1e1e1e; }
                QLabel { color: #e0e0e0; }
                QTreeWidget { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #555; }
                QTreeWidget::item:selected { background-color: #3498db; }
                QPushButton { background-color: #3a3d41; color: #ffffff; border: 1px solid #555; padding: 6px 12px; border-radius: 4px; }
                QPushButton:hover { background-color: #4a4d51; }
                QPushButton#danger { background-color: #c0392b; }
                QPushButton#success { background-color: #27ae60; }
                QPushButton#warn { background-color: #d68910; }
                QTableWidget { background-color: #2d2d2d; alternate-background-color: #333; gridline-color: #555; color: #fff; border: 1px solid #555; }
                QHeaderView::section { background-color: #3a3d41; color: white; padding: 6px; border: 1px solid #555; }
                QComboBox { background-color: #3a3d41; color: white; border: 1px solid #555; }
                QProgressBar { text-align: center; border: 1px solid #555; border-radius: 4px; background-color: #2d2d2d; color: white; }
                QProgressBar::chunk { background-color: #27ae60; }
                QTextBrowser, QTextEdit, QLineEdit { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #555; }
                QStatusBar { background-color: #2d2d2d; color: #27ae60; }
                QFrame { background-color: #2d2d2d; border-radius: 8px; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QDockWidget, QDialog { background-color: #f4f6f7; }
                QLabel { color: #2c3e50; }
                QTreeWidget { background-color: #ffffff; color: #2c3e50; border: 1px solid #bdc3c7; }
                QTreeWidget::item:selected { background-color: #3498db; color: white; }
                QPushButton { background-color: #3498db; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-weight: bold; }
                QPushButton:hover { background-color: #2980b9; }
                QPushButton#danger { background-color: #e74c3c; }
                QPushButton#success { background-color: #2ecc71; }
                QPushButton#warn { background-color: #f39c12; }
                QTableWidget { background-color: #ffffff; alternate-background-color: #ecf0f1; gridline-color: #bdc3c7; border: 1px solid #bdc3c7; }
                QHeaderView::section { background-color: #34495e; color: white; padding: 6px; }
                QProgressBar { text-align: center; border: 1px solid #bdc3c7; border-radius: 4px; background-color: #ecf0f1; }
                QProgressBar::chunk { background-color: #2ecc71; }
                QTextBrowser, QTextEdit, QLineEdit { background-color: #ffffff; color: #2c3e50; border: 1px solid #bdc3c7; }
                QStatusBar { background-color: #ecf0f1; color: #2c3e50; }
                QFrame { background-color: #ffffff; border-radius: 8px; }
            """)

    def init_ui(self):
        self.apply_theme()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.dashboard = DashboardWidget(self)
        self.stack.addWidget(self.dashboard)

        app_widget = QWidget()
        app_layout = QHBoxLayout(app_widget)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        app_layout.addWidget(self.splitter)

        # --- Left Panel ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        top_bar = QHBoxLayout()
        self.home_btn = QPushButton("🏠")
        self.home_btn.setFixedWidth(40)
        self.home_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        top_bar.addWidget(self.home_btn)
        
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        
        self.timer_label = QLabel("⏱️ 00:00")
        self.timer_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.timer_label.setStyleSheet("color: #e74c3c;")
        top_bar.addWidget(self.timer_label)
        
        self.focus_btn = QPushButton("🎯 Focus")
        self.focus_btn.setFixedWidth(60)
        self.focus_btn.clicked.connect(self.toggle_focus_mode)
        top_bar.addWidget(self.focus_btn)
        
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedWidth(40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.theme_btn)
        left_layout.addLayout(top_bar)

        self.given_label = QLabel()
        self.given_label.setWordWrap(True)
        left_layout.addWidget(self.given_label)

        self.prove_label = QLabel()
        self.prove_label.setWordWrap(True)
        left_layout.addWidget(self.prove_label)

        self.diagram_widget = GeometryDiagram()
        self.diagram_widget.point_clicked.connect(self.insert_point_from_diagram)
        self.diagram_widget.setStyleSheet("border: 1px solid #bdc3c7; border-radius: 4px;")
        left_layout.addWidget(self.diagram_widget, 1)
        
        self.diagram_hint = QLabel("💡 Drag points to manipulate. Click to insert letter.")
        self.diagram_hint.setStyleSheet("color: gray; font-size: 10px;")
        left_layout.addWidget(self.diagram_hint)
        
        self.splitter.addWidget(left_panel)

        # --- Middle Panel ---
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)

        header_layout = QHBoxLayout()
        proof_title = QLabel("Construct Your Proof:")
        proof_title.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(proof_title)
        header_layout.addStretch()
        
        # Scaffold Mode Selector
        header_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Normal", "Fill Reasons", "Fill Statements"])
        self.mode_combo.currentTextChanged.connect(self.change_learning_mode)
        header_layout.addWidget(self.mode_combo)
        middle_layout.addLayout(header_layout)

        symbol_layout = QHBoxLayout()
        symbols = ["∠", "≅", "△", "∥", "⊥", "∴", "∵", "≤", "≥", "m∠", "sqrt(", "x^2"]
        for sym in symbols:
            btn = QPushButton(sym)
            btn.setFixedSize(45, 30)
            btn.setStyleSheet("font-size: 14px;")
            btn.clicked.connect(lambda checked, s=sym: self.insert_symbol(s))
            symbol_layout.addWidget(btn)
        symbol_layout.addStretch()
        middle_layout.addLayout(symbol_layout)

        self.proof_table = ProofTable(self)
        self.proof_table.setColumnCount(3)
        self.proof_table.setHorizontalHeaderLabels(["Statement", "Reason", "Status"])
        self.proof_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.proof_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.proof_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.proof_table.setColumnWidth(2, 60)
        self.proof_table.setAlternatingRowColors(True)
        self.proof_table.currentItemChanged.connect(self.on_row_changed)
        self.proof_table.itemChanged.connect(self.auto_format_text)
        
        self.proof_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.proof_table.customContextMenuRequested.connect(self.show_table_context_menu)
        middle_layout.addWidget(self.proof_table)

        step_mgmt_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add")
        self.add_btn.clicked.connect(self.add_step)
        step_mgmt_layout.addWidget(self.add_btn)

        self.up_btn = QPushButton("⬆️")
        self.up_btn.setFixedWidth(50)
        self.up_btn.clicked.connect(lambda: self.move_step(self.proof_table.currentRow(), self.proof_table.currentRow()-1))
        step_mgmt_layout.addWidget(self.up_btn)

        self.down_btn = QPushButton("⬇️")
        self.down_btn.setFixedWidth(50)
        self.down_btn.clicked.connect(lambda: self.move_step(self.proof_table.currentRow(), self.proof_table.currentRow()+1))
        step_mgmt_layout.addWidget(self.down_btn)

        self.delete_btn = QPushButton("❌ Delete")
        self.delete_btn.setObjectName("danger")
        self.delete_btn.clicked.connect(self.delete_step)
        step_mgmt_layout.addWidget(self.delete_btn)
        
        self.undo_btn = QPushButton("↩️ Undo")
        self.undo_btn.clicked.connect(self.undo)
        step_mgmt_layout.addWidget(self.undo_btn)
        
        self.tts_btn = QPushButton("🔊 Read")
        self.tts_btn.clicked.connect(self.read_proof_aloud)
        step_mgmt_layout.addWidget(self.tts_btn)
        middle_layout.addLayout(step_mgmt_layout)

        action_layout = QHBoxLayout()
        self.hint_btn = QPushButton("💡 Hint (0)")
        self.hint_btn.setObjectName("warn")
        self.hint_btn.clicked.connect(self.show_hint)
        action_layout.addWidget(self.hint_btn)

        self.solve_btn = QPushButton("👁️ Show Solution")
        self.solve_btn.setObjectName("danger")
        self.solve_btn.clicked.connect(self.animate_solution)
        action_layout.addWidget(self.solve_btn)

        self.check_btn = QPushButton("✅ Check All")
        self.check_btn.setObjectName("success")
        self.check_btn.clicked.connect(self.check_proof)
        action_layout.addWidget(self.check_btn)
        middle_layout.addLayout(action_layout)

        export_layout = QHBoxLayout()
        self.export_pdf_btn = QPushButton("📄 Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        export_layout.addWidget(self.export_pdf_btn)
        
        self.export_png_btn = QPushButton("🖼️ Export Diagram")
        self.export_png_btn.clicked.connect(self.export_png)
        export_layout.addWidget(self.export_png_btn)
        middle_layout.addLayout(export_layout)

        self.splitter.addWidget(middle_panel)

        # --- Right Panel ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("<b>Problem Curriculum</b>"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search problems...")
        self.search_input.textChanged.connect(self.update_problem_tree)
        right_layout.addWidget(self.search_input)
        
        self.problem_tree = QTreeWidget()
        self.problem_tree.setHeaderHidden(True)
        self.problem_tree.itemClicked.connect(self.change_problem_from_tree)
        right_layout.addWidget(self.problem_tree)
        
        io_layout = QHBoxLayout()
        self.add_problem_btn = QPushButton("➕ Create")
        self.add_problem_btn.clicked.connect(self.open_custom_problem_dialog)
        io_layout.addWidget(self.add_problem_btn)
        
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self.import_curriculum)
        io_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self.export_curriculum)
        io_layout.addWidget(self.export_btn)
        right_layout.addLayout(io_layout)
        
        self.stats_btn = QPushButton("🏆 View Stats")
        self.stats_btn.clicked.connect(self.show_stats)
        right_layout.addWidget(self.stats_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.problems))
        right_layout.addWidget(self.progress_bar)

        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([450, 600, 250])

        self.ref_dock = QDockWidget("Theorem Reference", self)
        ref_content = QWidget()
        ref_layout = QVBoxLayout(ref_content)
        self.ref_text = QTextBrowser()
        self.ref_text.setOpenExternalLinks(True)
        ref_layout.addWidget(self.ref_text)
        self.ref_dock.setWidget(ref_content)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.ref_dock)
        self.ref_dock.hide()
        
        self.scratch_dock = QDockWidget("📝 Scratchpad", self)
        scratch_content = QWidget()
        scratch_layout = QVBoxLayout(scratch_content)
        self.scratch_text = QTextEdit()
        self.scratch_text.setPlaceholderText("Jot down rough notes, algebra, or ideas here...")
        self.scratch_text.textChanged.connect(self.save_scratchpad)
        scratch_layout.addWidget(self.scratch_text)
        self.scratch_dock.setWidget(scratch_content)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.scratch_dock)
        self.scratch_dock.hide()
        
        self.statusBar().showMessage("🟩 Correct | 🟨 Partial Credit (Stmt OR Rsn) | 🟥 Incorrect")
        
        self.stack.addWidget(app_widget)
        self.stack.setCurrentIndex(1)

    def init_shortcuts(self):
        self.shortcut_check = QAction(self)
        self.shortcut_check.setShortcut(QKeySequence("Ctrl+Return"))
        self.shortcut_check.triggered.connect(self.check_proof)
        self.addAction(self.shortcut_check)

        self.shortcut_undo = QAction(self)
        self.shortcut_undo.setShortcut(QKeySequence("Ctrl+Z"))
        self.shortcut_undo.triggered.connect(self.undo)
        self.addAction(self.shortcut_undo)

        self.shortcut_redo = QAction(self)
        self.shortcut_redo.setShortcut(QKeySequence("Ctrl+Y"))
        self.shortcut_redo.triggered.connect(self.redo)
        self.addAction(self.shortcut_redo)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.theme_btn.setText("☀️" if self.is_dark_mode else "🌙")
        self.apply_theme()
        self.update_dashboard()
        self.save_state()

    def toggle_focus_mode(self):
        is_focused = not self.splitter.widget(2).isVisible()
        if is_focused:
            self.splitter.widget(2).setVisible(True)
            self.ref_dock.hide()
            self.scratch_dock.hide()
            self.focus_btn.setText("🎯 Focus")
        else:
            self.splitter.widget(2).setVisible(False)
            self.ref_dock.hide()
            self.scratch_dock.hide()
            self.focus_btn.setText("👁️ Exit")

    def change_learning_mode(self, mode):
        if mode != self.learning_mode:
            self.learning_mode = mode
            reply = QMessageBox.question(self, "Change Mode", f"Switching to '{mode}' mode will reset your current progress on this problem. Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                self.mode_combo.setCurrentText(self.learning_mode)
                return
            self.load_problem()

    def update_dashboard(self):
        total_probs = len(self.problems)
        completed = len(self.completed_proofs)
        pct = int((completed / total_probs) * 100) if total_probs > 0 else 0
        self.dashboard.progress_label.setText(f"{pct}% Complete\n({completed}/{total_probs})")
        
        total_time = sum(self.best_times.values())
        self.dashboard.time_label.setText(f"{total_time//60}m {total_time%60}s Spent")
        
        ach_count = len(self.stats.get("achievements", {}))
        self.dashboard.ach_label.setText(f"{ach_count}/4 Achievements")

    def open_custom_problem_dialog(self):
        dialog = CustomProblemDialog(self)
        if dialog.exec():
            new_problem = dialog.get_problem_data()
            self.problems.append(new_problem)
            self.progress_bar.setMaximum(len(self.problems))
            self.save_state()
            self.update_problem_tree()
            self.statusBar().showMessage("Custom problem added!", 3000)

    def import_curriculum(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Curriculum", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    new_probs = json.load(f)
                    self.problems.extend(new_probs)
                    self.save_state()
                    self.update_problem_tree()
                    QMessageBox.information(self, "Imported", f"Added {len(new_probs)} problems!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import: {e}")

    def export_curriculum(self):
        custom_probs = [p for p in self.problems if p not in DEFAULT_PROBLEMS]
        if not custom_probs:
            QMessageBox.information(self, "Export", "No custom problems to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Curriculum", "my_geometry_curriculum.json", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "w") as f:
                json.dump(custom_probs, f, indent=4)
            QMessageBox.information(self, "Exported", f"Exported {len(custom_probs)} problems!")

    def read_proof_aloud(self):
        text_to_read = ""
        for row in range(self.proof_table.rowCount()):
            stmt = self.proof_table.item(row, 0).text() if self.proof_table.item(row, 0) else ""
            combo = self.proof_table.cellWidget(row, 1)
            rsn = combo.currentText() if combo else ""
            if stmt:
                text_to_read += f"Step {row+1}. {stmt}. Reason: {rsn}. "
        
        if text_to_read:
            self.tts.say(text_to_read)
            self.statusBar().showMessage("🔊 Reading proof aloud...", 3000)

    def save_scratchpad(self):
        self.scratchpad_text = self.scratch_text.toPlainText()
        self.save_state()

    # --- Undo / Redo System ---
    def snapshot_table(self):
        state = []
        for r in range(self.proof_table.rowCount()):
            stmt = self.proof_table.item(r, 0).text() if self.proof_table.item(r, 0) else ""
            combo = self.proof_table.cellWidget(r, 1)
            rsn = combo.currentText() if combo else ""
            locked = not (self.proof_table.item(r, 0).flags() & Qt.ItemFlag.ItemIsEditable) if self.proof_table.item(r, 0) else False
            state.append([stmt, rsn, locked])
        self.undo_stack.append(state)
        if len(self.undo_stack) > 50: self.undo_stack.pop(0)
        self.redo_stack.clear()

    def restore_table(self, state):
        self.proof_table.setRowCount(0)
        for stmt, rsn, locked in state:
            self.add_step(stmt, rsn, locked=locked, skip_undo=True)

    def undo(self):
        if not self.undo_stack:
            self.statusBar().showMessage("Nothing to undo", 2000)
            return
        current_state = []
        for r in range(self.proof_table.rowCount()):
            stmt = self.proof_table.item(r, 0).text() if self.proof_table.item(r, 0) else ""
            combo = self.proof_table.cellWidget(r, 1)
            rsn = combo.currentText() if combo else ""
            locked = not (self.proof_table.item(r, 0).flags() & Qt.ItemFlag.ItemIsEditable) if self.proof_table.item(r, 0) else False
            current_state.append([stmt, rsn, locked])
        self.redo_stack.append(current_state)
        prev_state = self.undo_stack.pop()
        self.restore_table(prev_state)

    def redo(self):
        if not self.redo_stack:
            self.statusBar().showMessage("Nothing to redo", 2000)
            return
        current_state = []
        for r in range(self.proof_table.rowCount()):
            stmt = self.proof_table.item(r, 0).text() if self.proof_table.item(r, 0) else ""
            combo = self.proof_table.cellWidget(r, 1)
            rsn = combo.currentText() if combo else ""
            locked = not (self.proof_table.item(r, 0).flags() & Qt.ItemFlag.ItemIsEditable) if self.proof_table.item(r, 0) else False
            current_state.append([stmt, rsn, locked])
        self.undo_stack.append(current_state)
        next_state = self.redo_stack.pop()
        self.restore_table(next_state)

    # --- Timer ---
    def start_timer(self):
        self.elapsed_seconds = 0
        self.timer_running = True
        self.timer.start(1000)

    def stop_timer(self):
        self.timer_running = False
        self.timer.stop()

    def update_timer(self):
        if self.timer_running:
            self.elapsed_seconds += 1
            mins = self.elapsed_seconds // 60
            secs = self.elapsed_seconds % 60
            self.timer_label.setText(f"⏱️ {mins:02d}:{secs:02d}")

    # --- Context Menu ---
    def show_table_context_menu(self, pos):
        index = self.proof_table.indexAt(pos)
        if not index.isValid(): return
        row = index.row()
        item = self.proof_table.item(row, 0)
        is_locked = not (item.flags() & Qt.ItemFlag.ItemIsEditable)

        menu = QMenu(self)
        action_insert = menu.addAction("Insert Step Below")
        action_delete = menu.addAction("Delete Step")
        action_up = menu.addAction("Move Up")
        action_down = menu.addAction("Move Down")
        
        if is_locked:
            action_delete.setEnabled(False)
            if row == 0: action_up.setEnabled(False)
        if row == self.proof_table.rowCount() - 1: action_down.setEnabled(False)

        action = menu.exec(self.proof_table.viewport().mapToGlobal(pos))
        if action == action_insert:
            self.snapshot_table()
            self.proof_table.insertRow(row + 1)
            self.proof_table.setItem(row + 1, 0, QTableWidgetItem(""))
            self.proof_table.setItem(row + 1, 2, QTableWidgetItem(""))
            self.add_reason_combobox(row + 1)
        elif action == action_delete and not is_locked:
            self.snapshot_table()
            self.proof_table.removeRow(row)
        elif action == action_up and row > 0:
            self.move_step(row, row - 1)
        elif action == action_down and row < self.proof_table.rowCount() - 1:
            self.move_step(row, row + 1)

    def move_step(self, from_row, to_row):
        if from_row < 0 or to_row < 0 or from_row >= self.proof_table.rowCount() or to_row >= self.proof_table.rowCount(): return
        self.snapshot_table()
        stmt1 = self.proof_table.takeItem(from_row, 0)
        stmt2 = self.proof_table.takeItem(to_row, 0)
        self.proof_table.setItem(from_row, 0, stmt2)
        self.proof_table.setItem(to_row, 0, stmt1)
        
        combo1 = self.proof_table.cellWidget(from_row, 1)
        combo2 = self.proof_table.cellWidget(to_row, 1)
        if combo1 and combo2:
            text1, text2 = combo1.currentText(), combo2.currentText()
            combo1.setEditText(text2)
            combo2.setEditText(text1)
            
        self.update_row_status(from_row)
        self.update_row_status(to_row)

    # --- State ---
    def save_state(self):
        current_table = []
        for row in range(self.proof_table.rowCount()):
            stmt = self.proof_table.item(row, 0).text() if self.proof_table.item(row, 0) else ""
            combo = self.proof_table.cellWidget(row, 1)
            rsn = combo.currentText() if combo else ""
            current_table.append([stmt, rsn])
            
        self.saved_tables[str(self.current_problem_index)] = current_table
        state = {
            "completed": list(self.completed_proofs),
            "bookmarked": list(self.bookmarked_proofs),
            "current_problem": self.current_problem_index,
            "tables": self.saved_tables,
            "stats": self.stats,
            "best_times": self.best_times,
            "custom_problems": [p for p in self.problems if p not in DEFAULT_PROBLEMS],
            "is_dark_mode": self.is_dark_mode,
            "scratchpad": self.scratchpad_text,
            "learning_mode": self.learning_mode
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(state, f)
        self.statusBar().showMessage("💾 Saved! | 🟩 Correct | 🟨 Partial Credit | 🟥 Incorrect", 2000)
        self.update_dashboard()

    def load_state(self):
        if not os.path.exists(SAVE_FILE): return
        try:
            with open(SAVE_FILE, "r") as f: state = json.load(f)
            self.completed_proofs = set(state.get("completed", []))
            self.bookmarked_proofs = set(state.get("bookmarked", []))
            self.current_problem_index = state.get("current_problem", 0)
            self.saved_tables = state.get("tables", {})
            self.stats = state.get("stats", {"mistakes": {}, "achievements": {}})
            self.best_times = state.get("best_times", {})
            custom_probs = state.get("custom_problems", [])
            self.problems.extend(custom_probs)
            self.is_dark_mode = state.get("is_dark_mode", False)
            self.scratchpad_text = state.get("scratchpad", "")
            self.scratch_text.setText(self.scratchpad_text)
            self.learning_mode = state.get("learning_mode", "Normal")
            self.mode_combo.setCurrentText(self.learning_mode)
            self.theme_btn.setText("☀️" if self.is_dark_mode else "🌙")
            self.apply_theme()
            self.update_dashboard()
        except Exception:
            pass

    def closeEvent(self, event):
        self.save_state()
        event.accept()

    # --- UI Helpers ---
    def insert_point_from_diagram(self, point_name):
        widget = QApplication.focusWidget()
        if isinstance(widget, QTableWidget):
            item = widget.currentItem()
            if item and item.column() == 0:
                item.setText(item.text() + point_name)
                self.on_row_changed(item, None)
        elif hasattr(widget, "insert"):
            widget.insert(point_name)

    def insert_symbol(self, symbol):
        widget = QApplication.focusWidget()
        if isinstance(widget, QTableWidget):
            item = widget.currentItem()
            if item and item.column() == 0:
                item.setText(item.text() + symbol)
                self.on_row_changed(item, None)
        elif hasattr(widget, "insert"):
            widget.insert(symbol)

    def add_reason_combobox(self, row):
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItems(STANDARD_REASONS)
        combo.lineEdit().setPlaceholderText("Select reason...")
        combo.currentTextChanged.connect(lambda text: self.update_reference_dock(text))
        combo.currentTextChanged.connect(lambda: self.update_row_status(row))
        self.proof_table.setCellWidget(row, 1, combo)

    def update_reference_dock(self, reason_text):
        if reason_text in THEOREM_DEFINITIONS:
            self.ref_text.setText(f"<h3>{reason_text}</h3><p>{THEOREM_DEFINITIONS[reason_text]}</p>")
        elif reason_text == "":
            self.ref_text.setText("<i>Select a reason to see its definition.</i>")
        else:
            self.ref_text.setText(f"<i>No definition found for '{reason_text}'.</i>")

    def add_step(self, text="", reason="", locked=False, skip_undo=False):
        if not skip_undo:
            self.snapshot_table()
        row_count = self.proof_table.rowCount()
        self.proof_table.insertRow(row_count)
        
        item = QTableWidgetItem(text)
        if locked:
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setBackground(QColor("#cccccc"))
        self.proof_table.setItem(row_count, 0, item)
        
        self.add_reason_combobox(row_count)
        combo = self.proof_table.cellWidget(row_count, 1)
        
        status_item = QTableWidgetItem("")
        status_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.proof_table.setItem(row_count, 2, status_item)
        
        if reason: combo.setEditText(reason)
        if locked:
            combo.setEnabled(False)
            combo.setStyleSheet("background-color: #cccccc;")
            status_item.setText("🔒")

    def delete_step(self):
        current_row = self.proof_table.currentRow()
        if current_row >= 0:
            item = self.proof_table.item(current_row, 0)
            if item and (item.flags() & Qt.ItemFlag.ItemIsEditable):
                self.snapshot_table()
                self.proof_table.removeRow(current_row)

    def auto_format_text(self, item):
        if item.column() == 0 and (item.flags() & Qt.ItemFlag.ItemIsEditable):
            text = item.text()
            if text.count("(") != text.count(")") or re.search(r'∠[A-Z](?![A-Z])', text):
                item.setForeground(QColor("#e67e22")) # Orange for syntax warning
            else:
                item.setForeground(QColor("black") if not self.is_dark_mode else QColor("white"))
                
            if any(k in text.lower() for k in ["angle", "triangle", "cong", "equal"]):
                self.proof_table.blockSignals(True)
                new_text = re.sub(r'(?i)\bm\s*angle\b', 'm∠', text)
                new_text = re.sub(r'(?i)\bmeasure of angle\b', 'm∠', new_text)
                new_text = re.sub(r'(?i)\bangle\b', '∠', new_text)
                new_text = re.sub(r'(?i)\btriangle\b', '△', new_text)
                new_text = re.sub(r'(?i)\bis congruent to\b', '≅', new_text)
                new_text = re.sub(r'(?i)\bcongruent to\b', '≅', new_text)
                new_text = re.sub(r'(?i)\bcongruent\b', '≅', new_text)
                new_text = re.sub(r'(?i)\bis equal to\b', '=', new_text)
                item.setText(new_text)
                self.proof_table.blockSignals(False)
            self.update_row_status(item.row())

    def on_row_changed(self, current, previous):
        if not current: return
        text = current.text()
        self.diagram_widget.set_highlights_from_text(text)
        if current.column() == 1:
            combo = self.proof_table.cellWidget(current.row(), 1)
            if combo: self.update_reference_dock(combo.currentText())

    # --- Validation & Math Normalization ---
    def normalize_text(self, text):
        text = text.strip().lower()
        text = text.replace(" ", "").replace("∠", "<").replace("≅", "~=").replace("△", "^")
        return text

    def update_row_status(self, row):
        stmt_item = self.proof_table.item(row, 0)
        rsn_combo = self.proof_table.cellWidget(row, 1)
        status_item = self.proof_table.item(row, 2)
        if not stmt_item or not rsn_combo or not status_item: return
        if status_item.text() == "🔒": return

        user_stmt = self.normalize_text(stmt_item.text())
        user_rsn = self.normalize_text(rsn_combo.currentText())
        if not user_stmt or not user_rsn:
            status_item.setText("")
            return

        problem = self.problems[self.current_problem_index]
        matched = False
        for corr_stmt, corr_rsn in problem["correct_steps"]:
            if math_equiv(user_stmt, self.normalize_text(corr_stmt)) and user_rsn == self.normalize_text(corr_rsn):
                matched = True
                break

        if matched:
            status_item.setText("✅")
            status_item.setForeground(QColor("#27ae60"))
        else:
            status_item.setText("❌")
            status_item.setForeground(QColor("#e74c3c"))

    # --- Problem Nav & Tree ---
    def load_problem(self):
        self.stop_timer()
        self.undo_stack.clear()
        self.redo_stack.clear()
        if self.current_problem_index >= len(self.problems):
            self.current_problem_index = 0
        problem = self.problems[self.current_problem_index]
        self.title_label.setText(problem["title"])
        self.given_label.setText(f"<b>Given:</b> {problem['given']}")
        self.prove_label.setText(f"<b>To Prove:</b> {problem['to_prove']}")
        self.diagram_widget.load_data(problem["graphics_data"])
        
        self.proof_table.setRowCount(0)
        self.hints_used = 0
        self.mistakes_this_proof = 0
        self.hint_btn.setText(f"💡 Hint ({self.hints_used})")
        
        # Handle Learning Modes
        if self.learning_mode == "Fill Reasons":
            for stmt, rsn in problem["given_steps"]:
                self.add_step(stmt, rsn, locked=True)
            for stmt, rsn in problem["correct_steps"]:
                if (stmt, rsn) not in problem["given_steps"]:
                    self.add_step(stmt, "", locked=True) # Statement locked, Reason blank
        elif self.learning_mode == "Fill Statements":
            for stmt, rsn in problem["given_steps"]:
                self.add_step(stmt, rsn, locked=True)
            for stmt, rsn in problem["correct_steps"]:
                if (stmt, rsn) not in problem["given_steps"]:
                    self.add_step("", rsn, locked=False) # Statement blank, Reason locked
                    # Lock the reason combo box manually
                    row_idx = self.proof_table.rowCount() - 1
                    combo = self.proof_table.cellWidget(row_idx, 1)
                    combo.setEnabled(False)
                    combo.setStyleSheet("background-color: #cccccc;")
                    self.proof_table.item(row_idx, 2).setText("🔒")
        else:
            # Normal Mode
            for stmt, rsn in problem["given_steps"]:
                self.add_step(stmt, rsn, locked=True)
                
            saved_data = self.saved_tables.get(str(self.current_problem_index), [])
            if saved_data and len(saved_data) > len(problem["given_steps"]):
                for stmt, rsn in saved_data[len(problem["given_steps"]):]:
                    self.add_step(stmt, rsn)
            else:
                self.add_step()
                
        self.undo_stack.clear()
            
        self.update_problem_tree()
        self.update_progress_bar()
        
        if self.current_problem_index not in self.completed_proofs:
            self.start_timer()
        else:
            best = self.best_times.get(str(self.current_problem_index), 0)
            self.timer_label.setText(f"✅ Best: {best//60:02d}:{best%60:02d}")

    def update_problem_tree(self):
        search_text = self.search_input.text().lower()
        self.problem_tree.clear()
        
        categories = defaultdict(list)
        for i, prob in enumerate(self.problems):
            if search_text in prob["title"].lower():
                categories[prob["category"]].append(i)
                
        for cat, indices in categories.items():
            completed_in_cat = sum(1 for i in indices if i in self.completed_proofs)
            cat_item = QTreeWidgetItem(self.problem_tree, [f"📁 {cat} ({completed_in_cat}/{len(indices)})"])
            cat_item.setExpanded(True)
            
            for i in indices:
                prob = self.problems[i]
                prefix = "🟢" if i in self.completed_proofs else "⚪"
                if i in self.bookmarked_proofs: prefix = "⭐"
                
                time_str = f"({self.best_times.get(str(i), 0)}s)" if i in self.completed_proofs and str(i) in self.best_times else ""
                item_text = f"{prefix} {prob['title']} {time_str}"
                
                child = QTreeWidgetItem(cat_item, [item_text])
                child.setData(0, Qt.ItemDataRole.UserRole, i)
                
                if i == self.current_problem_index:
                    self.problem_tree.setCurrentItem(child)

    def change_problem_from_tree(self, item, column):
        index = item.data(0, Qt.ItemDataRole.UserRole)
        if index is not None and index != self.current_problem_index:
            self.save_state()
            self.current_problem_index = index
            self.load_problem()

    def update_progress_bar(self):
        self.progress_bar.setMaximum(len(self.problems))
        self.progress_bar.setValue(len(self.completed_proofs))

    def show_stats(self):
        dialog = StatsDialog(self.stats, self)
        dialog.exec()

    # --- Checking & Achievements ---
    def check_proof(self):
        problem = self.problems[self.current_problem_index]
        correct_steps = problem["correct_steps"]
        given_count = len(problem["given_steps"])
        all_correct = True
        used_indices = set()

        for row in range(given_count, self.proof_table.rowCount()):
            statement_item = self.proof_table.item(row, 0)
            reason_combo = self.proof_table.cellWidget(row, 1)
            if not statement_item or not reason_combo: continue

            user_stmt = self.normalize_text(statement_item.text())
            user_rsn = self.normalize_text(reason_combo.currentText())

            stmt_matched = False
            rsn_matched = False
            fully_matched = False
            
            for i, step in enumerate(correct_steps):
                if i not in used_indices:
                    corr_stmt = self.normalize_text(step[0])
                    corr_rsn = self.normalize_text(step[1])
                    
                    if math_equiv(user_stmt, corr_stmt) and user_rsn == corr_rsn:
                        fully_matched = True
                        used_indices.add(i)
                        break
                    elif math_equiv(user_stmt, corr_stmt):
                        stmt_matched = True
                    elif user_rsn == corr_rsn:
                        rsn_matched = True

            if fully_matched:
                statement_item.setBackground(QColor("#C8E6C9")) # Green
                reason_combo.setStyleSheet("background-color: #C8E6C9;")
            elif stmt_matched or rsn_matched:
                all_correct = False
                self.mistakes_this_proof += 1
                statement_item.setBackground(QColor("#FFF9C4")) # Yellow
                reason_combo.setStyleSheet("background-color: #FFF9C4;")
                if user_rsn: self.stats["mistakes"][user_rsn] = self.stats["mistakes"].get(user_rsn, 0) + 1
            else:
                all_correct = False
                self.mistakes_this_proof += 1
                statement_item.setBackground(QColor("#FFCDD2")) # Red
                reason_combo.setStyleSheet("background-color: #FFCDD2;")
                if user_rsn: self.stats["mistakes"][user_rsn] = self.stats["mistakes"].get(user_rsn, 0) + 1

        required_steps = len(correct_steps) + given_count
        if all_correct and self.proof_table.rowCount() == required_steps:
            self.completed_proofs.add(self.current_problem_index)
            self.update_progress_bar()
            self.save_state()
            self.stop_timer()
            
            if len(self.completed_proofs) == 1:
                self.unlock_achievement("First Steps")
            if self.elapsed_seconds < 60:
                self.unlock_achievement("Speed Demon")
            if self.mistakes_this_proof == 0 and self.hints_used == 0:
                self.unlock_achievement("Flawless")
            if len(self.completed_proofs) == len(self.problems):
                self.unlock_achievement("Master")
                
            p_idx_str = str(self.current_problem_index)
            if p_idx_str not in self.best_times or self.elapsed_seconds < self.best_times[p_idx_str]:
                self.best_times[p_idx_str] = self.elapsed_seconds
                QMessageBox.information(self, "New Record!", f"Proof complete! New best time: {self.elapsed_seconds//60:02d}:{self.elapsed_seconds%60:02d}")
            else:
                QMessageBox.information(self, "Perfect!", "Proof is logically sound and complete.")
            
            self.update_problem_tree()
            self.timer_label.setText(f"✅ Best: {self.best_times[p_idx_str]//60:02d}:{self.best_times[p_idx_str]%60:02d}")
        else:
            QMessageBox.warning(self, "Keep Trying", "Some steps are incorrect, missing, or out of order.\n🟩 Correct | 🟨 Partial Credit | 🟥 Incorrect")

    def unlock_achievement(self, name):
        if not self.stats.get("achievements", {}).get(name, False):
            self.stats.setdefault("achievements", {})[name] = True
            QMessageBox.information(self, "🏆 Achievement Unlocked!", f"You unlocked: {name}")

    def show_hint(self):
        problem = self.problems[self.current_problem_index]
        correct_steps = problem["correct_steps"]
        given_count = len(problem["given_steps"])
        
        # Find the first empty or incorrect row to hint
        hint_index = -1
        for row in range(given_count, self.proof_table.rowCount()):
            stmt_item = self.proof_table.item(row, 0)
            rsn_combo = self.proof_table.cellWidget(row, 1)
            
            is_empty = not stmt_item or not stmt_item.text().strip() or not rsn_combo or not rsn_combo.currentText().strip()
            is_wrong = False
            if not is_empty:
                user_stmt = self.normalize_text(stmt_item.text())
                user_rsn = self.normalize_text(rsn_combo.currentText())
                target_step_index = row - given_count
                if target_step_index < len(correct_steps):
                    corr_stmt, corr_rsn = correct_steps[target_step_index]
                    if not (math_equiv(user_stmt, self.normalize_text(corr_stmt)) and user_rsn == self.normalize_text(corr_rsn)):
                        is_wrong = True
            
            if is_empty or is_wrong:
                hint_index = row
                break
                
        if hint_index == -1:
            return

        target_step_index = hint_index - given_count
        if target_step_index >= len(correct_steps):
            return

        corr_stmt, corr_rsn = correct_steps[target_step_index]
        stmt_item = self.proof_table.item(hint_index, 0)
        rsn_combo = self.proof_table.cellWidget(hint_index, 1)
        
        # Incremental Hint Logic
        stmt_empty = not stmt_item.text().strip()
        rsn_empty = not rsn_combo.currentText().strip()
        
        if stmt_empty and rsn_empty:
            # Hint 1: Give the reason
            rsn_combo.setEditText(corr_rsn)
            rsn_combo.setStyleSheet("background-color: #BBDEFB;")
            self.statusBar().showMessage("💡 Hint 1: Reason revealed. Now try to figure out the statement.", 5000)
        elif not rsn_empty and stmt_empty:
            # Hint 2: Give the statement
            stmt_item.setText(corr_stmt)
            stmt_item.setBackground(QColor("#BBDEFB"))
            self.statusBar().showMessage("💡 Hint 2: Statement revealed. Check your work!", 5000)
        else:
            # Hint 3: Force fix the step entirely
            stmt_item.setText(corr_stmt)
            rsn_combo.setEditText(corr_rsn)
            stmt_item.setBackground(QColor("#BBDEFB"))
            rsn_combo.setStyleSheet("background-color: #BBDEFB;")
            self.statusBar().showMessage("💡 Hint 3: Step fully corrected.", 5000)
            
        self.hints_used += 1
        self.hint_btn.setText(f"💡 Hint ({self.hints_used})")
        self.update_row_status(hint_index)

    def animate_solution(self):
        reply = QMessageBox.question(self, "Show Solution", "This will automatically fill in the rest of the proof. Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return
        
        self.snapshot_table()
        problem = self.problems[self.current_problem_index]
        given_count = len(problem["given_steps"])
        while self.proof_table.rowCount() > given_count:
            self.proof_table.removeRow(self.proof_table.rowCount() - 1)
            
        self.solution_step = 0
        self.solution_timer.timeout.connect(self.fill_next_solution_step)
        self.solution_timer.start(800)

    def fill_next_solution_step(self):
        problem = self.problems[self.current_problem_index]
        correct_steps = problem["correct_steps"]
        given_count = len(problem["given_steps"])
        
        if self.solution_step >= len(correct_steps):
            self.solution_timer.stop()
            return
            
        statement, reason = correct_steps[self.solution_step]
        self.add_step(statement, reason)
        self.update_row_status(self.proof_table.rowCount() - 1)
        self.solution_step += 1

    # --- Exporting ---
    def export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Proof to PDF", f"proof_{self.current_problem_index+1}.pdf", "PDF Files (*.pdf)")
        if not file_path: return
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)
        
        html = f"""
        <html><head><style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ text-align: center; text-decoration: underline; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style></head><body>
        <h1>{self.title_label.text()}</h1>
        <p><b>Given:</b> {self.given_label.text().replace('<b>Given:</b> ', '')}</p>
        <p><b>To Prove:</b> {self.prove_label.text().replace('<b>To Prove:</b> ', '')}</p>
        <table>
            <tr><th style="width:10%">Step</th><th style="width:60%">Statement</th><th style="width:30%">Reason</th></tr>
        """
        for row in range(self.proof_table.rowCount()):
            stmt = self.proof_table.item(row, 0).text() if self.proof_table.item(row, 0) else ""
            combo = self.proof_table.cellWidget(row, 1)
            rsn = combo.currentText() if combo else ""
            html += f"<tr><td>{row+1}</td><td>{stmt}</td><td>{rsn}</td></tr>"
            
        html += "</table></body></html>"
        
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)
        self.statusBar().showMessage("📄 PDF Exported!", 3000)

    def export_png(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Diagram to PNG", "diagram.png", "PNG Files (*.png)")
        if not file_path: return
        
        pixmap = self.diagram_widget.grab()
        pixmap.save(file_path, "PNG")
        self.statusBar().showMessage("🖼️ Diagram Exported!", 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GeometryProofApp()
    window.show()
    sys.exit(app.exec())